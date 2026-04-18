from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

FieldKind = Literal[
    "string",
    "number",
    "integer",
    "boolean",
    "date",
    "datetime",
    "email",
    "enum",
    "object",
]

RiskLevel = Literal["read", "low", "medium", "high"]
RunStatus = Literal["needs_input", "needs_confirmation", "completed", "failed"]


class ActionField(BaseModel):
    key: str
    label: str
    kind: FieldKind
    description: Optional[str] = None
    required: bool = True
    enum_values: list[str] = Field(default_factory=list)
    sensitive: bool = False


class ConfirmationPolicy(BaseModel):
    required: bool = False
    message: Optional[str] = None


class ActionDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: str
    risk_level: RiskLevel
    input_fields: list[ActionField]
    confirmation_policy: ConfirmationPolicy = Field(default_factory=ConfirmationPolicy)


class ActionCreateRequest(ActionDefinition):
    pass


class ActionRunRequest(BaseModel):
    action_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False
    dry_run: bool = True
    end_user_ref: Optional[str] = None


class MissingField(BaseModel):
    key: str
    label: str
    kind: FieldKind
    description: Optional[str] = None


class ActionRunResponse(BaseModel):
    run_id: str
    action_id: str
    status: RunStatus
    message: str
    missing_fields: list[MissingField] = Field(default_factory=list)
    normalized_inputs: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class ActionRunRecord(ActionRunResponse):
    created_at: Optional[datetime] = None
