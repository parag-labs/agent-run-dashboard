"""Auth flow: registration, login, duplicate handling, and token protection."""

from __future__ import annotations

from tests.conftest import auth_headers


def test_register_returns_a_token(client):
    resp = client.post("/api/auth/register", json={"username": "bob", "password": "pw123"})
    assert resp.status_code == 201
    assert "access_token" in resp.json()


def test_register_rejects_duplicate_username(client):
    client.post("/api/auth/register", json={"username": "dup", "password": "pw"})
    resp = client.post("/api/auth/register", json={"username": "dup", "password": "pw"})
    assert resp.status_code == 409


def test_login_with_correct_password_succeeds(client):
    client.post("/api/auth/register", json={"username": "carol", "password": "pw"})
    resp = client.post("/api/auth/login", json={"username": "carol", "password": "pw"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_fails(client):
    client.post("/api/auth/register", json={"username": "dave", "password": "right"})
    resp = client.post("/api/auth/login", json={"username": "dave", "password": "wrong"})
    assert resp.status_code == 401


def test_protected_route_requires_a_token(client):
    assert client.get("/api/runs").status_code == 401


def test_protected_route_rejects_a_garbage_token(client):
    resp = client.get("/api/runs", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401


def test_health_is_open(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_valid_token_reaches_protected_route(client):
    headers = auth_headers(client)
    assert client.get("/api/runs", headers=headers).status_code == 200
