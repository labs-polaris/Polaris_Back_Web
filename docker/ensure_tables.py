from sqlalchemy import inspect

from app.core.database import engine
from app.models import Base


def ensure_tables() -> None:
    inspector = inspect(engine)
    if inspector.has_table("polaris_users"):
        return
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    ensure_tables()
