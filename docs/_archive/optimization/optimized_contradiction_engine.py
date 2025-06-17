#!/usr/bin/env python3
"""
Optimized Contradiction Engine
==============================

High-performance contradiction detection with:
- Vectorized operations
- Parallel processing
- Cached computations
- Optimized algorithms
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import numpy as np
from scipy.spatial.distance import cosine, pdist, squareform
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import threading
import time

# Import base classes
try:
    from ..core.geoid import GeoidState
except ImportError:
    # Fallback for standalone testing
    pass

@dataclass
class OptimizedTensionGradient:
    """Optimized tension gradient with additional metrics"""
    geoid_a: str
    geoid_b: str
    tension_score: float
    gradient_type: str
    embedding_score: float
    layer_score: float
    symbolic_score: float
    confidence: float

class OptimizedContradictionEngine:
    """High-performance contradiction detection engine"""
    
    def __init__(self, tension_threshold: float = 0.75, max_workers: int = None):
        self.tension_threshold = tension_threshold
        self.max_workers = max_workers or min(8, max(1, threading.active_count()))
        
        # Caching for expensive computations
        self._similarity_cache = {}
        self._feature_cache = {}
        self._cache_lock = threading.RLock()
        
        # Pre-computed feature sets for optimization
        self._feature_sets_cache = {}
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_comparisons': 0,
            'avg_processing_time': 0.0
        }
    
    def detect_tension_gradients_optimized(self, geoids: List[GeoidState]) -> List[OptimizedTensionGradient]:
        """Optimized tension detection using vectorized operations and parallel processing"""
        if len(geoids) < 2:
            return []
        
        start_time = time.time()
        
        # Pre-process geoids for vectorized operations
        processed_geoids = self._preprocess_geoids(geoids)
        
        # Use different strategies based on number of geoids
        if len(geoids) <= 50:
            tensions = self._detect_tensions_small_batch(processed_geoids)
        else:
            tensions = self._detect_tensions_large_batch(processed_geoids)
        
        # Update performance metrics
        processing_time = time.time() - start_time
        self.metrics['avg_processing_time'] = (
            self.metrics['avg_processing_time'] * 0.9 + processing_time * 0.1
        )
        
        return tensions
    
    def _preprocess_geoids(self, geoids: List[GeoidState]) -> List[Dict]:
        """Preprocess geoids for optimized computation"""
        processed = []
        
        for geoid in geoids:
            # Extract and normalize features
            semantic_features = geoid.semantic_state or {}
            symbolic_features = geoid.symbolic_state or {}
            
            # Create feature vectors
            all_semantic_keys = set(semantic_features.keys())
            all_symbolic_keys = set(symbolic_features.keys())
            
            semantic_vector = np.array([
                semantic_features.get(key, 0.0) for key in sorted(all_semantic_keys)
            ], dtype=np.float32)
            
            processed.append({
                'geoid': geoid,
                'semantic_vector': semantic_vector,
                'semantic_keys': all_semantic_keys,
                'symbolic_keys': all_symbolic_keys,
                'semantic_features': semantic_features,
                'symbolic_features': symbolic_features
            })
        
        return processed
    
    def _detect_tensions_small_batch(self, processed_geoids: List[Dict]) -> List[OptimizedTensionGradient]:
        """Optimized detection for small batches using vectorized operations"""
        tensions = []
        n = len(processed_geoids)
        
        # Extract all semantic vectors
        semantic_vectors = np.array([
            pg['semantic_vector'] for pg in processed_geoids
        ])
        
        # Vectorized similarity computation
        if semantic_vectors.size > 0 and semantic_vectors.shape[1] > 0:
            # Compute pairwise cosine distances
            try:
                distances = pdist(semantic_vectors, metric='cosine')
                distance_matrix = squareform(distances)
            except Exception:
                # Fallback to manual computation
                distance_matrix = self._compute_distance_matrix_manual(semantic_vectors)
        else:
            distance_matrix = np.zeros((n, n))
        
        # Process pairs
        for i in range(n):
            for j in range(i + 1, n):
                geoid_a = processed_geoids[i]
                geoid_b = processed_geoids[j]
                
                # Get embedding score from precomputed matrix
                embedding_score = distance_matrix[i, j] if distance_matrix.size > 0 else 0.0
                
                # Compute other scores
                layer_score = self._layer_conflict_intensity_optimized(geoid_a, geoid_b)
                symbolic_score = self._symbolic_opposition_optimized(geoid_a, geoid_b)
                
                # Weighted composite score
                composite_score = (
                    embedding_score * 0.5 + 
                    layer_score * 0.3 + 
                    symbolic_score * 0.2
                )
                
                if composite_score > self.tension_threshold:
                    confidence = min(composite_score / self.tension_threshold, 1.0)
                    
                    tensions.append(OptimizedTensionGradient(
                        geoid_a=geoid_a['geoid'].geoid_id,
                        geoid_b=geoid_b['geoid'].geoid_id,
                        tension_score=composite_score,
                        gradient_type="composite",
                        embedding_score=embedding_score,
                        layer_score=layer_score,
                        symbolic_score=symbolic_score,
                        confidence=confidence
                    ))
        
        return tensions
    
    def _detect_tensions_large_batch(self, processed_geoids: List[Dict]) -> List[OptimizedTensionGradient]:
        """Optimized detection for large batches using parallel processing"""
        tensions = []
        n = len(processed_geoids)
        
        # Split into chunks for parallel processing
        chunk_size = max(10, n // self.max_workers)
        chunks = []
        
        for i in range(0, n, chunk_size):
            chunk = processed_geoids[i:i + chunk_size]
            chunks.append((i, chunk))
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for chunk_start, chunk in chunks:
                future = executor.submit(
                    self._process_chunk_tensions, 
                    chunk, 
                    processed_geoids, 
                    chunk_start
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures, timeout=30):
                try:
                    chunk_tensions = future.result()
                    tensions.extend(chunk_tensions)
                except Exception as e:
                    print(f"Warning: Chunk processing failed: {e}")
        
        return tensions
    
    def _process_chunk_tensions(self, chunk: List[Dict], all_geoids: List[Dict], 
                               chunk_start: int) -> List[OptimizedTensionGradient]:
        """Process a chunk of geoids for tensions"""
        tensions = []
        
        for i, geoid_a in enumerate(chunk):
            # Compare with all subsequent geoids
            for j in range(chunk_start + i + 1, len(all_geoids)):
                geoid_b = all_geoids[j]
                
                # Compute tension scores
                embedding_score = self._embedding_misalignment_optimized(geoid_a, geoid_b)
                layer_score = self._layer_conflict_intensity_optimized(geoid_a, geoid_b)
                symbolic_score = self._symbolic_opposition_optimized(geoid_a, geoid_b)
                
                # Weighted composite score
                composite_score = (
                    embedding_score * 0.5 + 
                    layer_score * 0.3 + 
                    symbolic_score * 0.2
                )
                
                if composite_score > self.tension_threshold:
                    confidence = min(composite_score / self.tension_threshold, 1.0)
                    
                    tensions.append(OptimizedTensionGradient(
                        geoid_a=geoid_a['geoid'].geoid_id,
                        geoid_b=geoid_b['geoid'].geoid_id,
                        tension_score=composite_score,
                        gradient_type="composite",
                        embedding_score=embedding_score,
                        layer_score=layer_score,
                        symbolic_score=symbolic_score,
                        confidence=confidence
                    ))
        
        return tensions
    
    def _compute_distance_matrix_manual(self, vectors: np.ndarray) -> np.ndarray:
        """Manual distance matrix computation as fallback"""
        n = len(vectors)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                try:
                    if np.linalg.norm(vectors[i]) > 0 and np.linalg.norm(vectors[j]) > 0:
                        dist = cosine(vectors[i], vectors[j])
                        distance_matrix[i, j] = distance_matrix[j, i] = dist
                except Exception:
                    distance_matrix[i, j] = distance_matrix[j, i] = 0.0
        
        return distance_matrix
    
    @lru_cache(maxsize=1000)
    def _embedding_misalignment_optimized(self, geoid_a: Dict, geoid_b: Dict) -> float:
        """Optimized embedding misalignment calculation"""
        vec_a = geoid_a['semantic_vector']
        vec_b = geoid_b['semantic_vector']
        
        # Fast path for empty vectors
        if vec_a.size == 0 or vec_b.size == 0:
            return 0.0
        
        # Fast path for zero vectors
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        # Optimized cosine distance
        dot_product = np.dot(vec_a, vec_b)
        cosine_sim = dot_product / (norm_a * norm_b)
        
        # Convert similarity to distance
        return 1.0 - cosine_sim
    
    def _layer_conflict_intensity_optimized(self, geoid_a: Dict, geoid_b: Dict) -> float:
        """Optimized layer conflict calculation using set operations"""
        sem_a = geoid_a['semantic_keys']
        sem_b = geoid_b['semantic_keys']
        sym_a = geoid_a['symbolic_keys']
        sym_b = geoid_b['symbolic_keys']
        
        # Fast path for empty sets
        if not (sem_a or sem_b or sym_a or sym_b):
            return 0.0
        
        # Optimized Jaccard distance calculation
        def jaccard_distance_fast(set_a: Set, set_b: Set) -> float:
            if not (set_a or set_b):
                return 0.0
            
            intersection_size = len(set_a & set_b)
            union_size = len(set_a | set_b)
            
            return 1.0 - (intersection_size / union_size) if union_size > 0 else 0.0
        
        sem_diff = jaccard_distance_fast(sem_a, sem_b)
        sym_diff = jaccard_distance_fast(sym_a, sym_b)
        
        return (sem_diff + sym_diff) / 2.0
    
    def _symbolic_opposition_optimized(self, geoid_a: Dict, geoid_b: Dict) -> float:
        """Optimized symbolic opposition calculation"""
        features_a = geoid_a['symbolic_features']
        features_b = geoid_b['symbolic_features']
        
        # Fast path for empty features
        if not features_a or not features_b:
            return 0.0
        
        # Find overlapping keys
        overlap = set(features_a.keys()) & set(features_b.keys())
        
        if not overlap:
            return 0.0
        
        # Count conflicts efficiently
        conflicts = sum(
            1 for key in overlap 
            if features_a[key] != features_b[key]
        )
        
        return conflicts / len(overlap)
    
    def calculate_pulse_strength_optimized(self, tension: OptimizedTensionGradient, 
                                         geoids: Dict[str, GeoidState]) -> float:
        """Optimized pulse strength calculation"""
        # Use confidence-weighted tension score
        base_strength = tension.tension_score * tension.confidence
        
        # Apply non-linear scaling for better discrimination
        return min(np.tanh(base_strength * 2.0), 1.0)
    
    def decide_collapse_or_surge_optimized(self, pulse_strength: float, 
                                         stability: Dict[str, float],
                                         profile: Dict[str, object] = None) -> str:
        """Optimized decision making with profile consideration"""
        
        # Extract profile settings
        allow_surges = True
        collapse_threshold = 0.5
        surge_threshold = 0.3
        
        if profile:
            allow_surges = bool(profile.get("allow_surges", True))
            collapse_threshold = float(profile.get("collapse_threshold", 0.5))
            surge_threshold = float(profile.get("surge_threshold", 0.3))
        
        # Stability-adjusted thresholds
        stability_factor = stability.get('semantic_cohesion', 0.5)
        adjusted_collapse = collapse_threshold * (1.0 + stability_factor * 0.2)
        adjusted_surge = surge_threshold * (1.0 - stability_factor * 0.2)
        
        # Decision logic
        if pulse_strength > adjusted_collapse:
            decision = "collapse"
        elif pulse_strength < adjusted_surge:
            decision = "surge"
        else:
            decision = "buffer"
        
        # Apply profile constraints
        if not allow_surges and decision == "surge":
            decision = "collapse"
        
        return decision
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for monitoring"""
        total_cache_ops = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (
            self.metrics['cache_hits'] / total_cache_ops 
            if total_cache_ops > 0 else 0.0
        )
        
        return {
            'cache_hit_rate': cache_hit_rate,
            'total_comparisons': self.metrics['total_comparisons'],
            'avg_processing_time': self.metrics['avg_processing_time'],
            'cache_size': len(self._similarity_cache)
        }
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        with self._cache_lock:
            self._similarity_cache.clear()
            self._feature_cache.clear()
            self._feature_sets_cache.clear()
        
        # Clear LRU cache
        self._embedding_misalignment_optimized.cache_clear()
    
    def optimize_for_batch_size(self, typical_batch_size: int):
        """Optimize engine parameters for typical batch size"""
        if typical_batch_size <= 20:
            self.max_workers = 2
        elif typical_batch_size <= 100:
            self.max_workers = 4
        else:
            self.max_workers = min(8, max(2, threading.active_count()))
        
        print(f"Optimized for batch size {typical_batch_size}, using {self.max_workers} workers")

