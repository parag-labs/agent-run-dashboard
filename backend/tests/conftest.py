"""Shared test fixtures: a fresh in-memory database and an authenticated client."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app


@pytest.fixture()
def client():
    # A private in-memory SQLite shared across the test's connections.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_headers(client, username="alice", password="s3cret!") -> dict[str, str]:
    resp = client.post("/api/auth/register", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
