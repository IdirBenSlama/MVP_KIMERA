"""
Proactive Contradiction Detection Engine

This module implements proactive scanning for contradictions across all geoids
to increase SCAR utilization and improve semantic memory formation.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session

from ..vault.database import SessionLocal, GeoidDB, ScarDB
from ..core.geoid import GeoidState
from ..core.native_math import NativeMath
from .contradiction_engine import ContradictionEngine, TensionGradient


@dataclass
class ProactiveDetectionConfig:
    """Configuration for proactive contradiction detection"""
    batch_size: int = 50
    similarity_threshold: float = 0.7  # For clustering similar geoids
    scan_interval_hours: int = 6
    max_comparisons_per_run: int = 1000
    enable_clustering: bool = True
    enable_temporal_analysis: bool = True


class ProactiveContradictionDetector:
    """
    Proactively scans for contradictions across all geoids to increase
    SCAR utilization and improve system learning.
    """
    
    def __init__(self, config: ProactiveDetectionConfig = None):
        self.config = config or ProactiveDetectionConfig()
        self.contradiction_engine = ContradictionEngine(tension_threshold=0.3)
        self.last_scan_time = None
        
    def should_run_scan(self) -> bool:
        """Determine if a proactive scan should be run"""
        if self.last_scan_time is None:
            return True
            
        time_since_last = datetime.utcnow() - self.last_scan_time
        return time_since_last.total_seconds() > (self.config.scan_interval_hours * 3600)
    
    def run_proactive_scan(self) -> Dict[str, any]:
        """Run a comprehensive proactive contradiction scan"""
        if not self.should_run_scan():
            return {"status": "skipped", "reason": "too_soon"}
            
        scan_start = datetime.utcnow()
        results = {
            "scan_start": scan_start.isoformat(),
            "tensions_found": [],
            "clusters_analyzed": 0,
            "comparisons_made": 0,
            "geoids_scanned": 0,
            "potential_scars": 0
        }
        
        with SessionLocal() as db:
            # Get all geoids for analysis
            all_geoids = self._load_geoids_for_analysis(db)
            results["geoids_scanned"] = len(all_geoids)
            
            if len(all_geoids) < 2:
                return {"status": "insufficient_data", "geoids_found": len(all_geoids)}
            
            # Strategy 1: Cluster-based analysis
            if self.config.enable_clustering:
                cluster_tensions = self._analyze_clusters(all_geoids, results)
                results["tensions_found"].extend(cluster_tensions)
            
            # Strategy 2: Temporal pattern analysis
            if self.config.enable_temporal_analysis:
                temporal_tensions = self._analyze_temporal_patterns(db, all_geoids, results)
                results["tensions_found"].extend(temporal_tensions)
            
            # Strategy 3: Cross-type contradiction detection
            cross_type_tensions = self._analyze_cross_type_contradictions(all_geoids, results)
            results["tensions_found"].extend(cross_type_tensions)
            
            # Strategy 4: Underutilized geoid analysis
            underutilized_tensions = self._analyze_underutilized_geoids(db, all_geoids, results)
            results["tensions_found"].extend(underutilized_tensions)
        
        self.last_scan_time = scan_start
        results["scan_duration"] = (datetime.utcnow() - scan_start).total_seconds()
        results["potential_scars"] = len(results["tensions_found"])
        results["status"] = "completed"
        
        return results
    
    def _load_geoids_for_analysis(self, db: Session) -> List[GeoidState]:
        """Load geoids from database for analysis"""
        # Prioritize geoids that haven't been in SCARs recently
        geoid_rows = db.query(GeoidDB).limit(self.config.batch_size * 2).all()
        
        geoids = []
        for row in geoid_rows:
            try:
                geoid = GeoidState(
                    geoid_id=row.geoid_id,
                    semantic_state=row.semantic_state_json or {},
                    symbolic_state=row.symbolic_state or {},
                    embedding_vector=row.semantic_vector or [],
                    metadata=row.metadata_json or {}
                )
                geoids.append(geoid)
            except Exception as e:
                # Skip malformed geoids
                continue
                
        return geoids
    
    def _analyze_clusters(self, geoids: List[GeoidState], results: Dict) -> List[TensionGradient]:
        """Analyze geoids in semantic clusters for contradictions"""
        tensions = []
        
        # Simple clustering based on embedding similarity
        clusters = self._create_semantic_clusters(geoids)
        results["clusters_analyzed"] = len(clusters)
        
        for cluster in clusters:
            if len(cluster) < 2:
                continue
                
            # Analyze contradictions within each cluster
            cluster_tensions = self.contradiction_engine.detect_tension_gradients(cluster)
            tensions.extend(cluster_tensions)
            
            results["comparisons_made"] += len(cluster) * (len(cluster) - 1) // 2
            
            # Limit comparisons to prevent performance issues
            if results["comparisons_made"] > self.config.max_comparisons_per_run:
                break
                
        return tensions
    
    def _create_semantic_clusters(self, geoids: List[GeoidState]) -> List[List[GeoidState]]:
        """Create clusters of semantically similar geoids"""
        clusters = []
        used_geoids = set()
        
        for i, geoid_a in enumerate(geoids):
            if geoid_a.geoid_id in used_geoids:
                continue
                
            cluster = [geoid_a]
            used_geoids.add(geoid_a.geoid_id)
            
            # Find similar geoids for this cluster
            for j, geoid_b in enumerate(geoids[i+1:], i+1):
                if geoid_b.geoid_id in used_geoids:
                    continue
                    
                similarity = self._calculate_similarity(geoid_a, geoid_b)
                if similarity > self.config.similarity_threshold:
                    cluster.append(geoid_b)
                    used_geoids.add(geoid_b.geoid_id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
                
        return clusters
    
    def _calculate_similarity(self, geoid_a: GeoidState, geoid_b: GeoidState) -> float:
        """Calculate semantic similarity between two geoids"""
        if not geoid_a.embedding_vector or not geoid_b.embedding_vector:
            return 0.0
            
        try:
            # Use native cosine similarity (higher = more similar)
            return NativeMath.cosine_similarity(geoid_a.embedding_vector, geoid_b.embedding_vector)
        except:
            return 0.0
    
    def _analyze_temporal_patterns(self, db: Session, geoids: List[GeoidState], results: Dict) -> List[TensionGradient]:
        """Analyze temporal patterns for contradiction detection"""
        tensions = []
        
        # Group geoids by creation time windows
        time_windows = self._group_by_time_windows(geoids)
        
        for window_geoids in time_windows:
            if len(window_geoids) < 2:
                continue
                
            # Look for contradictions within time windows
            window_tensions = self.contradiction_engine.detect_tension_gradients(window_geoids)
            tensions.extend(window_tensions)
            
        return tensions
    
    def _group_by_time_windows(self, geoids: List[GeoidState], window_hours: int = 24) -> List[List[GeoidState]]:
        """Group geoids by time windows"""
        time_groups = {}
        
        for geoid in geoids:
            # Extract timestamp from symbolic_state or metadata
            timestamp_str = None
            if 'timestamp' in geoid.symbolic_state:
                timestamp_str = geoid.symbolic_state['timestamp']
            elif 'timestamp' in geoid.metadata:
                timestamp_str = geoid.metadata['timestamp']
                
            if timestamp_str:
                try:
                    # Handle different timestamp formats
                    if isinstance(timestamp_str, (int, float)):
                        timestamp = datetime.fromtimestamp(timestamp_str / 1000)  # Assume milliseconds
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    
                    # Group by time window
                    window_key = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                    if window_key not in time_groups:
                        time_groups[window_key] = []
                    time_groups[window_key].append(geoid)
                except:
                    # Skip geoids with unparseable timestamps
                    continue
                    
        return list(time_groups.values())
    
    def _analyze_cross_type_contradictions(self, geoids: List[GeoidState], results: Dict) -> List[TensionGradient]:
        """Analyze contradictions between different geoid types"""
        tensions = []
        
        # Group geoids by type
        type_groups = {}
        for geoid in geoids:
            geoid_type = geoid.symbolic_state.get('type', 'unknown')
            if geoid_type not in type_groups:
                type_groups[geoid_type] = []
            type_groups[geoid_type].append(geoid)
        
        # Compare geoids across different types
        type_list = list(type_groups.keys())
        for i, type_a in enumerate(type_list):
            for type_b in type_list[i+1:]:
                # Sample geoids from each type to avoid too many comparisons
                sample_a = type_groups[type_a][:10]  # Limit to 10 per type
                sample_b = type_groups[type_b][:10]
                
                for geoid_a in sample_a:
                    for geoid_b in sample_b:
                        cross_tensions = self.contradiction_engine.detect_tension_gradients([geoid_a, geoid_b])
                        tensions.extend(cross_tensions)
                        
                        results["comparisons_made"] += 1
                        if results["comparisons_made"] > self.config.max_comparisons_per_run:
                            return tensions
                            
        return tensions
    
    def _analyze_underutilized_geoids(self, db: Session, geoids: List[GeoidState], results: Dict) -> List[TensionGradient]:
        """Focus on geoids that haven't been used in SCARs"""
        tensions = []
        
        # Get geoids that are referenced in SCARs
        referenced_geoids = set()
        scar_rows = db.query(ScarDB.geoids).all()
        for (geoids_json,) in scar_rows:
            try:
                import json
                geoid_list = json.loads(geoids_json)
                referenced_geoids.update(geoid_list)
            except:
                continue
        
        # Focus on underutilized geoids
        underutilized = [g for g in geoids if g.geoid_id not in referenced_geoids]
        
        if len(underutilized) >= 2:
            # Run contradiction detection on underutilized geoids
            underutilized_tensions = self.contradiction_engine.detect_tension_gradients(underutilized[:20])  # Limit batch size
            tensions.extend(underutilized_tensions)
            
        return tensions
    
    def get_scan_statistics(self) -> Dict[str, any]:
        """Get statistics about proactive scanning"""
        with SessionLocal() as db:
            total_geoids = db.query(GeoidDB).count()
            total_scars = db.query(ScarDB).count()
            
            # Calculate utilization rate
            referenced_geoids = set()
            scar_rows = db.query(ScarDB.geoids).all()
            for (geoids_json,) in scar_rows:
                try:
                    import json
                    geoid_list = json.loads(geoids_json)
                    referenced_geoids.update(geoid_list)
                except:
                    continue
            
            utilization_rate = len(referenced_geoids) / max(total_geoids, 1)
            
        return {
            "total_geoids": total_geoids,
            "total_scars": total_scars,
            "referenced_geoids": len(referenced_geoids),
            "utilization_rate": utilization_rate,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "config": {
                "batch_size": self.config.batch_size,
                "similarity_threshold": self.config.similarity_threshold,
                "scan_interval_hours": self.config.scan_interval_hours,
                "max_comparisons_per_run": self.config.max_comparisons_per_run
            }
        }