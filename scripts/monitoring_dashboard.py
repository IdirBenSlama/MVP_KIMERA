#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Kimera SWM
Provides live system metrics and performance monitoring
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import threading
from typing import Dict, List, Any
import curses
from collections import deque

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")
API_BASE_URL = "http://localhost:8000"

class KimeraMonitoringDashboard:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.metrics_history = {
            'query_times': deque(maxlen=60),
            'api_response_times': deque(maxlen=60),
            'active_connections': deque(maxlen=60),
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60)
        }
        self.running = True
        self.last_update = datetime.now()
        
    def get_database_metrics(self) -> Dict[str, Any]:
        """Get current database metrics"""
        with self.engine.connect() as conn:
            # Database size and connections
            db_metrics = conn.execute(text("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    pg_size_pretty(pg_database_size(current_database())) as db_size_pretty,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT count(*) FROM pg_stat_activity) as total_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE wait_event IS NOT NULL) as waiting_connections
            """)).fetchone()
            
            # Query statistics
            query_stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(mean_exec_time) as avg_query_time,
                    MAX(mean_exec_time) as max_query_time,
                    SUM(calls) as total_calls
                FROM pg_stat_statements
                WHERE query NOT LIKE '%pg_stat%'
            """)).fetchone() if self._has_pg_stat_statements(conn) else None
            
            # Table statistics
            table_stats = conn.execute(text("""
                SELECT 
                    tablename,
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_analyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 5
            """)).fetchall()
            
            # Index usage
            index_stats = conn.execute(text("""
                SELECT 
                    indexrelname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE idx_scan > 0
                ORDER BY idx_scan DESC
                LIMIT 5
            """)).fetchall()
            
            # Vector statistics
            vector_stats = conn.execute(text("""
                SELECT 
                    'geoids' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(semantic_vector) as vectors,
                    AVG(array_length(semantic_vector, 1)) as avg_dimension
                FROM geoids
                UNION ALL
                SELECT 
                    'scars' as table_name,
                    COUNT(*) as total_rows,
                    COUNT(scar_vector) as vectors,
                    AVG(array_length(scar_vector, 1)) as avg_dimension
                FROM scars
            """)).fetchall()
            
            return {
                'database': {
                    'size': db_metrics[1],
                    'size_bytes': db_metrics[0],
                    'active_connections': db_metrics[2],
                    'total_connections': db_metrics[3],
                    'idle_connections': db_metrics[4],
                    'waiting_connections': db_metrics[5]
                },
                'queries': {
                    'total_queries': query_stats[0] if query_stats else 0,
                    'avg_query_time': float(query_stats[1]) if query_stats and query_stats[1] else 0,
                    'max_query_time': float(query_stats[2]) if query_stats and query_stats[2] else 0,
                    'total_calls': query_stats[3] if query_stats else 0
                } if query_stats else None,
                'tables': [
                    {
                        'name': row[0],
                        'row_count': row[1],
                        'dead_rows': row[2],
                        'last_vacuum': row[3].strftime('%Y-%m-%d %H:%M') if row[3] else 'Never',
                        'last_analyze': row[4].strftime('%Y-%m-%d %H:%M') if row[4] else 'Never'
                    } for row in table_stats
                ],
                'indexes': [
                    {
                        'name': row[0],
                        'scans': row[1],
                        'tuples_read': row[2],
                        'tuples_fetched': row[3]
                    } for row in index_stats
                ],
                'vectors': [
                    {
                        'table': row[0],
                        'total_rows': row[1],
                        'vectors': row[2],
                        'coverage': f"{(row[2]/row[1]*100):.1f}%" if row[1] > 0 else "0%",
                        'avg_dimension': int(row[3]) if row[3] else 0
                    } for row in vector_stats
                ]
            }
    
    def _has_pg_stat_statements(self, conn) -> bool:
        """Check if pg_stat_statements extension is available"""
        try:
            result = conn.execute(text("""
                SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
            """)).scalar()
            return result is not None
        except:
            return False
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get API metrics"""
        api_metrics = {
            'endpoints': [],
            'overall_health': 'Unknown'
        }
        
        endpoints = [
            {'name': 'Health', 'url': '/system/health'},
            {'name': 'Status', 'url': '/system/status'},
            {'name': 'Monitoring', 'url': '/monitoring/status'}
        ]
        
        healthy_count = 0
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{API_BASE_URL}{endpoint['url']}", timeout=5)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                endpoint_status = {
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': 'UP' if response.status_code == 200 else 'DOWN',
                    'response_time': f"{response_time:.1f}ms",
                    'status_code': response.status_code
                }
                
                if response.status_code == 200:
                    healthy_count += 1
                    
            except Exception as e:
                endpoint_status = {
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'status': 'ERROR',
                    'response_time': 'N/A',
                    'error': str(e)[:50]
                }
            
            api_metrics['endpoints'].append(endpoint_status)
        
        # Overall health assessment
        if healthy_count == len(endpoints):
            api_metrics['overall_health'] = 'HEALTHY'
        elif healthy_count > 0:
            api_metrics['overall_health'] = 'DEGRADED'
        else:
            api_metrics['overall_health'] = 'DOWN'
        
        return api_metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        with self.engine.connect() as conn:
            # Recent query performance
            recent_queries = []
            try:
                if self._has_pg_stat_statements(conn):
                    queries = conn.execute(text("""
                        SELECT 
                            query,
                            calls,
                            mean_exec_time,
                            total_exec_time
                        FROM pg_stat_statements
                        WHERE query NOT LIKE '%pg_stat%'
                        ORDER BY mean_exec_time DESC
                        LIMIT 5
                    """)).fetchall()
                    
                    recent_queries = [
                        {
                            'query': row[0][:50] + '...' if len(row[0]) > 50 else row[0],
                            'calls': row[1],
                            'avg_time': f"{row[2]:.1f}ms",
                            'total_time': f"{row[3]:.1f}ms"
                        } for row in queries
                    ]
            except:
                pass
            
            # Cache hit ratio
            cache_stats = conn.execute(text("""
                SELECT 
                    sum(heap_blks_read) as heap_read,
                    sum(heap_blks_hit) as heap_hit,
                    sum(idx_blks_read) as idx_read,
                    sum(idx_blks_hit) as idx_hit
                FROM pg_statio_user_tables
            """)).fetchone()
            
            heap_hit_ratio = 0
            idx_hit_ratio = 0
            
            if cache_stats[0] and cache_stats[1]:
                heap_total = cache_stats[0] + cache_stats[1]
                heap_hit_ratio = (cache_stats[1] / heap_total * 100) if heap_total > 0 else 0
            
            if cache_stats[2] and cache_stats[3]:
                idx_total = cache_stats[2] + cache_stats[3]
                idx_hit_ratio = (cache_stats[3] / idx_total * 100) if idx_total > 0 else 0
            
            return {
                'recent_queries': recent_queries,
                'cache_hit_ratios': {
                    'heap': f"{heap_hit_ratio:.1f}%",
                    'index': f"{idx_hit_ratio:.1f}%"
                }
            }
    
    def get_system_alerts(self) -> List[Dict[str, str]]:
        """Check for system alerts and warnings"""
        alerts = []
        
        with self.engine.connect() as conn:
            # Check for high connection count
            conn_count = conn.execute(text("""
                SELECT count(*) FROM pg_stat_activity
            """)).scalar()
            
            if conn_count > 150:
                alerts.append({
                    'level': 'WARNING',
                    'message': f'High connection count: {conn_count}/200',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            
            # Check for long-running queries
            long_queries = conn.execute(text("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active' 
                AND query_start < NOW() - INTERVAL '5 minutes'
            """)).scalar()
            
            if long_queries > 0:
                alerts.append({
                    'level': 'WARNING',
                    'message': f'{long_queries} long-running queries detected',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            
            # Check for table bloat
            bloated_tables = conn.execute(text("""
                SELECT tablename, n_dead_tup 
                FROM pg_stat_user_tables 
                WHERE n_dead_tup > n_live_tup * 0.2 
                AND n_live_tup > 1000
            """)).fetchall()
            
            for table, dead_rows in bloated_tables:
                alerts.append({
                    'level': 'INFO',
                    'message': f'Table {table} needs vacuum ({dead_rows} dead rows)',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        # Check API health
        try:
            response = requests.get(f"{API_BASE_URL}/system/health", timeout=2)
            if response.status_code != 200:
                alerts.append({
                    'level': 'ERROR',
                    'message': 'API health check failed',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        except:
            alerts.append({
                'level': 'ERROR',
                'message': 'API unreachable',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
        return alerts[-5:]  # Keep only last 5 alerts
    
    def format_dashboard(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for display"""
        dashboard = []
        
        # Header
        dashboard.append("=" * 80)
        dashboard.append(f"KIMERA SWM MONITORING DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard.append("=" * 80)
        
        # Database Metrics
        db = metrics['database']
        dashboard.append("\n📊 DATABASE METRICS")
        dashboard.append(f"Size: {db['database']['size']} | Connections: {db['database']['active_connections']}/{db['database']['total_connections']} (Active/Total)")
        dashboard.append(f"Idle: {db['database']['idle_connections']} | Waiting: {db['database']['waiting_connections']}")
        
        # API Status
        api = metrics['api']
        dashboard.append(f"\n🌐 API STATUS: {api['overall_health']}")
        for endpoint in api['endpoints']:
            status_icon = "✅" if endpoint['status'] == 'UP' else "❌"
            dashboard.append(f"{status_icon} {endpoint['name']}: {endpoint['status']} - {endpoint['response_time']}")
        
        # Performance Metrics
        perf = metrics['performance']
        dashboard.append("\n⚡ PERFORMANCE")
        dashboard.append(f"Cache Hit Ratios - Heap: {perf['cache_hit_ratios']['heap']} | Index: {perf['cache_hit_ratios']['index']}")
        
        # Vector Coverage
        dashboard.append("\n🔍 VECTOR SEARCH")
        for vec in db['vectors']:
            dashboard.append(f"{vec['table']}: {vec['vectors']}/{vec['total_rows']} vectors ({vec['coverage']})")
        
        # Top Tables
        dashboard.append("\n📋 TOP TABLES")
        for table in db['tables'][:3]:
            dashboard.append(f"{table['name']}: {table['row_count']:,} rows | Dead: {table['dead_rows']}")
        
        # Alerts
        if metrics['alerts']:
            dashboard.append("\n🚨 ALERTS")
            for alert in metrics['alerts']:
                icon = "❌" if alert['level'] == 'ERROR' else "⚠️" if alert['level'] == 'WARNING' else "ℹ️"
                dashboard.append(f"{icon} [{alert['timestamp']}] {alert['message']}")
        
        return "\n".join(dashboard)
    
    def run_dashboard(self):
        """Run the monitoring dashboard"""
        print("Starting Kimera SWM Monitoring Dashboard...")
        print("Press Ctrl+C to exit\n")
        
        try:
            while self.running:
                # Collect all metrics
                metrics = {
                    'database': self.get_database_metrics(),
                    'api': self.get_api_metrics(),
                    'performance': self.get_performance_metrics(),
                    'alerts': self.get_system_alerts()
                }
                
                # Clear screen and display dashboard
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self.format_dashboard(metrics))
                
                # Save metrics to file
                with open('monitoring_metrics.json', 'w') as f:
                    json.dump(metrics, f, indent=2, default=str)
                
                # Wait before next update
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring dashboard stopped.")
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Run the monitoring dashboard"""
    dashboard = KimeraMonitoringDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()