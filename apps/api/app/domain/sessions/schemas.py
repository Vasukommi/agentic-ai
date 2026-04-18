from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    app_id: Optional[str] = None
    end_user_ref: str
    tenant_ref: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    ttl_seconds: int = 3600


class SessionCreateResponse(BaseModel):
    session_token: str
    token_type: str = "bearer"
    expires_at: datetime


class SessionContext(BaseModel):
    session_id: str
    app_id: str
    organization_id: str
    end_user_ref: str
    tenant_ref: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    expires_at: datetime
