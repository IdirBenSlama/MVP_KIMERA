import pytest
from fastapi.testclient import TestClient
from kimera_swm_mvp.backend.api.main import app, kimera_system

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_system_state():
    """Fixture to reset the system state before each test."""
    kimera_system['active_geoids'].clear()
    kimera_system['vault_manager'].vault_a.clear()
    kimera_system['vault_manager'].vault_b.clear()
    kimera_system['system_state']['cycle_count'] = 0
    yield

def test_contradiction_detection_and_collapse():
    """
    Tests the full contradiction detection pipeline:
    1. Create two contradictory geoids.
    2. Process them for contradictions.
    3. Assert that a tension is detected.
    4. Assert that the system decides to 'collapse' the tension.
    """
    # 1. Define two contradictory geoids
    # Geoid A: Positive market outlook
    geoid_a_payload = {
        "semantic_features": {
            "market_sentiment": 0.9,
            "growth_forecast": 0.8,
            "investor_confidence": 0.85
        },
        "symbolic_content": {"report_id": "report_positive_outlook_001"}
    }

    # Geoid B: Negative market outlook
    geoid_b_payload = {
        "semantic_features": {
            "market_sentiment": -0.9,
            "growth_forecast": -0.8,
            "investor_confidence": -0.85
        },
        "symbolic_content": {"report_id": "report_negative_outlook_002"}
    }

    # 2. Create the geoids via API
    response_a = client.post("/geoids", json=geoid_a_payload)
    assert response_a.status_code == 200
    geoid_a_id = response_a.json()['geoid_id']

    response_b = client.post("/geoids", json=geoid_b_payload)
    assert response_b.status_code == 200
    geoid_b_id = response_b.json()['geoid_id']

    # 3. Process the geoids for contradictions
    process_payload = {
        "geoid_ids": [geoid_a_id, geoid_b_id]
    }
    response_process = client.post("/process/contradictions", json=process_payload)
    assert response_process.status_code == 200

    # 4. Assert that a contradiction was detected and handled
    results = response_process.json()
    assert results['contradictions_detected'] == 1, \
        f"Expected 1 contradiction, but found {results['contradictions_detected']}. " \
        f"Full result: {results}"

    # Check the details of the tension
    tension_result = results['results'][0]
    assert tension_result['tension']['score'] > 0.75, \
        f"Tension score {tension_result['tension']['score']} is not above the threshold 0.75"

    assert tension_result['decision'] == 'collapse', \
        f"Expected decision 'collapse', but got '{tension_result['decision']}'" 