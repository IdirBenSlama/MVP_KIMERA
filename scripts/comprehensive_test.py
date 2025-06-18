#!/usr/bin/env python3
"""
Comprehensive Testing and Analysis for Optimized Kimera SWM
Tests all optimization improvements and analyzes performance
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from sqlalchemy import create_engine, text
from typing import Dict, List, Any, Tuple
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")
API_BASE_URL = "http://localhost:8000"

class KimeraSystemTester:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.test_results = {}
        self.performance_metrics = {}
        
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity and basic operations"""
        print("\n🔌 Testing Database Connectivity...")
        
        try:
            with self.engine.connect() as conn:
                # Test basic connection
                result = conn.execute(text("SELECT version()")).scalar()
                postgres_version = result.split()[1] if result else "Unknown"
                
                # Test pgvector extension
                vector_version = conn.execute(text("""
                    SELECT extversion FROM pg_extension WHERE extname = 'vector'
                """)).scalar()
                
                # Test database size
                db_size = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)).scalar()
                
                return {
                    "status": "success",
                    "postgres_version": postgres_version,
                    "pgvector_version": vector_version,
                    "database_size": db_size
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_schema_optimizations(self) -> Dict[str, Any]:
        """Test JSONB conversions and schema improvements"""
        print("\n📊 Testing Schema Optimizations...")
        
        with self.engine.connect() as conn:
            # Check JSONB columns
            jsonb_columns = conn.execute(text("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns 
                WHERE data_type = 'jsonb'
                ORDER BY table_name, column_name
            """)).fetchall()
            
            # Test JSONB operations
            jsonb_test_results = []
            
            # Test geoids JSONB query
            start_time = time.time()
            geoid_jsonb = conn.execute(text("""
                SELECT geoid_id, symbolic_state ? 'symbols' as has_symbols
                FROM geoids 
                WHERE symbolic_state IS NOT NULL
                LIMIT 5
            """)).fetchall()
            jsonb_query_time = time.time() - start_time
            
            jsonb_test_results.append({
                "table": "geoids",
                "operation": "jsonb_exists",
                "time": jsonb_query_time,
                "results": len(geoid_jsonb)
            })
            
            # Test SCARs JSONB query
            start_time = time.time()
            scar_jsonb = conn.execute(text("""
                SELECT scar_id, jsonb_array_length(geoids) as geoid_count
                FROM scars 
                WHERE geoids IS NOT NULL AND jsonb_typeof(geoids) = 'array'
                LIMIT 5
            """)).fetchall()
            jsonb_query_time = time.time() - start_time
            
            jsonb_test_results.append({
                "table": "scars",
                "operation": "jsonb_array_length",
                "time": jsonb_query_time,
                "results": len(scar_jsonb)
            })
            
            return {
                "jsonb_columns_count": len(jsonb_columns),
                "jsonb_columns": [f"{col[0]}.{col[1]}" for col in jsonb_columns],
                "jsonb_operations": jsonb_test_results
            }
    
    def test_vector_search_performance(self) -> Dict[str, Any]:
        """Test vector search capabilities and performance"""
        print("\n🔍 Testing Vector Search Performance...")
        
        with self.engine.connect() as conn:
            # Check vector coverage
            vector_stats = conn.execute(text("""
                SELECT 
                    'geoids' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(semantic_vector) as rows_with_vectors,
                    ROUND(COUNT(semantic_vector) * 100.0 / COUNT(*), 1) as coverage_pct
                FROM geoids
                UNION ALL
                SELECT 
                    'scars' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(scar_vector) as rows_with_vectors,
                    ROUND(COUNT(scar_vector) * 100.0 / COUNT(*), 1) as coverage_pct
                FROM scars
            """)).fetchall()
            
            # Test vector similarity queries
            similarity_tests = []
            
            # Test SCAR similarity
            start_time = time.time()
            scar_similarity = conn.execute(text("""
                SELECT 
                    s1.scar_id as scar1,
                    s2.scar_id as scar2,
                    1 - (s1.scar_vector <=> s2.scar_vector) as similarity
                FROM scars s1, scars s2
                WHERE s1.scar_vector IS NOT NULL 
                    AND s2.scar_vector IS NOT NULL
                    AND s1.scar_id < s2.scar_id
                ORDER BY s1.scar_vector <=> s2.scar_vector
                LIMIT 10
            """)).fetchall()
            scar_similarity_time = time.time() - start_time
            
            similarity_tests.append({
                "type": "scar_similarity",
                "time": scar_similarity_time,
                "results": len(scar_similarity),
                "avg_similarity": np.mean([float(row[2]) for row in scar_similarity]) if scar_similarity else 0
            })
            
            # Test Geoid similarity
            start_time = time.time()
            geoid_similarity = conn.execute(text("""
                SELECT 
                    g1.geoid_id as geoid1,
                    g2.geoid_id as geoid2,
                    1 - (g1.semantic_vector <=> g2.semantic_vector) as similarity
                FROM geoids g1, geoids g2
                WHERE g1.semantic_vector IS NOT NULL 
                    AND g2.semantic_vector IS NOT NULL
                    AND g1.geoid_id < g2.geoid_id
                ORDER BY g1.semantic_vector <=> g2.semantic_vector
                LIMIT 10
            """)).fetchall()
            geoid_similarity_time = time.time() - start_time
            
            similarity_tests.append({
                "type": "geoid_similarity",
                "time": geoid_similarity_time,
                "results": len(geoid_similarity),
                "avg_similarity": np.mean([float(row[2]) for row in geoid_similarity]) if geoid_similarity else 0
            })
            
            return {
                "vector_coverage": [dict(zip(["table_name", "total_rows", "rows_with_vectors", "coverage_pct"], row)) for row in vector_stats],
                "similarity_tests": similarity_tests
            }
    
    def test_index_performance(self) -> Dict[str, Any]:
        """Test index usage and performance"""
        print("\n📈 Testing Index Performance...")
        
        with self.engine.connect() as conn:
            # Get index statistics
            index_stats = conn.execute(text("""
                SELECT 
                    indexname,
                    tablename,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
            """)).fetchall()
            
            # Test specific index performance
            index_tests = []
            
            # Test GIN index on JSONB
            start_time = time.time()
            gin_test = conn.execute(text("""
                SELECT geoid_id FROM geoids 
                WHERE symbolic_state ? 'symbols'
                LIMIT 10
            """)).fetchall()
            gin_time = time.time() - start_time
            
            index_tests.append({
                "index_type": "gin_jsonb",
                "time": gin_time,
                "results": len(gin_test)
            })
            
            # Test vector index
            start_time = time.time()
            vector_test = conn.execute(text("""
                SELECT s1.scar_id FROM scars s1, scars s2
                WHERE s1.scar_vector IS NOT NULL 
                    AND s2.scar_vector IS NOT NULL
                    AND s1.scar_id != s2.scar_id
                ORDER BY s1.scar_vector <=> s2.scar_vector
                LIMIT 5
            """)).fetchall()
            vector_time = time.time() - start_time
            
            index_tests.append({
                "index_type": "ivfflat_vector",
                "time": vector_time,
                "results": len(vector_test)
            })
            
            # Test B-tree index
            start_time = time.time()
            btree_test = conn.execute(text("""
                SELECT scar_id FROM scars 
                WHERE timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 10
            """)).fetchall()
            btree_time = time.time() - start_time
            
            index_tests.append({
                "index_type": "btree_timestamp",
                "time": btree_time,
                "results": len(btree_test)
            })
            
            return {
                "total_indexes": len(index_stats),
                "index_statistics": [dict(zip(["indexname", "tablename", "idx_scan", "idx_tup_read", "idx_tup_fetch", "index_size"], row)) for row in index_stats],
                "performance_tests": index_tests
            }
    
    def test_materialized_views(self) -> Dict[str, Any]:
        """Test materialized views functionality"""
        print("\n📋 Testing Materialized Views...")
        
        with self.engine.connect() as conn:
            # List materialized views
            views = conn.execute(text("""
                SELECT matviewname, definition
                FROM pg_matviews
                WHERE schemaname = 'public'
            """)).fetchall()
            
            view_tests = []
            
            # Test SCAR patterns view
            try:
                start_time = time.time()
                scar_patterns = conn.execute(text("""
                    SELECT * FROM mv_scar_patterns LIMIT 10
                """)).fetchall()
                scar_patterns_time = time.time() - start_time
                
                view_tests.append({
                    "view": "mv_scar_patterns",
                    "time": scar_patterns_time,
                    "results": len(scar_patterns),
                    "status": "success"
                })
            except Exception as e:
                view_tests.append({
                    "view": "mv_scar_patterns",
                    "status": "error",
                    "error": str(e)
                })
            
            # Test Geoid complexity view
            try:
                start_time = time.time()
                geoid_complexity = conn.execute(text("""
                    SELECT * FROM mv_geoid_complexity LIMIT 10
                """)).fetchall()
                geoid_complexity_time = time.time() - start_time
                
                view_tests.append({
                    "view": "mv_geoid_complexity",
                    "time": geoid_complexity_time,
                    "results": len(geoid_complexity),
                    "status": "success"
                })
            except Exception as e:
                view_tests.append({
                    "view": "mv_geoid_complexity",
                    "status": "error",
                    "error": str(e)
                })
            
            return {
                "total_views": len(views),
                "view_names": [view[0] for view in views],
                "view_tests": view_tests
            }
    
    def test_similarity_functions(self) -> Dict[str, Any]:
        """Test custom similarity functions"""
        print("\n🔧 Testing Similarity Functions...")
        
        with self.engine.connect() as conn:
            # Check if functions exist
            functions = conn.execute(text("""
                SELECT proname, prosrc
                FROM pg_proc 
                WHERE proname IN ('find_similar_scars', 'find_related_geoids')
            """)).fetchall()
            
            function_tests = []
            
            # Test find_similar_scars function (with proper vector parameter)
            try:
                # Get a sample vector first
                sample_vector = conn.execute(text("""
                    SELECT scar_vector FROM scars 
                    WHERE scar_vector IS NOT NULL 
                    LIMIT 1
                """)).scalar()
                
                if sample_vector:
                    start_time = time.time()
                    similar_scars = conn.execute(text("""
                        SELECT scar_id, similarity, reason, delta_entropy
                        FROM find_similar_scars(:vector, 5)
                    """), {"vector": sample_vector}).fetchall()
                    similar_scars_time = time.time() - start_time
                    
                    function_tests.append({
                        "function": "find_similar_scars",
                        "time": similar_scars_time,
                        "results": len(similar_scars),
                        "status": "success"
                    })
                else:
                    function_tests.append({
                        "function": "find_similar_scars",
                        "status": "no_data",
                        "message": "No vectors available for testing"
                    })
            except Exception as e:
                function_tests.append({
                    "function": "find_similar_scars",
                    "status": "error",
                    "error": str(e)
                })
            
            # Test find_related_geoids function
            try:
                # Get a sample geoid
                sample_geoid = conn.execute(text("""
                    SELECT geoid_id FROM geoids 
                    WHERE semantic_vector IS NOT NULL 
                    LIMIT 1
                """)).scalar()
                
                if sample_geoid:
                    start_time = time.time()
                    related_geoids = conn.execute(text("""
                        SELECT geoid_id, similarity
                        FROM find_related_geoids(:geoid_id, 3)
                    """), {"geoid_id": sample_geoid}).fetchall()
                    related_geoids_time = time.time() - start_time
                    
                    function_tests.append({
                        "function": "find_related_geoids",
                        "time": related_geoids_time,
                        "results": len(related_geoids),
                        "status": "success"
                    })
                else:
                    function_tests.append({
                        "function": "find_related_geoids",
                        "status": "no_data",
                        "message": "No geoids available for testing"
                    })
            except Exception as e:
                function_tests.append({
                    "function": "find_related_geoids",
                    "status": "error",
                    "error": str(e)
                })
            
            return {
                "total_functions": len(functions),
                "function_names": [func[0] for func in functions],
                "function_tests": function_tests
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test Kimera API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        api_tests = []
        
        endpoints = [
            {"url": "/docs", "method": "GET", "name": "API Documentation"},
            {"url": "/system/health", "method": "GET", "name": "Health Check"},
            {"url": "/system/status", "method": "GET", "name": "System Status"},
            {"url": "/monitoring/status", "method": "GET", "name": "Monitoring Status"}
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{API_BASE_URL}{endpoint['url']}", timeout=10)
                response_time = time.time() - start_time
                
                api_tests.append({
                    "endpoint": endpoint["url"],
                    "name": endpoint["name"],
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "status": "success" if response.status_code == 200 else "error"
                })
            except Exception as e:
                api_tests.append({
                    "endpoint": endpoint["url"],
                    "name": endpoint["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return {"api_tests": api_tests}
    
    def test_data_integrity(self) -> Dict[str, Any]:
        """Test data integrity after optimizations"""
        print("\n🔒 Testing Data Integrity...")
        
        with self.engine.connect() as conn:
            # Count records in each table
            table_counts = {}
            tables = ["geoids", "scars", "insights", "multimodal_groundings", 
                     "causal_relationships", "enhanced_scars"]
            
            for table in tables:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    table_counts[table] = count
                except Exception as e:
                    table_counts[table] = f"Error: {e}"
            
            # Check for data consistency
            consistency_checks = []
            
            # Check SCAR-Geoid relationships
            scar_geoid_check = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_scars,
                    COUNT(CASE WHEN geoids IS NOT NULL THEN 1 END) as scars_with_geoids,
                    COUNT(CASE WHEN jsonb_typeof(geoids) = 'array' THEN 1 END) as scars_with_geoid_arrays
                FROM scars
            """)).fetchone()
            
            consistency_checks.append({
                "check": "scar_geoid_relationships",
                "total_scars": scar_geoid_check[0],
                "scars_with_geoids": scar_geoid_check[1],
                "scars_with_geoid_arrays": scar_geoid_check[2]
            })
            
            # Check vector dimensions
            vector_check = conn.execute(text("""
                SELECT 
                    'geoids' as table_name,
                    COUNT(*) as total_vectors,
                    COUNT(CASE WHEN array_length(semantic_vector, 1) = 1024 THEN 1 END) as correct_dimension_vectors
                FROM geoids
                WHERE semantic_vector IS NOT NULL
                UNION ALL
                SELECT 
                    'scars' as table_name,
                    COUNT(*) as total_vectors,
                    COUNT(CASE WHEN array_length(scar_vector, 1) = 1024 THEN 1 END) as correct_dimension_vectors
                FROM scars
                WHERE scar_vector IS NOT NULL
            """)).fetchall()
            
            consistency_checks.extend([
                {
                    "check": f"{row[0]}_vector_dimensions",
                    "total_vectors": row[1],
                    "correct_dimension_vectors": row[2]
                } for row in vector_check
            ])
            
            return {
                "table_counts": table_counts,
                "consistency_checks": consistency_checks
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and compile results"""
        print("🚀 Running Comprehensive Kimera SWM Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "database_connectivity": self.test_database_connectivity(),
            "schema_optimizations": self.test_schema_optimizations(),
            "vector_search": self.test_vector_search_performance(),
            "index_performance": self.test_index_performance(),
            "materialized_views": self.test_materialized_views(),
            "similarity_functions": self.test_similarity_functions(),
            "api_endpoints": self.test_api_endpoints(),
            "data_integrity": self.test_data_integrity()
        }
        
        total_time = time.time() - start_time
        test_results["total_test_time"] = total_time
        
        return test_results
    
    def analyze_results(self, results: Dict[str, Any]) -> None:
        """Analyze and display test results"""
        print(f"\n📊 Test Analysis Complete (Total time: {results['total_test_time']:.2f}s)")
        print("=" * 60)
        
        # Database connectivity
        db_conn = results["database_connectivity"]
        if db_conn["status"] == "success":
            print(f"✅ Database: PostgreSQL {db_conn['postgres_version']} with pgvector {db_conn['pgvector_version']}")
            print(f"   Database size: {db_conn['database_size']}")
        else:
            print(f"❌ Database connectivity failed: {db_conn.get('error', 'Unknown error')}")
        
        # Schema optimizations
        schema = results["schema_optimizations"]
        print(f"\n✅ Schema: {schema['jsonb_columns_count']} JSONB columns optimized")
        for op in schema["jsonb_operations"]:
            print(f"   {op['table']} {op['operation']}: {op['time']:.3f}s ({op['results']} results)")
        
        # Vector search
        vector = results["vector_search"]
        print(f"\n✅ Vector Search:")
        for coverage in vector["vector_coverage"]:
            print(f"   {coverage['table_name']}: {coverage['coverage_pct']}% coverage ({coverage['rows_with_vectors']}/{coverage['total_rows']})")
        for test in vector["similarity_tests"]:
            print(f"   {test['type']}: {test['time']:.3f}s (avg similarity: {test['avg_similarity']:.3f})")
        
        # Index performance
        index = results["index_performance"]
        print(f"\n✅ Indexes: {index['total_indexes']} indexes created")
        for test in index["performance_tests"]:
            print(f"   {test['index_type']}: {test['time']:.3f}s ({test['results']} results)")
        
        # Materialized views
        views = results["materialized_views"]
        print(f"\n✅ Views: {views['total_views']} materialized views")
        for test in views["view_tests"]:
            if test["status"] == "success":
                print(f"   {test['view']}: {test['time']:.3f}s ({test['results']} results)")
            else:
                print(f"   ❌ {test['view']}: {test.get('error', 'Failed')}")
        
        # Similarity functions
        functions = results["similarity_functions"]
        print(f"\n✅ Functions: {functions['total_functions']} similarity functions")
        for test in functions["function_tests"]:
            if test["status"] == "success":
                print(f"   {test['function']}: {test['time']:.3f}s ({test['results']} results)")
            else:
                print(f"   ⚠️  {test['function']}: {test.get('error', test.get('message', 'Failed'))}")
        
        # API endpoints
        api = results["api_endpoints"]
        print(f"\n✅ API Endpoints:")
        for test in api["api_tests"]:
            if test["status"] == "success":
                print(f"   {test['name']}: {test['status_code']} ({test['response_time']:.3f}s)")
            else:
                print(f"   ❌ {test['name']}: {test.get('error', 'Failed')}")
        
        # Data integrity
        integrity = results["data_integrity"]
        print(f"\n✅ Data Integrity:")
        for table, count in integrity["table_counts"].items():
            print(f"   {table}: {count} records")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment:")
        
        success_indicators = [
            db_conn["status"] == "success",
            schema["jsonb_columns_count"] > 0,
            len([t for t in vector["similarity_tests"] if t["results"] > 0]) > 0,
            index["total_indexes"] > 0,
            views["total_views"] > 0,
            len([t for t in api["api_tests"] if t["status"] == "success"]) > 0
        ]
        
        success_rate = sum(success_indicators) / len(success_indicators) * 100
        
        if success_rate >= 90:
            print(f"   🎉 EXCELLENT: {success_rate:.0f}% of systems operational")
        elif success_rate >= 75:
            print(f"   ✅ GOOD: {success_rate:.0f}% of systems operational")
        elif success_rate >= 50:
            print(f"   ⚠️  FAIR: {success_rate:.0f}% of systems operational")
        else:
            print(f"   ❌ POOR: {success_rate:.0f}% of systems operational")

def main():
    """Run comprehensive testing and analysis"""
    tester = KimeraSystemTester()
    
    try:
        # Run all tests
        results = tester.run_comprehensive_test()
        
        # Save results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Analyze and display results
        tester.analyze_results(results)
        
        print(f"\n📄 Detailed results saved to: comprehensive_test_results.json")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())