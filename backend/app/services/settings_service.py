from sqlmodel import select

from ..database import get_session
from ..models import AppSettings
from ..schemas import SettingsResponse, SettingsUpdate
from .log_service import record_log


def get_settings_snapshot() -> SettingsResponse:
    with get_session() as session:
        settings = session.exec(select(AppSettings)).first()
        if not settings:
            settings = AppSettings()
            session.add(settings)
            session.commit()
            session.refresh(settings)
    response = SettingsResponse(
        abs_url=settings.abs_url,
        google_books_api_key=settings.google_books_api_key,
        open_library_enabled=settings.open_library_enabled,
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        demo_mode=settings.demo_mode,
    )
    return response


def update_settings(payload: SettingsUpdate) -> SettingsResponse:
    with get_session() as session:
        settings = session.exec(select(AppSettings)).first()
        if not settings:
            settings = AppSettings()
            session.add(settings)
            session.commit()
            session.refresh(settings)
        update_data = payload.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    response = SettingsResponse(
        abs_url=settings.abs_url,
        google_books_api_key=settings.google_books_api_key,
        open_library_enabled=settings.open_library_enabled,
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        demo_mode=settings.demo_mode,
    )
    record_log(
        "INFO",
        "Settings updated",
        context={"abs_url": bool(settings.abs_url), "demo_mode": settings.demo_mode},
    )
    return response
