"""Tests for users database operations."""

import json
import sqlite3
import tempfile
import time
import unittest
import unittest.mock
import uuid
from pathlib import Path

from quinn.db.database import create_tables
from quinn.db.users import User, Users


class TestUsers(unittest.TestCase):
    """Test cases for User model and Users operations."""

    def setUp(self) -> None:
        """Set up test database."""
        self.db_file = Path(tempfile.mktemp(suffix=".db"))
        
        # Create tables in test database
        with unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file)):
            create_tables()

        # Patch DATABASE_FILE for all tests
        self.db_patcher = unittest.mock.patch("quinn.db.database.DATABASE_FILE", str(self.db_file))
        self.db_patcher.start()

    def tearDown(self) -> None:
        """Clean up test database."""
        self.db_patcher.stop()
        if self.db_file.exists():
            self.db_file.unlink()

    def test_user_model_defaults(self) -> None:
        """Test User model with default values."""
        user_id = str(uuid.uuid4())
        email_addresses = ["test@example.com"]
        
        user = User(id=user_id, email_addresses=email_addresses)
        
        assert user.id == user_id
        assert user.email_addresses == email_addresses
        assert user.name is None
        assert user.settings is None
        assert isinstance(user.created_at, int)
        assert isinstance(user.updated_at, int)

    def test_user_model_with_optional_fields(self) -> None:
        """Test User model with all fields."""
        user_id = str(uuid.uuid4())
        email_addresses = ["test@example.com", "test2@example.com"]
        settings = {"theme": "dark", "notifications": True}
        
        user = User(
            id=user_id,
            email_addresses=email_addresses,
            name="Test User",
            settings=settings
        )
        
        assert user.id == user_id
        assert user.email_addresses == email_addresses
        assert user.name == "Test User"
        assert user.settings == settings

    def test_create_user(self) -> None:
        """Test creating a user in the database."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com"],
            name="Test User"
        )
        
        Users.create(user)
        
        # Verify it was created
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user.id,))
            count = cursor.fetchone()[0]
            assert count == 1

    def test_get_user_by_id(self) -> None:
        """Test retrieving a user by ID."""
        original = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com", "test2@example.com"],
            name="Test User",
            settings={"key": "value"}
        )
        
        Users.create(original)
        retrieved = Users.get_by_id(original.id)
        
        assert retrieved is not None
        assert retrieved.id == original.id
        assert retrieved.email_addresses == original.email_addresses
        assert retrieved.name == original.name
        assert retrieved.settings == original.settings
        assert retrieved.created_at == original.created_at
        assert retrieved.updated_at == original.updated_at

    def test_get_user_by_id_not_found(self) -> None:
        """Test retrieving a non-existent user."""
        result = Users.get_by_id("non-existent-id")
        assert result is None

    def test_update_user(self) -> None:
        """Test updating an existing user."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["original@example.com"],
            name="Original Name"
        )
        
        Users.create(user)
        
        # Update the user
        user.name = "Updated Name"
        user.email_addresses = ["updated@example.com", "second@example.com"]
        user.settings = {"updated": True, "theme": "light"}
        
        original_updated_at = user.updated_at
        # Mock time to simulate timestamp change without actual delay
        with unittest.mock.patch('time.time', return_value=time.time() + 2):
            Users.update(user)
        
        # Verify the update
        retrieved = Users.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.name == "Updated Name"
        assert retrieved.email_addresses == ["updated@example.com", "second@example.com"]
        assert retrieved.settings == {"updated": True, "theme": "light"}
        assert retrieved.updated_at > original_updated_at

    def test_delete_user(self) -> None:
        """Test deleting a user."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com"]
        )
        
        Users.create(user)
        
        # Verify it exists
        assert Users.get_by_id(user.id) is not None
        
        # Delete it
        Users.delete(user.id)
        
        # Verify it's gone
        assert Users.get_by_id(user.id) is None

    def test_user_with_null_settings(self) -> None:
        """Test user with null settings."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com"],
            settings=None
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.settings is None

    def test_user_with_null_name(self) -> None:
        """Test user with null name."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com"],
            name=None
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.name is None

    def test_user_email_addresses_serialization(self) -> None:
        """Test that email addresses are properly JSON serialized/deserialized."""
        email_addresses = [
            "primary@example.com",
            "secondary@example.com",
            "work@company.com"
        ]
        
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=email_addresses
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.email_addresses == email_addresses

    def test_user_settings_json_serialization(self) -> None:
        """Test that settings are properly JSON serialized/deserialized."""
        complex_settings = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": False,
                "frequency": "daily"
            },
            "preferences": {
                "language": "en",
                "timezone": "UTC",
                "features": ["beta", "experimental"]
            },
            "limits": {
                "max_conversations": 100,
                "max_messages_per_conversation": 1000
            }
        }
        
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["test@example.com"],
            settings=complex_settings
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.settings == complex_settings

    def test_user_single_email_address(self) -> None:
        """Test user with single email address."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=["single@example.com"]
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.email_addresses == ["single@example.com"]

    def test_user_empty_email_addresses_list(self) -> None:
        """Test user with empty email addresses list."""
        user = User(
            id=str(uuid.uuid4()),
            email_addresses=[]
        )
        
        Users.create(user)
        retrieved = Users.get_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.email_addresses == []

    def test_get_user_by_email(self) -> None:
        """Test retrieving user by email address."""
        user = User(
            id=str(uuid.uuid4()),
            name="Email Test User",
            email_addresses=["primary@example.com", "secondary@example.com"],
        )
        Users.create(user)

        # Test finding by primary email
        retrieved_user = Users.get_by_email("primary@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.name == "Email Test User"

        # Test finding by secondary email
        retrieved_user = Users.get_by_email("secondary@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user.id

        # Test with non-existent email
        retrieved_user = Users.get_by_email("nonexistent@example.com")
        assert retrieved_user is None

    def test_add_alternative_email(self) -> None:
        """Test adding alternative email addresses to existing user."""
        user = User(
            id=str(uuid.uuid4()),
            name="Alt Email User",
            email_addresses=["original@example.com"],
        )
        Users.create(user)

        # Add new alternative email
        result = Users.add_alternative_email(user.id, "alternative@example.com")
        assert result is True

        # Verify email was added
        retrieved_user = Users.get_by_id(user.id)
        assert retrieved_user is not None
        assert len(retrieved_user.email_addresses) == 2
        assert "original@example.com" in retrieved_user.email_addresses
        assert "alternative@example.com" in retrieved_user.email_addresses

        # Verify we can find user by new email
        retrieved_user = Users.get_by_email("alternative@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user.id

        # Try to add duplicate email
        result = Users.add_alternative_email(user.id, "alternative@example.com")
        assert result is False

        # Verify no duplicate was added
        retrieved_user = Users.get_by_id(user.id)
        assert retrieved_user is not None
        assert len(retrieved_user.email_addresses) == 2

        # Try to add email to non-existent user
        result = Users.add_alternative_email("non-existent-user", "test@example.com")
        assert result is False


if __name__ == "__main__":
    unittest.main()