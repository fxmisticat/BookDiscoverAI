from __future__ import annotations

import random
from collections import Counter
from typing import List

from sqlmodel import delete, select

from ..database import get_session
from ..models import Book, BookTrope
from ..schemas import TropeRecommendationResponse
from .log_service import record_log

TROPE_LIBRARY: List[str] = [
    "enemies to lovers",
    "forbidden romance",
    "forced proximity",
    "mates bond",
    "magical academy",
    "morally gray hero",
    "slow burn",
    "found family",
    "royal intrigue",
    "redemption arc",
]

BOOK_TROPE_ASSIGNMENTS = {
    "Dragon's Embrace": ["mates bond", "morally gray hero", "forbidden romance"],
    "Moonlit Oath": ["forced proximity", "slow burn", "royal intrigue"],
    "Academy of Thorns": ["magical academy", "enemies to lovers", "found family"],
    "Stormbound Hearts": ["redemption arc", "slow burn", "forbidden romance"],
}

TROPE_CANDIDATES = [
    {
        "id": "shadow-court-bargain",
        "title": "Shadow Court Bargain",
        "author": "Mira Lark",
        "description": "A human negotiator is bound to a fae prince after a perilous bargain for her sister's freedom.",
        "cover_url": "https://placehold.co/400x600?text=Shadow",
        "tropes": ["enemies to lovers", "forbidden romance", "royal intrigue"],
        "explanation": "This pick leans hard into the enemies-to-lovers tension and royal intrigue you keep revisiting.",
    },
    {
        "id": "ashborne-vow",
        "title": "Ashborne Vow",
        "author": "Khalia Dusk",
        "description": "An exiled fire mage must fake an engagement with her rival to reclaim her throne.",
        "cover_url": "https://placehold.co/400x600?text=Ashborne",
        "tropes": ["forced proximity", "enemies to lovers", "redemption arc"],
        "explanation": "A fiery forced-proximity partnership that mirrors your favorite redemption arcs.",
    },
    {
        "id": "celestial-threads",
        "title": "Celestial Threads",
        "author": "Rowan Illyr",
        "description": "Twin seers are drafted into a celestial academy where fate knots their hearts together.",
        "cover_url": "https://placehold.co/400x600?text=Celestial",
        "tropes": ["magical academy", "slow burn", "found family"],
        "explanation": "A lush academy setting with the slow-burn tension and found family comfort you crave.",
    },
    {
        "id": "siren-of-the-tempest",
        "title": "Siren of the Tempest",
        "author": "Elara Voss",
        "description": "A stormcaller and a pirate queen must join forces to calm a raging sea god.",
        "cover_url": "https://placehold.co/400x600?text=Tempest",
        "tropes": ["found family", "mates bond", "morally gray hero"],
        "explanation": "This sea-swept adventure pairs a morally gray hero with a fated mate bond twist.",
    },
    {
        "id": "gilded-sanctum",
        "title": "Gilded Sanctum",
        "author": "Aster Quinn",
        "description": "A healer infiltrates a holy order and discovers her soulmate among the sworn protectors.",
        "cover_url": "https://placehold.co/400x600?text=Sanctum",
        "tropes": ["mates bond", "forbidden romance", "slow burn"],
        "explanation": "Sweeping forbidden romance with a patient slow burn and undeniable soulmate pull.",
    },
]


def _random_tropes() -> List[str]:
    return random.sample(TROPE_LIBRARY, 3)


def extract_tropes(force: bool = False) -> int:
    """Populate the book_tropes table with demo data."""

    with get_session() as session:
        if force:
            session.exec(delete(BookTrope))
        books = list(session.exec(select(Book)))
        processed = 0
        for book in books:
            assigned = BOOK_TROPE_ASSIGNMENTS.get(book.title) or _random_tropes()
            for trope in assigned:
                existing = session.exec(
                    select(BookTrope).where(
                        BookTrope.book_id == book.id, BookTrope.trope == trope
                    )
                ).first()
                if existing:
                    continue
                session.add(
                    BookTrope(
                        book_id=book.id,
                        trope=trope,
                        source="demo-llm",
                        confidence=round(random.uniform(0.6, 0.95), 3),
                    )
                )
                processed += 1
        session.commit()

    record_log(
        "INFO",
        "Trope extraction completed",
        source="trope-engine",
        context={"force": force, "processed": processed},
    )
    return processed


def get_trope_recommendations(limit: int = 10) -> List[TropeRecommendationResponse]:
    with get_session() as session:
        if not list(session.exec(select(BookTrope).limit(1))):
            extract_tropes(force=False)
        trope_rows = list(session.exec(select(BookTrope)))
        if not trope_rows:
            return []
        profile = Counter(row.trope for row in trope_rows)

    if not profile:
        return []

    scored_candidates: List[TropeRecommendationResponse] = []
    for candidate in TROPE_CANDIDATES:
        candidate_tropes = candidate["tropes"]
        overlap = [trope for trope in candidate_tropes if trope in profile]
        if not overlap:
            continue
        score = 0.0
        for trope in overlap:
            freq = profile[trope]
            score += 1.0 / (freq + 1.0)
        normalized = min(0.99, 0.55 + score / (len(overlap) * 2))
        explanation = candidate["explanation"]
        scored_candidates.append(
            TropeRecommendationResponse(
                id=candidate["id"],
                title=candidate["title"],
                author=candidate["author"],
                description=candidate.get("description"),
                cover_url=candidate.get("cover_url"),
                matched_tropes=overlap,
                all_tropes=candidate_tropes,
                score=round(normalized * 100, 2),
                explanation=explanation,
            )
        )

    scored_candidates.sort(key=lambda item: item.score, reverse=True)
    top_results = scored_candidates[:limit]

    record_log(
        "INFO",
        "Generated trope-based recommendations",
        source="trope-engine",
        context={"results": len(top_results)},
    )
    return top_results
