#!/usr/bin/env python3
"""
Database Maintenance and Monitoring for Kimera SWM
Automated maintenance tasks and performance monitoring
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from typing import Dict, List, Any
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")

class DatabaseMaintenance:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for maintenance tasks"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kimera_maintenance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def refresh_materialized_views(self) -> Dict[str, bool]:
        """Refresh all materialized views"""
        self.logger.info("Refreshing materialized views...")
        
        views = ["mv_scar_patterns", "mv_geoid_complexity"]
        results = {}
        
        with self.engine.connect() as conn:
            for view in views:
                try:
                    start_time = time.time()
                    conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                    duration = time.time() - start_time
                    results[view] = True
                    self.logger.info(f"Refreshed {view} in {duration:.2f}s")
                except Exception as e:
                    results[view] = False
                    self.logger.error(f"Failed to refresh {view}: {e}")
            conn.commit()
        
        return results
    
    def update_table_statistics(self) -> Dict[str, Any]:
        """Update table statistics for query optimization"""
        self.logger.info("Updating table statistics...")
        
        tables = ["geoids", "scars", "insights", "multimodal_groundings", 
                 "causal_relationships", "enhanced_scars"]
        
        stats = {}
        
        with self.engine.connect() as conn:
            for table in tables:
                try:
                    # Get table size and row count
                    size_result = conn.execute(text(f"""
                        SELECT 
                            pg_size_pretty(pg_total_relation_size('{table}')) as size,
                            pg_total_relation_size('{table}') as size_bytes,
                            (SELECT COUNT(*) FROM {table}) as row_count
                    """)).fetchone()
                    
                    # Update statistics
                    conn.execute(text(f"ANALYZE {table}"))
                    
                    stats[table] = {
                        "size": size_result[0],
                        "size_bytes": size_result[1],
                        "row_count": size_result[2]
                    }
                    
                    self.logger.info(f"Updated stats for {table}: {size_result[2]} rows, {size_result[0]}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to update stats for {table}: {e}")
                    stats[table] = {"error": str(e)}
        
        return stats
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old temporary data"""
        self.logger.info(f"Cleaning up data older than {days_old} days...")
        
        cleanup_results = {}
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self.engine.connect() as conn:
            # Clean up old sync queue entries
            try:
                result = conn.execute(text("""
                    DELETE FROM neo4j_sync_queue 
                    WHERE processed = true AND created_at < :cutoff_date
                """), {"cutoff_date": cutoff_date})
                cleanup_results["neo4j_sync_queue"] = result.rowcount
                self.logger.info(f"Cleaned up {result.rowcount} old sync queue entries")
            except Exception as e:
                self.logger.error(f"Failed to clean sync queue: {e}")
                cleanup_results["neo4j_sync_queue"] = 0
            
            # Clean up old cluster data
            try:
                result = conn.execute(text("""
                    DELETE FROM geoid_clusters 
                    WHERE created_at < :cutoff_date
                """), {"cutoff_date": cutoff_date})
                cleanup_results["geoid_clusters"] = result.rowcount
                
                result = conn.execute(text("""
                    DELETE FROM scar_clusters 
                    WHERE created_at < :cutoff_date
                """), {"cutoff_date": cutoff_date})
                cleanup_results["scar_clusters"] = result.rowcount
                
                self.logger.info(f"Cleaned up old cluster data")
            except Exception as e:
                self.logger.error(f"Failed to clean cluster data: {e}")
            
            conn.commit()
        
        return cleanup_results
    
    def monitor_query_performance(self) -> Dict[str, Any]:
        """Monitor slow queries and performance metrics"""
        self.logger.info("Monitoring query performance...")
        
        with self.engine.connect() as conn:
            # Get slow queries (if pg_stat_statements is enabled)
            try:
                slow_queries = conn.execute(text("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > 100
                    ORDER BY mean_exec_time DESC
                    LIMIT 10
                """)).fetchall()
                
                slow_query_data = [dict(row._mapping) for row in slow_queries]
            except Exception:
                # pg_stat_statements not available
                slow_query_data = []
            
            # Get database size and connection info
            db_stats = conn.execute(text("""
                SELECT 
                    pg_database_size(current_database()) as db_size_bytes,
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections
            """)).fetchone()
            
            # Get index usage statistics
            index_stats = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE idx_scan > 0
                ORDER BY idx_scan DESC
                LIMIT 20
            """)).fetchall()
            
        return {
            "slow_queries": slow_query_data,
            "database_stats": dict(db_stats._mapping),
            "index_usage": [dict(row._mapping) for row in index_stats]
        }
    
    def check_vector_index_health(self) -> Dict[str, Any]:
        """Check the health of vector indexes"""
        self.logger.info("Checking vector index health...")
        
        with self.engine.connect() as conn:
            # Check index sizes and usage
            vector_indexes = conn.execute(text("""
                SELECT 
                    indexname,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size,
                    idx_scan,
                    idx_tup_read
                FROM pg_stat_user_indexes 
                WHERE indexname LIKE '%vector%'
            """)).fetchall()
            
            # Check for null vectors
            null_vectors = conn.execute(text("""
                SELECT 
                    'geoids' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(semantic_vector) as rows_with_vectors,
                    COUNT(*) - COUNT(semantic_vector) as null_vectors
                FROM geoids
                UNION ALL
                SELECT 
                    'scars' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(scar_vector) as rows_with_vectors,
                    COUNT(*) - COUNT(scar_vector) as null_vectors
                FROM scars
            """)).fetchall()
            
        return {
            "vector_indexes": [dict(row._mapping) for row in vector_indexes],
            "null_vector_stats": [dict(row._mapping) for row in null_vectors]
        }
    
    def optimize_database_settings(self) -> Dict[str, Any]:
        """Optimize database settings based on current usage"""
        self.logger.info("Optimizing database settings...")
        
        with self.engine.connect() as conn:
            # Get current settings
            current_settings = conn.execute(text("""
                SELECT name, setting, unit, context
                FROM pg_settings 
                WHERE name IN (
                    'shared_buffers', 'effective_cache_size', 'work_mem',
                    'maintenance_work_mem', 'max_connections'
                )
            """)).fetchall()
            
            # Get database size for optimization calculations
            db_size = conn.execute(text("""
                SELECT pg_database_size(current_database()) as size_bytes
            """)).scalar()
            
            # Calculate recommended settings (simplified)
            recommendations = {}
            
            # Shared buffers: 25% of RAM (assuming 4GB available)
            recommendations['shared_buffers'] = '1GB'
            
            # Effective cache size: 75% of RAM
            recommendations['effective_cache_size'] = '3GB'
            
            # Work mem: based on max_connections and available memory
            recommendations['work_mem'] = '16MB'
            
            # Maintenance work mem: for VACUUM, CREATE INDEX
            recommendations['maintenance_work_mem'] = '256MB'
            
        return {
            "current_settings": [dict(row._mapping) for row in current_settings],
            "recommendations": recommendations,
            "database_size_bytes": db_size
        }
    
    def generate_maintenance_report(self) -> Dict[str, Any]:
        """Generate comprehensive maintenance report"""
        self.logger.info("Generating maintenance report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "materialized_views": self.refresh_materialized_views(),
            "table_statistics": self.update_table_statistics(),
            "cleanup_results": self.cleanup_old_data(),
            "performance_monitoring": self.monitor_query_performance(),
            "vector_index_health": self.check_vector_index_health(),
            "optimization_recommendations": self.optimize_database_settings()
        }
        
        return report
    
    def run_maintenance_cycle(self) -> None:
        """Run a complete maintenance cycle"""
        self.logger.info("Starting maintenance cycle...")
        
        start_time = time.time()
        
        try:
            report = self.generate_maintenance_report()
            
            # Save report
            report_filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            duration = time.time() - start_time
            self.logger.info(f"Maintenance cycle completed in {duration:.2f}s")
            self.logger.info(f"Report saved to {report_filename}")
            
            # Print summary
            print(f"\n📊 Maintenance Summary:")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Views refreshed: {sum(report['materialized_views'].values())}")
            print(f"   Tables analyzed: {len(report['table_statistics'])}")
            print(f"   Records cleaned: {sum(report['cleanup_results'].values())}")
            print(f"   Active connections: {report['performance_monitoring']['database_stats']['active_connections']}")
            print(f"   Database size: {report['performance_monitoring']['database_stats']['db_size']}")
            
        except Exception as e:
            self.logger.error(f"Maintenance cycle failed: {e}")
            raise

def main():
    """Run database maintenance"""
    print("🔧 Kimera Database Maintenance")
    print("=" * 40)
    
    maintenance = DatabaseMaintenance()
    maintenance.run_maintenance_cycle()
    
    print("\n✅ Maintenance complete!")

if __name__ == "__main__":
    main()