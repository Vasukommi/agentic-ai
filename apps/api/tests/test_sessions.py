import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

from app.core.config import get_settings


def _signed_headers(
    secret: str,
    body: bytes,
    timestamp: Optional[int] = None,
) -> dict[str, str]:
    signed_at = timestamp or int(datetime.now(timezone.utc).timestamp())
    payload = f"{signed_at}.".encode("utf-8") + body
    signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Agentic-Timestamp": str(signed_at),
        "X-Agentic-Signature": f"sha256={signature}",
    }


def _configure_signing(monkeypatch, *, secret: str, ttl_seconds: Optional[int] = None) -> None:
    monkeypatch.setenv("AGENTIC_SESSION_SIGNING_SECRET", secret)
    if ttl_seconds is not None:
        monkeypatch.setenv("AGENTIC_SESSION_SIGNATURE_TTL_SECONDS", str(ttl_seconds))
    get_settings.cache_clear()


def test_create_session_requires_valid_signature_when_secret_is_configured(client, monkeypatch):
    _configure_signing(monkeypatch, secret="topsecret")

    response = client.post(
        "/v1/sessions",
        json={
            "end_user_ref": "user_123",
            "tenant_ref": "tenant_123",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing session request signature"}


def test_create_session_accepts_valid_signed_request(client, monkeypatch):
    secret = "topsecret"
    _configure_signing(monkeypatch, secret=secret)
    body = json.dumps(
        {
            "end_user_ref": "user_123",
            "tenant_ref": "tenant_123",
            "roles": ["member"],
            "permissions": ["runs:read_all_tenant"],
        }
    ).encode("utf-8")

    response = client.post(
        "/v1/sessions",
        content=body,
        headers=_signed_headers(secret, body),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["session_token"].startswith("ags_")


def test_create_session_rejects_expired_signature(client, monkeypatch):
    secret = "topsecret"
    _configure_signing(monkeypatch, secret=secret, ttl_seconds=60)
    body = json.dumps({"end_user_ref": "user_123"}).encode("utf-8")

    response = client.post(
        "/v1/sessions",
        content=body,
        headers=_signed_headers(secret, body, timestamp=1),
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Session request signature expired"}
