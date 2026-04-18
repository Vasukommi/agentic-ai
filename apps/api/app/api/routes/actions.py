from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.actions.schemas import ActionCreateRequest, ActionDefinition
from app.services.action_registry import action_service
from app.services.bootstrap import get_or_create_default_app

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("")
def list_actions(db: Session = Depends(get_db)) -> list[ActionDefinition]:
    app = get_or_create_default_app(db)
    return action_service.list_actions(db, app_id=app.id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_action(
    request: ActionCreateRequest,
    db: Session = Depends(get_db),
) -> ActionDefinition:
    app = get_or_create_default_app(db)
    try:
        action = action_service.create_action(db, request, app_id=app.id)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Action already exists") from error
    return action_service.to_definition(action)


@router.get("/{action_id}")
def get_action(action_id: str, db: Session = Depends(get_db)) -> ActionDefinition:
    app = get_or_create_default_app(db)
    action = action_service.get_action(db, action_id, app_id=app.id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return action_service.to_definition(action)
