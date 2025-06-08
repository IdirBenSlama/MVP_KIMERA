import sys, os; sys.path.insert(0, os.path.abspath("."))
import json
from fastapi.testclient import TestClient
from backend.api.main import app, kimera_system

client = TestClient(app)

def test_create_geoid_and_status():
    response = client.post('/geoids', json={'semantic_features': {'approval_score': 0.9, 'risk_factor': 0.1}})
    assert response.status_code == 200
    data = response.json()
    gid = data['geoid_id']
    assert gid in kimera_system['active_geoids']

    status = client.get('/system/status').json()
    assert status['active_geoids'] >= 1
    assert 'system_entropy' in status

    # create another geoid for contradiction test
    response2 = client.post('/geoids', json={'semantic_features': {'approval_score': -0.8, 'risk_factor': 0.9}})
    assert response2.status_code == 200
    gid2 = response2.json()['geoid_id']

    contr = client.post('/process/contradictions', json={'geoid_ids': [gid, gid2]})
    assert contr.status_code == 200
    results = contr.json()
    assert 'analysis_results' in results
    assert 'scars_created' in results


def test_scar_persistence():
    # Create geoids with distinct semantic features
    res1 = client.post('/geoids', json={'semantic_features': {'alpha': 1.0}})
    res2 = client.post('/geoids', json={'semantic_features': {'beta': 1.0}})
    assert res1.status_code == 200 and res2.status_code == 200
    gid1 = res1.json()['geoid_id']
    gid2 = res2.json()['geoid_id']

    cycle_before = kimera_system['system_state']['cycle_count']
    status_before = client.get('/system/status').json()
    prev_scars = status_before['vault_a_scars'] + status_before['vault_b_scars']

    contr = client.post('/process/contradictions', json={'geoid_ids': [gid1, gid2]})
    assert contr.status_code == 200
    result = contr.json()
    assert result['scars_created'] >= 0

    status_after = client.get('/system/status').json()
    new_scars = status_after['vault_a_scars'] + status_after['vault_b_scars']
    assert new_scars >= prev_scars + result['scars_created']
    assert status_after['cycle_count'] == cycle_before + 1
