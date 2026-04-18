from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    app_id = Column(String(36), ForeignKey("apps.id"), nullable=False, index=True)
    action_id = Column(String(36), ForeignKey("actions.id"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("app_sessions.id"), nullable=True, index=True)
    status = Column(String(40), nullable=False, index=True)
    message = Column(String(1000), nullable=False)
    inputs = Column(JSON, nullable=False, default=dict)
    normalized_inputs = Column(JSON, nullable=False, default=dict)
    missing_fields = Column(JSON, nullable=False, default=list)
    result = Column(JSON, nullable=False, default=dict)
    confirmed = Column(Boolean, nullable=False, default=False)
    dry_run = Column(Boolean, nullable=False, default=True)
    actor_type = Column(String(40), nullable=False, default="end_user")
    end_user_ref = Column(String(255), nullable=True)
    tenant_ref = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    app = relationship("SaasApp", back_populates="runs")
    action = relationship("Action", back_populates="runs")
    session = relationship("AppSession", back_populates="runs")
    audit_events = relationship("AuditEvent", back_populates="run", cascade="all, delete-orphan")
