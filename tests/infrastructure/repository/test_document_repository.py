import uuid

from domain.document import Document
from domain.document_knowledge_base import ProductBaseKnowledge
from infrastructure.repository.sqlalchemy_document_repository import (
    SqlAlchemyDocumentRepositoryAdapter,
)

# Important to ensure mappers are active for integration tests
from infrastructure.repository.orm import start_mappers
start_mappers()

def test_search_knowledge_by_embedding(db_session):
    # Setup Documents
    doc1_id = uuid.uuid4()
    doc1 = Document(id=doc1_id, name="General Immigration Rules")
    
    doc2_id = uuid.uuid4()
    doc2 = Document(id=doc2_id, name="Specific Visa Requirements")
    
    db_session.add_all([doc1, doc2])
    db_session.flush()

    # Setup Knowledge Base Entries
    knowledge_general = ProductBaseKnowledge(
        document_id=doc1_id,
        content="General rules apply to all applicants.",
        embedding=[0.1, 0.2, 0.3],
        metadata_={"topic": "general"}
    )
    knowledge_specific = ProductBaseKnowledge(
        document_id=doc2_id,
        content="Specific visa requires X, Y, Z.",
        embedding=[0.9, 0.8, 0.7],
        metadata_={"topic": "specific"}
    )
    knowledge_other = ProductBaseKnowledge(
        document_id=doc1_id,
        content="Other exceptions might apply.",
        embedding=[0.2, 0.2, 0.3], # Very close to general
        metadata_={"topic": "exceptions"}
    )
    
    db_session.add_all([knowledge_general, knowledge_specific, knowledge_other])
    db_session.commit()

    # Instantiate adapter using the current active db_session
    repository = SqlAlchemyDocumentRepositoryAdapter(lambda: db_session)
    
    # Test closest match (Should match general over other, and specific last)
    query_embedding = [0.11, 0.21, 0.31]
    result = repository.search_knowledge_by_embedding(
        query_embedding=query_embedding, limit=2
    )

    assert len(result) == 2
    assert result[0].content == "General rules apply to all applicants."
    assert result[1].content == "Other exceptions might apply."
    assert result[0].metadata_.get("topic") == "general"

    # Test limit 1 for a different vector
    query_specific_embedding = [0.85, 0.85, 0.75]
    result_specific = repository.search_knowledge_by_embedding(
        query_embedding=query_specific_embedding, limit=1
    )
    
    assert len(result_specific) == 1
    assert result_specific[0].content == "Specific visa requires X, Y, Z."
