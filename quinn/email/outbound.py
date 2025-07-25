"""Functions for sending emails via Postmark."""

import asyncio
import os
from typing import Any
from uuid import uuid4

import httpx

from quinn.db.emails import EmailStore
from quinn.models.email import EmailDirection, EmailMessage
from quinn.utils.logging import get_logger

logger = get_logger(__name__)

POSTMARK_ENDPOINT = "https://api.postmarkapp.com/email"


async def send_email(
    email: EmailMessage,
    server_token: str,
    retries: int = 3,
) -> httpx.Response:
    """Send an email using the Postmark API."""
    payload: dict[str, Any] = {
        "From": email.from_email,
        "To": ",".join(email.to),
        "Cc": ",".join(email.cc),
        "Bcc": ",".join(email.bcc),
        "Subject": email.subject,
        "TextBody": email.text,
        "HtmlBody": email.html,
        "Headers": [{"Name": k, "Value": v} for k, v in email.headers.items()],
    }
    attempt = 0
    while True:
        try:
            logger.info("Sending email %s", email.id)
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    POSTMARK_ENDPOINT,
                    headers={
                        "Accept": "application/json",
                        "X-Postmark-Server-Token": server_token,
                    },
                    json=payload,
                )
            resp.raise_for_status()
            EmailStore.create(email)
            return resp
        except Exception:  # pragma: no cover - network failure scenario
            attempt += 1
            if attempt > retries:
                raise
            await asyncio.sleep(min(2**attempt, 10))


def format_reply(
    original: EmailMessage,
    reply_text: str,
    from_addr: str,
    html_body: str | None = None,
) -> EmailMessage:
    """Create a reply email referencing the original thread."""
    new_headers = dict(original.headers)
    new_headers["In-Reply-To"] = original.id
    refs = [*original.references, original.id]
    new_headers["References"] = " ".join(refs)
    return EmailMessage(
        id=f"<{uuid4()}@quinn.email>",
        subject=f"Re: {original.subject}",
        from_email=from_addr,
        to=[original.sender_address],
        cc=original.cc,
        bcc=original.bcc,
        text=reply_text,
        html=html_body or "",
        headers=new_headers,
        in_reply_to=original.id,
        references=refs,
        conversation_id=original.conversation_id,
        direction=EmailDirection.OUTBOUND,
    )


def main() -> None:
    """Simple demonstration for sending an email."""
    token = os.environ.get("POSTMARK_TOKEN", "POSTMARK_API_TEST")
    email = EmailMessage(
        id=str(uuid4()),
        conversation_id="demo",
        from_email="support@quinn.email",
        to=["user@example.com"],
        subject="Demo",
        text="Hello from Quinn",
        direction=EmailDirection.OUTBOUND,
    )
    asyncio.run(send_email(email, token))


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
