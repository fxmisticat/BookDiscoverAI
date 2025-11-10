from sqlmodel import select

from ..database import get_session
from ..models import Feedback
from ..schemas import FeedbackPayload, FeedbackRequest, FeedbackResponse
from .log_service import record_log


def record_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    with get_session() as session:
        feedback = Feedback(book_id=payload.book_id, reaction=payload.reaction, note=payload.note)
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
    response = FeedbackResponse(
        id=feedback.id,
        book_id=feedback.book_id,
        reaction=feedback.reaction,
        note=feedback.note,
        created_at=feedback.created_at,
    )
    record_log("INFO", "Feedback captured", context={"book_id": feedback.book_id, "reaction": feedback.reaction})
    return response


def fetch_feedback(limit: int = 50) -> FeedbackPayload:
    with get_session() as session:
        entries = session.exec(select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)).all()
    items = [
        FeedbackResponse(
            id=entry.id,
            book_id=entry.book_id,
            reaction=entry.reaction,
            note=entry.note,
            created_at=entry.created_at,
        )
        for entry in entries
    ]
    return FeedbackPayload(items=items)
