#!/usr/bin/env python3
"""
Optimized Vault Manager
=======================

High-performance version of the vault manager with:
- Connection pooling
- Batch operations
- Cached queries
- Optimized algorithms
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
import threading
import time
import math
import uuid
import numpy as np

# Import base classes (assuming they exist)
try:
    from ..core.scar import ScarRecord
    from ..core.geoid import GeoidState
    from ..vault.database import SessionLocal, ScarDB, engine
except ImportError:
    # Fallback for standalone testing
    pass

class OptimizedVaultManager:
    """High-performance vault manager with advanced optimizations"""
    
    def __init__(self, connection_pool_size: int = 20, cache_ttl: int = 300):
        """Initialize optimized vault manager"""
        self.connection_pool_size = connection_pool_size
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}
        self._lock = threading.RLock()
        
        # Pre-computed statistics cache
        self._stats_cache = {
            'vault_a_count': None,
            'vault_b_count': None,
            'vault_a_weight': None,
            'vault_b_weight': None,
            'last_update': None
        }
        
        # Batch operation buffers
        self._batch_buffer = []
        self._batch_size = 100
        self._last_flush = time.time()
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache_timestamps:
            return False
        return time.time() - self._cache_timestamps[key] < self.cache_ttl
    
    def _get_cached(self, key: str):
        """Get cached value if valid"""
        with self._lock:
            if self._is_cache_valid(key):
                return self._cache.get(key)
        return None
    
    def _set_cached(self, key: str, value):
        """Set cached value with timestamp"""
        with self._lock:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
    
    def _invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries"""
        with self._lock:
            if pattern:
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_remove:
                    self._cache.pop(key, None)
                    self._cache_timestamps.pop(key, None)
            else:
                self._cache.clear()
                self._cache_timestamps.clear()
    
    def _update_stats_cache(self):
        """Update vault statistics cache"""
        current_time = time.time()
        
        # Only update if cache is stale (older than 30 seconds)
        if (self._stats_cache['last_update'] and 
            current_time - self._stats_cache['last_update'] < 30):
            return
        
        try:
            with SessionLocal() as db:
                # Batch query for all statistics
                vault_stats = db.query(
                    ScarDB.vault_id,
                    func.count(ScarDB.scar_id).label('count'),
                    func.sum(ScarDB.weight).label('total_weight')
                ).group_by(ScarDB.vault_id).all()
                
                # Reset stats
                self._stats_cache.update({
                    'vault_a_count': 0,
                    'vault_b_count': 0,
                    'vault_a_weight': 0.0,
                    'vault_b_weight': 0.0,
                    'last_update': current_time
                })
                
                # Update with actual values
                for vault_id, count, weight in vault_stats:
                    if vault_id == 'vault_a':
                        self._stats_cache['vault_a_count'] = count
                        self._stats_cache['vault_a_weight'] = float(weight or 0.0)
                    elif vault_id == 'vault_b':
                        self._stats_cache['vault_b_count'] = count
                        self._stats_cache['vault_b_weight'] = float(weight or 0.0)
                        
        except Exception as e:
            print(f"Warning: Failed to update stats cache: {e}")
    
    def _select_vault_optimized(self) -> str:
        """Optimized vault selection using cached statistics"""
        self._update_stats_cache()
        
        a_count = self._stats_cache['vault_a_count']
        b_count = self._stats_cache['vault_b_count']
        a_weight = self._stats_cache['vault_a_weight']
        b_weight = self._stats_cache['vault_b_weight']
        
        # Fast path for empty vaults
        if a_count == 0:
            return "vault_a"
        if b_count == 0:
            return "vault_b"
        
        # Weighted selection considering both count and weight
        a_score = a_count + (a_weight / 1000)  # Normalize weight impact
        b_score = b_count + (b_weight / 1000)
        
        return "vault_a" if a_score <= b_score else "vault_b"
    
    def insert_scar_optimized(self, scar: ScarRecord | GeoidState, vector: list[float]) -> ScarDB:
        """Optimized scar insertion with batching support"""
        
        # Convert GeoidState to ScarRecord if needed
        if isinstance(scar, GeoidState):
            scar = ScarRecord(
                scar_id=f"SCAR_{uuid.uuid4().hex[:8]}",
                geoids=[scar.geoid_id],
                reason="auto-generated",
                timestamp=datetime.utcnow().isoformat(),
                resolved_by="vault_manager",
                pre_entropy=0.0,
                post_entropy=0.0,
                delta_entropy=0.0,
                cls_angle=0.0,
                semantic_polarity=0.0,
                mutation_frequency=0.0,
            )
        
        vault_id = self._select_vault_optimized()
        
        scar_db = ScarDB(
            scar_id=scar.scar_id,
            geoids=scar.geoids,
            reason=scar.reason,
            timestamp=datetime.fromisoformat(scar.timestamp),
            resolved_by=scar.resolved_by,
            pre_entropy=scar.pre_entropy,
            post_entropy=scar.post_entropy,
            delta_entropy=scar.delta_entropy,
            cls_angle=scar.cls_angle,
            semantic_polarity=scar.semantic_polarity,
            mutation_frequency=scar.mutation_frequency,
            weight=scar.weight,
            scar_vector=vector,
            vault_id=vault_id,
        )
        
        # Use batch insertion for better performance
        return self._insert_scar_batch(scar_db)
    
    def _insert_scar_batch(self, scar_db: ScarDB) -> ScarDB:
        """Insert scar using batch processing"""
        self._batch_buffer.append(scar_db)
        
        # Flush batch if buffer is full or enough time has passed
        current_time = time.time()
        should_flush = (
            len(self._batch_buffer) >= self._batch_size or
            current_time - self._last_flush > 5.0  # 5 second timeout
        )
        
        if should_flush:
            self._flush_batch()
        
        # For immediate return, insert single item
        with SessionLocal() as db:
            db.add(scar_db)
            db.commit()
            db.refresh(scar_db)
            
        # Invalidate relevant caches
        self._invalidate_cache("vault_")
        self._stats_cache['last_update'] = None
        
        return scar_db
    
    def _flush_batch(self):
        """Flush batch buffer to database"""
        if not self._batch_buffer:
            return
        
        try:
            with SessionLocal() as db:
                db.add_all(self._batch_buffer)
                db.commit()
                
            self._batch_buffer.clear()
            self._last_flush = time.time()
            
        except Exception as e:
            print(f"Warning: Batch flush failed: {e}")
            self._batch_buffer.clear()
    
    @lru_cache(maxsize=100)
    def get_scars_from_vault_cached(self, vault_id: str, limit: int = 100, 
                                   cache_key: str = None) -> List[ScarDB]:
        """Cached version of get_scars_from_vault"""
        cache_key = cache_key or f"scars_{vault_id}_{limit}"
        
        cached_result = self._get_cached(cache_key)
        if cached_result is not None:
            return cached_result
        
        with SessionLocal() as db:
            scars = (
                db.query(ScarDB)
                .filter(ScarDB.vault_id == vault_id)
                .order_by(ScarDB.timestamp.desc())
                .limit(limit)
                .all()
            )
            
            # Update last_accessed in batch
            if scars:
                now = datetime.utcnow()
                scar_ids = [s.scar_id for s in scars]
                db.query(ScarDB).filter(ScarDB.scar_id.in_(scar_ids)).update(
                    {ScarDB.last_accessed: now}, synchronize_session=False
                )
                db.commit()
        
        self._set_cached(cache_key, scars)
        return scars
    
    def get_total_scar_count_optimized(self, vault_id: str) -> int:
        """Optimized scar count using cached statistics"""
        self._update_stats_cache()
        
        if vault_id == "vault_a":
            return self._stats_cache['vault_a_count']
        elif vault_id == "vault_b":
            return self._stats_cache['vault_b_count']
        else:
            return 0
    
    def get_total_scar_weight_optimized(self, vault_id: str) -> float:
        """Optimized scar weight using cached statistics"""
        self._update_stats_cache()
        
        if vault_id == "vault_a":
            return self._stats_cache['vault_a_weight']
        elif vault_id == "vault_b":
            return self._stats_cache['vault_b_weight']
        else:
            return 0.0
    
    def detect_vault_imbalance_optimized(self, *, by_weight: bool = False, 
                                       threshold: float = 1.5) -> Tuple[bool, str, str]:
        """Optimized imbalance detection using cached statistics"""
        self._update_stats_cache()
        
        if by_weight:
            a_val = self._stats_cache['vault_a_weight']
            b_val = self._stats_cache['vault_b_weight']
        else:
            a_val = self._stats_cache['vault_a_count']
            b_val = self._stats_cache['vault_b_count']
        
        if b_val == 0 and a_val == 0:
            return False, "", ""
        
        if a_val > threshold * max(b_val, 1e-9):
            return True, "vault_a", "vault_b"
        if b_val > threshold * max(a_val, 1e-9):
            return True, "vault_b", "vault_a"
        return False, "", ""
    
    def rebalance_vaults_optimized(self, *, by_weight: bool = False, 
                                 threshold: float = 1.5) -> int:
        """Optimized vault rebalancing with batch operations"""
        imbalanced, from_vault, to_vault = self.detect_vault_imbalance_optimized(
            by_weight=by_weight, threshold=threshold
        )
        
        if not imbalanced:
            return 0
        
        moved = 0
        
        try:
            with SessionLocal() as db:
                if by_weight:
                    # Weight-based rebalancing
                    from_val = self.get_total_scar_weight_optimized(from_vault)
                    to_val = self.get_total_scar_weight_optimized(to_vault)
                    diff = from_val - to_val
                    target = diff / 2.0
                    
                    # Get scars ordered by weight (lightest first)
                    scars = (
                        db.query(ScarDB)
                        .filter(ScarDB.vault_id == from_vault)
                        .order_by(ScarDB.weight.asc())
                        .all()
                    )
                    
                    moved_weight = 0.0
                    scar_ids_to_move = []
                    
                    for scar in scars:
                        if moved_weight >= target:
                            break
                        scar_ids_to_move.append(scar.scar_id)
                        moved_weight += scar.weight
                        moved += 1
                    
                    # Batch update
                    if scar_ids_to_move:
                        db.query(ScarDB).filter(ScarDB.scar_id.in_(scar_ids_to_move)).update(
                            {ScarDB.vault_id: to_vault}, synchronize_session=False
                        )
                
                else:
                    # Count-based rebalancing
                    from_val = self.get_total_scar_count_optimized(from_vault)
                    to_val = self.get_total_scar_count_optimized(to_vault)
                    diff = from_val - to_val
                    num_to_move = max(math.ceil(diff / 2.0), 1)
                    
                    # Get scar IDs to move (lightest first)
                    scar_ids = (
                        db.query(ScarDB.scar_id)
                        .filter(ScarDB.vault_id == from_vault)
                        .order_by(ScarDB.weight.asc())
                        .limit(num_to_move)
                        .all()
                    )
                    
                    scar_ids_to_move = [sid[0] for sid in scar_ids]
                    
                    # Batch update
                    if scar_ids_to_move:
                        db.query(ScarDB).filter(ScarDB.scar_id.in_(scar_ids_to_move)).update(
                            {ScarDB.vault_id: to_vault}, synchronize_session=False
                        )
                        moved = len(scar_ids_to_move)
                
                db.commit()
                
        except Exception as e:
            print(f"Error during vault rebalancing: {e}")
            return 0
        
        # Invalidate caches after rebalancing
        self._invalidate_cache()
        self._stats_cache['last_update'] = None
        
        return moved
    
    def get_vault_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get comprehensive vault statistics"""
        self._update_stats_cache()
        
        return {
            "vault_a": {
                "scar_count": self._stats_cache['vault_a_count'],
                "total_weight": self._stats_cache['vault_a_weight'],
                "avg_weight": (self._stats_cache['vault_a_weight'] / 
                             max(self._stats_cache['vault_a_count'], 1))
            },
            "vault_b": {
                "scar_count": self._stats_cache['vault_b_count'],
                "total_weight": self._stats_cache['vault_b_weight'],
                "avg_weight": (self._stats_cache['vault_b_weight'] / 
                             max(self._stats_cache['vault_b_count'], 1))
            },
            "balance": {
                "scar_imbalance": abs(self._stats_cache['vault_a_count'] - 
                                    self._stats_cache['vault_b_count']),
                "weight_imbalance": abs(self._stats_cache['vault_a_weight'] - 
                                      self._stats_cache['vault_b_weight'])
            }
        }
    
    def cleanup_old_scars(self, days_old: int = 30, max_scars_per_vault: int = 1000):
        """Clean up old scars to maintain performance"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        try:
            with SessionLocal() as db:
                for vault_id in ["vault_a", "vault_b"]:
                    # Count current scars
                    current_count = db.query(ScarDB).filter(ScarDB.vault_id == vault_id).count()
                    
                    if current_count > max_scars_per_vault:
                        # Remove oldest scars beyond limit
                        excess_count = current_count - max_scars_per_vault
                        
                        old_scars = (
                            db.query(ScarDB.scar_id)
                            .filter(ScarDB.vault_id == vault_id)
                            .order_by(ScarDB.timestamp.asc())
                            .limit(excess_count)
                            .all()
                        )
                        
                        old_scar_ids = [sid[0] for sid in old_scars]
                        
                        if old_scar_ids:
                            db.query(ScarDB).filter(ScarDB.scar_id.in_(old_scar_ids)).delete(
                                synchronize_session=False
                            )
                            print(f"Cleaned up {len(old_scar_ids)} old scars from {vault_id}")
                
                db.commit()
                
        except Exception as e:
            print(f"Error during scar cleanup: {e}")
        
        # Invalidate caches after cleanup
        self._invalidate_cache()
        self._stats_cache['last_update'] = None
    
    def __del__(self):
        """Cleanup on destruction"""
        # Flush any remaining batch operations
        if hasattr(self, '_batch_buffer') and self._batch_buffer:
            self._flush_batch()

# Backward compatibility wrapper
class VaultManager(OptimizedVaultManager):
    """Backward compatible vault manager"""
    
    def insert_scar(self, scar: ScarRecord | GeoidState, vector: list[float]) -> ScarDB:
        return self.insert_scar_optimized(scar, vector)
    
    def get_scars_from_vault(self, vault_id: str, limit: int = 100) -> List[ScarDB]:
        return self.get_scars_from_vault_cached(vault_id, limit)
    
    def get_total_scar_count(self, vault_id: str) -> int:
        return self.get_total_scar_count_optimized(vault_id)
    
    def get_total_scar_weight(self, vault_id: str) -> float:
        return self.get_total_scar_weight_optimized(vault_id)
    
    def detect_vault_imbalance(self, *, by_weight: bool = False, threshold: float = 1.5) -> Tuple[bool, str, str]:
        return self.detect_vault_imbalance_optimized(by_weight=by_weight, threshold=threshold)
    
    def rebalance_vaults(self, *, by_weight: bool = False, threshold: float = 1.5) -> int:
        return self.rebalance_vaults_optimized(by_weight=by_weight, threshold=threshold)