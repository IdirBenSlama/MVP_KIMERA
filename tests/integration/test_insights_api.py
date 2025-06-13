import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def _create_dummy_geoid():
    resp = client.post(
        "/geoids",
        json={
            "semantic_features": {"alpha": 1.0, "beta": 0.5},
            "symbolic_content": {},
            "metadata": {},
        },
    )
    resp.raise_for_status()
    return resp.json()["geoid_id"]


def test_insight_generation_flow():
    gid = _create_dummy_geoid()

    resp = client.post("/insights/generate", json={"source_geoid": gid})
    assert resp.status_code == 200
    insight = resp.json()["insight"]

    insight_id = insight["insight_id"]
    assert client.get(f"/insights/{insight_id}").status_code == 200

    fb = client.post(f"/insights/{insight_id}/feedback", json={"feedback_event": "user_explored"})
    assert fb.status_code == 200

    lin = client.get(f"/insights/{insight_id}/lineage")
    assert lin.status_code == 200
    assert lin.json()["insight"]["insight_id"] == insight_id 