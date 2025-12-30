import time

from sqlalchemy import create_engine, text

from app.core.config import settings


def wait_for_db(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    last_error = None
    for _ in range(max_attempts):
        try:
            engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as exc:  # pragma: no cover - retry loop
            last_error = exc
            time.sleep(delay_seconds)
    raise SystemExit(f"Database not ready: {last_error}")


if __name__ == "__main__":
    wait_for_db()
