from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from http import HTTPStatus

import pytest
from fasthtml.core import Client
from typing import Any, cast
from unittest.mock import patch

from quinn.email import web
from quinn.email.web import app

def _signature(token: str, body: bytes) -> str:
    digest = hmac.new(token.encode(), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def test_postmark_webhook_route() -> None:
    payload = {"MessageID": "<id@pm>", "From": "Alice <alice@example.com>"}
    body = json.dumps(payload).encode()
    token = "secret"
    os.environ["POSTMARK_INBOUND_TOKEN"] = token
    sig = _signature(token, body)
    with patch("quinn.email.web.parse_postmark_webhook") as parse:
        client = Client(app)
        resp = cast("Any", client).post(
            "/webhook/postmark",
            content=body,
            headers={"x-postmark-signature": sig},
        )
        assert resp.status_code == HTTPStatus.OK
        parse.assert_called_once_with(payload, None)
    del os.environ["POSTMARK_INBOUND_TOKEN"]


def test_postmark_webhook_allowed_senders(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"MessageID": "<id@pm>", "From": "Alice <alice@example.com>"}
    body = json.dumps(payload).encode()
    monkeypatch.delenv("POSTMARK_INBOUND_TOKEN", raising=False)
    monkeypatch.setenv(
        "QUINN_ALLOWED_SENDERS",
        "alice@example.com, bob@example.com",
    )
    with (
        patch("quinn.email.web.parse_postmark_webhook") as parse,
        patch("quinn.email.web.verify_postmark_signature") as verify,
    ):
        client = Client(app)
        resp = client.post("/webhook/postmark", data=body)  # type: ignore[attr-defined]
        assert resp.status_code == HTTPStatus.OK
        parse.assert_called_once_with(payload, ["alice@example.com", "bob@example.com"])
        verify.assert_not_called()


def test_main_calls_serve() -> None:
    with patch("quinn.email.web.serve") as mocked:
        web.main()
        mocked.assert_called_once_with()
