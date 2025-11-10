from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    abs_url: Optional[str] = Field(default=None, description="Audiobookshelf base URL")
    abs_token: Optional[str] = Field(default=None, description="Audiobookshelf API token")
    google_books_api_key: Optional[str] = None
    open_library_enabled: Optional[bool] = None
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    demo_mode: Optional[bool] = None


class SettingsResponse(BaseModel):
    abs_url: Optional[str]
    google_books_api_key: Optional[str]
    open_library_enabled: bool
    embedding_provider: str
    embedding_model: str
    llm_provider: str
    llm_model: str
    demo_mode: bool


class SyncJobResponse(BaseModel):
    id: int
    job_type: str
    status: str
    message: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str]
    cover_url: Optional[str]
    reason: Optional[str]


class RecommendationResponse(BaseModel):
    id: int
    book: BookResponse
    score: float
    explanation: Optional[str]
    generated_at: datetime


class LogEntryResponse(BaseModel):
    id: int
    level: str
    source: str
    message: str
    context: Optional[dict]
    created_at: datetime


class ClientLogEntry(BaseModel):
    level: str = Field(default="ERROR")
    source: str = Field(default="frontend")
    message: str
    context: Optional[dict] = None


class FeedbackRequest(BaseModel):
    book_id: int
    reaction: str
    note: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    book_id: int
    reaction: str
    note: Optional[str]
    created_at: datetime


class RecommendationsPayload(BaseModel):
    items: List[RecommendationResponse]


class LogsPayload(BaseModel):
    items: List[LogEntryResponse]


class FeedbackPayload(BaseModel):
    items: List[FeedbackResponse]


class TropeExtractionResponse(BaseModel):
    status: str = Field(default="scheduled")
    scheduled: bool = Field(default=True)
    processed: int = Field(default=0)
    message: str = Field(default="Trope extraction job queued")


class TropeRecommendationResponse(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str]
    cover_url: Optional[str]
    matched_tropes: List[str]
    all_tropes: List[str]
    score: float
    explanation: str


class TropeRecommendationsPayload(BaseModel):
    items: List[TropeRecommendationResponse]
