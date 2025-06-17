#!/usr/bin/env python3
"""
Synchronize existing SQLite data to Neo4j

This script reads all existing SCARs and Geoids from SQLite and 
creates corresponding nodes and relationships in Neo4j.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.graph.models import create_geoid, create_scar

def sync_sqlite_to_neo4j():
    """Sync all SQLite data to Neo4j"""
    print("🔄 Synchronizing SQLite data to Neo4j...")
    
    try:
        # Connect to SQLite
        conn = sqlite3.connect("kimera_swm.db")
        cursor = conn.cursor()
        
        # First, sync all Geoids
        print("\n📊 Syncing Geoids...")
        cursor.execute("""
            SELECT geoid_id, symbolic_state, metadata_json, semantic_state_json, semantic_vector
            FROM geoids
        """)
        
        geoids = cursor.fetchall()
        geoid_count = 0
        
        for geoid_id, symbolic_json, metadata_json, semantic_json, vector_json in geoids:
            try:
                # Parse JSON fields
                symbolic_state = json.loads(symbolic_json) if symbolic_json else {}
                metadata = json.loads(metadata_json) if metadata_json else {}
                semantic_state = json.loads(semantic_json) if semantic_json else {}
                semantic_vector = json.loads(vector_json) if vector_json else []
                
                # Create geoid properties
                props = {
                    "geoid_id": geoid_id,
                    "symbolic_state": symbolic_state,
                    "metadata": metadata,
                    "semantic_state": semantic_state,
                    "semantic_vector": semantic_vector[:10]  # Store only first 10 dims for Neo4j
                }
                
                # Create in Neo4j
                create_geoid(props)
                geoid_count += 1
                
                if geoid_count % 50 == 0:
                    print(f"   ✅ Synced {geoid_count} geoids...")
                    
            except Exception as e:
                print(f"   ❌ Error syncing geoid {geoid_id}: {e}")
        
        print(f"   ✅ Total Geoids synced: {geoid_count}")
        
        # Then, sync all SCARs
        print("\n📊 Syncing SCARs...")
        cursor.execute("""
            SELECT scar_id, geoids, reason, timestamp, resolved_by,
                   pre_entropy, post_entropy, delta_entropy, cls_angle,
                   semantic_polarity, mutation_frequency, weight, vault_id
            FROM scars
        """)
        
        scars = cursor.fetchall()
        scar_count = 0
        
        for scar in scars:
            try:
                scar_id, geoids_json, reason, timestamp, resolved_by, pre_e, post_e, delta_e, cls_angle, sem_pol, mut_freq, weight, vault_id = scar
                
                # Parse geoids
                geoids = json.loads(geoids_json) if geoids_json else []
                
                # Create scar properties
                props = {
                    "scar_id": scar_id,
                    "geoids": geoids,
                    "reason": reason,
                    "timestamp": timestamp,
                    "resolved_by": resolved_by,
                    "pre_entropy": pre_e,
                    "post_entropy": post_e,
                    "delta_entropy": delta_e,
                    "cls_angle": cls_angle,
                    "semantic_polarity": sem_pol,
                    "mutation_frequency": mut_freq,
                    "weight": weight,
                    "vault_id": vault_id
                }
                
                # Remove None values
                props = {k: v for k, v in props.items() if v is not None}
                
                # Create in Neo4j
                create_scar(props)
                scar_count += 1
                
                print(f"   ✅ Synced SCAR {scar_id} ({reason})")
                
            except Exception as e:
                print(f"   ❌ Error syncing scar {scar_id}: {e}")
        
        print(f"   ✅ Total SCARs synced: {scar_count}")
        
        conn.close()
        
        print("\n✅ Synchronization complete!")
        print(f"   Synced {geoid_count} Geoids and {scar_count} SCARs to Neo4j")
        
    except Exception as e:
        print(f"❌ Synchronization failed: {e}")
        return False
    
    return True

def verify_sync():
    """Verify the synchronization by checking Neo4j"""
    print("\n🔍 Verifying synchronization...")
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Count nodes
            result = session.run("""
                MATCH (g:Geoid) RETURN count(g) as geoid_count
            """)
            geoid_count = result.single()["geoid_count"]
            
            result = session.run("""
                MATCH (s:Scar) RETURN count(s) as scar_count
            """)
            scar_count = result.single()["scar_count"]
            
            result = session.run("""
                MATCH ()-[r:INVOLVES]->() RETURN count(r) as rel_count
            """)
            rel_count = result.single()["rel_count"]
            
            print(f"   📊 Neo4j now contains:")
            print(f"      Geoids: {geoid_count}")
            print(f"      SCARs: {scar_count}")
            print(f"      INVOLVES relationships: {rel_count}")
            
            # Show sample data
            print("\n   📌 Sample data in Neo4j:")
            result = session.run("""
                MATCH (s:Scar)-[:INVOLVES]->(g:Geoid)
                RETURN s.scar_id as scar, s.reason as reason, 
                       collect(g.geoid_id) as geoids
                LIMIT 3
            """)
            
            for record in result:
                print(f"      {record['scar']} ({record['reason']}) -> {record['geoids']}")
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

def main():
    """Main sync function"""
    print("🚀 KIMERA SQLite to Neo4j Synchronization")
    print("=" * 50)
    
    # Perform sync
    if sync_sqlite_to_neo4j():
        # Verify results
        verify_sync()
    
    print("\n✅ Process complete!")

if __name__ == "__main__":
    main()