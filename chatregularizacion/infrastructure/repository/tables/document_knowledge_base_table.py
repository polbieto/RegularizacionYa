import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, MetaData, Table, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID


def table_builder(metadata: MetaData) -> Table:
    return Table(
        "document_knowledge_base",
        metadata,
        Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column(
            "document",
            UUID(as_uuid=True),
            ForeignKey("document.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("content", Text, nullable=False),
        Column("embedding", Vector),
        Column("metadata", JSONB),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
    )
