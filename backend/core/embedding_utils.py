from __future__ import annotations

import hashlib
import os
import time
from typing import List, Dict, Optional, Union
from threading import Lock
import logging
from pathlib import Path

import numpy as np
import torch

from .constants import EMBEDDING_DIM

try:
    import onnxruntime as ort
except Exception:
    ort = None  # type: ignore

try:
    from transformers import AutoModel, AutoTokenizer
    import torch.nn.functional as F
except Exception:  # pragma: no cover
    AutoModel = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    F = None  # type: ignore

# FlagEmbedding is optional, handle separately
try:
    from FlagEmbedding import BGEM3FlagModel
except Exception:
    BGEM3FlagModel = None  # type: ignore

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class _DummyTransformer:
    def encode(self, text: str, max_length: int = 512):
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
MODEL_NAME = "BAAI/bge-m3"
ONNX_MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "./models/bge-m3-onnx")
LIGHTWEIGHT_MODE = os.getenv("LIGHTWEIGHT_EMBEDDING", "0") == "1"
USE_ONNX = os.getenv("USE_ONNX", "1") == "1"
USE_FLAG_EMBEDDING = os.getenv("USE_FLAG_EMBEDDING", "1") == "1"
MAX_LENGTH = int(os.getenv("MAX_EMBEDDING_LENGTH", "512"))
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

# Performance tracking
_performance_stats = {
    "total_embeddings": 0,
    "total_time": 0.0,
    "avg_time_per_embedding": 0.0,
    "model_load_time": 0.0
}

def _lightweight_encoder(text: str) -> List[float]:
    """Create a consistent random vector based on the hash of the text."""
    seed = hash(text) % (2**32 - 1)
    rng = np.random.RandomState(seed)
    return rng.rand(EMBEDDING_DIM).tolist()

def get_performance_stats() -> Dict[str, float]:
    """Get embedding performance statistics."""
    return _performance_stats.copy()


class EmbeddingModelWrapper:
    """Wrapper to provide a consistent .encode() interface."""
    
    def __init__(self, model):
        self._model = model
    
    def encode(self, text: str):
        """Encode text using the underlying model."""
        embedding_list = encode_text(text)
        # Return as numpy array so .tolist() works in the API
        return np.array(embedding_list)

def get_embedding_model():
    """Returns the embedding model, initializing it if necessary."""
    model = _get_model()
    return EmbeddingModelWrapper(model)


def initialize_embedding_model():
    """Explicitly initializes the embedding model with optimized loading strategy."""
    global _embedding_model, _performance_stats
    if _embedding_model is None:
        with _model_lock:
            if _embedding_model is None:
                start_time = time.time()
                
                # Priority 1: Try FlagEmbedding BGE-M3 (most optimized)
                if USE_FLAG_EMBEDDING and BGEM3FlagModel is not None:
                    log.info(f"Initializing FlagEmbedding BGE-M3 model on {DEVICE.upper()}...")
                    try:
                        _embedding_model = {
                            'flag_model': BGEM3FlagModel(MODEL_NAME, use_fp16=DEVICE == "cuda"),
                            'type': 'flag_embedding'
                        }
                        log.info("FlagEmbedding BGE-M3 model loaded successfully.")
                    except Exception as e:
                        log.warning(f"Failed to load FlagEmbedding model: {e}. Falling back to ONNX.")
                        _embedding_model = None
                
                # Priority 2: Try ONNX Runtime (optimized inference)
                if _embedding_model is None and USE_ONNX and ort is not None:
                    log.info(f"Initializing ONNX embedding model '{MODEL_NAME}' on {DEVICE.upper()}...")
                    try:
                        onnx_path = Path(ONNX_MODEL_PATH) / "model.onnx"
                        if onnx_path.exists():
                            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if DEVICE == "cuda" else ['CPUExecutionProvider']
                            _embedding_model = {
                                'session': ort.InferenceSession(str(onnx_path), providers=providers),
                                'tokenizer': AutoTokenizer.from_pretrained(MODEL_NAME),
                                'type': 'onnx'
                            }
                            log.info("ONNX embedding model loaded successfully.")
                        else:
                            log.warning(f"ONNX model not found at {onnx_path}. Falling back to Transformers.")
                            _embedding_model = None
                    except Exception as e:
                        log.warning(f"Failed to load ONNX model: {e}. Falling back to Transformers model.")
                        _embedding_model = None
                
                # Priority 3: Standard Transformers model
                if _embedding_model is None:
                    log.info(f"Initializing Transformers embedding model '{MODEL_NAME}' on {DEVICE.upper()}...")
                    try:
                        model = AutoModel.from_pretrained(MODEL_NAME, torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32)
                        _embedding_model = {
                            'model': model.to(DEVICE),
                            'tokenizer': AutoTokenizer.from_pretrained(MODEL_NAME),
                            'type': 'transformers'
                        }
                        log.info("Transformers embedding model loaded successfully.")
                    except Exception as e:
                        log.error(f"Failed to load any embedding model: {e}. Using dummy encoder.")
                        _embedding_model = {'type': 'dummy'}
                
                load_time = time.time() - start_time
                _performance_stats["model_load_time"] = load_time
                log.info(f"Model initialization completed in {load_time:.2f}s")
                
    return _embedding_model


