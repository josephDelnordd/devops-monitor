from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
API_KEY = "dev-secret-key"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "cpu_percent" in r.json()


def test_post_server_no_key():
    r = client.post(
        "/servers",
        json={"name": "x", "host": "localhost", "port": 80},
    )
    assert r.status_code == 403


def test_post_and_get_server():
    r = client.post(
        "/servers",
        headers={"X-API-Key": API_KEY},
        json={"name": "local", "host": "localhost", "port": 8000},
    )
    assert r.status_code == 201

    server_id = r.json()["id"]

    r2 = client.get("/servers")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1

    r3 = client.get(f"/servers/{server_id}")
    assert r3.status_code == 200
    assert r3.json()["id"] == server_id


def test_get_unknown_server():
    r = client.get("/servers/unknown")
    assert r.status_code == 404


def test_check_server():
    # Create server
    r = client.post(
        "/servers",
        headers={"X-API-Key": API_KEY},
        json={"name": "check-me", "host": "localhost", "port": 8000},
    )
    server_id = r.json()["id"]

    # Trigger health check
    r2 = client.post(f"/servers/{server_id}/check")
    assert r2.status_code == 200
    assert "status" in r2.json()


def test_delete_server():
    # Create server
    r = client.post(
        "/servers",
        headers={"X-API-Key": API_KEY},
        json={"name": "to-delete", "host": "localhost", "port": 8000},
    )
    server_id = r.json()["id"]

    # Delete server
    r2 = client.delete(
        f"/servers/{server_id}",
        headers={"X-API-Key": API_KEY},
    )
    assert r2.status_code == 200

    # Ensure it's gone
    r3 = client.get(f"/servers/{server_id}")
    assert r3.status_code == 404