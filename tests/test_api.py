import os
import sys
sys.path.insert(0, os.path.abspath("."))
import importlib
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from backend.core.scar import ScarRecord


def _init_app(db_url: str):
    os.environ["DATABASE_URL"] = db_url
    os.environ["ENABLE_JOBS"] = "0"
    sys.path.insert(0, os.path.abspath("."))
    import backend.vault.database as db_module
    importlib.reload(db_module)
    import backend.vault.vault_manager as vm_module
    importlib.reload(vm_module)
    from backend.api.main import app, kimera_system
    kimera_system['vault_manager'] = vm_module.VaultManager()
    client = TestClient(app)
    return client, kimera_system, db_module.SessionLocal, db_module.ScarDB


@pytest.fixture()
def api_env(tmp_path):
    db_file = tmp_path / "api.db"
    return _init_app(f"sqlite:///{db_file}")


def test_create_geoid_and_status(api_env):
    client, kimera_system, SessionLocal, ScarDB = api_env
    response = client.post(
        '/geoids',
        json={
            'semantic_features': {
                'approval_score': 0.9,
                'risk_factor': 0.1,
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    gid = data['geoid_id']
    assert gid in kimera_system['active_geoids']

    status = client.get('/system/status').json()
    assert status['active_geoids'] >= 1
    assert 'system_entropy' in status

    response2 = client.post(
        '/geoids',
        json={
            'semantic_features': {
                'approval_score': -0.8,
                'risk_factor': 0.9,
            }
        },
    )
    assert response2.status_code == 200

    contr = client.post(
        '/process/contradictions',
        json={'trigger_geoid_id': gid, 'search_limit': 5},
    )
    assert contr.status_code == 200
    results = contr.json()
    assert 'analysis_results' in results
    assert 'scars_created' in results


def test_geoid_search(api_env):
    client, kimera_system, *_ = api_env
    create = client.post(
        '/geoids',
        json={'semantic_features': {'alpha': 1.0}},
    )
    assert create.status_code == 200

    res = client.get('/geoids/search', params={'query': 'alpha'})
    assert res.status_code == 200
    data = res.json()
    assert 'similar_geoids' in data
    assert len(data['similar_geoids']) > 0


def test_autonomous_contradictions(api_env):
    client, kimera_system, SessionLocal, ScarDB = api_env
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

    search = client.get('/scars/search', params={'query': 'tension'})
    assert search.status_code == 200
    sdata = search.json()
    assert 'similar_scars' in sdata

    sid = sdata['similar_scars'][0]['scar_id']
    with SessionLocal() as db:
        scar = db.query(ScarDB).filter_by(scar_id=sid).first()
        assert scar.weight >= 2.0
        assert scar.last_accessed is not None


def test_system_stability_endpoint(api_env):
    client, *_ = api_env
    res = client.get('/system/stability')
    assert res.status_code == 200
    data = res.json()
    assert 'vault_pressure' in data
    assert 'semantic_cohesion' in data


def test_create_geoid_from_image(api_env):
    client, *_ = api_env
    from PIL import Image
    import io

    img = Image.new('RGB', (2, 2), color='red')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    files = {'file': ('test.png', buf.getvalue(), 'image/png')}
    res = client.post('/geoids/from_image', files=files)
    assert res.status_code == 200
    data = res.json()
    assert 'geoid_id' in data


def test_speak_geoid_endpoint(api_env):
    client, kimera_system, *_ = api_env
    create = client.post('/geoids', json={'semantic_features': {'z': 1.0}})
    assert create.status_code == 200
    gid = create.json()['geoid_id']
    res = client.get(f'/geoids/{gid}/speak')
    assert res.status_code in (200, 409)


def test_echoform_parsing_and_storage(api_env):
    client, kimera_system, *_ = api_env
    res = client.post(
        '/geoids',
        json={
            'semantic_features': {'e': 1.0},
            'echoform_text': '(hello world (nested))'
        },
    )
    assert res.status_code == 200
    gid = res.json()['geoid_id']
    geoid = kimera_system['active_geoids'][gid]
    assert geoid.symbolic_state['echoform'] == [['hello', 'world', ['nested']]]


def test_complex_echoform_parsing(api_env):
    client, kimera_system, *_ = api_env
    text = "(greet 'world (+ 1 2) '(nested a))"
    res = client.post(
        '/geoids',
        json={
            'semantic_features': {'c': 1.0},
            'echoform_text': text
        },
    )
    assert res.status_code == 200
    gid = res.json()['geoid_id']
    geoid = kimera_system['active_geoids'][gid]
    expected = [['greet', ['quote', 'world'], ['+', 1, 2], ['quote', ['nested', 'a']]]]
    assert geoid.symbolic_state['echoform'] == expected


def test_system_cycle_endpoint(api_env):
    client, kimera_system, *_ = api_env
    g1 = client.post('/geoids', json={'semantic_features': {'c1': 1.0}})
    assert g1.status_code == 200
    g2 = client.post('/geoids', json={'semantic_features': {'c2': 1.0}})
    assert g2.status_code == 200

    before = client.get('/system/status').json()['cycle_count']
    res = client.post('/system/cycle')
    assert res.status_code == 200
    after = client.get('/system/status').json()['cycle_count']
    assert after == before + 1


def test_vault_rebalance_endpoint(api_env):
    client, kimera_system, SessionLocal, ScarDB = api_env
    vm = kimera_system['vault_manager']
    with SessionLocal() as db:
        db.query(ScarDB).delete()
        db.commit()
    for i in range(4):
        scar = ScarRecord(
            scar_id=f"AP{i}",
            geoids=[f"G{i}"],
            reason="test",
            timestamp=datetime.utcnow().isoformat(),
            resolved_by="api_test",
            pre_entropy=0.0,
            post_entropy=0.0,
            delta_entropy=0.0,
            cls_angle=0.0,
            semantic_polarity=0.0,
            mutation_frequency=0.0,
            weight=1.0,
        )
        vm.insert_scar(scar, [0.0])
    with SessionLocal() as db:
        db.query(ScarDB).update({ScarDB.vault_id: "vault_a"})
        db.commit()

    res = client.post('/vaults/rebalance')
    assert res.status_code == 200
    data = res.json()
    assert 'moved_scars' in data

