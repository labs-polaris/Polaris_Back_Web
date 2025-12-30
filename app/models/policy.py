from uuid import uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import PolicyType


class Policy(Base, TimestampMixin):
    __tablename__ = "polaris_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("polaris_organizations.id"), nullable=False)
    type: Mapped[PolicyType] = mapped_column(Enum(PolicyType, name="polaris_policytype"), nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization = relationship("Organization", back_populates="policies")
