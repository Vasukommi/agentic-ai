from typing import Optional

from app.domain.actions.schemas import (
    ActionCreateRequest,
    ActionDefinition,
    ConfirmationPolicy,
)
from app.models.action import Action


class ActionService:
    def list_actions(self, db, app_id: Optional[str] = None) -> list[ActionDefinition]:
        query = db.query(Action).filter(Action.enabled.is_(True)).order_by(Action.created_at.asc())
        if app_id:
            query = query.filter(Action.app_id == app_id)
        return [self.to_definition(action) for action in query.all()]

    def get_action(self, db, action_id: str, app_id: Optional[str] = None) -> Optional[Action]:
        query = db.query(Action).filter(Action.key == action_id, Action.enabled.is_(True))
        if app_id:
            query = query.filter(Action.app_id == app_id)
        return query.first()

    def create_action(
        self,
        db,
        request: ActionCreateRequest,
        app_id: str,
        commit: bool = True,
    ) -> Action:
        action = Action(
            app_id=app_id,
            key=request.id,
            name=request.name,
            description=request.description,
            category=request.category,
            risk_level=request.risk_level,
            input_fields=[field.model_dump() for field in request.input_fields],
            confirmation_policy=request.confirmation_policy.model_dump(),
        )
        db.add(action)
        if commit:
            db.commit()
            db.refresh(action)
        else:
            db.flush()
        return action

    def to_definition(self, action: Action) -> ActionDefinition:
        return ActionDefinition(
            id=action.key,
            name=action.name,
            description=action.description,
            category=action.category,
            risk_level=action.risk_level,
            input_fields=action.input_fields,
            confirmation_policy=ConfirmationPolicy(**action.confirmation_policy),
        )


action_service = ActionService()
