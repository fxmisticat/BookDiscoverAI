from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Column, DateTime, Field, JSON, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


class AppSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    abs_url: Optional[str] = Field(default=None, description="Audiobookshelf base URL")
    abs_token: Optional[str] = Field(default=None, description="Audiobookshelf API token")
    google_books_api_key: Optional[str] = Field(default=None)
    open_library_enabled: bool = Field(default=True)
    embedding_provider: str = Field(default="openai")
    embedding_model: str = Field(default="text-embedding-3-small")
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4o-mini")
    demo_mode: bool = Field(default=True)


class SyncJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_type: str = Field(default="abs_sync")
    status: str = Field(default="pending")
    message: Optional[str] = Field(default=None)
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    finished_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    description: Optional[str] = Field(default=None)
    cover_url: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None)
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class Recommendation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    score: float = Field(default=0.0)
    explanation: Optional[str] = Field(default=None)
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class LogEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str = Field(default="INFO")
    source: str = Field(default="backend")
    message: str
    context: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    reaction: str = Field(default="neutral")
    note: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class BookTrope(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("book_id", "trope", name="uix_book_trope"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    trope: str = Field(index=True)
    source: str = Field(default="llm")
    confidence: Optional[float] = Field(default=None)
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
