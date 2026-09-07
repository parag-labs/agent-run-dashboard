"""Persistence models: a user and the agent runs they record."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=_now)


class Run(SQLModel, table=True):
    """One recorded agent run - what the dashboard lists and aggregates."""

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(index=True, foreign_key="user.id")
    name: str
    model: str
    status: str = "success"  # success | error | running
    tokens: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=_now)