# Backward compatibility wrapper
class ContradictionEngine(OptimizedContradictionEngine):
    """Backward compatible contradiction engine"""
    
    def detect_tension_gradients(self, geoids: List[GeoidState]) -> List:
        """Backward compatible method"""
        optimized_tensions = self.detect_tension_gradients_optimized(geoids)
        
        # Convert to original format
        from dataclasses import dataclass
        
        @dataclass
        class TensionGradient:
            geoid_a: str
            geoid_b: str
            tension_score: float
            gradient_type: str
        
        return [
            TensionGradient(
                geoid_a=t.geoid_a,
                geoid_b=t.geoid_b,
                tension_score=t.tension_score,
                gradient_type=t.gradient_type
            )
            for t in optimized_tensions
        ]
    
    def calculate_pulse_strength(self, tension, geoids: Dict[str, GeoidState]) -> float:
        """Backward compatible pulse strength calculation"""
        if hasattr(tension, 'confidence'):
            return self.calculate_pulse_strength_optimized(tension, geoids)
        else:
            # Fallback for old tension format
            return min(tension.tension_score, 1.0)
    
    def decide_collapse_or_surge(self, pulse_strength: float, stability: Dict[str, float],
                               profile: Dict[str, object] = None) -> str:
        """Backward compatible decision making"""
        return self.decide_collapse_or_surge_optimized(pulse_strength, stability, profile)