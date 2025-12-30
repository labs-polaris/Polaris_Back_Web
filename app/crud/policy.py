from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.policy import Policy


def list_policies(db: Session, org_id: str) -> list[Policy]:
    return db.execute(select(Policy).where(Policy.org_id == org_id).order_by(Policy.created_at.desc())).scalars().all()


def get_policy(db: Session, policy_id: str) -> Policy | None:
    return db.execute(select(Policy).where(Policy.id == policy_id)).scalar_one_or_none()


def create_policy(db: Session, org_id: str, policy_type: str, config_json: dict, is_enabled: bool) -> Policy:
    policy = Policy(org_id=org_id, type=policy_type, config_json=config_json, is_enabled=is_enabled)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_policy(
    db: Session,
    policy: Policy,
    policy_type: str | None,
    config_json: dict | None,
    is_enabled: bool | None,
) -> Policy:
    if policy_type is not None:
        policy.type = policy_type
    if config_json is not None:
        policy.config_json = config_json
    if is_enabled is not None:
        policy.is_enabled = is_enabled
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def delete_policy(db: Session, policy: Policy) -> None:
    db.delete(policy)
    db.commit()
