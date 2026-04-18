from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_app_session
from app.db.session import get_db
from app.domain.actions.schemas import ActionRunRecord, ActionRunRequest, ActionRunResponse
from app.models.app_session import AppSession
from app.services.action_registry import action_service
from app.services.run_service import run_service

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("")
def list_runs(
    db: Session = Depends(get_db),
    app_session: AppSession = Depends(get_current_app_session),
) -> list[ActionRunRecord]:
    return run_service.list_runs_for_session(db, app_session=app_session)


@router.post("")
def create_run(
    request: ActionRunRequest,
    db: Session = Depends(get_db),
    app_session: AppSession = Depends(get_current_app_session),
) -> ActionRunResponse:
    action = action_service.get_action(db, request.action_id, app_id=app_session.app_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return run_service.create_run(
        db=db,
        action=action,
        request=request,
        app_session=app_session,
    )
