from typing import Protocol, Sequence
from domain.entidad_colaboradora import EntidadColaboradora

class EntidadColaboradoraRepositoryPort(Protocol):
    def get_by_provincia(self, provincia: str) -> Sequence[EntidadColaboradora]: ...
