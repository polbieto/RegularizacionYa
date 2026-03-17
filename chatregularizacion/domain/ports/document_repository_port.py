from typing import Protocol, Sequence

from domain.document_knowledge_base import ProductBaseKnowledge


class DocumentRepositoryPort(Protocol):
    def search_knowledge_by_embedding(
        self, query_embedding: list[float], limit: int
    ) -> Sequence[ProductBaseKnowledge]: ...
