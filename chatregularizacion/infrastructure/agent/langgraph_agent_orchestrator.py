from collections.abc import Callable
from typing import Annotated, Any, Optional, TypedDict

from application.agent_orchestrator import AgentOrchestrator
from infrastructure.agent.mappers.chat_history import ChatHistoryMapper
from infrastructure.agent.ports.tool_runtime import ToolRuntimePort
from infrastructure.agent.prompts.system import build_default_system_prompt
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

import logging

logger = logging.getLogger(__name__)

_REWRITE_PROMPT = (
    "Eres un reformulador de consultas de búsqueda. "
    "Dado el contexto de una conversación sobre la Regularización Extraordinaria "
    "de personas migrantes en España, reformula la última pregunta del usuario "
    "como una consulta de búsqueda precisa y autónoma.\n\n"
    "Reglas:\n"
    "- Usa terminología técnica del ámbito de extranjería: arraigo, protección "
    "internacional, vía familiar, vía laboral, vía de vulnerabilidad, antecedentes "
    "penales, antecedentes policiales, padrón, NIE, asilo, tarjeta roja, unidad "
    "familiar, cédula de inscripción, apostilla, Mercurio, BOE, etc.\n"
    "- La consulta debe ser comprensible sin la conversación previa.\n"
    "- Devuelve SOLO la consulta reformulada, sin explicaciones ni comillas.\n"
)


class AgentState(TypedDict):
    client_id: str
    messages: Annotated[list[BaseMessage], add_messages]


class LangGraphAgentOrchestrator(AgentOrchestrator):
    def __init__(
        self,
        llm_with_tools: Any,
        tool_runtime: ToolRuntimePort | None,
        history_mapper: Optional[ChatHistoryMapper] = None,
        system_prompt_builder: Callable[[str], str] | None = None,
        retriever: Callable[[str], str] | None = None,
    ):
        self.llm_with_tools = llm_with_tools
        self.tool_runtime = tool_runtime
        self.history_mapper = history_mapper or ChatHistoryMapper()
        self.system_prompt_builder = (
            system_prompt_builder or build_default_system_prompt
        )
        self.retriever = retriever
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", self._agent_node)
        graph_builder.add_node("tools", self._tool_node)
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges(
            "agent",
            self._route_after_agent,
            {"tools": "tools", "end": END},
        )
        graph_builder.add_edge("tools", "agent")
        return graph_builder.compile()

    @staticmethod
    def _route_after_agent(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and getattr(
            last_message, "tool_calls", None
        ):
            return "tools"
        return "end"

    async def _rewrite_query(
        self, user_message: str, messages: list[BaseMessage]
    ) -> str:
        """Rewrite user message into a precise search query using conversation context."""
        recent_turns = []
        for msg in messages[-6:]:
            if isinstance(msg, HumanMessage):
                recent_turns.append(f"Usuario: {msg.content}")
            elif isinstance(msg, AIMessage) and msg.content:
                # Truncate long AI responses to save tokens
                snippet = msg.content[:300]
                recent_turns.append(f"Asistente: {snippet}")

        # First message in conversation — no rewriting needed
        human_count = sum(1 for m in messages if isinstance(m, HumanMessage))
        if human_count <= 1:
            return user_message

        conversation_context = "\n".join(recent_turns)
        rewrite_input = (
            f"Conversación reciente:\n{conversation_context}\n\n"
            f"Última pregunta del usuario: {user_message}"
        )

        try:
            response = await self.llm_with_tools.ainvoke([
                SystemMessage(content=_REWRITE_PROMPT),
                HumanMessage(content=rewrite_input),
            ])
            rewritten = response.content.strip()
            if rewritten:
                logger.info(
                    "Query rewritten: '%s' -> '%s'", user_message, rewritten
                )
                return rewritten
        except Exception:
            logger.warning("Query rewriting failed, using original message.")

        return user_message

    async def _agent_node(self, state: AgentState) -> dict[str, list[BaseMessage]]:
        retrieved_context = ""
        if self.retriever:
            last_user_message = self._last_user_message(state["messages"])
            if last_user_message:
                retrieval_query = await self._rewrite_query(
                    last_user_message, state["messages"]
                )
                retrieved_context = self.retriever(retrieval_query)

        system_content = self.system_prompt_builder(state["client_id"])
        system_content += (
            "\n\n---\nFRAGMENTOS RECUPERADOS DEL MANUAL:\n"
            f"{retrieved_context or 'No se encontraron fragmentos relevantes.'}"
            "\n---"
        )

        request_messages = [
            SystemMessage(content=system_content),
            *state["messages"],
        ]

        try:
            response = await self.llm_with_tools.ainvoke(request_messages)
            return {"messages": [response]}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Lo siento, en este momento estoy experimentando problemas técnicos y no puedo responder a tu consulta. Por favor, inténtalo de nuevo en unos instantes."
                        )
                    )
                ]
            }

    def _tool_node(self, state: AgentState) -> dict[str, list[BaseMessage]]:
        if self.tool_runtime is None:
            return {"messages": []}

        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": []}

        tool_messages: list[BaseMessage] = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = dict(tool_call.get("args", {}))
            try:
                result = self.tool_runtime.execute(
                    tool_name, tool_args, state["client_id"]
                )
            except Exception:
                result = "Tool execution failed."

            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )
        return {"messages": tool_messages}

    @staticmethod
    def _last_user_message(messages: list[BaseMessage]) -> str | None:
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
        return None

    async def process_message(
        self,
        message: str,
        client_id: str,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, list[dict[str, str]]]:
        prior_messages = self.history_mapper.to_messages(history or [])[-20:]
        result = await self.graph.ainvoke(
            {
                "client_id": client_id,
                "messages": [*prior_messages, HumanMessage(content=message)],
            }
        )
        final_messages = result.get("messages", [])
        response_text = self.history_mapper.last_ai_text(final_messages)
        updated_history = self.history_mapper.to_history(final_messages)
        return response_text, updated_history[-20:]
