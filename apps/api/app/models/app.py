from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SaasApp(Base):
    __tablename__ = "apps"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_apps_org_slug"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(120), nullable=False)
    environment = Column(String(40), nullable=False, default="development")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    organization = relationship("Organization", back_populates="apps")
    actions = relationship("Action", back_populates="app", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="app", cascade="all, delete-orphan")
