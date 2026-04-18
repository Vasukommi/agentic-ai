from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_signed_session_create_request
from app.db.session import get_db
from app.domain.sessions.schemas import SessionCreateRequest, SessionCreateResponse
from app.services.session_service import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    request: SessionCreateRequest = Depends(get_signed_session_create_request),
    db: Session = Depends(get_db),
) -> SessionCreateResponse:
    try:
        return session_service.create_session(db, request)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
