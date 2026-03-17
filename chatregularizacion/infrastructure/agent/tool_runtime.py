from typing import Any

from infrastructure.agent.ports.tool_runtime import ToolRuntimePort
from langchain_core.tools import BaseTool


class LangChainToolRuntime(ToolRuntimePort):
    def __init__(self, tools: list[BaseTool]):
        self._tools_by_name = {tool.name: tool for tool in tools}

    def execute(self, tool_name: str, tool_args: dict[str, Any], client_id: str) -> str:
        tool = self._tools_by_name.get(tool_name)
        if tool is None:
            return f"Tool `{tool_name}` is not configured."

        payload = dict(tool_args or {})
        payload["client_id"] = client_id
        result = tool.invoke(payload)
        return str(result)
