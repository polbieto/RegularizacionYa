import os

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value is not None else default


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    return float(value) if value is not None else default


DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://user:password@db:5432/regularizaion_ya"
)
ORM_POOL_SIZE = _env_int("ORM_POOL_SIZE", 30)
ORM_OVERFLOW_SIZE = _env_int("ORM_OVERFLOW_SIZE", 50)
ORM_CONNECTION_TIMEOUT = _env_int("ORM_CONNECTION_TIMEOUT", 60)

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TEMPERATURE = _env_float("OLLAMA_TEMPERATURE", 0.2)
