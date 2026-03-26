import argparse
import json
import logging
import os
import re
import time
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

logger = logging.getLogger(__name__)


def _require_env(value: str | None, name: str) -> str:
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _vector_to_pg(embedding: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in embedding) + "]"


def _sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _embed_documents(
    client: GoogleGenerativeAIEmbeddings, texts: list[str]
) -> list[list[float]]:
    embeddings: list[list[float]] = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        while True:
            try:
                batch_embeddings = client.embed_documents(
                    batch,
                    task_type="QUESTION_ANSWERING",
                    output_dimensionality=768,
                )
                embeddings.extend(batch_embeddings)
                break
            except Exception as exc:  # noqa: BLE001
                message = str(exc)
                if "429" not in message and "ResourceExhausted" not in message:
                    raise
                retry_seconds = 60
                retry_match = re.search(r"retry in ([0-9]+(?:\\.[0-9]+)?)s", message)
                if retry_match:
                    retry_seconds = max(1, int(float(retry_match.group(1))))
                logger.warning(
                    "Embedding quota reached, waiting %s seconds before retrying.",
                    retry_seconds,
                )
                time.sleep(retry_seconds + 1)
    return embeddings


def _load_file(file_path: Path) -> list:
    """Load a file using the appropriate LangChain loader based on extension."""
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        loader = PyPDFLoader(str(file_path))
        return loader.load()

    if extension in (".txt", ".md"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        return loader.load()

    raise ValueError(f"Unsupported file extension: {extension}")


def _split_markdown(source_path: Path, pages: list) -> list:
    """Two-pass markdown-aware chunking.

    Pass 1: MarkdownHeaderTextSplitter splits the document semantically by header
            hierarchy (#, ##, ###), preserving section context in metadata.
    Pass 2: RecursiveCharacterTextSplitter further splits any oversized sections
            while inheriting the header metadata from pass 1.
    """
    headers_to_split_on = [
        ("#", "section"),
        ("##", "subsection"),
        ("###", "subsubsection"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
    )

    full_text = "\n\n".join(page.page_content for page in pages)
    semantic_chunks = md_splitter.split_text(full_text)

    final_chunks = recursive_splitter.split_documents(semantic_chunks)

    # Ensure the source filename is always present in metadata.
    for chunk in final_chunks:
        chunk.metadata.setdefault("source", source_path.name)

    return final_chunks


def ingest_file(
    file_path: str,
    document_id: str,
    output_sql_path: str | None = None,
) -> Path:
    source_path = Path(file_path)
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = source_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    UUID(document_id)
    google_api_key = _require_env(GOOGLE_API_KEY, "GOOGLE_API_KEY")

    logger.info("Loading file: %s (type: %s)", source_path, extension)
    pages = _load_file(source_path)
    logger.info("Loaded %s page(s)/section(s)", len(pages))

    if extension == ".md":
        logger.info("Using markdown-aware chunking for: %s", source_path)
        chunks = _split_markdown(source_path, pages)
    else:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(pages)
    if not chunks:
        logger.warning("No chunks generated from file: %s", source_path)
        return


    logger.info("Generated %s chunks", len(chunks))
    embeddings_client = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=google_api_key,
    )
    texts = [chunk.page_content for chunk in chunks]
    embeddings = _embed_documents(embeddings_client, texts)

    logger.info("Generated %s embeddings", len(embeddings))
    if len(embeddings) != len(chunks):
        raise RuntimeError("Mismatch between generated chunks and embeddings.")
    if embeddings and len(embeddings[0]) != 768:
        raise ValueError(
            f"Embedding dimension {len(embeddings[0])} does not match VECTOR(768)."
        )

    sql_path = (
        Path(output_sql_path) if output_sql_path else source_path.with_suffix(".sql")
    )
    sql_path.parent.mkdir(parents=True, exist_ok=True)

    statements: list[str] = [
        "-- Generated by scripts/ingest_knowledge.py",
        f"-- Document id: {document_id}",
        "",
    ]
    escaped_document_id = _sql_quote(document_id)

    value_rows: list[str] = []
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        metadata: dict = {
            "page": chunk.metadata.get("page"),
            "source": Path(chunk.metadata.get("source", file_path)).name,
        }
        # Propagate markdown section headers when present.
        for key in ("section", "subsection", "subsubsection"):
            if chunk.metadata.get(key):
                metadata[key] = chunk.metadata[key]
        content_sql = _sql_quote(chunk.page_content)
        embedding_sql = _sql_quote(_vector_to_pg(embedding))
        metadata_sql = _sql_quote(json.dumps(metadata, ensure_ascii=True))
        value_rows.append(f"({content_sql}, {embedding_sql}, {metadata_sql})")

    statements.append(
        f"""INSERT INTO document_base_knowledge (document, content, embedding, metadata)
SELECT d.id, v.content, v.embedding::vector, v.metadata::jsonb
FROM document d
JOIN (
VALUES
{",\n".join(value_rows)}
) AS v(content, embedding, metadata) ON TRUE
WHERE d.id = {escaped_document_id}::uuid;"""
    )

    logger.info(
        "Generated SQL for %s chunks from %s for document id %s",
        len(chunks),
        source_path,
        document_id,
    )
    sql_path.write_text("\n\n".join(statements) + "\n", encoding="utf-8")
    logger.info("SQL written to: %s", sql_path)
    return sql_path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate SQL inserts for document knowledge base (pgvector). "
        "Supports PDF, TXT, and MD files."
    )
    parser.add_argument(
        "file_path",
        help="Path to the file to ingest (.pdf, .txt, or .md).",
    )
    parser.add_argument(
        "document_id",
        help="Document UUID for knowledge association.",
    )
    parser.add_argument(
        "--output-sql",
        dest="output_sql",
        help="Optional output .sql file path "
        "(default: same file path with .sql extension).",
    )
    args = parser.parse_args()

    try:
        ingest_file(
            args.file_path,
            args.document_id,
            args.output_sql,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Knowledge ingestion failed: %s", exc)
        raise SystemExit(1) from exc
