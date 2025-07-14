import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

DATABASE_FILE = "quinn.db"


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection]:
    """Context manager to handle database connections."""
    logger.debug("Opening database connection to %s", DATABASE_FILE)
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
        logger.debug("Database connection successful")
    except Exception as e:
        logger.error("Database connection error: %s", e)
        raise
    finally:
        conn.close()
        logger.debug("Database connection closed")


def create_tables() -> None:
    """Creates the database tables based on the schema.sql file."""
    schema_path = Path("quinn/db/schema.sql")
    logger.info("Creating database tables from schema: %s", schema_path)

    try:
        with get_db_connection() as conn, schema_path.open() as f:
            schema_sql = f.read()
            logger.debug("Executing schema SQL: %s characters", len(schema_sql))
            conn.executescript(schema_sql)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables: %s", e)
        raise
