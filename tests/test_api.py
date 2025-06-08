import sys, os; sys.path.insert(0, os.path.abspath("."))
import json
from fastapi.testclient import TestClient
from backend.api.main import app, kimera_system

client = TestClient(app)

def test_create_geoid_and_status():
    response = client.post('/geoids', json={'semantic_features': {'a': 0.6, 'b': 0.4}})
    assert response.status_code == 200
    data = response.json()
    gid = data['geoid_id']
    assert gid in kimera_system['active_geoids']

    status = client.get('/system/status').json()
    assert status['active_geoids'] >= 1
    assert 'system_entropy' in status

    # create another geoid for contradiction test
    response2 = client.post('/geoids', json={'semantic_features': {'a': 1.0}})
    assert response2.status_code == 200
    gid2 = response2.json()['geoid_id']

    contr = client.post('/process/contradictions', json={'geoid_ids': [gid, gid2]})
    assert contr.status_code == 200
    results = contr.json()
    assert 'results' in results
