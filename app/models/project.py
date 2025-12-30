from uuid import uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "polaris_projects"
    __table_args__ = (UniqueConstraint("org_id", "key", name="uq_polaris_project_key_org"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("polaris_organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    key: Mapped[str] = mapped_column(String(50), nullable=False)

    organization = relationship("Organization", back_populates="projects")
    services = relationship("Service", back_populates="project", cascade="all, delete-orphan")
