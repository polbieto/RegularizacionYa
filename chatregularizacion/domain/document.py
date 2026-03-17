import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True)
class Document:
    id: uuid.UUID
    name: str
    created_at: Optional[datetime] = None
