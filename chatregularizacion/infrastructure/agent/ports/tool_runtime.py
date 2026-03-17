from abc import ABC, abstractmethod
from typing import Any


class ToolRuntimePort(ABC):
    @abstractmethod
    def execute(self, tool_name: str, tool_args: dict[str, Any], client_id: str) -> str:
        raise NotImplementedError
