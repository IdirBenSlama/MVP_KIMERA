#!/usr/bin/env python3
"""
Performance Benchmark for Optimized Kimera SWM
Tests system performance under various loads
"""

import os
import sys
import time
import json
import requests
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")
API_BASE_URL = "http://localhost:8001"

class PerformanceBenchmark:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30)
        self.results = {}
    
    def benchmark_database_queries(self, iterations: int = 100) -> dict:
        """Benchmark database query performance"""
        print(f"\n🔍 Benchmarking Database Queries ({iterations} iterations)...")
        
        query_benchmarks = {}
        
        # 1. JSONB queries
        print("   Testing JSONB queries...")
        times = []
        for i in range(iterations):
            with self.engine.connect() as conn:
                start_time = time.time()
                result = conn.execute(text("""
                    SELECT geoid_id, symbolic_state->'symbols' as symbols
                    FROM geoids 
                    WHERE symbolic_state ? 'symbols'
                    LIMIT 10
                """)).fetchall()
                times.append(time.time() - start_time)
        
        query_benchmarks['jsonb_query'] = {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        # 2. Vector similarity queries
        print("   Testing vector similarity queries...")
        times = []
        for i in range(min(iterations, 50)):  # Fewer iterations for expensive queries
            with self.engine.connect() as conn:
                start_time = time.time()
                result = conn.execute(text("""
                    SELECT s1.scar_id, s2.scar_id, 
                           1 - (s1.scar_vector <=> s2.scar_vector) as similarity
                    FROM scars s1, scars s2
                    WHERE s1.scar_vector IS NOT NULL 
                        AND s2.scar_vector IS NOT NULL
                        AND s1.scar_id < s2.scar_id
                    ORDER BY s1.scar_vector <=> s2.scar_vector
                    LIMIT 5
                """)).fetchall()
                times.append(time.time() - start_time)
        
        query_benchmarks['vector_similarity'] = {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': len(times)
        }
        
        # 3. Materialized view queries
        print("   Testing materialized view queries...")
        times = []
        for i in range(iterations):
            with self.engine.connect() as conn:
                start_time = time.time()
                result = conn.execute(text("""
                    SELECT * FROM mv_scar_patterns LIMIT 10
                """)).fetchall()
                times.append(time.time() - start_time)
        
        query_benchmarks['materialized_view'] = {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        # 4. Index-optimized queries
        print("   Testing index-optimized queries...")
        times = []
        for i in range(iterations):
            with self.engine.connect() as conn:
                start_time = time.time()
                result = conn.execute(text("""
                    SELECT scar_id, reason, timestamp 
                    FROM scars 
                    WHERE timestamp > NOW() - INTERVAL '365 days'
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)).fetchall()
                times.append(time.time() - start_time)
        
        query_benchmarks['indexed_query'] = {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }
        
        return query_benchmarks
    
    def benchmark_concurrent_queries(self, num_threads: int = 10, queries_per_thread: int = 20) -> dict:
        """Benchmark concurrent query performance"""
        print(f"\n⚡ Benchmarking Concurrent Queries ({num_threads} threads, {queries_per_thread} queries each)...")
        
        def run_concurrent_queries(thread_id: int) -> list:
            """Run queries in a single thread"""
            times = []
            with self.engine.connect() as conn:
                for i in range(queries_per_thread):
                    start_time = time.time()
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM scars WHERE weight > 0.5
                    """)).scalar()
                    times.append(time.time() - start_time)
            return times
        
        # Run concurrent queries
        all_times = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(run_concurrent_queries, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                thread_times = future.result()
                all_times.extend(thread_times)
        
        total_time = time.time() - start_time
        
        return {
            'total_queries': len(all_times),
            'total_time': total_time,
            'queries_per_second': len(all_times) / total_time,
            'avg_query_time': statistics.mean(all_times),
            'min_query_time': min(all_times),
            'max_query_time': max(all_times),
            'std_dev': statistics.stdev(all_times) if len(all_times) > 1 else 0
        }
    
    def benchmark_api_endpoints(self, iterations: int = 50) -> dict:
        """Benchmark API endpoint performance"""
        print(f"\n🌐 Benchmarking API Endpoints ({iterations} iterations)...")
        
        endpoints = [
            {"url": "/system/health", "name": "health"},
            {"url": "/system/status", "name": "status"},
            {"url": "/monitoring/status", "name": "monitoring"}
        ]
        
        api_benchmarks = {}
        
        for endpoint in endpoints:
            print(f"   Testing {endpoint['name']} endpoint...")
            times = []
            success_count = 0
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    response = requests.get(f"{API_BASE_URL}{endpoint['url']}", timeout=10)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        success_count += 1
                        times.append(response_time)
                except Exception:
                    pass
            
            if times:
                api_benchmarks[endpoint['name']] = {
                    'avg_time': statistics.mean(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                    'success_rate': success_count / iterations,
                    'iterations': iterations
                }
            else:
                api_benchmarks[endpoint['name']] = {
                    'error': 'No successful requests',
                    'success_rate': 0,
                    'iterations': iterations
                }
        
        return api_benchmarks
    
    def benchmark_geoid_creation(self, iterations: int = 20) -> dict:
        """Benchmark geoid creation performance"""
        print(f"\n🧬 Benchmarking Geoid Creation ({iterations} iterations)...")
        
        times = []
        success_count = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                # Create a test geoid via API
                response = requests.post(f"{API_BASE_URL}/geoids/create", 
                    json={
                        "symbols": [f"test_symbol_{i}"],
                        "metadata": {"test": True, "iteration": i}
                    },
                    timeout=30
                )
                
                creation_time = time.time() - start_time
                
                if response.status_code in [200, 201]:
                    success_count += 1
                    times.append(creation_time)
                    
            except Exception as e:
                print(f"   Warning: Geoid creation {i} failed: {e}")
        
        if times:
            return {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                'success_rate': success_count / iterations,
                'iterations': iterations
            }
        else:
            return {
                'error': 'No successful geoid creations',
                'success_rate': 0,
                'iterations': iterations
            }
    
    def benchmark_memory_usage(self) -> dict:
        """Check memory usage patterns"""
        print("\n💾 Analyzing Memory Usage...")
        
        with self.engine.connect() as conn:
            # Database memory usage
            db_stats = conn.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT setting FROM pg_settings WHERE name = 'shared_buffers') as shared_buffers,
                    (SELECT setting FROM pg_settings WHERE name = 'effective_cache_size') as effective_cache_size
            """)).fetchone()
            
            # Table sizes
            table_sizes = conn.execute(text("""
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
                    pg_total_relation_size(tablename::regclass) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(tablename::regclass) DESC
            """)).fetchall()
            
            return {
                'database_size': db_stats[0],
                'active_connections': db_stats[1],
                'shared_buffers': db_stats[2],
                'effective_cache_size': db_stats[3],
                'table_sizes': [
                    {
                        'table': row[0],
                        'size': row[1],
                        'size_bytes': row[2]
                    } for row in table_sizes
                ]
            }
    
    def run_full_benchmark(self) -> dict:
        """Run complete performance benchmark suite"""
        print("🚀 Kimera SWM Performance Benchmark")
        print("=" * 50)
        
        start_time = time.time()
        
        benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'database_queries': self.benchmark_database_queries(100),
            'concurrent_queries': self.benchmark_concurrent_queries(10, 20),
            'api_endpoints': self.benchmark_api_endpoints(50),
            'geoid_creation': self.benchmark_geoid_creation(10),  # Fewer iterations for creation
            'memory_usage': self.benchmark_memory_usage()
        }
        
        total_time = time.time() - start_time
        benchmark_results['total_benchmark_time'] = total_time
        
        return benchmark_results
    
    def analyze_benchmark_results(self, results: dict) -> None:
        """Analyze and display benchmark results"""
        print(f"\n📊 Benchmark Analysis Complete (Total time: {results['total_benchmark_time']:.2f}s)")
        print("=" * 60)
        
        # Database query performance
        db_queries = results['database_queries']
        print("\n🔍 Database Query Performance:")
        for query_type, stats in db_queries.items():
            print(f"   {query_type}:")
            print(f"      Avg: {stats['avg_time']*1000:.1f}ms")
            print(f"      Range: {stats['min_time']*1000:.1f}ms - {stats['max_time']*1000:.1f}ms")
            print(f"      Std Dev: {stats['std_dev']*1000:.1f}ms")
        
        # Concurrent performance
        concurrent = results['concurrent_queries']
        print(f"\n⚡ Concurrent Query Performance:")
        print(f"   Queries per second: {concurrent['queries_per_second']:.1f}")
        print(f"   Average query time: {concurrent['avg_query_time']*1000:.1f}ms")
        print(f"   Total queries: {concurrent['total_queries']}")
        
        # API performance
        api_results = results['api_endpoints']
        print(f"\n🌐 API Endpoint Performance:")
        for endpoint, stats in api_results.items():
            if 'error' not in stats:
                print(f"   {endpoint}: {stats['avg_time']*1000:.1f}ms (success: {stats['success_rate']*100:.1f}%)")
            else:
                print(f"   {endpoint}: {stats['error']}")
        
        # Geoid creation
        geoid_creation = results['geoid_creation']
        print(f"\n🧬 Geoid Creation Performance:")
        if 'error' not in geoid_creation:
            print(f"   Average time: {geoid_creation['avg_time']:.2f}s")
            print(f"   Success rate: {geoid_creation['success_rate']*100:.1f}%")
        else:
            print(f"   {geoid_creation['error']}")
        
        # Memory usage
        memory = results['memory_usage']
        print(f"\n💾 Memory Usage:")
        print(f"   Database size: {memory['database_size']}")
        print(f"   Active connections: {memory['active_connections']}")
        print(f"   Largest tables:")
        for table in memory['table_sizes'][:5]:
            print(f"      {table['table']}: {table['size']}")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        
        # Calculate performance scores
        jsonb_score = "EXCELLENT" if db_queries['jsonb_query']['avg_time'] < 0.01 else "GOOD" if db_queries['jsonb_query']['avg_time'] < 0.05 else "FAIR"
        vector_score = "EXCELLENT" if db_queries['vector_similarity']['avg_time'] < 0.1 else "GOOD" if db_queries['vector_similarity']['avg_time'] < 0.5 else "FAIR"
        concurrent_score = "EXCELLENT" if concurrent['queries_per_second'] > 100 else "GOOD" if concurrent['queries_per_second'] > 50 else "FAIR"
        
        print(f"   JSONB Queries: {jsonb_score} ({db_queries['jsonb_query']['avg_time']*1000:.1f}ms avg)")
        print(f"   Vector Search: {vector_score} ({db_queries['vector_similarity']['avg_time']*1000:.1f}ms avg)")
        print(f"   Concurrency: {concurrent_score} ({concurrent['queries_per_second']:.1f} QPS)")
        
        # Overall system health
        api_health = sum(1 for stats in api_results.values() if 'error' not in stats and stats.get('success_rate', 0) > 0.9)
        total_apis = len(api_results)
        
        if api_health == total_apis and jsonb_score in ["EXCELLENT", "GOOD"] and vector_score in ["EXCELLENT", "GOOD"]:
            print(f"\n🎉 OVERALL: SYSTEM PERFORMING EXCELLENTLY")
        elif api_health >= total_apis * 0.8:
            print(f"\n✅ OVERALL: SYSTEM PERFORMING WELL")
        else:
            print(f"\n⚠️  OVERALL: SYSTEM NEEDS ATTENTION")

def main():
    """Run performance benchmark"""
    benchmark = PerformanceBenchmark()
    
    try:
        # Run benchmarks
        results = benchmark.run_full_benchmark()
        
        # Save results
        with open("performance_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        # Analyze results
        benchmark.analyze_benchmark_results(results)
        
        print(f"\n📄 Detailed results saved to: performance_benchmark_results.json")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())