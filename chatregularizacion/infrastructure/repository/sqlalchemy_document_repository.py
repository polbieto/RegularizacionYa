from typing import Any, Sequence, cast

from sqlalchemy import select

from chatregularizacion.domain.document_knowledge_base import ProductBaseKnowledge
from chatregularizacion.domain.ports.document_repository_port import (
    DocumentRepositoryPort,
)


class SqlAlchemyDocumentRepositoryAdapter(DocumentRepositoryPort):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def search_knowledge_by_embedding(
        self, query_embedding: list[float], limit: int
    ) -> Sequence[ProductBaseKnowledge]:
        with self.session_factory() as session:
            embedding = cast(Any, ProductBaseKnowledge.embedding)

            return session.scalars(
                select(ProductBaseKnowledge)
                .order_by(embedding.l2_distance(query_embedding))
                .limit(limit)
            ).all()
