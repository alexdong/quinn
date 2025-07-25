from unittest.mock import AsyncMock, patch

import pytest

from quinn.email.outbound import format_reply, send_email
from quinn.models.email import EmailDirection, EmailMessage


@pytest.mark.asyncio
async def test_send_email() -> None:
    email = EmailMessage(
        id="<id1@pm>",
        from_email="q@example.com",
        to=["a@example.com"],
        subject="hi",
        direction=EmailDirection.OUTBOUND,
        conversation_id="conv1",
    )
    with (
        patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post,
        patch("quinn.email.outbound.EmailStore.create"),
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status = lambda: None
        await send_email(email, "token")
        assert mock_post.call_args is not None


def test_format_reply() -> None:
    original = EmailMessage(
        id="<id@pm>",
        subject="Hello",
        from_email="bob@example.com",
        conversation_id="conv1",
    )
    reply = format_reply(original, "hi", "quinn@example.com")
    assert reply.in_reply_to == "<id@pm>"
    assert "References" in reply.headers
