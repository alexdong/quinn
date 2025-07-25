from unittest.mock import patch

from quinn.email.inbound import build_thread_context, parse_postmark_webhook
from quinn.models.email import EmailMessage


def test_parse_postmark_webhook_basic() -> None:
    payload = {
        "MessageID": "<msg1@pm>",
        "MailboxHash": "conv1",
        "From": "Alice <alice@example.com>",
        "To": "quinn@example.com",
        "Subject": "Test",
        "TextBody": "Hello\n> quote",
        "Headers": [
            {"Name": "In-Reply-To", "Value": "<old@pm>"},
            {"Name": "References", "Value": "<ref1> <ref2>"},
        ],
        "Attachments": [
            {
                "Name": "a.txt",
                "ContentType": "text/plain",
                "Content": "dGVzdA==",
                "ContentLength": 4,
            }
        ],
    }
    with patch("quinn.email.inbound.EmailStore.create"):
        email = parse_postmark_webhook(payload, ["alice@example.com"])
    assert email.id == "<msg1@pm>"
    assert email.in_reply_to == "<old@pm>"
    assert email.references == ["<ref1>", "<ref2>"]
    assert email.attachments[0].name == "a.txt"


def test_build_thread_context() -> None:
    history = [
        EmailMessage(from_email="a@example.com", text="Hi"),
        EmailMessage(from_email="b@example.com", text="Reply"),
    ]
    new = EmailMessage(from_email="c@example.com", text="Final")
    ctx = build_thread_context(new, history)
    assert "a@example.com: Hi" in ctx
    assert "c@example.com: Final" in ctx
