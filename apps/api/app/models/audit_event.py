from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    app_id = Column(String(36), ForeignKey("apps.id"), nullable=False, index=True)
    run_id = Column(String(36), ForeignKey("runs.id"), nullable=True, index=True)
    event_type = Column(String(120), nullable=False, index=True)
    summary = Column(String(1000), nullable=False)
    event_metadata = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    run = relationship("Run", back_populates="audit_events")
