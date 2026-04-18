from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.domain.sessions.schemas import (
    SessionContext,
    SessionCreateRequest,
    SessionCreateResponse,
)
from app.models.app import SaasApp
from app.models.app_session import AppSession
from app.services.bootstrap import get_or_create_default_app

TOKEN_PREFIX = "ags_"
MAX_TTL_SECONDS = 24 * 60 * 60


class SessionService:
    def create_session(self, db, request: SessionCreateRequest) -> SessionCreateResponse:
        app = self._resolve_app(db, request.app_id)
        ttl_seconds = min(max(request.ttl_seconds, 60), MAX_TTL_SECONDS)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        session_token = f"{TOKEN_PREFIX}{secrets.token_urlsafe(32)}"

        app_session = AppSession(
            app_id=app.id,
            session_token_hash=self.hash_token(session_token),
            end_user_ref=request.end_user_ref,
            tenant_ref=request.tenant_ref,
            roles=request.roles,
            permissions=request.permissions,
            expires_at=expires_at,
        )
        db.add(app_session)
        db.commit()

        return SessionCreateResponse(
            session_token=session_token,
            expires_at=expires_at,
        )

    def resolve_session(self, db, session_token: str) -> Optional[AppSession]:
        token_hash = self.hash_token(session_token)
        now = datetime.now(timezone.utc)
        return (
            db.query(AppSession)
            .filter(
                AppSession.session_token_hash == token_hash,
                AppSession.revoked_at.is_(None),
                AppSession.expires_at > now,
            )
            .first()
        )

    def to_context(self, app_session: AppSession) -> SessionContext:
        return SessionContext(
            session_id=app_session.id,
            app_id=app_session.app_id,
            organization_id=app_session.app.organization_id,
            end_user_ref=app_session.end_user_ref,
            tenant_ref=app_session.tenant_ref,
            roles=app_session.roles,
            permissions=app_session.permissions,
            expires_at=app_session.expires_at,
        )

    def hash_token(self, session_token: str) -> str:
        return hashlib.sha256(session_token.encode("utf-8")).hexdigest()

    def _resolve_app(self, db, app_id: Optional[str]) -> SaasApp:
        if app_id is None:
            return get_or_create_default_app(db)

        app = db.query(SaasApp).filter(SaasApp.id == app_id).first()
        if app is None:
            raise ValueError("App not found")
        return app


session_service = SessionService()
