#!/usr/bin/env python3
"""
Analyze the Tyrannic Crash Test Database
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def analyze_database(db_path):
    """Analyze the structure and content of the test database."""
    print(f"🔍 DATABASE ANALYSIS - {os.path.basename(db_path)}")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
    print(f"📁 File size: {file_size:.2f} MB")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        print()
        
        # Analyze each table
        for table_name in [t[0] for t in tables]:
            print(f"📋 Table: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"   {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Total records: {count:,}")
            
            # Sample data analysis
            if count > 0:
                # Get first few rows
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    row_str = str(row)
                    if len(row_str) > 150:
                        row_str = row_str[:150] + "..."
                    print(f"   Row {i}: {row_str}")
                
                # Analyze specific tables
                if table_name == "scars":
                    analyze_scars_table(cursor)
                elif table_name == "geoids":
                    analyze_geoids_table(cursor)
                elif table_name == "insights":
                    analyze_insights_table(cursor)
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")

def analyze_scars_table(cursor):
    """Detailed analysis of the scars table."""
    print("\n🔬 SCARS TABLE ANALYSIS:")
    
    # Count by vault
    cursor.execute("SELECT vault_id, COUNT(*) FROM scars GROUP BY vault_id")
    vault_counts = cursor.fetchall()
    print("   Distribution by vault:")
    for vault, count in vault_counts:
        print(f"     {vault}: {count:,} scars")
    
    # Analyze weights
    cursor.execute("SELECT MIN(weight), MAX(weight), AVG(weight) FROM scars")
    weight_stats = cursor.fetchone()
    print(f"   Weight statistics: min={weight_stats[0]:.4f}, max={weight_stats[1]:.4f}, avg={weight_stats[2]:.4f}")
    
    # Recent entries
    cursor.execute("SELECT COUNT(*) FROM scars WHERE created_at > datetime('now', '-1 hour')")
    recent_count = cursor.fetchone()[0]
    print(f"   Recent entries (last hour): {recent_count:,}")

def analyze_geoids_table(cursor):
    """Detailed analysis of the geoids table."""
    print("\n🌍 GEOIDS TABLE ANALYSIS:")
    
    # Count total
    cursor.execute("SELECT COUNT(*) FROM geoids")
    total = cursor.fetchone()[0]
    print(f"   Total geoids: {total:,}")
    
    # Analyze semantic state
    cursor.execute("SELECT semantic_state_json FROM geoids LIMIT 1")
    sample_semantic = cursor.fetchone()
    if sample_semantic and sample_semantic[0]:
        try:
            semantic_data = json.loads(sample_semantic[0])
            if isinstance(semantic_data, dict):
                print(f"   Sample semantic features: {len(semantic_data)} features")
                print(f"   Sample feature keys: {list(semantic_data.keys())[:5]}...")
            else:
                print(f"   Semantic data type: {type(semantic_data)}")
        except Exception as e:
            print(f"   Could not parse semantic state: {e}")
    
    # Analyze symbolic state
    cursor.execute("SELECT symbolic_state FROM geoids LIMIT 1")
    sample_symbolic = cursor.fetchone()
    if sample_symbolic and sample_symbolic[0]:
        try:
            symbolic_data = json.loads(sample_symbolic[0])
            print(f"   Sample symbolic structure: {type(symbolic_data)}")
            if isinstance(symbolic_data, dict):
                print(f"   Symbolic keys: {list(symbolic_data.keys())[:3]}...")
        except Exception as e:
            print(f"   Could not parse symbolic state: {e}")
    
    # Analyze metadata
    cursor.execute("SELECT metadata_json FROM geoids LIMIT 1")
    sample_metadata = cursor.fetchone()
    if sample_metadata and sample_metadata[0]:
        try:
            metadata = json.loads(sample_metadata[0])
            if isinstance(metadata, dict):
                print(f"   Metadata fields: {list(metadata.keys())}")
        except Exception as e:
            print(f"   Could not parse metadata: {e}")

def analyze_insights_table(cursor):
    """Detailed analysis of the insights table."""
    print("\n💡 INSIGHTS TABLE ANALYSIS:")
    
    # Count by type
    cursor.execute("SELECT insight_type, COUNT(*) FROM insights GROUP BY insight_type")
    type_counts = cursor.fetchall()
    print("   Distribution by type:")
    for insight_type, count in type_counts:
        print(f"     {insight_type}: {count:,} insights")
    
    # Confidence statistics
    cursor.execute("SELECT MIN(confidence), MAX(confidence), AVG(confidence) FROM insights")
    conf_stats = cursor.fetchone()
    print(f"   Confidence statistics: min={conf_stats[0]:.4f}, max={conf_stats[1]:.4f}, avg={conf_stats[2]:.4f}")

def find_latest_database():
    """Find the most recent tyrannic crash test database."""
    # Look for databases in current directory and test_databases
    patterns = [
        "./tyrannic_crash_test_*.db",
        "./test_databases/tyrannic_crash_test_*.db"
    ]
    
    latest_db = None
    latest_time = 0
    
    for pattern in patterns:
        for db_path in Path(".").glob(pattern.replace("./", "")):
            if db_path.is_file():
                mtime = db_path.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime
                    latest_db = str(db_path)
    
    return latest_db

def main():
    # Find the latest database
    latest_db = find_latest_database()
    
    if latest_db:
        print(f"🎯 Analyzing latest database: {latest_db}")
        print(f"📅 Modified: {datetime.fromtimestamp(Path(latest_db).stat().st_mtime)}")
        print()
        analyze_database(latest_db)
    else:
        print("❌ No tyrannic crash test databases found")
        print("Available databases:")
        for db_file in Path(".").rglob("*.db"):
            print(f"   {db_file}")

if __name__ == "__main__":
    main()