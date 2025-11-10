from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, echo=False, future=True)


def create_db_and_tables() -> None:
    """Create database tables based on SQLModel metadata."""

    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional database session."""

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
