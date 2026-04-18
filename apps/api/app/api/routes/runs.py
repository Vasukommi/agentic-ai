from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.actions.schemas import ActionRunRecord, ActionRunRequest, ActionRunResponse
from app.services.action_registry import action_service
from app.services.bootstrap import get_or_create_default_app
from app.services.run_service import run_service

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("")
def list_runs(db: Session = Depends(get_db)) -> list[ActionRunRecord]:
    return run_service.list_runs(db)


@router.post("")
def create_run(request: ActionRunRequest, db: Session = Depends(get_db)) -> ActionRunResponse:
    app = get_or_create_default_app(db)
    action = action_service.get_action(db, request.action_id, app_id=app.id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return run_service.create_run(db=db, action=action, request=request)
