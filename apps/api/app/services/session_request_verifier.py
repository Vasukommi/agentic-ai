from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Mapping

from app.core.config import get_settings

TIMESTAMP_HEADER = "X-Agentic-Timestamp"
SIGNATURE_HEADER = "X-Agentic-Signature"


class SessionRequestVerificationError(ValueError):
    pass


class SessionRequestVerifier:
    def verify(self, headers: Mapping[str, str], body: bytes) -> None:
        settings = get_settings()
        if not settings.session_signing_secret:
            return

        timestamp = headers.get(TIMESTAMP_HEADER)
        signature = headers.get(SIGNATURE_HEADER)
        if not timestamp or not signature:
            raise SessionRequestVerificationError("Missing session request signature")

        try:
            timestamp_seconds = int(timestamp)
        except ValueError as error:
            raise SessionRequestVerificationError("Invalid session request timestamp") from error

        now_seconds = int(datetime.now(timezone.utc).timestamp())
        if abs(now_seconds - timestamp_seconds) > settings.session_signature_ttl_seconds:
            raise SessionRequestVerificationError("Session request signature expired")

        expected_signature = self._build_signature(
            secret=settings.session_signing_secret,
            timestamp=timestamp,
            body=body,
        )
        normalized_signature = signature.removeprefix("sha256=")
        if not hmac.compare_digest(normalized_signature, expected_signature):
            raise SessionRequestVerificationError("Invalid session request signature")

    def _build_signature(self, secret: str, timestamp: str, body: bytes) -> str:
        payload = timestamp.encode("utf-8") + b"." + body
        return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


session_request_verifier = SessionRequestVerifier()
