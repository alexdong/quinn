"""Tests for database connection and table creation."""

import sqlite3
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from quinn.db.database import create_tables, get_db_connection


class TestDatabase(unittest.TestCase):
    """Test cases for database operations."""

    def setUp(self) -> None:
        """Set up test database file."""
        self.db_file = Path(tempfile.mktemp(suffix=".db"))

    def tearDown(self) -> None:
        """Clean up test database file."""
        if self.db_file.exists():
            self.db_file.unlink()

    def test_get_db_connection_context_manager(self) -> None:
        """Test database connection context manager."""
        # Create a simple database
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()

        # Test our context manager
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO test (id) VALUES (1)")
                conn.commit()

                cursor.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                assert count == 1

    def test_get_db_connection_closes_properly(self) -> None:
        """Test that database connection closes properly."""
        # Create a simple database
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()

        connection_ref = None
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            with get_db_connection() as conn:
                connection_ref = conn
                # Connection should be open here
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1

        # After context manager, connection should be closed
        # Note: SQLite doesn't have a direct "is_closed" method, but we can test
        # that operations fail after the context manager exits
        try:
            connection_ref.execute("SELECT 1")
            # If we get here, the connection wasn't closed (unexpected)
            assert False, "Connection should have been closed"
        except sqlite3.ProgrammingError:
            # This is expected - connection is closed
            pass

    def test_create_tables(self) -> None:
        """Test table creation from schema.sql."""
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            create_tables()

        # Verify tables were created
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            # Check that all expected tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ["conversations", "emails", "messages", "users"]
            assert set(tables) == set(expected_tables)

    def test_create_tables_schema_structure(self) -> None:
        """Test that created tables have the correct structure."""
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            create_tables()

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            # Test users table structure
            cursor.execute("PRAGMA table_info(users)")
            users_columns = {row[1]: row[2] for row in cursor.fetchall()}
            expected_users_columns = {
                "id": "TEXT",
                "created_at": "INTEGER",
                "updated_at": "INTEGER",
                "name": "TEXT",
                "email_addresses": "TEXT",
                "settings": "TEXT",
            }
            assert users_columns == expected_users_columns

            # Test conversations table structure
            cursor.execute("PRAGMA table_info(conversations)")
            conversations_columns = {row[1]: row[2] for row in cursor.fetchall()}
            expected_conversations_columns = {
                "id": "TEXT",
                "user_id": "TEXT",
                "created_at": "INTEGER",
                "updated_at": "INTEGER",
                "title": "TEXT",
                "status": "TEXT",
                "total_cost": "REAL",
                "message_count": "INTEGER",
                "metadata": "TEXT",
            }
            assert conversations_columns == expected_conversations_columns

            # Test messages table structure
            cursor.execute("PRAGMA table_info(messages)")
            messages_columns = {row[1]: row[2] for row in cursor.fetchall()}
            expected_messages_columns = {
                "id": "TEXT",
                "conversation_id": "TEXT",
                "user_id": "TEXT",
                "created_at": "INTEGER",
                "last_updated_at": "INTEGER",
                "system_prompt": "TEXT",
                "user_content": "TEXT",
                "assistant_content": "TEXT",
                "metadata": "TEXT",
            }
            assert messages_columns == expected_messages_columns

    def test_create_tables_foreign_keys(self) -> None:
        """Test that foreign key constraints are properly set up."""
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            create_tables()

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            # Test conversations foreign key to users
            cursor.execute("PRAGMA foreign_key_list(conversations)")
            conv_fks = cursor.fetchall()
            assert len(conv_fks) == 1
            assert conv_fks[0][2] == "users"  # Referenced table
            assert conv_fks[0][3] == "user_id"  # From column
            assert conv_fks[0][4] == "id"  # To column

            # Test messages foreign keys
            cursor.execute("PRAGMA foreign_key_list(messages)")
            msg_fks = cursor.fetchall()
            assert len(msg_fks) == 2

            # Sort by referenced table for consistent testing
            msg_fks_sorted = sorted(msg_fks, key=lambda x: x[2])

            # First FK should be to conversations
            assert msg_fks_sorted[0][2] == "conversations"
            assert msg_fks_sorted[0][3] == "conversation_id"
            assert msg_fks_sorted[0][4] == "id"

            # Second FK should be to users
            assert msg_fks_sorted[1][2] == "users"
            assert msg_fks_sorted[1][3] == "user_id"
            assert msg_fks_sorted[1][4] == "id"

    def test_database_file_constant(self) -> None:
        """Test that DATABASE_FILE constant is set correctly."""
        from quinn.db.database import DATABASE_FILE

        assert DATABASE_FILE == "quinn.db"


