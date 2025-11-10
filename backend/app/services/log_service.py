from typing import Optional

from sqlmodel import select

from ..database import get_session
from ..models import LogEntry
from ..schemas import ClientLogEntry, LogEntryResponse, LogsPayload


def record_log(level: str, message: str, source: str = "backend", context: Optional[dict] = None) -> LogEntry:
    with get_session() as session:
        entry = LogEntry(level=level.upper(), message=message, source=source, context=context)
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry


def record_client_log(payload: ClientLogEntry) -> LogEntryResponse:
    entry = record_log(payload.level, payload.message, payload.source, payload.context)
    return LogEntryResponse(
        id=entry.id,
        level=entry.level,
        source=entry.source,
        message=entry.message,
        context=entry.context,
        created_at=entry.created_at,
    )


def fetch_logs(level: Optional[str] = None, source: Optional[str] = None, limit: int = 100) -> LogsPayload:
    with get_session() as session:
        query = select(LogEntry).order_by(LogEntry.created_at.desc()).limit(limit)
        if level:
            query = query.where(LogEntry.level == level.upper())
        if source:
            query = query.where(LogEntry.source == source)
        entries = list(session.exec(query))
    items = [
        LogEntryResponse(
            id=entry.id,
            level=entry.level,
            source=entry.source,
            message=entry.message,
            context=entry.context,
            created_at=entry.created_at,
        )
        for entry in entries
    ]
    return LogsPayload(items=items)
