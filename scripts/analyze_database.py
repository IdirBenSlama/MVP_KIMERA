#!/usr/bin/env python3
"""
Database Analysis Script for Kimera SWM

Analyzes both SQLite and Neo4j databases to provide comprehensive insights
into the system's data structure, content, and relationships.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_sqlite_database(db_path: str = "kimera_swm.db") -> Dict[str, Any]:
    """Analyze the SQLite database structure and content"""
    print(f"🔍 Analyzing SQLite Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return {}
    
    analysis = {
        "file_info": {},
        "tables": {},
        "data_summary": {},
        "relationships": {},
        "performance_metrics": {}
    }
    
    # File information
    file_stats = os.stat(db_path)
    analysis["file_info"] = {
        "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
        "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
        "accessed": datetime.fromtimestamp(file_stats.st_atime).isoformat()
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
        
        for table in tables:
            print(f"\n🔍 Analyzing table: {table}")
            
            # Table schema
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            # Row count
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cursor.fetchone()[0]
            
            # Sample data
            cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
            sample_rows = cursor.fetchall()
            
            analysis["tables"][table] = {
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3], "primary_key": bool(col[5])} for col in columns],
                "row_count": row_count,
                "sample_data": sample_rows[:3] if sample_rows else []
            }
            
            print(f"   📈 Rows: {row_count}")
            print(f"   📋 Columns: {len(columns)}")
            
            # Specific analysis for key tables
            if table == "scars":
                analyze_scars_table(cursor, analysis)
            elif table == "geoids":
                analyze_geoids_table(cursor, analysis)
            elif table == "insights":
                analyze_insights_table(cursor, analysis)
        
        # Database-wide statistics
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index';")
        index_count = cursor.fetchone()[0]
        
        analysis["performance_metrics"] = {
            "total_tables": len(tables),
            "total_indexes": index_count,
            "database_size_mb": analysis["file_info"]["size_mb"]
        }
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing SQLite database: {e}")
        analysis["error"] = str(e)
    
    return analysis

def analyze_scars_table(cursor, analysis: Dict[str, Any]):
    """Detailed analysis of the SCARs table"""
    print("   🔍 SCAR Analysis:")
    
    # Vault distribution
    cursor.execute("SELECT vault_id, COUNT(*) FROM scars GROUP BY vault_id;")
    vault_dist = dict(cursor.fetchall())
    print(f"      🏦 Vault distribution: {vault_dist}")
    
    # Entropy statistics
    cursor.execute("SELECT AVG(pre_entropy), AVG(post_entropy), AVG(delta_entropy) FROM scars WHERE pre_entropy IS NOT NULL;")
    entropy_stats = cursor.fetchone()
    if entropy_stats[0]:
        print(f"      📊 Avg entropy - Pre: {entropy_stats[0]:.3f}, Post: {entropy_stats[1]:.3f}, Delta: {entropy_stats[2]:.3f}")
    
    # Recent activity
    cursor.execute("SELECT COUNT(*) FROM scars WHERE timestamp > datetime('now', '-24 hours');")
    recent_scars = cursor.fetchone()[0]
    print(f"      ⏰ Recent SCARs (24h): {recent_scars}")
    
    # Resolution methods
    cursor.execute("SELECT resolved_by, COUNT(*) FROM scars GROUP BY resolved_by LIMIT 5;")
    resolution_methods = dict(cursor.fetchall())
    print(f"      🔧 Top resolution methods: {resolution_methods}")
    
    analysis["data_summary"]["scars"] = {
        "vault_distribution": vault_dist,
        "entropy_stats": {
            "avg_pre_entropy": entropy_stats[0] if entropy_stats[0] else None,
            "avg_post_entropy": entropy_stats[1] if entropy_stats[1] else None,
            "avg_delta_entropy": entropy_stats[2] if entropy_stats[2] else None
        },
        "recent_activity": recent_scars,
        "resolution_methods": resolution_methods
    }

def analyze_geoids_table(cursor, analysis: Dict[str, Any]):
    """Detailed analysis of the Geoids table"""
    print("   🔍 Geoid Analysis:")
    
    # Vector dimensions analysis
    cursor.execute("SELECT semantic_vector FROM geoids WHERE semantic_vector IS NOT NULL LIMIT 1;")
    sample_vector = cursor.fetchone()
    if sample_vector and sample_vector[0]:
        try:
            vector_data = json.loads(sample_vector[0])
            if isinstance(vector_data, list):
                print(f"      📐 Vector dimensions: {len(vector_data)}")
                analysis["data_summary"]["geoids"] = {
                    "vector_dimensions": len(vector_data)
                }
        except:
            print("      📐 Vector format: Non-JSON or invalid")
    
    # Metadata analysis
    cursor.execute("SELECT metadata_json FROM geoids WHERE metadata_json IS NOT NULL LIMIT 5;")
    metadata_samples = cursor.fetchall()
    metadata_keys = set()
    for sample in metadata_samples:
        try:
            metadata = json.loads(sample[0])
            metadata_keys.update(metadata.keys())
        except:
            continue
    
    if metadata_keys:
        print(f"      🏷️ Common metadata keys: {list(metadata_keys)[:10]}")

def analyze_insights_table(cursor, analysis: Dict[str, Any]):
    """Detailed analysis of the Insights table"""
    print("   🔍 Insights Analysis:")
    
    # Insight types
    cursor.execute("SELECT insight_type, COUNT(*) FROM insights GROUP BY insight_type;")
    insight_types = dict(cursor.fetchall())
    print(f"      🧠 Insight types: {insight_types}")
    
    # Status distribution
    cursor.execute("SELECT status, COUNT(*) FROM insights GROUP BY status;")
    status_dist = dict(cursor.fetchall())
    print(f"      📊 Status distribution: {status_dist}")
    
    # Confidence scores
    cursor.execute("SELECT AVG(confidence), MIN(confidence), MAX(confidence) FROM insights WHERE confidence IS NOT NULL;")
    confidence_stats = cursor.fetchone()
    if confidence_stats[0]:
        print(f"      🎯 Confidence - Avg: {confidence_stats[0]:.3f}, Min: {confidence_stats[1]:.3f}, Max: {confidence_stats[2]:.3f}")
    
    analysis["data_summary"]["insights"] = {
        "insight_types": insight_types,
        "status_distribution": status_dist,
        "confidence_stats": {
            "avg": confidence_stats[0] if confidence_stats[0] else None,
            "min": confidence_stats[1] if confidence_stats[1] else None,
            "max": confidence_stats[2] if confidence_stats[2] else None
        }
    }

def analyze_neo4j_database() -> Dict[str, Any]:
    """Analyze Neo4j database if available"""
    print("\n🕸️ Analyzing Neo4j Database:")
    
    try:
        # Check if Neo4j modules are available
        from backend.graph.session import get_session, driver_liveness_check
        
        if not driver_liveness_check():
            print("❌ Neo4j database not available or not responding")
            return {"status": "unavailable", "reason": "not_responding"}
        
        analysis = {
            "status": "available",
            "nodes": {},
            "relationships": {},
            "constraints": [],
            "indexes": []
        }
        
        with get_session() as session:
            # Node counts by label
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
            node_counts = {}
            for record in result:
                labels = record["labels"]
                count = record["count"]
                if labels:
                    label = labels[0]  # Take first label
                    node_counts[label] = count
            
            analysis["nodes"] = node_counts
            print(f"   📊 Node counts: {node_counts}")
            
            # Relationship counts
            result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
            rel_counts = {}
            for record in result:
                rel_counts[record["rel_type"]] = record["count"]
            
            analysis["relationships"] = rel_counts
            print(f"   🔗 Relationship counts: {rel_counts}")
            
            # Constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record.data() for record in result]
            analysis["constraints"] = constraints
            print(f"   🔒 Constraints: {len(constraints)}")
            
            # Indexes
            result = session.run("SHOW INDEXES")
            indexes = [record.data() for record in result]
            analysis["indexes"] = indexes
            print(f"   📇 Indexes: {len(indexes)}")
            
            # Sample data
            if "Geoid" in node_counts:
                result = session.run("MATCH (g:Geoid) RETURN g LIMIT 3")
                sample_geoids = [record["g"] for record in result]
                analysis["sample_geoids"] = sample_geoids
                print(f"   🔍 Sample Geoids: {len(sample_geoids)}")
            
            if "Scar" in node_counts:
                result = session.run("MATCH (s:Scar) RETURN s LIMIT 3")
                sample_scars = [record["s"] for record in result]
                analysis["sample_scars"] = sample_scars
                print(f"   🔍 Sample SCARs: {len(sample_scars)}")
        
        return analysis
        
    except ImportError:
        print("❌ Neo4j modules not available")
        return {"status": "unavailable", "reason": "modules_not_found"}
    except Exception as e:
        print(f"❌ Error analyzing Neo4j: {e}")
        return {"status": "error", "reason": str(e)}

def generate_report(sqlite_analysis: Dict[str, Any], neo4j_analysis: Dict[str, Any]):
    """Generate a comprehensive database analysis report"""
    print("\n" + "="*70)
    print("📋 KIMERA SWM DATABASE ANALYSIS REPORT")
    print("="*70)
    
    # SQLite Summary
    print("\n🗄️ SQLite Database Summary:")
    if sqlite_analysis:
        file_info = sqlite_analysis.get("file_info", {})
        print(f"   📁 Size: {file_info.get('size_mb', 'Unknown')} MB")
        print(f"   📅 Last Modified: {file_info.get('modified', 'Unknown')}")
        
        tables = sqlite_analysis.get("tables", {})
        total_rows = sum(table.get("row_count", 0) for table in tables.values())
        print(f"   📊 Tables: {len(tables)}, Total Rows: {total_rows}")
        
        for table_name, table_info in tables.items():
            print(f"      • {table_name}: {table_info.get('row_count', 0)} rows")
    
    # Neo4j Summary
    print("\n🕸️ Neo4j Database Summary:")
    if neo4j_analysis.get("status") == "available":
        nodes = neo4j_analysis.get("nodes", {})
        relationships = neo4j_analysis.get("relationships", {})
        total_nodes = sum(nodes.values())
        total_rels = sum(relationships.values())
        
        print(f"   📊 Nodes: {total_nodes}, Relationships: {total_rels}")
        for label, count in nodes.items():
            print(f"      • {label}: {count} nodes")
        for rel_type, count in relationships.items():
            print(f"      • {rel_type}: {count} relationships")
    else:
        status = neo4j_analysis.get("status", "unknown")
        reason = neo4j_analysis.get("reason", "unknown")
        print(f"   ❌ Status: {status} ({reason})")
    
    # Data Quality Assessment
    print("\n🎯 Data Quality Assessment:")
    if sqlite_analysis:
        scars_data = sqlite_analysis.get("data_summary", {}).get("scars", {})
        if scars_data:
            vault_dist = scars_data.get("vault_distribution", {})
            if vault_dist:
                print(f"   🏦 Vault Balance: {vault_dist}")
            
            entropy_stats = scars_data.get("entropy_stats", {})
            if entropy_stats.get("avg_delta_entropy"):
                delta = entropy_stats["avg_delta_entropy"]
                trend = "decreasing" if delta < 0 else "increasing"
                print(f"   📈 Entropy Trend: {trend} (avg Δ: {delta:.3f})")
        
        geoids_data = sqlite_analysis.get("data_summary", {}).get("geoids", {})
        if geoids_data and geoids_data.get("vector_dimensions"):
            print(f"   📐 Vector Dimensions: {geoids_data['vector_dimensions']}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if sqlite_analysis:
        file_size = sqlite_analysis.get("file_info", {}).get("size_mb", 0)
        if file_size > 100:
            print("   ⚠️ Large database size - consider archiving old data")
        
        tables = sqlite_analysis.get("tables", {})
        scar_count = tables.get("scars", {}).get("row_count", 0)
        geoid_count = tables.get("geoids", {}).get("row_count", 0)
        
        if scar_count > geoid_count * 2:
            print("   ⚠️ High SCAR to Geoid ratio - system may be experiencing conflicts")
        
        if scar_count > 10000:
            print("   💡 Consider implementing SCAR archiving for performance")
    
    if neo4j_analysis.get("status") != "available":
        print("   💡 Enable Neo4j for enhanced semantic relationship analysis")
    
    print("\n✅ Analysis Complete!")
    
    # Save detailed report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "sqlite_analysis": sqlite_analysis,
        "neo4j_analysis": neo4j_analysis
    }
    
    with open("database_analysis_report.json", "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print("💾 Detailed report saved to: database_analysis_report.json")

def main():
    """Main analysis function"""
    print("🚀 KIMERA SWM Database Analysis")
    print("="*50)
    
    # Analyze SQLite database
    sqlite_analysis = analyze_sqlite_database()
    
    # Analyze Neo4j database
    neo4j_analysis = analyze_neo4j_database()
    
    # Generate comprehensive report
    generate_report(sqlite_analysis, neo4j_analysis)

if __name__ == "__main__":
    main()