def _get_model():
    """Initializes and returns the embedding model (thread-safe)."""
    global _embedding_model
    if _embedding_model is None:
        return initialize_embedding_model()
    return _embedding_model


def encode_text(text: str) -> List[float]:
    """Encodes a string of text into a vector embedding with performance tracking."""
    global _performance_stats
    
    if LIGHTWEIGHT_MODE:
        return _lightweight_encoder(text)
    
    start_time = time.time()
    model = _get_model()
    
    try:
        # Priority 1: FlagEmbedding BGE-M3 (most optimized)
        if isinstance(model, dict) and model.get('type') == 'flag_embedding':
            try:
                flag_model = model['flag_model']
                embedding = flag_model.encode([text])['dense_vecs'][0]
                return embedding.tolist()
            except Exception as e:
                log.error(f"FlagEmbedding inference failed: {e}. Falling back to next method.")
        
        # Priority 2: ONNX Runtime inference
        elif isinstance(model, dict) and model.get('type') == 'onnx':
            try:
                tokenizer = model['tokenizer']
                session = model['session']
                
                # Tokenize input
                inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True, max_length=MAX_LENGTH)
                
                # Run inference
                outputs = session.run(None, {
                    'input_ids': inputs['input_ids'],
                    'attention_mask': inputs['attention_mask']
                })
                
                # Extract and process embeddings
                embedding = outputs[0][0]  # Remove batch dimension
                # Normalize the embedding
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                return embedding.tolist()
                
            except Exception as e:
                log.error(f"ONNX inference failed: {e}. Falling back to Transformers.")
        
        # Priority 3: Transformers model inference
        elif isinstance(model, dict) and model.get('type') == 'transformers':
            try:
                tokenizer = model['tokenizer']
                transformer_model = model['model']
                
                # Tokenize input
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=MAX_LENGTH)
                inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
                
                # Get embeddings
                with torch.no_grad():
                    outputs = transformer_model(**inputs)
                    # Use mean pooling of last hidden state
                    embeddings = outputs.last_hidden_state
                    attention_mask = inputs['attention_mask']
                    
                    # Mean pooling
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
                    sum_embeddings = torch.sum(embeddings * input_mask_expanded, 1)
                    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    embedding = sum_embeddings / sum_mask
                    
                    # Normalize
                    embedding = F.normalize(embedding, p=2, dim=1)
                    
                return embedding[0].cpu().numpy().tolist()
                
            except Exception as e:
                log.error(f"Transformers inference failed: {e}. Falling back to dummy encoder.")
        
        # Fallback to dummy encoder
        log.warning("No valid embedding model available. Using dummy encoder.")
        return _DummyTransformer().encode(text)
        
    finally:
        # Update performance statistics
        inference_time = time.time() - start_time
        _performance_stats["total_embeddings"] += 1
        _performance_stats["total_time"] += inference_time
        _performance_stats["avg_time_per_embedding"] = _performance_stats["total_time"] / _performance_stats["total_embeddings"]


def encode_batch(texts: List[str]) -> List[List[float]]:
    """Encode multiple texts in batch for better performance."""
    if LIGHTWEIGHT_MODE:
        return [_lightweight_encoder(text) for text in texts]
    
    if not texts:
        return []
    
    # For single text, use regular encode_text
    if len(texts) == 1:
        return [encode_text(texts[0])]
    
    start_time = time.time()
    model = _get_model()
    
    try:
        # Batch processing for FlagEmbedding
        if isinstance(model, dict) and model.get('type') == 'flag_embedding':
            try:
                flag_model = model['flag_model']
                embeddings = flag_model.encode(texts)['dense_vecs']
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                log.error(f"FlagEmbedding batch inference failed: {e}. Falling back to individual processing.")
        
        # For other models, process individually (can be optimized later)
        return [encode_text(text) for text in texts]
        
    finally:
        # Update performance statistics
        inference_time = time.time() - start_time
        _performance_stats["total_embeddings"] += len(texts)
        _performance_stats["total_time"] += inference_time
        if _performance_stats["total_embeddings"] > 0:
            _performance_stats["avg_time_per_embedding"] = _performance_stats["total_time"] / _performance_stats["total_embeddings"]


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

