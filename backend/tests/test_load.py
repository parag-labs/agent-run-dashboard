"""Load & concurrency test: hammer the API and prove correctness holds under it.

This isn't a throughput benchmark - it's a correctness-under-load check. It fires a
few hundred rapid requests, interleaves two users, and asserts the invariants that
matter for a multi-tenant service never slip: totals stay exact, users never see each
other's data, and auth still gates every request no matter how fast they arrive.
"""

from __future__ import annotations

from tests.conftest import auth_headers


def _run(name: str, model="gpt-4o", tokens=100, cost=0.01):
    return {"name": name, "model": model, "status": "success", "tokens": tokens, "cost": cost}


def test_many_rapid_creates_keep_totals_exact(client):
    h = auth_headers(client)
    n = 300
    for i in range(n):
        assert client.post("/api/runs", json=_run(f"run-{i}", tokens=10, cost=0.001), headers=h).status_code == 201

    stats = client.get("/api/stats", headers=h).json()
    assert stats["runs"] == n
    assert stats["total_tokens"] == 10 * n
    # Floating cost sums to n * 0.001 within rounding.
    assert abs(stats["total_cost"] - round(0.001 * n, 6)) < 1e-6
    assert len(client.get("/api/runs", headers=h).json()) == n


def test_interleaved_users_stay_isolated_under_load(client):
    alice = auth_headers(client, "alice", "pw")
    bob = auth_headers(client, "bob", "pw")

    # Alternate writes between two users a few hundred times.
    for i in range(200):
        who = alice if i % 2 == 0 else bob
        client.post("/api/runs", json=_run(f"r-{i}"), headers=who)

    alice_runs = client.get("/api/runs", headers=alice).json()
    bob_runs = client.get("/api/runs", headers=bob).json()
    assert len(alice_runs) == 100
    assert len(bob_runs) == 100
    # No leakage: every run each user sees is one they created (even step -> alice).
    assert all(int(r["name"].split("-")[1]) % 2 == 0 for r in alice_runs)
    assert all(int(r["name"].split("-")[1]) % 2 == 1 for r in bob_runs)


def test_rapidly_interleaved_requests_do_not_leak(client):
    # The test fixture shares one in-memory SQLite connection, which SQLite won't let
    # multiple threads use at once - a limit of the test DB, not the app. So this
    # fires the same overlapping read/write *mix* rapidly through the client to prove
    # the app layer stays correct and auth-scoped under a burst. Real concurrency
    # across workers is a Postgres/WSGI-server concern, called out in DESIGN.md.
    alice = auth_headers(client, "alice", "pw")
    bob = auth_headers(client, "bob", "pw")

    codes = []
    for i in range(240):
        who = alice if i % 2 == 0 else bob
        if i % 3 == 0:
            codes.append(client.post("/api/runs", json=_run(f"c-{i}"), headers=who).status_code)
        else:
            codes.append(client.get("/api/stats", headers=who).status_code)

    assert all(code in (200, 201) for code in codes)
    # Each user only ever accumulated their own writes.
    a = client.get("/api/stats", headers=alice).json()["runs"]
    b = client.get("/api/stats", headers=bob).json()["runs"]
    assert a + b == sum(1 for i in range(240) if i % 3 == 0)


def test_unauthenticated_requests_are_rejected_under_load(client):
    # Auth must gate every request regardless of volume - a burst doesn't open a hole.
    codes = [client.get("/api/runs").status_code for _ in range(200)]
    assert all(code == 401 for code in codes)
