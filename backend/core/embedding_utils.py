from __future__ import annotations

import hashlib
import os
from typing import List

import numpy as np

from .constants import EMBEDDING_DIM

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - allow tests without heavy deps
    SentenceTransformer = None  # type: ignore


class _DummyTransformer:
    def encode(self, text: str):
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h, dtype=np.uint8).astype(float)
        reps = (EMBEDDING_DIM + len(vec) - 1) // len(vec)
        return np.tile(vec, reps)[:EMBEDDING_DIM] / 255.0


_LIGHTWEIGHT_EMBEDDING = os.getenv("LIGHTWEIGHT_EMBEDDING", "0") == "1"
_embedding_model = None


def _get_model():
    global _embedding_model
    if _embedding_model is None:
        if SentenceTransformer is not None and not _LIGHTWEIGHT_EMBEDDING:
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        else:  # pragma: no cover - lightweight fallback
            _embedding_model = _DummyTransformer()
    return _embedding_model


def encode_text(text: str) -> List[float]:
    """Return the embedding vector for the given text."""
    model = _get_model()
    vector = model.encode(text)
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)
