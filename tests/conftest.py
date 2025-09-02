"""Test cases for the order service controller."""

from collections.abc import Iterator
import sqlite3

from app.models.base import Base
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: sqlite3.Connection, _connection_record: None) -> None:
    """Set SQLite PRAGMA settings for testing."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function")
def session() -> Iterator[Session]:
    """Create a new SQLAlchemy session for testing."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = session_local()

    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(engine)
