"""
GPU-Optimized Cognitive Field Dynamics Engine

This engine is specifically designed to maximize RTX 4090 utilization by leveraging:
- PyTorch CUDA operations for massive parallelization
- GPU-optimized batch processing
- Tensor operations designed for NVIDIA GPU architecture
- Memory-efficient GPU tensor management
- Mixed precision for performance (FP16/FP32)

Performance targets:
- 500+ fields/sec creation rate (100x improvement)
- 1000+ neighbor searches/sec
- Full GPU utilization (>90%)
"""

import time
import logging
import torch
import torch.nn.functional as F
import numpy as np
from collections import defaultdict
from typing import Dict, List, Set, Optional, Tuple, NamedTuple
import asyncio
from dataclasses import dataclass

# Import configurations
from ..core.cognitive_field_config import CognitiveFieldConfig, cognitive_field_config as cfg
from ..monitoring.cognitive_field_metrics import get_metrics_collector

logger = logging.getLogger(__name__)

# GPU Configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
USE_MIXED_PRECISION = True  # Use FP16 for performance, FP32 for precision when needed
TENSOR_BATCH_SIZE = 1024    # Batch size for GPU operations
MEMORY_EFFICIENT = True     # Enable memory optimizations

logger.info(f"🚀 GPU Cognitive Field Dynamics initialized on {DEVICE}")
if torch.cuda.is_available():
    logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"   CUDA Version: {torch.version.cuda}")
    logger.info(f"   Mixed Precision: {USE_MIXED_PRECISION}")

@dataclass
class GPUFieldState:
    """GPU-optimized field state."""
    geoid_id: str
    embedding: torch.Tensor
    field_strength: float
    resonance_frequency: float
    phase: float
    decay_rate: float
    creation_time: float = 0.0

