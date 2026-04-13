from unittest.mock import MagicMock, patch

from infrastructure.google_embedding_provider import (
    EMBEDDINGS_MODEL_NAME,
    GoogleGenerativeAIEmbeddingProvider,
)


@patch(
    "infrastructure.google_embedding_provider.GoogleGenerativeAIEmbeddings"
)
def test_google_generative_ai_embedding_provider_initialization(mock_google_embeddings):
    # Act
    provider = GoogleGenerativeAIEmbeddingProvider()

    # Assert
    mock_google_embeddings.assert_called_once_with(model=EMBEDDINGS_MODEL_NAME)
    assert provider.embeddings == mock_google_embeddings.return_value


@patch(
    "infrastructure.google_embedding_provider.GoogleGenerativeAIEmbeddings"
)
def test_google_generative_ai_embedding_provider_embed_query(mock_google_embeddings):
    # Arrange
    mock_instance = MagicMock()
    mock_google_embeddings.return_value = mock_instance
    mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]

    provider = GoogleGenerativeAIEmbeddingProvider()
    test_text = "test query"

    # Act
    result = provider.embed_query(test_text)

    # Assert
    mock_instance.embed_query.assert_called_once_with(
        test_text,
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=768,
    )
    assert result == [0.1, 0.2, 0.3]
