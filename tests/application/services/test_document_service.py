from unittest.mock import MagicMock

from application.services.document_service import DocumentService
from domain.document_knowledge_base import ProductBaseKnowledge


def test_document_service_search_documents():
    # Arrange
    mock_repository = MagicMock()
    mock_embedding_provider = MagicMock()

    # Mock the embedding response
    mock_embedding = [0.1, 0.2, 0.3]
    mock_embedding_provider.embed_query.return_value = mock_embedding

    # Mock the repository response
    mock_knowledge_1 = MagicMock(spec=ProductBaseKnowledge)
    mock_knowledge_1.content = "Content 1"
    mock_knowledge_1.metadata_ = {"section": "Section 1", "subsection": "Sub 1"}

    mock_knowledge_2 = MagicMock(spec=ProductBaseKnowledge)
    mock_knowledge_2.content = "Content 2"
    mock_knowledge_2.metadata_ = {"section": "Section 2"}

    mock_repository.search_knowledge_by_embedding.return_value = [
        mock_knowledge_1,
        mock_knowledge_2,
    ]

    service = DocumentService(
        repository=mock_repository, embedding_provider=mock_embedding_provider
    )

    test_query = "test search query"
    test_limit = 2

    # Act
    result = service.search_documents(test_query, test_limit)

    # Assert
    mock_embedding_provider.embed_query.assert_called_once_with(test_query)

    mock_repository.search_knowledge_by_embedding.assert_called_once_with(
        query_embedding=mock_embedding, limit=test_limit
    )

    expected_string = (
        "[Fuente: Section 1 > Sub 1]\nContent 1\n\n---\n\n"
        "[Fuente: Section 2]\nContent 2"
    )

    assert result == expected_string
