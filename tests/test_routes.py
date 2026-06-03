from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "cpu_percent" in r.json()


def test_post_server_no_key():
    r = client.post("/servers", json={"name": "x", "host": "localhost", "port": 80})
    assert r.status_code == 403


def test_post_and_get_server():
    r = client.post(
        "/servers",
        headers={"X-API-Key": "dev-secret-key"},
        json={"name": "local", "host": "localhost", "port": 8000},
    )
    assert r.status_code == 201

    r2 = client.get("/servers")
    assert len(r2.json()) == 1


def test_get_unknown_server():
    r = client.get("/servers/unknown")
    assert r.status_code == 404