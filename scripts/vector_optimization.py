#!/usr/bin/env python3
"""
Vector Search Optimization for Kimera SWM
Implements similarity-based SCAR resolution and semantic search
"""

import os
import sys
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")

class VectorSearchOptimizer:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
    def analyze_vector_distribution(self) -> Dict[str, Any]:
        """Analyze the distribution of vectors in the database"""
        print("\n📊 Analyzing Vector Distribution...")
        
        with self.engine.connect() as conn:
            # Check vector completeness
            geoid_stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_geoids,
                    COUNT(semantic_vector) as geoids_with_vectors,
                    ROUND(COUNT(semantic_vector) * 100.0 / COUNT(*), 2) as vector_coverage_pct
                FROM geoids
            """)).fetchone()
            
            scar_stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_scars,
                    COUNT(scar_vector) as scars_with_vectors,
                    ROUND(COUNT(scar_vector) * 100.0 / COUNT(*), 2) as vector_coverage_pct
                FROM scars
            """)).fetchone()
            
            print(f"   Geoids: {geoid_stats[1]}/{geoid_stats[0]} have vectors ({geoid_stats[2]}%)")
            print(f"   SCARs: {scar_stats[1]}/{scar_stats[0]} have vectors ({scar_stats[2]}%)")
            
            return {
                "geoid_stats": dict(geoid_stats._mapping),
                "scar_stats": dict(scar_stats._mapping)
            }
    
    def generate_missing_vectors(self) -> int:
        """Generate vectors for records that don't have them"""
        print("\n🔧 Generating Missing Vectors...")
        
        generated_count = 0
        
        with self.engine.connect() as conn:
            # Find geoids without vectors
            geoids_without_vectors = conn.execute(text("""
                SELECT geoid_id, symbolic_state, metadata_json
                FROM geoids 
                WHERE semantic_vector IS NULL
                LIMIT 100
            """)).fetchall()
            
            for geoid in geoids_without_vectors:
                # Generate a simple vector based on content hash
                content = str(geoid.symbolic_state) + str(geoid.metadata_json)
                vector = self._generate_content_vector(content)
                
                conn.execute(text("""
                    UPDATE geoids 
                    SET semantic_vector = :vector 
                    WHERE geoid_id = :geoid_id
                """), {"vector": vector, "geoid_id": geoid.geoid_id})
                generated_count += 1
            
            # Find SCARs without vectors
            scars_without_vectors = conn.execute(text("""
                SELECT scar_id, reason, geoids
                FROM scars 
                WHERE scar_vector IS NULL
                LIMIT 100
            """)).fetchall()
            
            for scar in scars_without_vectors:
                # Generate vector based on reason and geoids
                content = str(scar.reason) + str(scar.geoids)
                vector = self._generate_content_vector(content)
                
                conn.execute(text("""
                    UPDATE scars 
                    SET scar_vector = :vector 
                    WHERE scar_id = :scar_id
                """), {"vector": vector, "scar_id": scar.scar_id})
                generated_count += 1
            
            conn.commit()
            
        print(f"   ✅ Generated {generated_count} vectors")
        return generated_count
    
    def _generate_content_vector(self, content: str, dim: int = 1024) -> List[float]:
        """Generate a simple content-based vector"""
        # Simple hash-based vector generation
        import hashlib
        
        # Create multiple hash values for different dimensions
        vectors = []
        for i in range(0, dim, 32):
            hash_input = f"{content}_{i}".encode()
            hash_val = hashlib.md5(hash_input).hexdigest()
            # Convert hex to normalized floats
            hex_vals = [int(hash_val[j:j+2], 16) for j in range(0, min(32, len(hash_val)), 2)]
            normalized = [(x - 127.5) / 127.5 for x in hex_vals]  # Normalize to [-1, 1]
            vectors.extend(normalized)
        
        # Ensure exact dimension
        if len(vectors) > dim:
            vectors = vectors[:dim]
        elif len(vectors) < dim:
            vectors.extend([0.0] * (dim - len(vectors)))
        
        # Normalize to unit vector
        norm = np.linalg.norm(vectors)
        if norm > 0:
            vectors = [x / norm for x in vectors]
        
        return vectors
    
    def find_similar_scars(self, scar_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find SCARs similar to the given SCAR"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    s2.scar_id,
                    s2.reason,
                    s2.delta_entropy,
                    s2.resolved_by,
                    1 - (s1.scar_vector <=> s2.scar_vector) as similarity
                FROM scars s1, scars s2
                WHERE s1.scar_id = :scar_id 
                    AND s2.scar_id != :scar_id
                    AND s1.scar_vector IS NOT NULL 
                    AND s2.scar_vector IS NOT NULL
                ORDER BY s1.scar_vector <=> s2.scar_vector
                LIMIT :limit
            """), {"scar_id": scar_id, "limit": limit}).fetchall()
            
            return [dict(row._mapping) for row in results]
    
    def find_related_geoids(self, geoid_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find geoids semantically related to the given geoid"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    g2.geoid_id,
                    1 - (g1.semantic_vector <=> g2.semantic_vector) as similarity
                FROM geoids g1, geoids g2
                WHERE g1.geoid_id = :geoid_id 
                    AND g2.geoid_id != :geoid_id
                    AND g1.semantic_vector IS NOT NULL 
                    AND g2.semantic_vector IS NOT NULL
                ORDER BY g1.semantic_vector <=> g2.semantic_vector
                LIMIT :limit
            """), {"geoid_id": geoid_id, "limit": limit}).fetchall()
            
            return [dict(row._mapping) for row in results]
    
    def implement_scar_resolution_suggestions(self) -> Dict[str, Any]:
        """Implement similarity-based SCAR resolution suggestions"""
        print("\n🔍 Implementing SCAR Resolution Suggestions...")
        
        suggestions = []
        
        with self.engine.connect() as conn:
            # Find unresolved SCARs
            unresolved_scars = conn.execute(text("""
                SELECT scar_id, reason, delta_entropy
                FROM scars 
                WHERE resolved_by IS NULL 
                    AND scar_vector IS NOT NULL
                ORDER BY ABS(delta_entropy) DESC
                LIMIT 20
            """)).fetchall()
            
            for scar in unresolved_scars:
                # Find similar resolved SCARs
                similar_resolved = conn.execute(text("""
                    SELECT 
                        s2.scar_id,
                        s2.reason,
                        s2.resolved_by,
                        s2.delta_entropy,
                        1 - (s1.scar_vector <=> s2.scar_vector) as similarity
                    FROM scars s1, scars s2
                    WHERE s1.scar_id = :scar_id 
                        AND s2.resolved_by IS NOT NULL
                        AND s1.scar_vector IS NOT NULL 
                        AND s2.scar_vector IS NOT NULL
                    ORDER BY s1.scar_vector <=> s2.scar_vector
                    LIMIT 3
                """), {"scar_id": scar.scar_id}).fetchall()
                
                if similar_resolved:
                    # Suggest resolution strategies based on similar SCARs
                    strategies = {}
                    for resolved in similar_resolved:
                        strategy = resolved.resolved_by
                        if strategy not in strategies:
                            strategies[strategy] = {
                                "count": 0,
                                "avg_similarity": 0,
                                "examples": []
                            }
                        strategies[strategy]["count"] += 1
                        strategies[strategy]["avg_similarity"] += resolved.similarity
                        strategies[strategy]["examples"].append({
                            "scar_id": resolved.scar_id,
                            "similarity": resolved.similarity,
                            "delta_entropy": resolved.delta_entropy
                        })
                    
                    # Calculate averages
                    for strategy in strategies:
                        strategies[strategy]["avg_similarity"] /= strategies[strategy]["count"]
                    
                    suggestions.append({
                        "scar_id": scar.scar_id,
                        "reason": scar.reason,
                        "suggested_strategies": strategies
                    })
        
        print(f"   ✅ Generated {len(suggestions)} resolution suggestions")
        return {"suggestions": suggestions}
    
    def create_semantic_clusters(self) -> Dict[str, Any]:
        """Create semantic clusters of geoids and SCARs"""
        print("\n🎯 Creating Semantic Clusters...")
        
        with self.engine.connect() as conn:
            # Create geoid clusters
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS geoid_clusters (
                    cluster_id SERIAL PRIMARY KEY,
                    geoid_ids TEXT[],
                    cluster_center VECTOR(1024),
                    cluster_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Simple clustering: find groups of similar geoids
            geoid_clusters = conn.execute(text("""
                WITH similarity_pairs AS (
                    SELECT 
                        g1.geoid_id as geoid1,
                        g2.geoid_id as geoid2,
                        1 - (g1.semantic_vector <=> g2.semantic_vector) as similarity
                    FROM geoids g1, geoids g2
                    WHERE g1.geoid_id < g2.geoid_id
                        AND g1.semantic_vector IS NOT NULL 
                        AND g2.semantic_vector IS NOT NULL
                        AND (1 - (g1.semantic_vector <=> g2.semantic_vector)) > 0.8
                )
                SELECT geoid1, geoid2, similarity
                FROM similarity_pairs
                ORDER BY similarity DESC
                LIMIT 50
            """)).fetchall()
            
            # Create SCAR clusters
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scar_clusters (
                    cluster_id SERIAL PRIMARY KEY,
                    scar_ids TEXT[],
                    cluster_center VECTOR(1024),
                    cluster_size INTEGER,
                    avg_entropy_reduction FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            scar_clusters = conn.execute(text("""
                WITH similarity_pairs AS (
                    SELECT 
                        s1.scar_id as scar1,
                        s2.scar_id as scar2,
                        1 - (s1.scar_vector <=> s2.scar_vector) as similarity,
                        (s1.delta_entropy + s2.delta_entropy) / 2 as avg_entropy
                    FROM scars s1, scars s2
                    WHERE s1.scar_id < s2.scar_id
                        AND s1.scar_vector IS NOT NULL 
                        AND s2.scar_vector IS NOT NULL
                        AND (1 - (s1.scar_vector <=> s2.scar_vector)) > 0.75
                )
                SELECT scar1, scar2, similarity, avg_entropy
                FROM similarity_pairs
                ORDER BY similarity DESC
                LIMIT 50
            """)).fetchall()
            
            conn.commit()
            
        print(f"   ✅ Found {len(geoid_clusters)} geoid similarity pairs")
        print(f"   ✅ Found {len(scar_clusters)} SCAR similarity pairs")
        
        return {
            "geoid_clusters": len(geoid_clusters),
            "scar_clusters": len(scar_clusters)
        }
    
    def optimize_vector_indexes(self) -> None:
        """Optimize vector indexes for better performance"""
        print("\n⚡ Optimizing Vector Indexes...")
        
        with self.engine.connect() as conn:
            # Update vector index parameters based on data size
            geoid_count = conn.execute(text("SELECT COUNT(*) FROM geoids WHERE semantic_vector IS NOT NULL")).scalar()
            scar_count = conn.execute(text("SELECT COUNT(*) FROM scars WHERE scar_vector IS NOT NULL")).scalar()
            
            # Calculate optimal list count (sqrt of data size)
            geoid_lists = max(10, min(1000, int(np.sqrt(geoid_count))))
            scar_lists = max(10, min(1000, int(np.sqrt(scar_count))))
            
            # Recreate indexes with optimal parameters
            try:
                conn.execute(text("DROP INDEX IF EXISTS idx_geoids_semantic_vector"))
                conn.execute(text(f"""
                    CREATE INDEX idx_geoids_semantic_vector 
                    ON geoids USING ivfflat (semantic_vector vector_cosine_ops) 
                    WITH (lists = {geoid_lists})
                """))
                print(f"   ✅ Optimized geoid vector index (lists={geoid_lists})")
                
                conn.execute(text("DROP INDEX IF EXISTS idx_scars_vector"))
                conn.execute(text(f"""
                    CREATE INDEX idx_scars_vector 
                    ON scars USING ivfflat (scar_vector vector_cosine_ops) 
                    WITH (lists = {scar_lists})
                """))
                print(f"   ✅ Optimized SCAR vector index (lists={scar_lists})")
                
                conn.commit()
            except Exception as e:
                print(f"   ⚠️  Index optimization warning: {e}")
                conn.rollback()
    
    def benchmark_vector_queries(self) -> Dict[str, float]:
        """Benchmark vector query performance"""
        print("\n🏃 Benchmarking Vector Query Performance...")
        
        import time
        
        with self.engine.connect() as conn:
            # Get a sample vector
            sample = conn.execute(text("""
                SELECT semantic_vector FROM geoids 
                WHERE semantic_vector IS NOT NULL 
                LIMIT 1
            """)).fetchone()
            
            if not sample:
                print("   ⚠️  No vectors found for benchmarking")
                return {}
            
            sample_vector = sample[0]
            
            # Benchmark similarity search
            start_time = time.time()
            results = conn.execute(text("""
                SELECT geoid_id, semantic_vector <=> :vector as distance
                FROM geoids 
                WHERE semantic_vector IS NOT NULL
                ORDER BY semantic_vector <=> :vector
                LIMIT 10
            """), {"vector": sample_vector}).fetchall()
            geoid_query_time = time.time() - start_time
            
            # Benchmark SCAR similarity
            start_time = time.time()
            scar_results = conn.execute(text("""
                SELECT scar_id, scar_vector <=> :vector as distance
                FROM scars 
                WHERE scar_vector IS NOT NULL
                ORDER BY scar_vector <=> :vector
                LIMIT 10
            """), {"vector": sample_vector}).fetchall()
            scar_query_time = time.time() - start_time
            
        print(f"   ✅ Geoid similarity query: {geoid_query_time:.3f}s")
        print(f"   ✅ SCAR similarity query: {scar_query_time:.3f}s")
        
        return {
            "geoid_query_time": geoid_query_time,
            "scar_query_time": scar_query_time
        }

def main():
    """Run vector optimization tasks"""
    print("🚀 Kimera Vector Search Optimization")
    print("=" * 50)
    
    optimizer = VectorSearchOptimizer()
    
    # Analyze current state
    distribution = optimizer.analyze_vector_distribution()
    
    # Generate missing vectors
    generated = optimizer.generate_missing_vectors()
    
    # Optimize indexes
    optimizer.optimize_vector_indexes()
    
    # Create semantic clusters
    clusters = optimizer.create_semantic_clusters()
    
    # Implement SCAR resolution suggestions
    suggestions = optimizer.implement_scar_resolution_suggestions()
    
    # Benchmark performance
    benchmarks = optimizer.benchmark_vector_queries()
    
    # Save optimization report
    report = {
        "timestamp": datetime.now().isoformat(),
        "vector_distribution": distribution,
        "vectors_generated": generated,
        "clusters_created": clusters,
        "resolution_suggestions": len(suggestions.get("suggestions", [])),
        "performance_benchmarks": benchmarks
    }
    
    # Convert any Decimal types to float for JSON serialization
    def convert_decimals(obj):
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            if isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
        elif hasattr(obj, '__class__') and 'Decimal' in str(obj.__class__):
            return float(obj)
        return obj
    
    report = convert_decimals(report)
    
    with open("vector_optimization_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Vector optimization complete!")
    print(f"📊 Report saved to vector_optimization_report.json")
    
    # Test similarity functions
    print("\n🧪 Testing Similarity Functions...")
    with optimizer.engine.connect() as conn:
        # Test find_similar_scars function
        test_scar = conn.execute(text("""
            SELECT scar_id FROM scars 
            WHERE scar_vector IS NOT NULL 
            LIMIT 1
        """)).scalar()
        
        if test_scar:
            similar = conn.execute(text("""
                SELECT * FROM find_similar_scars(:scar_id, 3)
            """), {"scar_id": test_scar}).fetchall()
            print(f"   ✅ Found {len(similar)} similar SCARs for {test_scar}")
        
        # Test find_related_geoids function
        test_geoid = conn.execute(text("""
            SELECT geoid_id FROM geoids 
            WHERE semantic_vector IS NOT NULL 
            LIMIT 1
        """)).scalar()
        
        if test_geoid:
            related = conn.execute(text("""
                SELECT * FROM find_related_geoids(:geoid_id, 3)
            """), {"geoid_id": test_geoid}).fetchall()
            print(f"   ✅ Found {len(related)} related geoids for {test_geoid}")

if __name__ == "__main__":
    main()