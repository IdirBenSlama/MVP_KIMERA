#!/usr/bin/env python3
"""
Detailed Vault Contents Inspector
=================================

This script provides detailed inspection of individual scars and their contents.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

def find_database() -> str:
    """Find the KIMERA database file"""
    possible_paths = [
        "kimera_swm.db",
        "data/kimera_swm.db", 
        "backend/kimera_swm.db"
    ]
    
    for path in possible_paths:
        full_path = os.path.join(ROOT_DIR, path)
        if os.path.exists(full_path):
            return full_path
    
    return os.path.join(ROOT_DIR, "kimera_swm.db")

def inspect_vault_contents():
    """Inspect detailed vault contents"""
    db_path = find_database()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    print("🔍 DETAILED VAULT CONTENTS INSPECTION")
    print("=" * 60)
    print(f"📁 Database: {db_path}")
    print(f"📊 Database Size: {os.path.getsize(db_path):,} bytes")
    print(f"🕐 Inspection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n🗂️  Available Tables: {', '.join(tables)}")
        
        # Inspect scars table
        if "scars" in tables:
            print(f"\n🏛️  SCARS TABLE ANALYSIS")
            print("-" * 40)
            
            # Get table schema
            cursor.execute("PRAGMA table_info(scars);")
            columns = cursor.fetchall()
            print(f"📋 Columns: {', '.join([col[1] for col in columns])}")
            
            # Get all scars
            cursor.execute("SELECT * FROM scars ORDER BY timestamp DESC;")
            scars = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"\n📊 Total Scars: {len(scars)}")
            
            if scars:
                print(f"\n🔍 DETAILED SCAR CONTENTS:")
                print("=" * 60)
                
                for i, scar_data in enumerate(scars, 1):
                    scar_dict = dict(zip(column_names, scar_data))
                    
                    print(f"\n🏷️  SCAR #{i}")
                    print("-" * 20)
                    print(f"ID: {scar_dict.get('scar_id', 'N/A')}")
                    print(f"Vault: {scar_dict.get('vault_id', 'N/A')}")
                    print(f"Reason: {scar_dict.get('reason', 'N/A')}")
                    print(f"Weight: {scar_dict.get('weight', 'N/A')}")
                    print(f"Timestamp: {scar_dict.get('timestamp', 'N/A')}")
                    print(f"Resolved By: {scar_dict.get('resolved_by', 'N/A')}")
                    
                    # Parse geoids if available
                    geoids_str = scar_dict.get('geoids', '')
                    if geoids_str:
                        try:
                            geoids = json.loads(geoids_str)
                            print(f"Geoids: {geoids}")
                        except:
                            print(f"Geoids (raw): {geoids_str}")
                    
                    # Show entropy metrics
                    pre_entropy = scar_dict.get('pre_entropy', 'N/A')
                    post_entropy = scar_dict.get('post_entropy', 'N/A')
                    delta_entropy = scar_dict.get('delta_entropy', 'N/A')
                    
                    print(f"Entropy - Pre: {pre_entropy}, Post: {post_entropy}, Delta: {delta_entropy}")
                    
                    # Show additional metrics
                    cls_angle = scar_dict.get('cls_angle', 'N/A')
                    semantic_polarity = scar_dict.get('semantic_polarity', 'N/A')
                    mutation_frequency = scar_dict.get('mutation_frequency', 'N/A')
                    
                    print(f"CLS Angle: {cls_angle}")
                    print(f"Semantic Polarity: {semantic_polarity}")
                    print(f"Mutation Frequency: {mutation_frequency}")
                    
                    # Show scar vector if available (truncated)
                    scar_vector = scar_dict.get('scar_vector', '')
                    if scar_vector:
                        try:
                            vector = json.loads(scar_vector)
                            if isinstance(vector, list) and len(vector) > 0:
                                print(f"Scar Vector: [{vector[0]:.4f}, {vector[1]:.4f}, ..., {vector[-1]:.4f}] (length: {len(vector)})")
                        except:
                            print(f"Scar Vector: {scar_vector[:100]}..." if len(scar_vector) > 100 else scar_vector)
        
        # Inspect geoids table
        if "geoids" in tables:
            print(f"\n🧠 GEOIDS TABLE ANALYSIS")
            print("-" * 40)
            
            cursor.execute("SELECT COUNT(*) FROM geoids;")
            geoid_count = cursor.fetchone()[0]
            print(f"📊 Total Geoids: {geoid_count}")
            
            if geoid_count > 0:
                # Get recent geoids
                cursor.execute("SELECT geoid_id, semantic_state, symbolic_state FROM geoids ORDER BY rowid DESC LIMIT 5;")
                recent_geoids = cursor.fetchall()
                
                print(f"\n🔍 RECENT GEOIDS (Last 5):")
                for i, (geoid_id, semantic_state, symbolic_state) in enumerate(recent_geoids, 1):
                    print(f"\n🏷️  GEOID #{i}")
                    print(f"ID: {geoid_id}")
                    
                    # Parse semantic state
                    try:
                        semantic = json.loads(semantic_state) if semantic_state else {}
                        print(f"Semantic Features: {list(semantic.keys())[:5]}..." if len(semantic) > 5 else f"Semantic Features: {list(semantic.keys())}")
                    except:
                        print(f"Semantic State (raw): {semantic_state[:100]}..." if semantic_state and len(semantic_state) > 100 else semantic_state)
                    
                    # Parse symbolic state
                    try:
                        symbolic = json.loads(symbolic_state) if symbolic_state else {}
                        print(f"Symbolic Content: {symbolic}")
                    except:
                        print(f"Symbolic State (raw): {symbolic_state[:100]}..." if symbolic_state and len(symbolic_state) > 100 else symbolic_state)
        
        # Vault distribution analysis
        if "scars" in tables:
            print(f"\n📊 VAULT DISTRIBUTION ANALYSIS")
            print("-" * 40)
            
            cursor.execute("SELECT vault_id, COUNT(*), SUM(weight), AVG(weight) FROM scars GROUP BY vault_id;")
            vault_stats = cursor.fetchall()
            
            for vault_id, count, total_weight, avg_weight in vault_stats:
                print(f"{vault_id.upper()}:")
                print(f"  Scars: {count}")
                print(f"  Total Weight: {total_weight:.2f}")
                print(f"  Average Weight: {avg_weight:.4f}")
            
            # Calculate balance
            if len(vault_stats) >= 2:
                vault_a_count = next((count for vault_id, count, _, _ in vault_stats if vault_id == "vault_a"), 0)
                vault_b_count = next((count for vault_id, count, _, _ in vault_stats if vault_id == "vault_b"), 0)
                imbalance = abs(vault_a_count - vault_b_count)
                
                print(f"\n⚖️  BALANCE ASSESSMENT:")
                print(f"Imbalance: {imbalance} scars")
                
                if imbalance == 0:
                    balance_quality = "PERFECT"
                elif imbalance <= 1:
                    balance_quality = "EXCELLENT"
                elif imbalance <= 5:
                    balance_quality = "GOOD"
                else:
                    balance_quality = "POOR"
                
                print(f"Quality: {balance_quality}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_vault_contents()