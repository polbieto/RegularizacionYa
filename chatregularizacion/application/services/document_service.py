import logging

from application.ports.embedding_provider_port import (
    EmbeddingProviderPort,
)
from domain.document_knowledge_base import ProductBaseKnowledge
from domain.ports.document_repository_port import (
    DocumentRepositoryPort,
)

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepositoryPort,
        embedding_provider: EmbeddingProviderPort,
    ):
        self._repository = repository
        self._embedding_provider = embedding_provider

    def search_documents(self, query: str, limit: int = 7) -> str:
        logger.info("Searching for documents. limit=%s, query=%s", limit, query)
        query_embedding = self._embedding_provider.embed_query(query)

        knowledge_results = self._repository.search_knowledge_by_embedding(
            query_embedding=query_embedding, limit=limit
        )

        formatted_results = [
            self._format_result(item) for item in knowledge_results
        ]

        logger.debug("Retrieved %s documents.", len(knowledge_results))
        return "\n\n---\n\n".join(formatted_results) if formatted_results else ""

    @staticmethod
    def _format_result(item: ProductBaseKnowledge) -> str:
        meta = item.metadata_ or {}
        breadcrumb_parts = []
        for key in ("section", "subsection", "subsubsection", "subsubsubsection"):
            value = meta.get(key)
            if value:
                breadcrumb_parts.append(value)
        breadcrumb = " > ".join(breadcrumb_parts)
        header = f"[Fuente: {breadcrumb}]\n" if breadcrumb else ""
        return f"{header}{item.content}"
