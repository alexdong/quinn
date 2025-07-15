"""Tests for users database operations."""

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest

from quinn.db.users import Users
from quinn.models.user import User


def test_user_model_defaults():
    """Test User model with default values."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    assert user.id == user_id
    assert user.email_addresses == email_addresses
    assert user.name is None
    assert user.settings is None
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_user_model_with_optional_fields():
    """Test User model with all optional fields."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com", "test2@example.com"]
    name = "Test User"
    settings = {"theme": "dark", "notifications": True}
    
    user = User(
        id=user_id,
        email_addresses=email_addresses,
        name=name,
        settings=settings
    )
    
    assert user.id == user_id
    assert user.email_addresses == email_addresses
    assert user.name == name
    assert user.settings == settings


def test_user_single_email_address():
    """Test User model with single email address."""
    user_id = str(uuid.uuid4())
    email_addresses = ["single@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    assert len(user.email_addresses) == 1
    assert user.email_addresses[0] == "single@example.com"


def test_user_empty_email_addresses_list():
    """Test User model validation with empty email addresses list."""
    user_id = str(uuid.uuid4())
    email_addresses = []
    
    # Should raise validation error for empty email addresses
    with pytest.raises(ValueError, match="At least one email address is required"):
        User(id=user_id, email_addresses=email_addresses)


def test_user_with_null_name():
    """Test User model with explicitly null name."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses, name=None)
    
    assert user.name is None


def test_user_with_null_settings():
    """Test User model with explicitly null settings."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses, settings=None)
    
    assert user.settings is None


def test_user_email_addresses_serialization():
    """Test that email addresses are properly handled as list."""
    user_id = str(uuid.uuid4())
    email_addresses = ["primary@example.com", "secondary@example.com", "tertiary@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    assert isinstance(user.email_addresses, list)
    assert len(user.email_addresses) == 3
    assert "primary@example.com" in user.email_addresses
    assert "secondary@example.com" in user.email_addresses
    assert "tertiary@example.com" in user.email_addresses


def test_user_settings_json_serialization():
    """Test that settings are properly handled as dict."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    settings = {
        "theme": "dark",
        "notifications": True,
        "language": "en",
        "timezone": "UTC",
        "preferences": {
            "email_frequency": "daily",
            "auto_save": True
        }
    }
    
    user = User(id=user_id, email_addresses=email_addresses, settings=settings)
    
    assert isinstance(user.settings, dict)
    assert user.settings["theme"] == "dark"
    assert user.settings["notifications"] is True
    assert user.settings["preferences"]["email_frequency"] == "daily"


def test_create_user(clean_db):
    """Test creating a new user."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    name = "Test User"
    settings = {"theme": "dark"}
    
    user = User(
        id=user_id,
        email_addresses=email_addresses,
        name=name,
        settings=settings
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Verify user was created
        retrieved_user = Users.get_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.email_addresses == email_addresses
        assert retrieved_user.name == name
        assert retrieved_user.settings == settings


def test_get_user_by_id(clean_db, test_user_data):
    """Test retrieving a user by ID."""
    user = User(
        id=test_user_data["id"],
        email_addresses=test_user_data["email_addresses"],
        name=test_user_data["name"],
        settings=test_user_data["settings"]
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        retrieved_user = Users.get_by_id(test_user_data["id"])
        assert retrieved_user is not None
        assert retrieved_user.id == test_user_data["id"]
        assert retrieved_user.email_addresses == test_user_data["email_addresses"]
        assert retrieved_user.name == test_user_data["name"]
        assert retrieved_user.settings == test_user_data["settings"]


def test_get_user_by_id_not_found(clean_db):
    """Test retrieving a non-existent user."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        retrieved_user = Users.get_by_id("non-existent-id")
        assert retrieved_user is None


def test_update_user(clean_db, test_user_data):
    """Test updating an existing user."""
    import time
    
    user = User(
        id=test_user_data["id"],
        email_addresses=test_user_data["email_addresses"],
        name=test_user_data["name"],
        settings=test_user_data["settings"]
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Wait a moment to ensure different timestamp
        time.sleep(0.001)
        
        # Update user data
        user.name = "Updated Name"
        user.email_addresses = ["updated@example.com", "new@example.com"]
        user.settings = {"theme": "light", "notifications": False}
        
        Users.update(user)
        
        # Verify updates
        retrieved_user = Users.get_by_id(test_user_data["id"])
        assert retrieved_user is not None
        assert retrieved_user.name == "Updated Name"
        assert retrieved_user.email_addresses == ["updated@example.com", "new@example.com"]
        assert retrieved_user.settings == {"theme": "light", "notifications": False}
        assert retrieved_user.updated_at >= retrieved_user.created_at


def test_delete_user(clean_db, test_user_data):
    """Test deleting a user."""
    user = User(
        id=test_user_data["id"],
        email_addresses=test_user_data["email_addresses"],
        name=test_user_data["name"],
        settings=test_user_data["settings"]
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Verify user exists
        retrieved_user = Users.get_by_id(test_user_data["id"])
        assert retrieved_user is not None
        
        # Delete user
        Users.delete(test_user_data["id"])
        
        # Verify user is deleted
        retrieved_user = Users.get_by_id(test_user_data["id"])
        assert retrieved_user is None

def test_get_by_email(clean_db):
    """Test retrieving a user by email address."""
    user_id = str(uuid.uuid4())
    email_addresses = ["primary@example.com", "secondary@example.com"]
    name = "Test User"
    
    user = User(
        id=user_id,
        email_addresses=email_addresses,
        name=name
    )
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Test finding by primary email
        retrieved_user = Users.get_by_email("primary@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.name == name
        
        # Test finding by secondary email
        retrieved_user = Users.get_by_email("secondary@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        
        # Test with non-existent email
        retrieved_user = Users.get_by_email("nonexistent@example.com")
        assert retrieved_user is None


def test_add_alternative_email(clean_db):
    """Test adding alternative email to existing user."""
    user_id = str(uuid.uuid4())
    email_addresses = ["original@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Add new email
        result = Users.add_alternative_email(user_id, "new@example.com")
        assert result is True
        
        # Verify email was added
        retrieved_user = Users.get_by_id(user_id)
        assert retrieved_user is not None
        assert "original@example.com" in retrieved_user.email_addresses
        assert "new@example.com" in retrieved_user.email_addresses
        assert len(retrieved_user.email_addresses) == 2


def test_add_alternative_email_duplicate(clean_db):
    """Test adding duplicate email to existing user."""
    user_id = str(uuid.uuid4())
    email_addresses = ["test@example.com"]
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        Users.create(user)
        
        # Try to add existing email
        result = Users.add_alternative_email(user_id, "test@example.com")
        assert result is False
        
        # Verify no duplicate was added
        retrieved_user = Users.get_by_id(user_id)
        assert retrieved_user is not None
        assert len(retrieved_user.email_addresses) == 1


def test_add_alternative_email_user_not_found(clean_db):
    """Test adding email to non-existent user."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        result = Users.add_alternative_email("nonexistent-user", "test@example.com")
        assert result is False


def test_delete_nonexistent_user(clean_db):
    """Test deleting a user that does not exist."""
    with patch("quinn.db.database.DATABASE_FILE", str(clean_db)):
        # Should not raise an exception
        Users.delete("nonexistent-user-id")


def test_user_operations_error_handling(clean_db):
    """Test error handling in user operations."""
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email_addresses=["test@example.com"])
    
    # Mock database connection to raise an exception
    with patch("quinn.db.users.get_db_connection", side_effect=Exception("Database error")):
        with pytest.raises(Exception, match="Database error"):
            Users.create(user)
        
        with pytest.raises(Exception, match="Database error"):
            Users.get_by_id(user_id)
        
        with pytest.raises(Exception, match="Database error"):
            Users.get_by_email("test@example.com")
        
        with pytest.raises(Exception, match="Database error"):
            Users.update(user)
        
        with pytest.raises(Exception, match="Database error"):
            Users.delete(user_id)
        
        with pytest.raises(Exception, match="Database error"):
            Users.add_alternative_email(user_id, "new@example.com")

