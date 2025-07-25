import base64
import hashlib
import hmac
import json
import os
from http import HTTPStatus
from typing import Any, cast
from unittest.mock import patch

from fasthtml.core import Client

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
