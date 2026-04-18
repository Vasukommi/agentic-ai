from fastapi import Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.sessions.schemas import SessionCreateRequest
from app.models.app_session import AppSession
from app.services.session_request_verifier import (
    SessionRequestVerificationError,
    session_request_verifier,
)
from app.services.session_service import session_service

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_app_session(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AppSession:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session token",
        )

    app_session = session_service.resolve_session(db, credentials.credentials)
    if app_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    return app_session


async def get_signed_session_create_request(request: Request) -> SessionCreateRequest:
    body = await request.body()
    try:
        session_request_verifier.verify(request.headers, body)
        return SessionCreateRequest.model_validate_json(body)
    except SessionRequestVerificationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error
