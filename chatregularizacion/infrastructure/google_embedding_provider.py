from langchain_google_genai import GoogleGenerativeAIEmbeddings

from application.ports.embedding_provider_port import (
    EmbeddingProviderPort,
)

EMBEDDINGS_MODEL_NAME = "models/gemini-embedding-001"


class GoogleGenerativeAIEmbeddingProvider(EmbeddingProviderPort):
    def __init__(self, model_name: str = EMBEDDINGS_MODEL_NAME):
        self.embeddings = GoogleGenerativeAIEmbeddings(model=model_name)

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(
            text,
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        )
