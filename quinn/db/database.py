import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

DATABASE_FILE = "quinn.db"


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection]:
    """Context manager to handle database connections."""
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
    finally:
        conn.close()


def create_tables() -> None:
    """Creates the database tables based on the schema.sql file."""
    with get_db_connection() as conn, Path("quinn/db/schema.sql").open() as f:
        conn.executescript(f.read())
