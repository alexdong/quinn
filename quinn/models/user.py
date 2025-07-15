"""User data model."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """User model for storing user information."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    name: str | None = None
    email_addresses: list[str] = Field(default_factory=list)
    settings: dict | None = None

    @field_validator("email_addresses")
    @classmethod
    def validate_email_addresses(cls, v: list[str]) -> list[str]:
        """Validate email addresses list is not empty."""
        if not v:
            msg = "At least one email address is required"
            raise ValueError(msg)
        return v


if __name__ == "__main__":
    import sys

    # Only run demonstration if not in test environment
    if "pytest" not in sys.modules:
        # Demonstrate User usage
        print("User demonstration:")

        # Create user
        user = User(
            name="John Doe",
            email_addresses=["john@example.com", "john.doe@company.com"],
            settings={"theme": "dark", "notifications": True},
        )
        print(f"User created: {user.name} (ID: {user.id[:8]}...)")
        print(f"Email addresses: {user.email_addresses}")
        print(f"Settings: {user.settings}")
        print(f"Created at: {user.created_at}")

        print("User demonstration completed.")
