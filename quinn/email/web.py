import json
import os

from fasthtml.core import JSONResponse, serve
from fasthtml.fastapp import fast_app
from fasthtml.starlette import Request

from quinn.email.inbound import parse_postmark_webhook
from quinn.email.security import verify_postmark_signature
from quinn.utils.logging import get_logger

logger = get_logger(__name__)

app, _ = fast_app()


def _get_allowed_senders() -> list[str] | None:
    """Return allowed senders list from the environment."""
    allowed = os.getenv("QUINN_ALLOWED_SENDERS", "")
    parts = [s.strip() for s in allowed.split(",")]
    filtered = [p for p in parts if p]
    return filtered or None


@app.post("/webhook/postmark")
async def postmark(req: Request) -> JSONResponse:
    """Handle inbound Postmark webhook."""
    body = await req.body()
    token = os.getenv("POSTMARK_INBOUND_TOKEN", "")
    if token:
        signature = req.headers.get("x-postmark-signature", "")
        assert verify_postmark_signature(token, body, signature), "invalid signature"
    senders = _get_allowed_senders()
    payload = json.loads(body)
    email = parse_postmark_webhook(payload, senders)
    logger.info("Inbound email processed %s", email.id)
    return JSONResponse({"status": "ok"})


def main() -> None:
    serve()


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()


__all__ = ["app", "main", "postmark"]
