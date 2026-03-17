from application.agent_orchestrator import AgentOrchestrator as DomainAgentOrchestrator
from infrastructure.repository.sqlalchemy_document_repository import \
    SqlAlchemyDocumentRepositoryAdapter

from infrastructure.google_embedding_provider import GoogleGenerativeAIEmbeddingProvider
from application.services.document_service import DocumentService
from infrastructure.agent.tools_registry import build_tools

from infrastructure.agent.langgraph_agent_orchestrator import LangGraphAgentOrchestrator
from infrastructure.agent.llm_provider import build_ollama_llm_with_tools
from infrastructure.agent.mappers.chat_history import ChatHistoryMapper
from infrastructure.agent.tool_runtime import LangChainToolRuntime



def build_agent_orchestrator(session_factory) -> DomainAgentOrchestrator:
    
    embedding_provider = GoogleGenerativeAIEmbeddingProvider()
    document_repository = SqlAlchemyDocumentRepositoryAdapter(session_factory)
    document_service = DocumentService(document_repository, embedding_provider=embedding_provider)
    
    tools = build_tools(
        document_service=document_service,
    )
    

    llm_with_tools = build_ollama_llm_with_tools(tools)
    tool_runtime = LangChainToolRuntime(tools)
    return LangGraphAgentOrchestrator(
        llm_with_tools=llm_with_tools,
        tool_runtime=tool_runtime,
        history_mapper=ChatHistoryMapper(),
    )
