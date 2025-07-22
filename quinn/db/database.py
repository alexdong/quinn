import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

DATABASE_FILE = "quinn.db"


def _log_database_error(error: Exception, context: str) -> None:
    """Log database errors appropriately based on error type."""
    if "already exists" in str(error):
        logger.debug("%s: %s", context, error)
    else:
        logger.error("%s: %s", context, error)


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection]:
    """Context manager to handle database connections."""
    logger.debug("Opening database connection to %s", DATABASE_FILE)
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        # Enable foreign key constraints
        pragma_sql = "PRAGMA foreign_keys = ON"
        logger.info("SQL: %s", pragma_sql)
        conn.execute(pragma_sql)
        try:
            yield conn
            logger.debug("Database connection successful")
        except Exception as e:
            _log_database_error(e, "Database connection error")
            conn.rollback()
            raise
    except Exception as e:
        _log_database_error(e, "Database setup error")
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed")
            except Exception as close_error:
                logger.warning("Error closing database connection: %s", close_error)


def create_tables() -> None:
    """Creates the database tables based on the schema.sql file."""
    schema_path = Path("quinn/db/schema.sql")
    logger.info("Creating database tables from schema: %s", schema_path)

    try:
        with get_db_connection() as conn, schema_path.open() as f:
            schema_sql = f.read()
            logger.info("SQL: %s", schema_sql)
            conn.executescript(schema_sql)
            logger.info("Database tables created successfully")
    except Exception as e:
        # Only log as error if it's not a "table already exists" error
        if "already exists" in str(e):
            logger.debug("Database tables already exist, skipping creation")
        else:
            logger.error("Failed to create database tables: %s", e)
            raise
