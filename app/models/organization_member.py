from uuid import uuid4

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import OrgRole


class OrganizationMember(Base, TimestampMixin):
    __tablename__ = "polaris_organization_members"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_polaris_org_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("polaris_organizations.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("polaris_users.id"), nullable=False)
    role: Mapped[OrgRole] = mapped_column(Enum(OrgRole, name="polaris_orgrole"), nullable=False, default=OrgRole.member)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="memberships")
