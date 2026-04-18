from fastapi import APIRouter, HTTPException

from app.domain.actions.schemas import ActionDefinition
from app.services.action_registry import action_registry

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("")
def list_actions() -> list[ActionDefinition]:
    return action_registry.list_actions()


@router.get("/{action_id}")
def get_action(action_id: str) -> ActionDefinition:
    action = action_registry.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return action
