"""Email data models."""

from datetime import UTC, datetime
from email.utils import parseaddr
from enum import Enum

from pydantic import BaseModel, Field


class EmailDirection(str, Enum):
    """Inbound or outbound email."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class EmailAttachment(BaseModel):
    """Representation of an email attachment."""

    name: str = ""
    content_type: str = ""
    content: str = ""
    content_length: int = 0


class EmailMessage(BaseModel):
    """Simplified email message model."""

    id: str = ""
    conversation_id: str = ""
    direction: EmailDirection = EmailDirection.INBOUND
    subject: str = ""
    from_email: str = ""
    to: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    text: str = ""
    html: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    attachments: list[EmailAttachment] = Field(default_factory=list)
    mailbox_hash: str | None = None
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def sender_address(self) -> str:
        """Return the plain email address of the sender."""
        _, addr = parseaddr(self.from_email)
        return addr


if __name__ == "__main__":
    import sys

    if "pytest" not in sys.modules:
        sample = EmailMessage(
            id="<demo@quinn.email>",
            subject="Demo",
            from_email="Alice <alice@example.com>",
            to=["quinn@example.com"],
        )
        print(sample)
