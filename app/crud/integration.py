from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.integration import Integration


def list_integrations(db: Session, org_id: str) -> list[Integration]:
    return db.execute(
        select(Integration).where(Integration.org_id == org_id).order_by(Integration.created_at.desc())
    ).scalars().all()


def get_integration(db: Session, integration_id: str) -> Integration | None:
    return db.execute(select(Integration).where(Integration.id == integration_id)).scalar_one_or_none()


def create_integration(
    db: Session,
    org_id: str,
    provider: str,
    config_json: dict,
    is_enabled: bool,
) -> Integration:
    integration = Integration(org_id=org_id, provider=provider, config_json=config_json, is_enabled=is_enabled)
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def update_integration(
    db: Session,
    integration: Integration,
    provider: str | None,
    config_json: dict | None,
    is_enabled: bool | None,
) -> Integration:
    if provider is not None:
        integration.provider = provider
    if config_json is not None:
        integration.config_json = config_json
    if is_enabled is not None:
        integration.is_enabled = is_enabled
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def delete_integration(db: Session, integration: Integration) -> None:
    db.delete(integration)
    db.commit()
