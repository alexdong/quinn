"""Utilities for handling inbound Postmark webhooks."""

import json
import sys
from email.utils import parseaddr
from typing import Any

from quinn.db.emails import EmailStore
from quinn.models.email import EmailAttachment, EmailDirection, EmailMessage
from quinn.utils.logging import get_logger

logger = get_logger(__name__)


def _parse_attachments(data: list[dict[str, Any]]) -> list[EmailAttachment]:
    return [
        EmailAttachment(
            name=att.get("Name", ""),
            content_type=att.get("ContentType", ""),
            content=att.get("Content", ""),
            content_length=int(att.get("ContentLength", 0)),
        )
        for att in data or []
    ]


def parse_postmark_webhook(
    payload: dict[str, Any], allowed_senders: list[str] | None = None
) -> EmailMessage:
    """Parse Postmark inbound webhook JSON to an :class:`EmailMessage`."""
    message_id = payload.get("MessageID", "")
    subject = payload.get("Subject", "")
    text_body = payload.get("TextBody", "")
    html_body = payload.get("HtmlBody", "")
    from_field = payload.get("From", "")

    if allowed_senders is not None:
        _, addr = parseaddr(from_field)
        if addr.lower() not in {a.lower() for a in allowed_senders}:
            msg = "Sender not allowed"
            raise ValueError(msg)

    to_field = payload.get("To", "")
    cc_field = payload.get("Cc", "")
    bcc_field = payload.get("Bcc", "")

    headers = {h["Name"]: h["Value"] for h in payload.get("Headers", [])}
    in_reply_to = headers.get("In-Reply-To")
    references_header = headers.get("References", "")
    references = [r for r in references_header.split() if r]

    attachments = _parse_attachments(payload.get("Attachments", []))

    email = EmailMessage(
        id=message_id,
        subject=subject,
        from_email=from_field,
        to=[addr.strip() for addr in to_field.split(";") if addr.strip()],
        cc=[addr.strip() for addr in cc_field.split(";") if addr.strip()],
        bcc=[addr.strip() for addr in bcc_field.split(";") if addr.strip()],
        text=text_body,
        html=html_body,
        headers=headers,
        attachments=attachments,
        mailbox_hash=payload.get("MailboxHash"),
        in_reply_to=in_reply_to,
        references=references,
        direction=EmailDirection.INBOUND,
        conversation_id=payload.get("MailboxHash", ""),
    )
    logger.info("Parsed inbound email %s hash=%s", email.id, email.mailbox_hash)
    EmailStore.create(email)
    return email


def build_thread_context(new_email: EmailMessage, history: list[EmailMessage]) -> str:
    """Build conversation text from previous emails and the new one."""
    parts = [f"{msg.sender_address}: {msg.text}" for msg in history]
    parts.append(f"{new_email.sender_address}: {new_email.text}")
    return "\n\n".join(parts)


def main() -> None:
    """CLI entry for parsing inbound payload from stdin."""
    raw = sys.stdin.read()
    payload = json.loads(raw)
    email = parse_postmark_webhook(payload)
    print(email.model_dump())


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
