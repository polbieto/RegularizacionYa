from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama


def build_ollama_llm_with_tools(tools: list[BaseTool]):
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=OLLAMA_TEMPERATURE,
    )
    return llm.bind_tools(tools)
