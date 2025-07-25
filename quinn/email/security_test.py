import base64
import hashlib
import hmac

from quinn.email.security import verify_postmark_signature


def test_verify_postmark_signature() -> None:
    token = "token"
    body = b"{}"
    digest = hmac.new(token.encode(), body, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()
    assert verify_postmark_signature(token, body, signature)
