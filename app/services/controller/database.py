"""TODO: Add a description of the module here."""

import os
import shutil

from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

# Custom exception for database connection errors


class DatabaseConnectionError(Exception):
    """Exception raised when there is a database connection error."""

    def __init__(self, msg: str = "Could not connect to the database.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class FileNotFoundError(Exception):
    """Exception raised when a file is not found."""

    def __init__(self, msg: str = "File not found.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


# Define the base directory and database URL
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'local.db')}"

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db_tables() -> list[str]:
    """Retrieve the names of all tables in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def drop_table(table_name: str) -> None:
    """Drop a specific table from the database."""
    meta = MetaData()
    table = Table(table_name, meta, autoload_with=engine)
    table.drop(engine)


def drop_all_tables() -> None:
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)


def test_connection() -> bool:
    """Test the database connection."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise DatabaseConnectionError from e
    finally:
        db.close()
    return True


def get_db_size() -> int:
    """Get the size of the database file in bytes."""
    db_path = os.path.join(BASE_DIR, "local.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError
    return os.path.getsize(db_path)


def backup_db() -> None:
    """Backup the database file."""
    backup_path = os.path.join(BASE_DIR, "backup", "local_backup.db")
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copyfile(os.path.join(BASE_DIR, "local.db"), backup_path)


def restore_db(backup_file: str) -> None:
    """Restore the database from a backup file."""
    if not os.path.exists(backup_file):
        raise FileNotFoundError
    shutil.copyfile(backup_file, os.path.join(BASE_DIR, "local.db"))
