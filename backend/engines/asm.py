from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import numpy as np
from scipy.spatial.distance import pdist
from ..vault.database import ScarDB, GeoidDB


class AxisStabilityMonitor:
    """Calculate simplified global stability metrics for the MVP."""

    def __init__(self, db: Session):
        self.db = db

    def get_stability_metrics(self) -> dict:
        """Return a dictionary of global stability metrics."""

        # Metric 1: Vault Pressure - recent knowledge consolidation rate
        recent_scars_count = self.db.query(ScarDB).filter(
            ScarDB.timestamp > datetime.utcnow() - timedelta(hours=1)
        ).count()
        vault_pressure = min(recent_scars_count / 10.0, 1.0)

        # Metric 2: Semantic Cohesion - focus of recent geoids
        recent_geoids = (
            self.db.query(GeoidDB)
            .order_by(GeoidDB.geoid_id.desc())
            .limit(20)
            .all()
        )
        semantic_cohesion = 1.0
        if len(recent_geoids) > 1:
            vectors = [
                g.semantic_vector
                for g in recent_geoids
                if g.semantic_vector is not None
            ]
            if len(vectors) > 1:
                min_len = min(len(v) for v in vectors)
                norm_vectors = [np.array(v[:min_len]) for v in vectors]
                # Compute pairwise cosine distances without heavy dependencies
                distances = pdist(np.vstack(norm_vectors), metric="cosine")
                avg_distance = float(np.mean(distances))
                if np.isnan(avg_distance):
                    semantic_cohesion = 0.0
                else:
                    semantic_cohesion = 1.0 - avg_distance

        # Metric 3: Entropic Stability - trend of entropy change
        recent_scars = (
            self.db.query(ScarDB)
            .order_by(ScarDB.timestamp.desc())
            .limit(20)
            .all()
        )
        entropic_stability = 0.5
        if recent_scars:
            avg_delta_entropy = float(
                np.mean([s.delta_entropy for s in recent_scars])
            )
            entropic_stability = (avg_delta_entropy + 1.0) / 2.0

        return {
            "vault_pressure": vault_pressure,
            "semantic_cohesion": semantic_cohesion,
            "entropic_stability": entropic_stability,
            "axis_convergence": semantic_cohesion,
            "vault_resonance": 1.0 - vault_pressure,
            "contradiction_lineage_ambiguity": vault_pressure,
        }
