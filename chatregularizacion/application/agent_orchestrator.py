from abc import ABC, abstractmethod
from typing import Optional


class AgentOrchestrator(ABC):
    @abstractmethod
    async def process_message(
        self,
        message: str,
        client_id: str,
        history: Optional[list[dict[str, str]]] = [],
    ) -> tuple[str, list[dict[str, str]]]:
        raise NotImplementedError
