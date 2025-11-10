import random
import time
from datetime import datetime
from typing import List

from sqlmodel import select

from ..database import get_session
from ..models import Book, SyncJob
from ..schemas import BookResponse, RecommendationResponse
from .log_service import record_log


SEED_BOOKS: List[dict] = [
    {
        "title": "Dragon's Embrace",
        "author": "Lena Hargrave",
        "description": "A fierce dragon rider falls for an enigmatic mage in a realm on the brink of war.",
        "cover_url": "https://placehold.co/400x600?text=Dragon",
    },
    {
        "title": "Moonlit Oath",
        "author": "Isla Fenwick",
        "description": "Two rival witches unite to break a blood oath beneath an eclipse.",
        "cover_url": "https://placehold.co/400x600?text=Moonlit",
    },
    {
        "title": "Academy of Thorns",
        "author": "C. J. Rowen",
        "description": "A scholarship student navigates dangerous politics and forbidden romance at a magical academy.",
        "cover_url": "https://placehold.co/400x600?text=Academy",
    },
    {
        "title": "Stormbound Hearts",
        "author": "N. D. Rook",
        "description": "Elemental guardians must reconcile their past to calm the tempest threatening their world.",
        "cover_url": "https://placehold.co/400x600?text=Storm",
    },
]


def _seed_books(session) -> None:
    existing = list(session.exec(select(Book)))
    if existing:
        return
    for book in SEED_BOOKS:
        session.add(Book(**book, reason="Seeded demo title"))
    session.commit()


def run_sync_job(job: SyncJob) -> None:
    """Simulate a sync against external services."""

    record_log("INFO", "Starting demo sync job", context={"job_id": job.id})
    time.sleep(0.5)
    with get_session() as session:
        persisted_job = session.get(SyncJob, job.id)
        if not persisted_job:
            return
        persisted_job.status = "running"
        session.add(persisted_job)
        session.commit()
        session.refresh(persisted_job)

    with get_session() as session:
        _seed_books(session)
        persisted_job = session.get(SyncJob, job.id)
        if not persisted_job:
            return
        persisted_job.status = "completed"
        persisted_job.finished_at = datetime.utcnow()
        persisted_job.message = "Demo sync populated seed titles"
        session.add(persisted_job)
        session.commit()
    record_log("INFO", "Demo sync completed", context={"job_id": job.id})


def start_sync_job() -> SyncJob:
    with get_session() as session:
        job = SyncJob(status="queued", message="Sync scheduled")
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def get_last_job() -> SyncJob | None:
    with get_session() as session:
        return session.exec(select(SyncJob).order_by(SyncJob.started_at.desc())).first()


def get_recommendations(limit: int = 10) -> List[RecommendationResponse]:
    with get_session() as session:
        books = list(session.exec(select(Book).limit(limit)))
        if not books:
            _seed_books(session)
            books = list(session.exec(select(Book).limit(limit)))
        recommendations = []
        for book in books:
            explanation = book.reason or random.choice(
                [
                    "Shares the same slow-burn magic academy vibe you love.",
                    "Features a fierce heroine and a brooding mage love interest.",
                    "Combines political intrigue with enchanting worldbuilding.",
                ]
            )
            score = round(random.uniform(0.7, 0.99), 3)
            book_payload = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "cover_url": book.cover_url,
                "reason": book.reason,
            }
            recommendations.append(
                RecommendationResponse(
                    id=book.id,
                    book=BookResponse(**book_payload),
                    score=score,
                    explanation=explanation,
                    generated_at=datetime.utcnow(),
                )
            )
    return recommendations
