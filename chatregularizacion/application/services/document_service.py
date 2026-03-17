import logging

from chatregularizacion.application.ports.embedding_provider_port import (
    EmbeddingProviderPort,
)
from chatregularizacion.domain.ports.document_repository_port import (
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

    def search_documents(self, query: str, limit: int = 5) -> str:
        logger.info(f"Searching for documents semantic match. limit={limit}")
        query_embedding = self._embedding_provider.embed_query(query)

        knowledge_results = self._repository.search_knowledge_by_embedding(
            query_embedding=query_embedding, limit=limit
        )

        formatted_results = []
        for item in knowledge_results:
            formatted_results.append(
                f"Content: {item.content}\nMetadata: {item.metadata_}"
            )

        logger.debug(f"Retrieved {len(knowledge_results)} documents.")
        return "\n\n".join(formatted_results)
