from typing import Protocol


class EmbeddingProviderPort(Protocol):
    def embed_query(self, text: str) -> list[float]: ...

