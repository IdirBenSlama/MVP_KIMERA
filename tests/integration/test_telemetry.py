from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)

def test_telemetry_metrics_endpoint():
    resp = client.get("/telemetry/metrics")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    # Basic metric present
    assert b"kimera_active_geoids" in resp.content 