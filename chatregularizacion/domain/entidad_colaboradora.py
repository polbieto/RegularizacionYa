from dataclasses import dataclass
from typing import Optional

@dataclass(kw_only=True)
class EntidadColaboradora:
    nombre: str
    provincia: str
    web_page: Optional[str] = None