if __name__ == "__main__":
    unittest.main()

    def test_get_db_connection_error_handling(self):
        """Test error handling in get_db_connection."""
        from unittest.mock import patch, MagicMock
        import pytest

        # Test connection error
        with patch(
            "quinn.db.database.sqlite3.connect",
            side_effect=Exception("Connection failed"),
        ):
            with pytest.raises(Exception, match="Connection failed"):
                with get_db_connection():
                    pass

    def test_get_db_connection_rollback_on_error(self):
        """Test rollback is called when an error occurs."""
        from unittest.mock import patch, MagicMock
        import pytest

        mock_conn = MagicMock()
        with patch("quinn.db.database.sqlite3.connect", return_value=mock_conn):
            with pytest.raises(Exception, match="Test error"):
                with get_db_connection() as conn:
                    raise Exception("Test error")

            # Verify rollback was called
            mock_conn.rollback.assert_called_once()

    def test_get_db_connection_close_error(self):
        """Test handling of close errors."""
        from unittest.mock import patch, MagicMock

        mock_conn = MagicMock()
        mock_conn.close.side_effect = Exception("Close failed")

        with patch("quinn.db.database.sqlite3.connect", return_value=mock_conn):
            # Should not raise exception even if close fails
            with get_db_connection():
                pass

            # Verify close was attempted
            mock_conn.close.assert_called_once()

    def test_create_tables_error_handling(self):
        """Test error handling in create_tables."""
        from unittest.mock import patch
        import pytest

        # Test when get_db_connection fails
        with patch(
            "quinn.db.database.get_db_connection", side_effect=Exception("DB error")
        ):
            with pytest.raises(Exception, match="DB error"):
                create_tables()

        # Test when schema file cannot be read
        with patch(
            "pathlib.Path.open", side_effect=FileNotFoundError("Schema not found")
        ):
            with pytest.raises(FileNotFoundError, match="Schema not found"):
                create_tables()

    def test_get_db_connection_error_handling(self):
        """Test error handling in get_db_connection."""
        from unittest.mock import patch
        import pytest

        # Test connection error
        with patch(
            "quinn.db.database.sqlite3.connect",
            side_effect=Exception("Connection failed"),
        ):
            with pytest.raises(Exception, match="Connection failed"):
                with get_db_connection():
                    pass

    def test_get_db_connection_rollback_on_error(self):
        """Test rollback is called when an error occurs."""
        from unittest.mock import patch, MagicMock
        import pytest

        mock_conn = MagicMock()
        with patch("quinn.db.database.sqlite3.connect", return_value=mock_conn):
            with pytest.raises(Exception, match="Test error"):
                with get_db_connection() as conn:
                    raise Exception("Test error")

            # Verify rollback was called
            mock_conn.rollback.assert_called_once()

    def test_get_db_connection_close_error(self):
        """Test handling of close errors."""
        from unittest.mock import patch, MagicMock

        mock_conn = MagicMock()
        mock_conn.close.side_effect = Exception("Close failed")

        with patch("quinn.db.database.sqlite3.connect", return_value=mock_conn):
            # Should not raise exception even if close fails
            with get_db_connection():
                pass

            # Verify close was attempted
            mock_conn.close.assert_called_once()

    def test_create_tables_error_handling(self):
        """Test error handling in create_tables."""
        from unittest.mock import patch
        import pytest

        # Test when get_db_connection fails
        with patch(
            "quinn.db.database.get_db_connection", side_effect=Exception("DB error")
        ):
            with pytest.raises(Exception, match="DB error"):
                create_tables()

        # Test when schema file cannot be read
        with patch(
            "pathlib.Path.open", side_effect=FileNotFoundError("Schema not found")
        ):
            with pytest.raises(FileNotFoundError, match="Schema not found"):
                create_tables()
