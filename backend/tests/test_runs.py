"""Run CRUD, per-user isolation, and stats aggregation."""

from __future__ import annotations

from tests.conftest import auth_headers


def _run(name="nightly", model="gpt-4o", status="success", tokens=100, cost=0.01):
    return {"name": name, "model": model, "status": status, "tokens": tokens, "cost": cost}


def test_create_and_list_runs(client):
    h = auth_headers(client)
    client.post("/api/runs", json=_run(name="a"), headers=h)
    client.post("/api/runs", json=_run(name="b"), headers=h)
    runs = client.get("/api/runs", headers=h).json()
    assert [r["name"] for r in runs] == ["b", "a"]  # newest first


def test_runs_are_isolated_per_user(client):
    alice = auth_headers(client, "alice", "pw")
    bob = auth_headers(client, "bob", "pw")
    client.post("/api/runs", json=_run(name="alice-run"), headers=alice)

    assert len(client.get("/api/runs", headers=bob).json()) == 0
    assert len(client.get("/api/runs", headers=alice).json()) == 1


def test_delete_only_your_own_run(client):
    alice = auth_headers(client, "alice", "pw")
    bob = auth_headers(client, "bob", "pw")
    run_id = client.post("/api/runs", json=_run(), headers=alice).json()["id"]

    # Bob cannot delete Alice's run.
    assert client.delete(f"/api/runs/{run_id}", headers=bob).status_code == 404
    # Alice can.
    assert client.delete(f"/api/runs/{run_id}", headers=alice).status_code == 204
    assert len(client.get("/api/runs", headers=alice).json()) == 0


def test_stats_aggregate_correctly(client):
    h = auth_headers(client)
    client.post("/api/runs", json=_run(model="gpt-4o", status="success", tokens=100, cost=0.5), headers=h)
    client.post("/api/runs", json=_run(model="gpt-4o", status="error", tokens=50, cost=0.25), headers=h)
    client.post("/api/runs", json=_run(model="o3-mini", status="success", tokens=200, cost=1.0), headers=h)

    stats = client.get("/api/stats", headers=h).json()
    assert stats["runs"] == 3
    assert stats["total_tokens"] == 350
    assert stats["total_cost"] == 1.75
    assert stats["by_status"] == {"success": 2, "error": 1}
    assert stats["by_model"] == {"gpt-4o": 2, "o3-mini": 1}


def test_stats_start_empty(client):
    h = auth_headers(client)
    stats = client.get("/api/stats", headers=h).json()
    assert stats == {"runs": 0, "total_tokens": 0, "total_cost": 0.0, "by_status": {}, "by_model": {}}
