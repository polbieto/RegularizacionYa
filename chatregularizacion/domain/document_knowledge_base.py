from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from chatregularizacion.domain.document import Document


@dataclass(kw_only=True)
class ProductBaseKnowledge:
    document_id: uuid.UUID
    content: str
    embedding: list[float] | None = None
    metadata_: dict | None = None
    id: uuid.UUID | None = None
    created_at: datetime | None = None

    document: Document = field(init=False, default=None, repr=False)
