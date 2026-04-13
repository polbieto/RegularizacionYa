from typing import Any, Sequence, cast

from sqlalchemy import select

from domain.document_knowledge_base import ProductBaseKnowledge
from domain.ports.document_repository_port import (
    DocumentRepositoryPort,
)


class SqlAlchemyDocumentRepositoryAdapter(DocumentRepositoryPort):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def search_knowledge_by_embedding(
        self,
        query_embedding: list[float],
        limit: int,
        max_distance: float = 0.35,
    ) -> Sequence[ProductBaseKnowledge]:
        with self.session_factory() as session:
            embedding = cast(Any, ProductBaseKnowledge.embedding)
            distance = embedding.cosine_distance(query_embedding)

            return session.scalars(
                select(ProductBaseKnowledge)
                .where(distance < max_distance)
                .order_by(distance)
                .limit(limit)
            ).all()