class GPUSemanticFieldSystem:
    """GPU-optimized semantic field system for massive parallelization."""
    
    def __init__(self, dimension: int, device: torch.device = DEVICE):
        self.dimension = dimension
        self.device = device
        self.dtype = torch.float16 if USE_MIXED_PRECISION else torch.float32
        
        # GPU tensor storage for batch operations
        self.field_embeddings = torch.empty((0, dimension), device=device, dtype=self.dtype)
        self.field_strengths = torch.empty(0, device=device, dtype=torch.float32)
        self.resonance_frequencies = torch.empty(0, device=device, dtype=torch.float32)
        self.phases = torch.empty(0, device=device, dtype=torch.float32)
        self.decay_rates = torch.empty(0, device=device, dtype=torch.float32)
        
        # Mapping structures
        self.geoid_to_index = {}
        self.index_to_geoid = {}
        self.next_index = 0
        
        # Performance tracking
        self.gpu_memory_used = 0
        self.operation_count = 0
        
        logger.info(f"🔥 GPU Field System initialized: {dimension}D on {device}")

    def add_field_batch(self, geoid_ids: List[str], embeddings: torch.Tensor) -> List[GPUFieldState]:
        """Add multiple fields in a single GPU batch operation."""
        batch_size = len(geoid_ids)
        
        if embeddings.shape[0] != batch_size:
            raise ValueError(f"Batch size mismatch: {batch_size} IDs vs {embeddings.shape[0]} embeddings")
        
        # Ensure embeddings are on GPU with correct dtype
        embeddings = embeddings.to(device=self.device, dtype=self.dtype)
        
        # Normalize embeddings in batch (GPU operation)
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        # Calculate field properties in batch
        with torch.cuda.amp.autocast(enabled=USE_MIXED_PRECISION):
            # Resonance frequencies from embedding energy distribution
            energy_per_dim = torch.sum(embeddings * embeddings, dim=1)
            resonance_freqs = 10.0 + torch.sqrt(energy_per_dim) * 20.0
            
            # Phases from embedding asymmetry
            split_point = self.dimension // 2
            first_half = torch.sum(embeddings[:, :split_point], dim=1)
            second_half = torch.sum(embeddings[:, split_point:], dim=1)
            phases = torch.atan2(first_half, second_half + 1e-8)
            
            # Field strengths (normalized)
            field_strengths = torch.ones(batch_size, device=self.device)
            
            # Decay rates based on frequency
            decay_rates = torch.clamp(resonance_freqs * 0.01, 0.001, 0.1)
        
        # Expand tensor storage
        start_idx = self.next_index
        end_idx = start_idx + batch_size
        
        # Expand tensors
        new_embeddings = torch.cat([self.field_embeddings, embeddings], dim=0)
        new_strengths = torch.cat([self.field_strengths, field_strengths.float()], dim=0)
        new_frequencies = torch.cat([self.resonance_frequencies, resonance_freqs.float()], dim=0)
        new_phases = torch.cat([self.phases, phases.float()], dim=0)
        new_decay_rates = torch.cat([self.decay_rates, decay_rates.float()], dim=0)
        
        # Update storage
        self.field_embeddings = new_embeddings
        self.field_strengths = new_strengths
        self.resonance_frequencies = new_frequencies
        self.phases = new_phases
        self.decay_rates = new_decay_rates
        
        # Update mappings
        field_states = []
        for i, geoid_id in enumerate(geoid_ids):
            idx = start_idx + i
            self.geoid_to_index[geoid_id] = idx
            self.index_to_geoid[idx] = geoid_id
            
            field_state = GPUFieldState(
                geoid_id=geoid_id,
                embedding=embeddings[i],
                field_strength=field_strengths[i].item(),
                resonance_frequency=resonance_freqs[i].item(),
                phase=phases[i].item(),
                decay_rate=decay_rates[i].item(),
                creation_time=time.time()
            )
            field_states.append(field_state)
        
        self.next_index = end_idx
        self.operation_count += batch_size
        
        return field_states

    def find_neighbors_gpu_batch(self, query_indices: List[int], 
                                energy_threshold: float = 0.1,
                                top_k: int = 50) -> List[List[Tuple[str, float]]]:
        """Find neighbors for multiple queries using GPU batch operations."""
        if len(query_indices) == 0:
            return []
        
        query_indices_tensor = torch.tensor(query_indices, device=self.device)
        query_embeddings = self.field_embeddings[query_indices_tensor]
        
        with torch.cuda.amp.autocast(enabled=USE_MIXED_PRECISION):
            # Compute all pairwise similarities in one GPU operation
            similarities = torch.mm(query_embeddings, self.field_embeddings.t())
            
            # Add resonance frequency matching
            query_freqs = self.resonance_frequencies[query_indices_tensor]
            freq_similarities = 1.0 / (1.0 + torch.abs(
                query_freqs.unsqueeze(1) - self.resonance_frequencies.unsqueeze(0)
            ))
            
            # Combined similarity score
            combined_similarities = similarities * 0.7 + freq_similarities * 0.3
            
            # Apply threshold and get top-k
            mask = combined_similarities > energy_threshold
            
            # Zero out self-similarities
            for i, query_idx in enumerate(query_indices):
                combined_similarities[i, query_idx] = 0.0
        
        # Process results
        results = []
        for i, query_idx in enumerate(query_indices):
            row_similarities = combined_similarities[i]
            valid_mask = mask[i]
            
            if valid_mask.sum() == 0:
                results.append([])
                continue
            
            # Get valid similarities and indices
            valid_similarities = row_similarities[valid_mask]
            valid_indices = torch.where(valid_mask)[0]
            
            # Sort and get top-k
            if len(valid_similarities) > top_k:
                top_values, top_local_indices = torch.topk(valid_similarities, top_k, largest=True)
                top_indices = valid_indices[top_local_indices]
            else:
                sorted_indices = torch.argsort(valid_similarities, descending=True)
                top_indices = valid_indices[sorted_indices]
                top_values = valid_similarities[sorted_indices]
            
            # Convert to list of tuples
            neighbors = []
            for idx, similarity in zip(top_indices, top_values):
                geoid_id = self.index_to_geoid[idx.item()]
                neighbors.append((geoid_id, similarity.item()))
            
            results.append(neighbors)
        
        return results

    def compute_influence_field_gpu(self, source_indices: List[int]) -> List[Dict[str, float]]:
        """Compute influence fields using GPU acceleration."""
        if len(source_indices) == 0:
            return []
        
        source_indices_tensor = torch.tensor(source_indices, device=self.device)
        source_embeddings = self.field_embeddings[source_indices_tensor]
        source_strengths = self.field_strengths[source_indices_tensor]
        
        with torch.cuda.amp.autocast(enabled=USE_MIXED_PRECISION):
            # Compute distances from sources to all fields
            distances = torch.cdist(source_embeddings, self.field_embeddings, p=2)
            
            # Influence = strength / (1 + distance)
            influences = source_strengths.unsqueeze(1) / (1.0 + distances)
            
            # Zero out self-influences
            for i, source_idx in enumerate(source_indices):
                influences[i, source_idx] = 0.0
        
        # Convert to dictionaries
        results = []
        for i, source_idx in enumerate(source_indices):
            influence_dict = {}
            for target_idx in range(self.field_embeddings.shape[0]):
                if target_idx != source_idx:
                    geoid_id = self.index_to_geoid[target_idx]
                    influence_dict[geoid_id] = influences[i, target_idx].item()
            results.append(influence_dict)
        
        return results

    def get_gpu_memory_stats(self) -> Dict[str, float]:
        """Get GPU memory usage statistics."""
        if torch.cuda.is_available():
            return {
                "allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
                "reserved_mb": torch.cuda.memory_reserved() / 1024 / 1024,
                "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024 / 1024,
                "utilization_percent": torch.cuda.utilization() if hasattr(torch.cuda, 'utilization') else 0.0
            }
        return {"allocated_mb": 0, "reserved_mb": 0, "max_allocated_mb": 0, "utilization_percent": 0}

