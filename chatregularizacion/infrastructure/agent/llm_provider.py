import litellm
from config import LLM_MODEL, LLM_TEMPERATURE
from langchain_litellm import ChatLiteLLM

litellm._turn_on_debug()


class LLMProvider:
    def __init__(
        self,
        model_name: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
    ):
        self.model_name = model_name
        self.temperature = temperature

    def get_llm(self):
        return ChatLiteLLM(
            model=self.model_name,
            temperature=self.temperature,
        )


def build_llm():
    provider = LLMProvider()
    return provider.get_llm()


def build_llm_with_tools(tools):
    provider = LLMProvider()
    llm = provider.get_llm()
    return llm.bind_tools(tools)
