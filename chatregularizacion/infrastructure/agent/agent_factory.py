from application.agent_orchestrator import AgentOrchestrator as DomainAgentOrchestrator
from infrastructure.repository.sqlalchemy_document_repository import \
    SqlAlchemyDocumentRepositoryAdapter

from infrastructure.google_embedding_provider import GoogleGenerativeAIEmbeddingProvider
from application.services.document_service import DocumentService
from infrastructure.agent.langgraph_agent_orchestrator import LangGraphAgentOrchestrator
from infrastructure.agent.llm_provider import build_llm
from infrastructure.agent.mappers.chat_history import ChatHistoryMapper


def build_agent_orchestrator(session_factory) -> DomainAgentOrchestrator:
    embedding_provider = GoogleGenerativeAIEmbeddingProvider()
    document_repository = SqlAlchemyDocumentRepositoryAdapter(session_factory)
    document_service = DocumentService(
        document_repository, embedding_provider=embedding_provider
    )

    llm = build_llm()
    return LangGraphAgentOrchestrator(
        llm_with_tools=llm,
        tool_runtime=None,
        history_mapper=ChatHistoryMapper(),
        retriever=document_service.search_documents,
    )
