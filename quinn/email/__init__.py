"""Email utilities for Quinn."""

from quinn.models.email import EmailAttachment, EmailMessage

from .inbound import build_thread_context, parse_postmark_webhook
from .outbound import format_reply, send_email
from .security import verify_postmark_signature
from .web import app as postmark_web_app

__all__ = [
    "EmailAttachment",
    "EmailMessage",
    "build_thread_context",
    "format_reply",
    "parse_postmark_webhook",
    "postmark_web_app",
    "send_email",
    "verify_postmark_signature",
]
