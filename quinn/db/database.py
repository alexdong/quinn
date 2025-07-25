import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from quinn.utils.logging import get_logger, span_for_db

logger = get_logger(__name__)

DATABASE_FILE = "quinn.db"


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection]:
    """Context manager to handle database connections."""
    span_for_db("connection", DATABASE_FILE)
    logger.debug("Opening database connection to %s", DATABASE_FILE)
    conn = sqlite3.connect(DATABASE_FILE)
    assert conn is not None, f"Failed to connect to {DATABASE_FILE}"

    # Enable foreign key constraints
    pragma_sql = "PRAGMA foreign_keys = ON"
    logger.info("SQL: %s", pragma_sql)
    conn.execute(pragma_sql)

    try:
        yield conn
        logger.debug("Database connection successful")
    finally:
        conn.close()
        logger.debug("Database connection closed")


def create_tables() -> None:
    """Create database tables based on the schema.sql file."""
    schema_path = Path("quinn/db/schema.sql")
    logger.info("Creating database tables from schema: %s", schema_path)
    span_for_db("schema", str(schema_path))

    assert schema_path.exists(), f"Missing schema file at {schema_path}"

    with get_db_connection() as conn, schema_path.open() as f:
        schema_sql = f.read()
        logger.info("SQL: %s", schema_sql)
        conn.executescript(schema_sql)
        logger.info("Database tables created successfully")
