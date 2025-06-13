from __future__ import annotations

import hashlib
import os
from typing import List, Dict
from threading import Lock
import logging

import numpy as np
import torch

from .constants import EMBEDDING_DIM

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - allow tests without heavy deps
    SentenceTransformer = None  # type: ignore

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class _DummyTransformer:
    def encode(self, text: str):
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h, dtype=np.uint8).astype(float)
        reps = (EMBEDDING_DIM + len(vec) - 1) // len(vec)
        return np.tile(vec, reps)[:EMBEDDING_DIM] / 255.0


# --- Globals ---
_embedding_model = None
_model_lock = Lock()

# --- Device Configuration ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
log.info(f"Embedding model will use device: {DEVICE.upper()}")

# --- Environment Configuration ---
MODEL_NAME = "all-MiniLM-L6-v2"
LIGHTWEIGHT_MODE = os.getenv("LIGHTWEIGHT_EMBEDDING", "0") == "1"

if LIGHTWEIGHT_MODE:
    # In lightweight mode, we just use a random vector generator
    def _lightweight_encoder(text: str):
        # Create a consistent random vector based on the hash of the text
        # This is not semantically meaningful but is deterministic for testing
        seed = hash(text) % (2**32 - 1)
        rng = np.random.RandomState(seed)
        return rng.rand(384).tolist()


def get_embedding_model():
    """Returns the embedding model, initializing it if necessary."""
    return _get_model()


def initialize_embedding_model():
    """Explicitly initializes the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        with _model_lock:
            if _embedding_model is None:
                log.info(f"Initializing embedding model '{MODEL_NAME}' on {DEVICE.upper()}...")
                _embedding_model = SentenceTransformer(MODEL_NAME, device=DEVICE)
                log.info("Embedding model loaded successfully.")
    return _embedding_model


def _get_model():
    """Initializes and returns the SentenceTransformer model (thread-safe)."""
    global _embedding_model
    if _embedding_model is None:
        return initialize_embedding_model()
    return _embedding_model


def encode_text(text: str) -> List[float]:
    """Encodes a string of text into a vector embedding."""
    if LIGHTWEIGHT_MODE:
        return _lightweight_encoder(text)
    
    model = _get_model()
    # The model handles batching, but we're sending one at a time.
    # Convert to list for JSON serialization.
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


def extract_semantic_features(text: str) -> Dict[str, float]:
    """
    (Placeholder) Extracts a dictionary of semantic concepts from text.
    
    In a real implementation, this would use NLP techniques like keyword
    extraction, topic modeling, or a fine-tuned classifier. For the MVP,
    it uses a simple keyword spotting approach.
    """
    text = text.lower()
    features = {}
    
    # Example concepts for demonstration
    concept_map = {
        "cat": ["cat", "feline", "kitten"],
        "dog": ["dog", "canine", "puppy"],
        "mat": ["mat", "rug", "carpet"],
        "kennel": ["kennel", "crate", "pen"],
        "economy": ["economy", "gdp", "growth", "recession"],
        "stability": ["stable", "stability", "steady"],
        "risk": ["risk", "volatile", "uncertain"],
    }
    
    for concept, keywords in concept_map.items():
        if any(keyword in text for keyword in keywords):
            features[concept] = 1.0
            
    # Add a general 'complexity' score based on text length
    if len(text) > 0:
        features["complexity"] = min(len(text) / 100.0, 1.0)
        
    return features

