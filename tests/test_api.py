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
