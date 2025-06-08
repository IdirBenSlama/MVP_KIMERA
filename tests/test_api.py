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

    contr = client.post('/process/contradictions', json={'trigger_geoid_id': gid, 'search_limit': 5})
    assert contr.status_code == 200
    results = contr.json()
    assert 'analysis_results' in results
    assert 'scars_created' in results

def test_geoid_search():
    # create geoid to search for
    create = client.post('/geoids', json={'semantic_features': {'alpha': 1.0}})
    assert create.status_code == 200
    gid = create.json()['geoid_id']

    res = client.get('/geoids/search', params={'query': 'alpha'})
    assert res.status_code == 200
    data = res.json()
    assert 'similar_geoids' in data
    assert len(data['similar_geoids']) > 0


def test_autonomous_contradictions():
    g1 = client.post('/geoids', json={'semantic_features': {'x': 0.1, 'y': 0.2}})
    assert g1.status_code == 200
    gid1 = g1.json()['geoid_id']

    g2 = client.post('/geoids', json={'semantic_features': {'x': -0.3, 'y': 0.4}})
    assert g2.status_code == 200

    g3 = client.post('/geoids', json={'semantic_features': {'x': 0.2, 'y': -0.5}})
    assert g3.status_code == 200

    res = client.post('/process/contradictions', json={'trigger_geoid_id': gid1, 'search_limit': 2})
    assert res.status_code == 200
    data = res.json()
    assert 'analysis_results' in data
    assert isinstance(data.get('contradictions_detected'), int)
