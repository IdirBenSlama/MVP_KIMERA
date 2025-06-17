#!/usr/bin/env python3
"""
Examine the contents of a tyrannic crash test database
"""
import sqlite3
import sys
import json
from datetime import datetime

def examine_database(db_path):
    print(f"\n=== Examining Database: {db_path} ===\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Tables found: {[t[0] for t in tables]}\n")
    
    for table in tables:
        table_name = table[0]
        print(f"\n--- Table: {table_name} ---")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Columns:", [col[1] for col in columns])
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        # Show sample data
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print(f"\nSample data (first 5 rows):")
            for i, row in enumerate(rows):
                print(f"  Row {i+1}: {row[:3]}..." if len(row) > 3 else f"  Row {i+1}: {row}")
        
        # Special handling for geoids table
        if table_name == 'geoids' and count > 0:
            # Get statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(LENGTH(semantic_state_json)) as avg_semantic_size,
                    AVG(LENGTH(symbolic_state)) as avg_symbolic_size,
                    AVG(LENGTH(metadata_json)) as avg_metadata_size
                FROM geoids
            """)
            stats = cursor.fetchone()
            print(f"\nGeoid Statistics:")
            print(f"  Total geoids: {stats[0]}")
            print(f"  Avg semantic state size: {stats[1]:.0f} bytes")
            print(f"  Avg symbolic state size: {stats[2]:.0f} bytes")
            print(f"  Avg metadata size: {stats[3]:.0f} bytes")
            
            # Check for patterns in metadata
            cursor.execute("SELECT metadata_json FROM geoids LIMIT 1")
            sample_metadata = cursor.fetchone()[0]
            if sample_metadata:
                try:
                    metadata = json.loads(sample_metadata)
                    print(f"\nSample metadata structure: {list(metadata.keys())}")
                except:
                    pass
    
    conn.close()

if __name__ == "__main__":
    # Get the most recent database
    import glob
    import os
    
    db_files = glob.glob("tyrannic_crash_test_*.db")
    if not db_files:
        print("No tyrannic crash test databases found!")
        sys.exit(1)
    
    # Sort by modification time
    db_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Examine the most recent one
    most_recent = db_files[0]
    examine_database(most_recent)
    
    print(f"\n\nOther databases found: {db_files[1:5]}")