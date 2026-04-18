from fastapi import APIRouter, HTTPException

from app.domain.actions.schemas import ActionRunRequest, ActionRunResponse
from app.services.action_registry import action_registry
from app.services.run_service import run_service

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("")
def create_run(request: ActionRunRequest) -> ActionRunResponse:
    action = action_registry.get_action(request.action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return run_service.create_run(action=action, request=request)
