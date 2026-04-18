from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class AppSession(Base):
    __tablename__ = "app_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    app_id = Column(String(36), ForeignKey("apps.id"), nullable=False, index=True)
    session_token_hash = Column(String(64), nullable=False, unique=True, index=True)
    end_user_ref = Column(String(255), nullable=False, index=True)
    tenant_ref = Column(String(255), nullable=True, index=True)
    roles = Column(JSON, nullable=False, default=list)
    permissions = Column(JSON, nullable=False, default=list)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    app = relationship("SaasApp", back_populates="sessions")
    runs = relationship("Run", back_populates="session")
