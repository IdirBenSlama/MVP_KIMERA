#!/usr/bin/env python3
"""
Validation Script for Kimera SWM Optimizations
Ensures all optimizations are properly implemented and functioning
"""

import os
import sys
import json
import time
from datetime import datetime
from sqlalchemy import create_engine, text
from typing import Dict, List, Tuple, Any
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")
API_BASE_URL = "http://localhost:8001"

class OptimizationValidator:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.validation_results = {}
        self.passed_tests = 0
        self.total_tests = 0
        
    def validate_database_setup(self) -> Dict[str, Any]:
        """Validate database configuration and extensions"""
        print("\n🔍 Validating Database Setup...")
        results = {}
        
        with self.engine.connect() as conn:
            # Check PostgreSQL version
            version = conn.execute(text("SELECT version()")).scalar()
            pg_version = version.split()[1] if version else "Unknown"
            results['postgresql_version'] = {
                'value': pg_version,
                'status': 'PASS' if pg_version.startswith(('15', '16')) else 'WARN',
                'message': f'PostgreSQL {pg_version}'
            }
            self._update_test_count(results['postgresql_version']['status'] == 'PASS')
            
            # Check required extensions
            extensions = ['vector', 'pg_trgm', 'uuid-ossp']
            for ext in extensions:
                ext_version = conn.execute(text(f"""
                    SELECT extversion FROM pg_extension WHERE extname = '{ext}'
                """)).scalar()
                
                results[f'extension_{ext}'] = {
                    'value': ext_version or 'Not installed',
                    'status': 'PASS' if ext_version else 'FAIL',
                    'message': f'{ext} extension: {ext_version or "Not installed"}'
                }
                self._update_test_count(ext_version is not None)
            
            # Check database size
            db_size = conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)).scalar()
            results['database_size'] = {
                'value': db_size,
                'status': 'PASS',
                'message': f'Database size: {db_size}'
            }
            self._update_test_count(True)
            
        return results
    
    def validate_schema_optimizations(self) -> Dict[str, Any]:
        """Validate JSONB conversions and schema improvements"""
        print("\n🔍 Validating Schema Optimizations...")
        results = {}
        
        with self.engine.connect() as conn:
            # Check JSONB columns
            jsonb_count = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE data_type = 'jsonb' AND table_schema = 'public'
            """)).scalar()
            
            results['jsonb_columns'] = {
                'value': jsonb_count,
                'status': 'PASS' if jsonb_count >= 15 else 'FAIL',
                'message': f'{jsonb_count} JSONB columns (expected ≥15)'
            }
            self._update_test_count(jsonb_count >= 15)
            
            # Test JSONB query performance
            start_time = time.time()
            result = conn.execute(text("""
                SELECT COUNT(*) FROM geoids WHERE symbolic_state ? 'symbols'
            """)).scalar()
            query_time = time.time() - start_time
            
            results['jsonb_query_performance'] = {
                'value': f'{query_time*1000:.1f}ms',
                'status': 'PASS' if query_time < 0.01 else 'WARN',
                'message': f'JSONB query time: {query_time*1000:.1f}ms'
            }
            self._update_test_count(query_time < 0.01)
            
            # Check vector columns
            vector_tables = conn.execute(text("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE data_type = 'USER-DEFINED' 
                AND udt_name = 'vector'
                AND table_schema = 'public'
            """)).fetchall()
            
            results['vector_columns'] = {
                'value': len(vector_tables),
                'status': 'PASS' if len(vector_tables) >= 2 else 'FAIL',
                'message': f'{len(vector_tables)} vector columns found'
            }
            self._update_test_count(len(vector_tables) >= 2)
            
        return results
    
    def validate_indexes(self) -> Dict[str, Any]:
        """Validate index creation and usage"""
        print("\n🔍 Validating Indexes...")
        results = {}
        
        with self.engine.connect() as conn:
            # Count custom indexes
            index_count = conn.execute(text("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
            """)).scalar()
            
            results['custom_indexes'] = {
                'value': index_count,
                'status': 'PASS' if index_count >= 15 else 'WARN',
                'message': f'{index_count} custom indexes (expected ≥15)'
            }
            self._update_test_count(index_count >= 15)
            
            # Check specific index types
            index_types = {
                'gin': "indexdef LIKE '%USING gin%'",
                'ivfflat': "indexdef LIKE '%USING ivfflat%'",
                'btree': "indexdef LIKE '%USING btree%' OR indexdef NOT LIKE '%USING%'"
            }
            
            for idx_type, condition in index_types.items():
                count = conn.execute(text(f"""
                    SELECT COUNT(*) FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND {condition}
                """)).scalar()
                
                results[f'{idx_type}_indexes'] = {
                    'value': count,
                    'status': 'PASS' if count > 0 else 'FAIL',
                    'message': f'{count} {idx_type} indexes'
                }
                self._update_test_count(count > 0)
            
        return results
    
    def validate_vector_search(self) -> Dict[str, Any]:
        """Validate vector search functionality"""
        print("\n🔍 Validating Vector Search...")
        results = {}
        
        with self.engine.connect() as conn:
            # Check vector coverage
            for table, column in [('geoids', 'semantic_vector'), ('scars', 'scar_vector')]:
                coverage = conn.execute(text(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT({column}) as with_vectors,
                        ROUND(COUNT({column}) * 100.0 / NULLIF(COUNT(*), 0), 1) as coverage_pct
                    FROM {table}
                """)).fetchone()
                
                results[f'{table}_vector_coverage'] = {
                    'value': f'{coverage[2]}%',
                    'status': 'PASS' if coverage[2] >= 90 else 'WARN',
                    'message': f'{table}: {coverage[1]}/{coverage[0]} vectors ({coverage[2]}%)'
                }
                self._update_test_count(coverage[2] >= 90)
            
            # Test vector similarity query
            start_time = time.time()
            similar = conn.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT s1.scar_id, s2.scar_id
                    FROM scars s1, scars s2
                    WHERE s1.scar_vector IS NOT NULL 
                        AND s2.scar_vector IS NOT NULL
                        AND s1.scar_id < s2.scar_id
                    ORDER BY s1.scar_vector <=> s2.scar_vector
                    LIMIT 5
                ) t
            """)).scalar()
            vector_time = time.time() - start_time
            
            results['vector_similarity_performance'] = {
                'value': f'{vector_time:.2f}s',
                'status': 'PASS' if vector_time < 3 else 'WARN',
                'message': f'Vector similarity query: {vector_time:.2f}s'
            }
            self._update_test_count(vector_time < 3)
            
        return results
    
    def validate_materialized_views(self) -> Dict[str, Any]:
        """Validate materialized views"""
        print("\n🔍 Validating Materialized Views...")
        results = {}
        
        with self.engine.connect() as conn:
            # Check materialized views exist
            views = conn.execute(text("""
                SELECT matviewname 
                FROM pg_matviews 
                WHERE schemaname = 'public'
            """)).fetchall()
            
            results['materialized_views'] = {
                'value': len(views),
                'status': 'PASS' if len(views) >= 2 else 'FAIL',
                'message': f'{len(views)} materialized views'
            }
            self._update_test_count(len(views) >= 2)
            
            # Test view performance
            for view in views:
                view_name = view[0]
                try:
                    start_time = time.time()
                    conn.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar()
                    query_time = time.time() - start_time
                    
                    results[f'view_{view_name}'] = {
                        'value': f'{query_time*1000:.1f}ms',
                        'status': 'PASS' if query_time < 0.01 else 'WARN',
                        'message': f'{view_name} query: {query_time*1000:.1f}ms'
                    }
                    self._update_test_count(query_time < 0.01)
                except Exception as e:
                    results[f'view_{view_name}'] = {
                        'value': 'Error',
                        'status': 'FAIL',
                        'message': str(e)
                    }
                    self._update_test_count(False)
            
        return results
    
    def validate_functions(self) -> Dict[str, Any]:
        """Validate custom functions"""
        print("\n🔍 Validating Functions...")
        results = {}
        
        with self.engine.connect() as conn:
            # Check similarity functions
            functions = ['find_similar_scars', 'find_related_geoids']
            for func in functions:
                exists = conn.execute(text(f"""
                    SELECT COUNT(*) FROM pg_proc WHERE proname = '{func}'
                """)).scalar()
                
                results[f'function_{func}'] = {
                    'value': 'Exists' if exists else 'Missing',
                    'status': 'PASS' if exists else 'FAIL',
                    'message': f'{func}: {"Exists" if exists else "Missing"}'
                }
                self._update_test_count(exists > 0)
            
        return results
    
    def validate_performance(self) -> Dict[str, Any]:
        """Validate overall performance metrics"""
        print("\n🔍 Validating Performance...")
        results = {}
        
        with self.engine.connect() as conn:
            # Test concurrent query performance
            import concurrent.futures
            
            def run_query():
                with self.engine.connect() as conn:
                    return conn.execute(text("SELECT COUNT(*) FROM scars WHERE weight > 0.5")).scalar()
            
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(run_query) for _ in range(50)]
                results_list = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
            qps = len(results_list) / total_time
            
            results['concurrent_performance'] = {
                'value': f'{qps:.1f} QPS',
                'status': 'PASS' if qps > 100 else 'WARN',
                'message': f'Concurrent queries: {qps:.1f} queries/second'
            }
            self._update_test_count(qps > 100)
            
            # Check cache hit ratio
            cache_stats = conn.execute(text("""
                SELECT 
                    sum(heap_blks_hit)::float / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 as cache_hit_ratio
                FROM pg_statio_user_tables
            """)).scalar()
            
            results['cache_hit_ratio'] = {
                'value': f'{cache_stats:.1f}%' if cache_stats else 'N/A',
                'status': 'PASS' if cache_stats and cache_stats > 90 else 'WARN',
                'message': f'Cache hit ratio: {cache_stats:.1f}%' if cache_stats else 'No cache stats'
            }
            self._update_test_count(cache_stats and cache_stats > 90)
            
        return results
    
    def validate_api_integration(self) -> Dict[str, Any]:
        """Validate API integration"""
        print("\n🔍 Validating API Integration...")
        results = {}
        
        endpoints = [
            '/system/health',
            '/system/status',
            '/monitoring/status'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                results[f'api_{endpoint}'] = {
                    'value': response.status_code,
                    'status': 'PASS' if response.status_code == 200 else 'FAIL',
                    'message': f'{endpoint}: {response.status_code}'
                }
                self._update_test_count(response.status_code == 200)
            except Exception as e:
                results[f'api_{endpoint}'] = {
                    'value': 'Error',
                    'status': 'FAIL',
                    'message': f'{endpoint}: {str(e)}'
                }
                self._update_test_count(False)
        
        return results
    
    def _update_test_count(self, passed: bool):
        """Update test counters"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        print("\n" + "="*60)
        print("KIMERA SWM OPTIMIZATION VALIDATION REPORT")
        print("="*60)
        
        # Run all validations
        validations = {
            'database_setup': self.validate_database_setup(),
            'schema_optimizations': self.validate_schema_optimizations(),
            'indexes': self.validate_indexes(),
            'vector_search': self.validate_vector_search(),
            'materialized_views': self.validate_materialized_views(),
            'functions': self.validate_functions(),
            'performance': self.validate_performance(),
            'api_integration': self.validate_api_integration()
        }
        
        # Display results
        for category, results in validations.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            for test, result in results.items():
                status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'WARN' else "❌"
                print(f"  {status_icon} {result['message']}")
        
        # Overall summary
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "="*60)
        print(f"OVERALL VALIDATION RESULTS:")
        print(f"  Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print(f"  Status: 🎉 EXCELLENT - All optimizations working properly")
        elif success_rate >= 75:
            print(f"  Status: ✅ GOOD - Most optimizations working")
        elif success_rate >= 50:
            print(f"  Status: ⚠️  FAIR - Some optimizations need attention")
        else:
            print(f"  Status: ❌ POOR - Significant issues detected")
        
        print("="*60)
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'validations': validations,
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'success_rate': success_rate,
                'status': 'EXCELLENT' if success_rate >= 90 else 'GOOD' if success_rate >= 75 else 'FAIR' if success_rate >= 50 else 'POOR'
            }
        }
        
        with open('optimization_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: optimization_validation_report.json")
        
        return report

def main():
    """Run optimization validation"""
    validator = OptimizationValidator()
    
    try:
        report = validator.generate_report()
        
        # Return appropriate exit code
        if report['summary']['success_rate'] >= 90:
            return 0
        elif report['summary']['success_rate'] >= 75:
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 3

if __name__ == "__main__":
    exit(main())