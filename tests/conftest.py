import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

# Keep imports aligned with the project's current module layout.
PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from chatregularizacion.infrastructure.repository.orm import Base, start_mappers  # noqa: E402


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("pgvector/pgvector:pg15") as postgres:
        yield postgres.get_connection_url().replace("psycopg2", "psycopg2")


@pytest.fixture(scope="session")
def engine(postgres_url):
    db_engine = create_engine(postgres_url, future=True)
    with db_engine.begin() as connection:
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
    start_mappers()
    Base.metadata.create_all(db_engine)
    try:
        yield db_engine
    finally:
        Base.metadata.drop_all(db_engine)
        db_engine.dispose()


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