class CognitiveFieldDynamicsGPU:
    """High-performance GPU-optimized Cognitive Field Dynamics engine."""
    
    def __init__(self, dimension: int, config: Optional[CognitiveFieldConfig] = None):
        self.dimension = dimension
        self.config = config or cfg
        self.device = DEVICE
        
        # Initialize GPU field system
        self.field_system = GPUSemanticFieldSystem(dimension, self.device)
        
        # Performance metrics
        self.metrics_collector = get_metrics_collector()
        self.performance_stats = {
            "fields_created": 0,
            "neighbor_searches": 0,
            "batch_operations": 0,
            "gpu_time_ms": 0.0,
            "total_time_ms": 0.0
        }
        
        # Batch optimization
        self.pending_fields = []
        self.batch_size = TENSOR_BATCH_SIZE
        
        logger.info(f"🚀 CognitiveFieldDynamicsGPU initialized: {dimension}D on {self.device}")
        if torch.cuda.is_available():
            memory_stats = self.field_system.get_gpu_memory_stats()
            logger.info(f"   Initial GPU memory: {memory_stats['allocated_mb']:.1f} MB")

    def add_geoid(self, geoid_id: str, embedding: torch.Tensor) -> Optional[GPUFieldState]:
        """Add a single geoid (batched internally for performance)."""
        if geoid_id in self.field_system.geoid_to_index:
            # Return existing field
            idx = self.field_system.geoid_to_index[geoid_id]
            return self._get_field_state_by_index(idx)
        
        # Convert numpy to tensor if needed
        if isinstance(embedding, np.ndarray):
            embedding = torch.from_numpy(embedding)
        
        # Add to pending batch
        self.pending_fields.append((geoid_id, embedding))
        
        # Process batch if full or force flush
        if len(self.pending_fields) >= self.batch_size:
            return self._flush_pending_fields()[-1]  # Return last added field
        
        # For immediate processing (compatibility mode)
        return self._flush_pending_fields()[-1] if self.pending_fields else None

    def _flush_pending_fields(self) -> List[GPUFieldState]:
        """Flush pending fields in a batch operation."""
        if not self.pending_fields:
            return []
        
        start_time = time.perf_counter()
        
        # Prepare batch data
        geoid_ids = [item[0] for item in self.pending_fields]
        embeddings = torch.stack([item[1] for item in self.pending_fields])
        
        # GPU batch processing
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        gpu_start = time.perf_counter()
        
        field_states = self.field_system.add_field_batch(geoid_ids, embeddings)
        
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        gpu_end = time.perf_counter()
        
        # Update performance stats
        gpu_time_ms = (gpu_end - gpu_start) * 1000
        total_time_ms = (time.perf_counter() - start_time) * 1000
        
        self.performance_stats["fields_created"] += len(geoid_ids)
        self.performance_stats["batch_operations"] += 1
        self.performance_stats["gpu_time_ms"] += gpu_time_ms
        self.performance_stats["total_time_ms"] += total_time_ms
        
        logger.debug(f"Batch processed: {len(geoid_ids)} fields in {gpu_time_ms:.2f}ms GPU time")
        
        # Clear pending
        self.pending_fields.clear()
        
        return field_states

    def find_semantic_neighbors(self, geoid_id: str, energy_threshold: float = 0.1) -> List[Tuple[str, float]]:
        """Find semantic neighbors using GPU acceleration."""
        if geoid_id not in self.field_system.geoid_to_index:
            return []
        
        # Flush any pending fields first
        self._flush_pending_fields()
        
        start_time = time.perf_counter()
        
        query_idx = self.field_system.geoid_to_index[geoid_id]
        results = self.field_system.find_neighbors_gpu_batch([query_idx], energy_threshold)
        
        gpu_time_ms = (time.perf_counter() - start_time) * 1000
        self.performance_stats["neighbor_searches"] += 1
        self.performance_stats["gpu_time_ms"] += gpu_time_ms
        
        return results[0] if results else []

    def find_influence_field(self, geoid_id: str) -> Dict[str, float]:
        """Find influence field using GPU acceleration."""
        if geoid_id not in self.field_system.geoid_to_index:
            return {}
        
        # Flush any pending fields first
        self._flush_pending_fields()
        
        source_idx = self.field_system.geoid_to_index[geoid_id]
        results = self.field_system.compute_influence_field_gpu([source_idx])
        
        return results[0] if results else {}

    def detect_semantic_anomalies(self) -> List[Dict]:
        """Detect semantic anomalies using GPU-accelerated statistical analysis."""
        self._flush_pending_fields()
        
        if self.field_system.field_embeddings.shape[0] == 0:
            return []
        
        anomalies = []
        
        with torch.cuda.amp.autocast(enabled=USE_MIXED_PRECISION):
            # High field strength anomalies
            strength_threshold = torch.mean(self.field_system.field_strengths) + 2 * torch.std(self.field_system.field_strengths)
            high_strength_mask = self.field_system.field_strengths > strength_threshold
            
            # High frequency anomalies
            freq_threshold = torch.mean(self.field_system.resonance_frequencies) + 2 * torch.std(self.field_system.resonance_frequencies)
            high_freq_mask = self.field_system.resonance_frequencies > freq_threshold
            
            # Isolation anomalies (fields with very few neighbors)
            similarities = torch.mm(self.field_system.field_embeddings, self.field_system.field_embeddings.t())
            neighbor_counts = torch.sum(similarities > 0.5, dim=1) - 1  # Exclude self
            isolation_threshold = torch.quantile(neighbor_counts.float(), 0.1)  # Bottom 10%
            isolation_mask = neighbor_counts < isolation_threshold
        
        # Collect anomalies
        for i in range(self.field_system.field_embeddings.shape[0]):
            geoid_id = self.field_system.index_to_geoid[i]
            
            anomaly_types = []
            if high_strength_mask[i]:
                anomaly_types.append("high_field_strength")
            if high_freq_mask[i]:
                anomaly_types.append("high_resonance_frequency")
            if isolation_mask[i]:
                anomaly_types.append("semantic_isolation")
            
            if anomaly_types:
                anomalies.append({
                    "geoid_id": geoid_id,
                    "anomaly_types": anomaly_types,
                    "field_strength": self.field_system.field_strengths[i].item(),
                    "resonance_frequency": self.field_system.resonance_frequencies[i].item(),
                    "neighbor_count": neighbor_counts[i].item()
                })
        
        return anomalies

    def _get_field_state_by_index(self, idx: int) -> Optional[GPUFieldState]:
        """Get field state by index."""
        if idx >= self.field_system.field_embeddings.shape[0]:
            return None
        
        geoid_id = self.field_system.index_to_geoid[idx]
        return GPUFieldState(
            geoid_id=geoid_id,
            embedding=self.field_system.field_embeddings[idx],
            field_strength=self.field_system.field_strengths[idx].item(),
            resonance_frequency=self.field_system.resonance_frequencies[idx].item(),
            phase=self.field_system.phases[idx].item(),
            decay_rate=self.field_system.decay_rates[idx].item()
        )

    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics."""
        gpu_stats = self.field_system.get_gpu_memory_stats()
        
        total_fields = self.performance_stats["fields_created"]
        total_gpu_time = self.performance_stats["gpu_time_ms"]
        
        return {
            "total_fields": total_fields,
            "neighbor_searches": self.performance_stats["neighbor_searches"],
            "batch_operations": self.performance_stats["batch_operations"],
            "gpu_time_ms": total_gpu_time,
            "total_time_ms": self.performance_stats["total_time_ms"],
            "gpu_efficiency": (total_gpu_time / self.performance_stats["total_time_ms"]) * 100 if self.performance_stats["total_time_ms"] > 0 else 0,
            "fields_per_second": total_fields / (self.performance_stats["total_time_ms"] / 1000) if self.performance_stats["total_time_ms"] > 0 else 0,
            "gpu_memory": gpu_stats,
            "device": str(self.device),
            "mixed_precision": USE_MIXED_PRECISION
        }

    def optimize_for_inference(self):
        """Optimize the system for inference (compile models, etc.)."""
        if self.field_system.field_embeddings.shape[0] == 0:
            logger.warning("No fields to optimize - add fields first")
            return
        
        logger.info("🔥 Optimizing GPU engine for inference...")
        
        # Compile frequently used operations
        with torch.cuda.amp.autocast(enabled=USE_MIXED_PRECISION):
            # Warm up GPU kernels
            dummy_query = self.field_system.field_embeddings[:1]
            _ = torch.mm(dummy_query, self.field_system.field_embeddings.t())
            
            # Pre-compute any cacheable operations
            if hasattr(torch.backends.cudnn, 'benchmark'):
                torch.backends.cudnn.benchmark = True
        
        logger.info("✅ GPU optimization complete")

    @property
    def fields(self) -> Dict[str, GPUFieldState]:
        """Get all fields as a dictionary."""
        self._flush_pending_fields()
        
        fields_dict = {}
        for geoid_id, idx in self.field_system.geoid_to_index.items():
            fields_dict[geoid_id] = self._get_field_state_by_index(idx)
        
        return fields_dict

# Alias for compatibility
CognitiveFieldDynamics = CognitiveFieldDynamicsGPU 