from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, registry, relationship

from domain.document import Document
from domain.document_knowledge_base import ProductBaseKnowledge
from infrastructure.repository.tables.document_knowledge_base_table import (
    table_builder as builder_document_kb,
)
from infrastructure.repository.tables.document_table import (
    table_builder as builder_document,
)

Base = declarative_base()
mapper_registry = registry(metadata=Base.metadata)
metadata: MetaData = mapper_registry.metadata


def start_mappers() -> None:
    if mapper_registry.mappers:
        return

    document = builder_document(metadata)
    document_knowledge_base = builder_document_kb(metadata)

    mapper_registry.map_imperatively(Document, document)

    mapper_registry.map_imperatively(
        ProductBaseKnowledge,
        document_knowledge_base,
        properties={
            "document_id": document_knowledge_base.c.document,
            "metadata_": document_knowledge_base.c.metadata,
            "document": relationship(Document),
        },
    )
