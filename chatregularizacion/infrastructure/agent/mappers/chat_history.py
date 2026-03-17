from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ChatHistoryMapper:
    @staticmethod
    def to_messages(history: list[dict[str, str]]) -> list[BaseMessage]:
        messages: list[BaseMessage] = []
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages

    @staticmethod
    def to_history(messages: list[BaseMessage]) -> list[dict[str, str]]:
        history: list[dict[str, str]] = []
        for message in messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": str(message.content)})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": str(message.content)})
        return history

    @staticmethod
    def last_ai_text(messages: list[BaseMessage]) -> str:
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return str(message.content)
        return "I could not generate a response."
