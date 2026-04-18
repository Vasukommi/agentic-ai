from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.domain.actions.defaults import DEFAULT_ACTIONS
from app.services.action_registry import action_service
from app.services.bootstrap import get_or_create_default_app


def init_db() -> None:
    settings = get_settings()
    if not settings.auto_create_tables:
        return

    # Local bootstrap only. Production should use Alembic migrations.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    seed_default_data()


def seed_default_data() -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        app = get_or_create_default_app(db)
        for action in DEFAULT_ACTIONS:
            if action_service.get_action(db, action.id, app_id=app.id) is None:
                action_service.create_action(db, action, app_id=app.id, commit=False)
        db.commit()
    finally:
        db.close()
