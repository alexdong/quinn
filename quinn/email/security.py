"""Security utilities for Postmark webhooks."""

import base64
import hashlib
import hmac

from quinn.utils.logging import get_logger

logger = get_logger(__name__)

__all__ = ["main", "verify_postmark_signature"]


def verify_postmark_signature(token: str, body: bytes, signature: str) -> bool:
    """Return ``True`` if signature matches ``body`` using the given token."""
    digest = hmac.new(token.encode(), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)


def main() -> None:
    """Demonstrate signature verification."""
    token = "demo"
    body = b"{}"
    digest = hmac.new(token.encode(), body, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()
    print(verify_postmark_signature(token, body, signature))


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
