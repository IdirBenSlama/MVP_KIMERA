import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import numpy as np
import random
import string

sys.path.insert(0, os.path.abspath("."))

from apscheduler.schedulers.background import BackgroundScheduler

try:
    from locust import FastHttpUser, task
    LOCUST_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    LOCUST_AVAILABLE = False

from backend.api.main import app
from backend.core.geoid import GeoidState
from backend.vault.vault_manager import VaultManager


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="module")
def vault_manager():
    return VaultManager()

@pytest.fixture(scope="module")
def scheduler():
    sched = BackgroundScheduler()
    sched.start()
    yield sched
    sched.shutdown()


class TestKimeraStress:
    THERMO_BATCH_SIZE = 1000

    def test_thermodynamic_overload(self, test_client, vault_manager):
        compensation_count = 0
        start_time = datetime.now()
        geoids = [
            GeoidState(
                geoid_id=f"GEOID_{i}",
                semantic_state={"feature_A": random.random()},
                symbolic_state={"type": "test"}
            ) for i in range(self.THERMO_BATCH_SIZE)
        ]
        for geoid in geoids:
            response = test_client.post("/geoids", json={"semantic_features": geoid.semantic_state})
            if response.status_code == 200 and response.json().get("metadata", {}).get("compensation_feature"):
                compensation_count += 1
        processing_time = (datetime.now() - start_time).total_seconds()
        assert processing_time < 5
        assert compensation_count / self.THERMO_BATCH_SIZE < 0.2

    def test_contradiction_cascade(self, test_client):
        ids = []
        for _ in range(10):
            res = test_client.post("/geoids", json={"semantic_features": {"x": random.random()}})
            ids.append(res.json()["geoid_id"])
        res = test_client.post("/process/contradictions", json={"trigger_geoid_id": ids[0], "search_limit": 5})
        assert res.status_code == 200
        data = res.json()
        assert "contradictions_detected" in data

    def test_vault_fracture_resilience(self, vault_manager):
        scars_before = vault_manager.get_total_scar_count("vault_a") + vault_manager.get_total_scar_count("vault_b")
        scar = random.choice(string.ascii_letters)
        vault_manager.insert_scar(
            GeoidState(
                geoid_id="dummy",
                semantic_state={"a": 1.0}
            ),
            [0.0]*10
        )
        scars_after = vault_manager.get_total_scar_count("vault_a") + vault_manager.get_total_scar_count("vault_b")
        assert scars_after >= scars_before

    def test_cross_modal_storm(self):
        from backend.engines.clip_service import clip_service
        TEXT_BATCH = 10
        IMAGE_BATCH = 5
        text_times = []
        for _ in range(TEXT_BATCH):
            start = datetime.now()
            _ = clip_service.get_text_embedding("sample")
            text_times.append((datetime.now() - start).total_seconds())
        image = np.random.rand(224, 224, 3)
        image_times = []
        for _ in range(IMAGE_BATCH):
            start = datetime.now()
            _ = clip_service.get_image_embedding(image)
            image_times.append((datetime.now() - start).total_seconds())
        assert np.percentile(text_times, 95) < 1
        assert np.percentile(image_times, 95) < 1.5


if LOCUST_AVAILABLE:
    class KimeraLoadUser(FastHttpUser):
        @task(weight=3)
        def create_geoid(self):
            self.client.post("/geoids", json={"semantic_features": {"feature": random.random()}})

        @task(weight=1)
        def process_contradictions(self):
            self.client.post("/process/contradictions", json={"trigger_geoid_id": "GEOID_1", "search_limit": 1})

