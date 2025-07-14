"""Tests for users database operations."""

import uuid
from unittest.mock import patch

import pytest

from quinn.db.users import User, Users


def test_user_model_defaults():
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
    """Test User model with empty email addresses list."""
    user_id = str(uuid.uuid4())
    email_addresses = []
    
    user = User(id=user_id, email_addresses=email_addresses)
    
    assert user.email_addresses == []


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
    user = User(**test_user_data)
    
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
    
    user = User(**test_user_data)
    
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
    user = User(**test_user_data)
    
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