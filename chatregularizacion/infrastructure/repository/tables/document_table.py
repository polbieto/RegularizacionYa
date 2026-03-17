import uuid

from sqlalchemy import Column, DateTime, MetaData, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID


def table_builder(metadata: MetaData) -> Table:
    return Table(
        "document",
        metadata,
        Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column("name", Text, nullable=False),
        Column("created_at", DateTime(timezone=True), server_default=func.now()),
    )
