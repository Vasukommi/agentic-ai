from typing import Optional

from app.domain.actions.schemas import (
    ActionDefinition,
    ActionField,
    ConfirmationPolicy,
)


class ActionRegistry:
    def __init__(self) -> None:
        self._actions = {
            action.id: action
            for action in [
                ActionDefinition(
                    id="invite_team_member",
                    name="Invite team member",
                    description="Invite a new user into the current workspace.",
                    category="identity",
                    risk_level="medium",
                    input_fields=[
                        ActionField(
                            key="email",
                            label="Email",
                            kind="email",
                            description="Email address of the person to invite.",
                        ),
                        ActionField(
                            key="role",
                            label="Role",
                            kind="enum",
                            enum_values=["viewer", "editor", "admin"],
                            description="Role to assign after the invite is accepted.",
                        ),
                    ],
                    confirmation_policy=ConfirmationPolicy(
                        required=True,
                        message="Invite this user to the workspace?",
                    ),
                ),
                ActionDefinition(
                    id="create_project",
                    name="Create project",
                    description="Create a project for the current account.",
                    category="workspace",
                    risk_level="low",
                    input_fields=[
                        ActionField(
                            key="name",
                            label="Project name",
                            kind="string",
                        ),
                        ActionField(
                            key="description",
                            label="Description",
                            kind="string",
                            required=False,
                        ),
                    ],
                ),
                ActionDefinition(
                    id="change_plan",
                    name="Change subscription plan",
                    description="Change the current workspace subscription plan.",
                    category="billing",
                    risk_level="high",
                    input_fields=[
                        ActionField(
                            key="plan",
                            label="Plan",
                            kind="enum",
                            enum_values=["starter", "growth", "enterprise"],
                        ),
                        ActionField(
                            key="effective_date",
                            label="Effective date",
                            kind="date",
                            required=False,
                        ),
                    ],
                    confirmation_policy=ConfirmationPolicy(
                        required=True,
                        message="Changing plans may affect billing. Confirm before continuing.",
                    ),
                ),
            ]
        }

    def list_actions(self) -> list[ActionDefinition]:
        return list(self._actions.values())

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        return self._actions.get(action_id)


action_registry = ActionRegistry()
