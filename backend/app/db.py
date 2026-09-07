"""Database engine and session helpers.

SQLite by default so the app runs with zero setup; point DATABASE_URL at Postgres
in production. The engine is created lazily so tests can swap in an in-memory
database before the app starts.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./agent_ops.db")

# check_same_thread=False lets the SQLite connection be shared across requests.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=_connect_args)


def init_db() -> None:
    # Import models so SQLModel sees the tables before creating them.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
