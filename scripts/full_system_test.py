#!/usr/bin/env python3
"""
Full System Test for Kimera SWM
Tests the entire system end-to-end with all optimizations
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from sqlalchemy import create_engine, text
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")

def get_api_base_url():
    """Reads the port from .port.tmp to build the API URL."""
    try:
        with open(".port.tmp", "r") as f:
            port = int(f.read().strip())
        print(f"🔗 Connecting to API server on port {port}")
        return f"http://localhost:{port}"
    except (IOError, ValueError):
        print("⚠️ Could not read .port.tmp, defaulting to port 8001. This may fail.")
        return "http://localhost:8001"

API_BASE_URL = get_api_base_url()

class FullSystemTest:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "performance_metrics": {},
            "errors": []
        }
        
    def test_database_operations(self):
        """Test all database operations with optimizations"""
        print("\n🔍 Testing Database Operations...")
        
        results = {}
        
        with self.engine.connect() as conn:
            # 1. Test JSONB operations
            print("   Testing JSONB queries...")
            start = time.time()
            jsonb_result = conn.execute(text("""
                SELECT geoid_id, symbolic_state->'symbols' as symbols,
                       jsonb_array_length(COALESCE(symbolic_state->'symbols', '[]'::jsonb)) as symbol_count
                FROM geoids 
                WHERE symbolic_state ? 'symbols'
                LIMIT 5
            """)).fetchall()
            jsonb_time = time.time() - start
            results['jsonb_query'] = {
                'time': jsonb_time,
                'rows': len(jsonb_result),
                'status': 'PASS' if jsonb_time < 0.01 else 'WARN'
            }
            print(f"      ✅ JSONB query: {jsonb_time*1000:.1f}ms ({len(jsonb_result)} rows)")
            
            # 2. Test Vector similarity search
            print("   Testing vector similarity search...")
            start = time.time()
            vector_result = conn.execute(text("""
                SELECT s1.scar_id, s2.scar_id, 
                       1 - (s1.scar_vector <=> s2.scar_vector) as similarity
                FROM scars s1, scars s2
                WHERE s1.scar_vector IS NOT NULL 
                    AND s2.scar_vector IS NOT NULL
                    AND s1.scar_id < s2.scar_id
                ORDER BY s1.scar_vector <=> s2.scar_vector
                LIMIT 10
            """)).fetchall()
            vector_time = time.time() - start
            results['vector_similarity'] = {
                'time': vector_time,
                'rows': len(vector_result),
                'avg_similarity': np.mean([row[2] for row in vector_result]) if vector_result else 0,
                'status': 'PASS' if vector_time < 2 else 'WARN'
            }
            print(f"      ✅ Vector similarity: {vector_time:.2f}s ({len(vector_result)} pairs)")
            
            # 3. Test Materialized Views
            print("   Testing materialized views...")
            for view in ['mv_scar_patterns', 'mv_geoid_complexity']:
                start = time.time()
                view_result = conn.execute(text(f"SELECT COUNT(*) FROM {view}")).scalar()
                view_time = time.time() - start
                results[f'view_{view}'] = {
                    'time': view_time,
                    'rows': view_result,
                    'status': 'PASS' if view_time < 0.01 else 'WARN'
                }
                print(f"      ✅ {view}: {view_time*1000:.1f}ms ({view_result} rows)")
            
            # 4. Test custom functions
            print("   Testing similarity functions...")
            # Get a sample vector for testing
            sample_vector = conn.execute(text("""
                SELECT scar_vector FROM scars 
                WHERE scar_vector IS NOT NULL 
                LIMIT 1
            """)).scalar()
            
            if sample_vector:
                start = time.time()
                func_result = conn.execute(text("""
                    SELECT scar_id, similarity, reason 
                    FROM find_similar_scars(:vector, 5)
                """), {"vector": sample_vector}).fetchall()
                func_time = time.time() - start
                results['similarity_function'] = {
                    'time': func_time,
                    'results': len(func_result),
                    'status': 'PASS'
                }
                print(f"      ✅ find_similar_scars(): {func_time:.2f}s ({len(func_result)} results)")
            
        self.test_results['tests']['database'] = results
        return results
    
    def test_api_operations(self):
        """Test API endpoints and operations"""
        print("\n🌐 Testing API Operations...")
        
        results = {}
        
        # 1. Health checks
        print("   Testing health endpoints...")
        # Test the new fast health check
        try:
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/system/health", timeout=3)
            api_time = time.time() - start
            results['/system/health'] = {
                'status_code': response.status_code,
                'time': api_time,
                'status': 'PASS' if response.status_code == 200 else 'FAIL'
            }
            print(f"      ✅ /system/health: {response.status_code} ({api_time*1000:.0f}ms)")
        except Exception as e:
            results['/system/health'] = {'status': 'FAIL', 'error': str(e)}
            print(f"      ❌ /system/health: {str(e)[:50]}")
            
        # Test the original detailed health check and other status endpoints
        for endpoint in ['/system/health/detailed', '/system/status', '/monitoring/status']:
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=20)
                api_time = time.time() - start
                results[endpoint] = {
                    'status_code': response.status_code,
                    'time': api_time,
                    'status': 'PASS' if response.status_code == 200 else 'FAIL'
                }
                print(f"      ✅ {endpoint}: {response.status_code} ({api_time*1000:.0f}ms)")
            except Exception as e:
                results[endpoint] = {'status': 'FAIL', 'error': str(e)}
                print(f"      ❌ {endpoint}: {str(e)[:50]}")
        
        # 2. Create a test geoid
        print("   Testing geoid creation...")
        try:
            start = time.time()
            geoid_data = {
                "semantic_features": {
                    "test_feature_1": 0.8,
                    "test_feature_2": 0.6,
                    "optimization_test": 1.0
                },
                "metadata": {
                    "test_type": "full_system_test",
                    "timestamp": datetime.now().isoformat()
                }
            }
            response = requests.post(f"{API_BASE_URL}/geoids", json=geoid_data, timeout=10)
            create_time = time.time() - start
            
            if response.status_code in [200, 201]:
                geoid_id = response.json().get('geoid_id')
                results['geoid_creation'] = {
                    'status': 'PASS',
                    'time': create_time,
                    'geoid_id': geoid_id
                }
                print(f"      ✅ Geoid created: {geoid_id} ({create_time:.2f}s)")
                
                # 3. Test contradiction processing
                print("   Testing contradiction processing...")
                try:
                    geoid_id_to_test = results.get('geoid_creation', {}).get('geoid_id', 'GEOID_prototype_001')
                    start = time.time()
                    response = requests.post(f"{API_BASE_URL}/process/contradictions", json={'trigger_geoid_id': geoid_id_to_test, 'search_limit': 5}, timeout=30)
                    api_time = time.time() - start
                    
                    results['contradiction_processing'] = {
                        'status_code': response.status_code,
                        'time': api_time
                    }

                    if response.status_code == 202:
                        results['contradiction_processing']['status'] = 'PASS'
                        print(f"      ✅ Contradiction processing task started: {response.status_code} ({api_time*1000:.0f}ms)")
                    else:
                        results['contradiction_processing']['status'] = 'FAIL'
                        error_details = "No details in response."
                        try:
                            error_details = response.json()
                        except:
                            pass
                        results['contradiction_processing']['error'] = error_details
                        print(f"      ❌ Contradiction processing failed to start: {response.status_code} ({api_time*1000:.0f}ms) - {error_details}")

                except Exception as e:
                    results['contradiction_processing'] = {'status': 'FAIL', 'error': str(e)}
                    print(f"      ❌ Contradiction processing: {str(e)}")
                
        except Exception as e:
            results['api_operations'] = {'status': 'FAIL', 'error': str(e)}
            self.test_results['errors'].append(f"API operation error: {str(e)}")
        
        self.test_results['tests']['api'] = results
        return results
    
    def test_concurrent_load(self):
        """Test system under concurrent load"""
        print("\n⚡ Testing Concurrent Load...")
        
        import concurrent.futures
        
        results = {}
        
        # Database concurrent queries
        print("   Testing concurrent database queries...")
        def db_query():
            with self.engine.connect() as conn:
                start = time.time()
                conn.execute(text("SELECT COUNT(*) FROM scars WHERE weight > 0.5")).scalar()
                return time.time() - start
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(db_query) for _ in range(100)]
            query_times = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        qps = len(query_times) / total_time
        
        results['database_concurrent'] = {
            'queries': len(query_times),
            'total_time': total_time,
            'qps': qps,
            'avg_query_time': np.mean(query_times),
            'status': 'PASS' if qps > 500 else 'WARN'
        }
        print(f"      ✅ Database: {qps:.1f} queries/second")
        
        # API concurrent requests
        print("   Testing concurrent API requests...")
        def api_request():
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/system/health", timeout=5)
                return time.time() - start, response.status_code == 200
            except:
                return None, False
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(api_request) for _ in range(50)]
            api_results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in api_results if r[1]]
        total_time = time.time() - start_time
        
        results['api_concurrent'] = {
            'requests': len(api_results),
            'successful': len(successful_requests),
            'total_time': total_time,
            'rps': len(successful_requests) / total_time if total_time > 0 else 0,
            'status': 'PASS' if len(successful_requests) > len(api_results) * 0.9 else 'WARN'
        }
        print(f"      ✅ API: {len(successful_requests)}/{len(api_results)} successful ({len(successful_requests)/total_time:.1f} req/s)")
        
        self.test_results['tests']['concurrent'] = results
        return results
    
    def test_data_integrity(self):
        """Verify data integrity after optimizations"""
        print("\n🔒 Testing Data Integrity...")
        
        results = {}
        
        with self.engine.connect() as conn:
            # Check vector dimensions
            print("   Checking vector dimensions...")
            vector_check = conn.execute(text("""
                SELECT 
                    'geoids' as table_name,
                    COUNT(*) as total,
                    COUNT(CASE WHEN vector_dims(semantic_vector) = 1024 THEN 1 END) as correct_dim,
                    COUNT(CASE WHEN semantic_vector IS NULL THEN 1 END) as null_vectors
                FROM geoids
                UNION ALL
                SELECT 
                    'scars' as table_name,
                    COUNT(*) as total,
                    COUNT(CASE WHEN vector_dims(scar_vector) = 1024 THEN 1 END) as correct_dim,
                    COUNT(CASE WHEN scar_vector IS NULL THEN 1 END) as null_vectors
                FROM scars
            """)).fetchall()
            
            for row in vector_check:
                table, total, correct, nulls = row
                results[f'{table}_vectors'] = {
                    'total': total,
                    'correct_dimension': correct,
                    'null_vectors': nulls,
                    'status': 'PASS' if nulls == 0 and correct == total else 'WARN'
                }
                print(f"      ✅ {table}: {correct}/{total} correct dimensions, {nulls} nulls")
            
            # Check JSONB validity
            print("   Checking JSONB data integrity...")
            jsonb_check = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_geoids,
                    COUNT(CASE WHEN jsonb_typeof(symbolic_state) = 'object' THEN 1 END) as valid_symbolic,
                    COUNT(CASE WHEN jsonb_typeof(metadata_json) = 'object' THEN 1 END) as valid_metadata
                FROM geoids
            """)).fetchone()
            
            results['jsonb_integrity'] = {
                'total': jsonb_check[0],
                'valid_symbolic': jsonb_check[1],
                'valid_metadata': jsonb_check[2],
                'status': 'PASS' if jsonb_check[1] == jsonb_check[0] else 'WARN'
            }
            print(f"      ✅ JSONB: {jsonb_check[1]}/{jsonb_check[0]} valid symbolic states")
            
        self.test_results['tests']['integrity'] = results
        return results
    
    def calculate_performance_metrics(self):
        """Calculate overall performance metrics"""
        print("\n📊 Calculating Performance Metrics...")
        
        metrics = {
            'database_performance': 'EXCELLENT',
            'api_performance': 'EXCELLENT',
            'concurrent_performance': 'EXCELLENT',
            'data_integrity': 'EXCELLENT',
            'overall': 'EXCELLENT'
        }
        
        # Analyze test results
        all_tests = []
        for category, tests in self.test_results['tests'].items():
            for test_name, test_result in tests.items():
                if isinstance(test_result, dict) and 'status' in test_result:
                    all_tests.append(test_result['status'])
        
        pass_rate = all_tests.count('PASS') / len(all_tests) if all_tests else 0
        
        if pass_rate >= 0.95:
            metrics['overall'] = 'EXCELLENT'
        elif pass_rate >= 0.8:
            metrics['overall'] = 'GOOD'
        elif pass_rate >= 0.6:
            metrics['overall'] = 'FAIR'
        else:
            metrics['overall'] = 'NEEDS ATTENTION'
        
        self.test_results['performance_metrics'] = metrics
        self.test_results['pass_rate'] = pass_rate
        
        return metrics
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("KIMERA SWM FULL SYSTEM TEST REPORT")
        print("="*60)
        
        # Summary
        metrics = self.test_results.get('performance_metrics', {})
        pass_rate = self.test_results.get('pass_rate', 0)
        
        print(f"\n📈 Overall Assessment: {metrics.get('overall', 'UNKNOWN')}")
        print(f"   Pass Rate: {pass_rate*100:.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        
        # Database tests
        if 'database' in self.test_results['tests']:
            print("\n   Database Operations:")
            db_tests = self.test_results['tests']['database']
            for test, result in db_tests.items():
                if isinstance(result, dict) and 'status' in result:
                    status_icon = "✅" if result['status'] == 'PASS' else "⚠️"
                    time_str = f"{result.get('time', 0)*1000:.1f}ms" if result.get('time', 0) < 1 else f"{result.get('time', 0):.2f}s"
                    print(f"      {status_icon} {test}: {time_str}")
        
        # API tests
        if 'api' in self.test_results['tests']:
            print("\n   API Operations:")
            api_tests = self.test_results['tests']['api']
            for test, result in api_tests.items():
                if isinstance(result, dict) and 'status' in result:
                    status_icon = "✅" if result['status'] == 'PASS' else "❌"
                    print(f"      {status_icon} {test}: {result.get('status', 'UNKNOWN')}")
        
        # Concurrent tests
        if 'concurrent' in self.test_results['tests']:
            print("\n   Concurrent Performance:")
            concurrent = self.test_results['tests']['concurrent']
            if 'database_concurrent' in concurrent:
                db_conc = concurrent['database_concurrent']
                print(f"      ✅ Database: {db_conc.get('qps', 0):.1f} QPS")
            if 'api_concurrent' in concurrent:
                api_conc = concurrent['api_concurrent']
                print(f"      ✅ API: {api_conc.get('successful', 0)}/{api_conc.get('requests', 0)} successful")
        
        # Save detailed report
        report_file = f"full_system_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Final verdict
        print("\n" + "="*60)
        if metrics.get('overall') == 'EXCELLENT':
            print("🎉 SYSTEM TEST PASSED - All optimizations working perfectly!")
        elif metrics.get('overall') == 'GOOD':
            print("✅ SYSTEM TEST PASSED - Minor issues detected")
        else:
            print("⚠️  SYSTEM TEST COMPLETED - Issues need attention")
        print("="*60)
        
        return self.test_results

def main():
    """Run full system test"""
    print("🚀 Starting Kimera SWM Full System Test")
    print("This will test all optimizations and system components...\n")
    
    tester = FullSystemTest()
    
    try:
        # Run all tests
        tester.test_database_operations()
        tester.test_api_operations()
        tester.test_concurrent_load()
        tester.test_data_integrity()
        
        # Calculate metrics and generate report
        tester.calculate_performance_metrics()
        report = tester.generate_report()
        
        # Return appropriate exit code
        if report['performance_metrics']['overall'] == 'EXCELLENT':
            return 0
        elif report['performance_metrics']['overall'] == 'GOOD':
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit(main())