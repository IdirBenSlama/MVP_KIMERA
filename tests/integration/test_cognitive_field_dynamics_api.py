import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
import numpy as np
import asyncio

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_geoids():
    """Set up the semantic field with some initial geoids."""
    # Add geoids from the database first
    response = client.post("/cognitive-fields/geoid/add_from_db?limit=10")
    assert response.status_code == 200
    print(response.json())

    # Add a few specific geoids for targeted tests
    geoids_to_add = [
        {"geoid_id": "TEST_GEOID_1", "embedding": list(np.random.rand(1024))},
        {"geoid_id": "TEST_GEOID_2", "embedding": list(np.random.rand(1024))},
        {"geoid_id": "TEST_GEOID_3", "embedding": list(np.random.rand(1024))}
    ]
    for geoid_data in geoids_to_add:
        response = client.post("/cognitive-fields/geoid/add", json=geoid_data)
        assert response.status_code == 200
    
    return "TEST_GEOID_1" # Return one geoid for other tests to use

def test_add_geoids_from_db():
    """Test loading geoids from the database into the semantic field."""
    response = client.post("/cognitive-fields/geoid/add_from_db?limit=20")
    assert response.status_code == 200
    assert "Added" in response.json()["status"]

def test_find_semantic_neighbors(setup_geoids):
    """Test finding semantic neighbors for a geoid."""
    test_geoid_id = setup_geoids
    response = client.post(
        "/cognitive-fields/neighbors/find",
        json={"geoid_id": test_geoid_id, "energy_threshold": 0.01}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["geoid_id"] == test_geoid_id
    assert "neighbors" in data
    assert isinstance(data["neighbors"], list)

def test_get_influence_field(setup_geoids):
    """Test getting the influence field of a geoid."""
    test_geoid_id = setup_geoids
    response = client.get(f"/cognitive-fields/influence/{test_geoid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["geoid_id"] == test_geoid_id
    assert "influence_map" in data
    assert "total_influence" in data
    assert "average_influence" in data

def test_detect_semantic_anomalies(setup_geoids):
    """Test detecting semantic anomalies."""
    response = client.get("/cognitive-fields/anomalies/detect")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data
    assert "total_fields" in data
    assert "field_health" in data
    assert isinstance(data["anomalies"], list)

def test_find_resonance_clusters(setup_geoids):
    """Test finding resonance clusters."""
    response = client.get("/cognitive-fields/clusters/resonance")
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
    assert "total_clusters" in data
    assert data["clustering_method"] == "resonance_pattern"
    assert isinstance(data["clusters"], list)

def test_get_semantic_field_map(setup_geoids):
    """Test getting the semantic field map."""
    response = client.get("/cognitive-fields/field-map")
    assert response.status_code == 200
    data = response.json()
    assert "fields" in data
    assert "interactions" in data
    assert "topology" in data

@pytest.mark.asyncio
async def test_direct_field_evolution():
    """Test the field evolution logic directly."""
    from backend.api.cognitive_field_routes import field_service
    initial_time = field_service.time
    
    # Evolve the fields
    await field_service.evolve_fields(time_step=0.1)
    
    # Check that time has advanced
    assert field_service.time > initial_time

def test_find_neighbors_not_found():
    """Test error handling for a non-existent geoid."""
    response = client.post(
        "/cognitive-fields/neighbors/find",
        json={"geoid_id": "NON_EXISTENT_GEOID", "energy_threshold": 0.1}
    )
    assert response.status_code == 400

def test_influence_field_not_found():
    """Test error handling for a non-existent geoid in influence field."""
    response = client.get("/cognitive-fields/influence/NON_EXISTENT_GEOID")
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main() 