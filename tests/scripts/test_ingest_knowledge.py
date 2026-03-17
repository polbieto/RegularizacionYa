import importlib
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

SCRIPTS_DIR = str(Path(__file__).resolve().parents[2] / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import ingest_knowledge as mod  # noqa: E402

FAKE_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
FAKE_EMBEDDING = [0.123] * 768


class TestIngestKnowledgeIntegration:
    """High-level integration tests for the knowledge ingestion script."""

    @patch("ingest_knowledge.GoogleGenerativeAIEmbeddings")
    @patch.object(mod, "GOOGLE_API_KEY", "fake-api-key")
    def test_ingest_markdown_file_creates_valid_sql(self, mock_gai_class, tmp_path):
        """
        Tests the entire flow:
        1. Create a real markdown file on disk.
        2. Call the script's entrypoint function `ingest_file`.
        3. Verify that the file is loaded, chunks are created, 
           embeddings are mapped, and the correct SQL file is generated.
        """
        # 1. Setup real file
        md_file = tmp_path / "test_document.md"
        md_content = "# Section 1\nThis is the first section.\n\n# Section 2\nThis is the second section."
        md_file.write_text(md_content)

        # 2. Setup mocks to avoid real API calls
        mock_client_instance = mock_gai_class.return_value
        # The text splitter will likely create 1 chunk for this short text
        mock_client_instance.embed_documents.return_value = [FAKE_EMBEDDING]

        # 3. Run the ingestion
        output_sql_file = tmp_path / "output.sql"
        
        result_path = mod.ingest_file(
            file_path=str(md_file),
            document_id=FAKE_UUID,
            output_sql_path=str(output_sql_file)
        )

        # 4. Assertions
        assert result_path == output_sql_file
        assert output_sql_file.exists(), "The SQL file should have been created."

        sql_content = output_sql_file.read_text(encoding="utf-8")
        
        # Verify SQL structure
        assert "INSERT INTO document_base_knowledge" in sql_content
        assert f"WHERE d.id = '{FAKE_UUID}'::uuid;" in sql_content
        
        # Verify content was inserted
        assert "This is the first section." in sql_content
        assert "This is the second section." in sql_content
        
        # Verify metadata
        assert '"source": "test_document.md"' in sql_content
        
        # Verify vector formatting (should contain our fake embedding value)
        assert "0.123" in sql_content

    @patch("ingest_knowledge.GoogleGenerativeAIEmbeddings")
    @patch.object(mod, "GOOGLE_API_KEY", "fake-api-key")
    def test_ingest_txt_file_creates_valid_sql_in_default_location(self, mock_gai_class, tmp_path):
        """Tests that if no output path is provided, it defaults to the same directory as the input."""
        txt_file = tmp_path / "test_notes.txt"
        txt_file.write_text("Just some plain text notes.")

        mock_client_instance = mock_gai_class.return_value
        mock_client_instance.embed_documents.return_value = [FAKE_EMBEDDING]

        # Call without output_sql_path
        result_path = mod.ingest_file(
            file_path=str(txt_file),
            document_id=FAKE_UUID
        )

        expected_default_path = tmp_path / "test_notes.sql"
        assert result_path == expected_default_path
        assert expected_default_path.exists()
        
        sql_content = expected_default_path.read_text(encoding="utf-8")
        assert "INSERT INTO document_base_knowledge" in sql_content
        assert "Just some plain text notes." in sql_content
