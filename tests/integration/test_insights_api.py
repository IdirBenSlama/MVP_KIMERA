import pytest
from fastapi.testclient import TestClient

from backend.api.main import app, kimera_system

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


def test_generate_insight_and_feedback():
    # Ensure at least one geoid exists
    gid = _create_dummy_geoid()

    # Generate insight
    resp = client.post("/insights/generate", json={"source_geoid": gid})
    assert resp.status_code == 200
    insight = resp.json()["insight"]

    # Retrieve the insight
    insight_id = insight["insight_id"]
    assert client.get(f"/insights/{insight_id}").status_code == 200

    # Feedback
    fb_resp = client.post(
        f"/insights/{insight_id}/feedback",
        json={"feedback_event": "user_explored"},
    )
    assert fb_resp.status_code == 200

    # Lineage
    lineage_resp = client.get(f"/insights/{insight_id}/lineage")
    assert lineage_resp.status_code == 200
    assert lineage_resp.json()["insight"]["insight_id"] == insight_id 