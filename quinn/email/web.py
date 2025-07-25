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


@app.post("/webhook/postmark")
async def postmark(req: Request) -> JSONResponse:
    """Handle inbound Postmark webhook."""
    body = await req.body()
    token = os.getenv("POSTMARK_INBOUND_TOKEN", "")
    if token:
        signature = req.headers.get("x-postmark-signature", "")
        assert verify_postmark_signature(token, body, signature), "invalid signature"
    allowed = os.getenv("QUINN_ALLOWED_SENDERS")
    senders = [s.strip() for s in allowed.split(",") if s.strip()] if allowed else None
    payload = json.loads(body)
    email = parse_postmark_webhook(payload, senders)
    logger.info("Inbound email processed %s", email.id)
    return JSONResponse({"status": "ok"})


def main() -> None:
    serve()


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
