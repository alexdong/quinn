import base64
import hashlib
import hmac

import pytest

from quinn.email.security import main, verify_postmark_signature


def test_verify_postmark_signature() -> None:
    token = "token"
    body = b"{}"
    digest = hmac.new(token.encode(), body, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()
    assert verify_postmark_signature(token, body, signature)


def test_main_prints_true(capsys: pytest.CaptureFixture[str]) -> None:
    """Ensure the demo main function prints True."""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "True"
