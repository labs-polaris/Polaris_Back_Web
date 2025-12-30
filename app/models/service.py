from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import EnvironmentType, ServiceType


class Service(Base, TimestampMixin):
    __tablename__ = "polaris_services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("polaris_projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[ServiceType] = mapped_column(Enum(ServiceType, name="polaris_servicetype"), nullable=False)
    environment: Mapped[EnvironmentType] = mapped_column(Enum(EnvironmentType, name="polaris_environmenttype"), nullable=False)

    project = relationship("Project", back_populates="services")
