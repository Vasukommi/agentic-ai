from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Action(Base):
    __tablename__ = "actions"
    __table_args__ = (UniqueConstraint("app_id", "key", name="uq_actions_app_key"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    app_id = Column(String(36), ForeignKey("apps.id"), nullable=False, index=True)
    key = Column(String(120), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    category = Column(String(120), nullable=False)
    risk_level = Column(String(40), nullable=False)
    input_fields = Column(JSON, nullable=False, default=list)
    confirmation_policy = Column(JSON, nullable=False, default=dict)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    app = relationship("SaasApp", back_populates="actions")
    runs = relationship("Run", back_populates="action")
