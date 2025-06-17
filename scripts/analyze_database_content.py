#!/usr/bin/env python3
"""
Deep Database Content Analysis for Kimera SWM

This script performs a detailed analysis of the actual content stored in both
SQLite and Neo4j databases, providing insights into the semantic data,
relationships, and patterns.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, Any, List
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_sqlite_content(db_path: str = "kimera_swm.db") -> Dict[str, Any]:
    """Perform deep content analysis of SQLite database"""
    print(f"🔍 Deep Content Analysis of SQLite Database: {db_path}")
    
    analysis = {
        "scars": {},
        "geoids": {},
        "relationships": {},
        "patterns": {},
        "semantic_analysis": {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Analyze SCARs in detail
        print("\n📊 SCAR Content Analysis:")
        cursor.execute("""
            SELECT scar_id, geoids, reason, timestamp, resolved_by, 
                   pre_entropy, post_entropy, delta_entropy, vault_id,
                   cls_angle, semantic_polarity, mutation_frequency
            FROM scars
            ORDER BY timestamp DESC
        """)
        
        scars = cursor.fetchall()
        scar_reasons = Counter()
        resolution_methods = Counter()
        vault_distribution = Counter()
        entropy_changes = []
        
        print(f"   Total SCARs: {len(scars)}")
        
        for scar in scars:
            scar_id, geoids_json, reason, timestamp, resolved_by, pre_e, post_e, delta_e, vault_id, cls_angle, sem_pol, mut_freq = scar
            
            # Parse geoids
            try:
                geoids = json.loads(geoids_json) if geoids_json else []
            except:
                geoids = []
            
            scar_reasons[reason] += 1
            resolution_methods[resolved_by] += 1
            vault_distribution[vault_id] += 1
            
            if delta_e is not None:
                entropy_changes.append(delta_e)
            
            # Show recent SCARs
            if len(analysis["scars"]) < 3:
                analysis["scars"][scar_id] = {
                    "reason": reason,
                    "timestamp": timestamp,
                    "resolved_by": resolved_by,
                    "geoids": geoids,
                    "entropy_change": delta_e,
                    "vault": vault_id,
                    "cls_angle": cls_angle,
                    "semantic_polarity": sem_pol
                }
                print(f"\n   📌 {scar_id}:")
                print(f"      Reason: {reason}")
                print(f"      Time: {timestamp}")
                print(f"      Vault: {vault_id}")
                print(f"      Entropy Δ: {delta_e:.3f}" if delta_e else "      Entropy Δ: N/A")
                print(f"      Geoids involved: {len(geoids)}")
        
        print(f"\n   📈 SCAR Statistics:")
        print(f"      Reasons: {dict(scar_reasons)}")
        print(f"      Resolution Methods: {dict(resolution_methods)}")
        print(f"      Vault Distribution: {dict(vault_distribution)}")
        if entropy_changes:
            print(f"      Average Entropy Change: {np.mean(entropy_changes):.3f}")
        
        # Analyze Geoids in detail
        print("\n\n📊 Geoid Content Analysis:")
        cursor.execute("""
            SELECT geoid_id, symbolic_state, metadata_json, semantic_state_json
            FROM geoids
            LIMIT 10
        """)
        
        geoids = cursor.fetchall()
        symbolic_types = Counter()
        metadata_sources = Counter()
        semantic_dimensions = defaultdict(list)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM geoids")
        total_geoids = cursor.fetchone()[0]
        print(f"   Total Geoids: {total_geoids}")
        
        for geoid in geoids:
            geoid_id, symbolic_json, metadata_json, semantic_json = geoid
            
            try:
                symbolic = json.loads(symbolic_json) if symbolic_json else {}
                metadata = json.loads(metadata_json) if metadata_json else {}
                semantic = json.loads(semantic_json) if semantic_json else {}
                
                # Analyze symbolic content
                if 'type' in symbolic:
                    symbolic_types[symbolic['type']] += 1
                
                # Analyze metadata
                if 'created_by' in metadata:
                    metadata_sources[metadata['created_by']] += 1
                
                # Analyze semantic dimensions
                for key, value in semantic.items():
                    if isinstance(value, (int, float)):
                        semantic_dimensions[key].append(value)
                
                # Show sample geoid
                if len(analysis["geoids"]) < 3:
                    analysis["geoids"][geoid_id] = {
                        "symbolic": symbolic,
                        "metadata": metadata,
                        "semantic": semantic
                    }
                    print(f"\n   📌 {geoid_id}:")
                    print(f"      Symbolic: {symbolic}")
                    print(f"      Semantic dimensions: {list(semantic.keys())}")
                    
            except Exception as e:
                print(f"      Error parsing geoid {geoid_id}: {e}")
        
        # Analyze semantic patterns
        print(f"\n   📈 Geoid Statistics:")
        print(f"      Symbolic Types: {dict(symbolic_types)}")
        print(f"      Metadata Sources: {dict(metadata_sources)}")
        print(f"      Common Semantic Dimensions: {list(semantic_dimensions.keys())[:10]}")
        
        # Calculate semantic statistics
        if semantic_dimensions:
            print(f"\n   🧠 Semantic Dimension Analysis:")
            for dim, values in list(semantic_dimensions.items())[:5]:
                if values:
                    print(f"      {dim}: mean={np.mean(values):.3f}, std={np.std(values):.3f}, range=[{min(values):.3f}, {max(values):.3f}]")
        
        # Analyze relationships between SCARs and Geoids
        print("\n\n🔗 Relationship Analysis:")
        cursor.execute("""
            SELECT s.scar_id, s.geoids, s.reason, s.vault_id
            FROM scars s
            WHERE s.geoids IS NOT NULL
        """)
        
        relationships = cursor.fetchall()
        geoid_involvement = Counter()
        scar_geoid_pairs = []
        
        for scar_id, geoids_json, reason, vault_id in relationships:
            try:
                geoids = json.loads(geoids_json) if geoids_json else []
                for geoid in geoids:
                    geoid_involvement[geoid] += 1
                    scar_geoid_pairs.append((scar_id, geoid, reason, vault_id))
            except:
                pass
        
        print(f"   Total SCAR-Geoid relationships: {len(scar_geoid_pairs)}")
        print(f"   Most involved Geoids: {geoid_involvement.most_common(5)}")
        
        # Analyze patterns
        analysis["patterns"] = {
            "scar_reasons": dict(scar_reasons),
            "resolution_methods": dict(resolution_methods),
            "vault_distribution": dict(vault_distribution),
            "symbolic_types": dict(symbolic_types),
            "metadata_sources": dict(metadata_sources),
            "geoid_involvement": dict(geoid_involvement.most_common(10)),
            "semantic_dimensions": list(semantic_dimensions.keys())
        }
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing SQLite content: {e}")
        analysis["error"] = str(e)
    
    return analysis

def analyze_neo4j_content() -> Dict[str, Any]:
    """Perform deep content analysis of Neo4j database"""
    print("\n\n🕸️ Deep Content Analysis of Neo4j Database:")
    
    analysis = {
        "nodes": {},
        "relationships": {},
        "patterns": {}
    }
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            node_counts = {}
            for record in result:
                if record["label"]:
                    node_counts[record["label"]] = record["count"]
            
            print(f"   Node counts: {node_counts}")
            
            # Sample Geoids
            if "Geoid" in node_counts and node_counts["Geoid"] > 0:
                print("\n   📌 Sample Geoids in Neo4j:")
                result = session.run("""
                    MATCH (g:Geoid)
                    RETURN g
                    LIMIT 3
                """)
                
                for record in result:
                    geoid = dict(record["g"])
                    print(f"      {geoid.get('geoid_id', 'Unknown')}:")
                    # Show deserialized properties
                    for key, value in geoid.items():
                        if key not in ['geoid_id']:
                            if isinstance(value, str) and key in ['semantic_state', 'symbolic_state', 'metadata']:
                                try:
                                    parsed = json.loads(value)
                                    print(f"         {key}: {parsed}")
                                except:
                                    print(f"         {key}: {value[:50]}..." if len(str(value)) > 50 else f"         {key}: {value}")
                            else:
                                print(f"         {key}: {value}")
            
            # Sample SCARs
            if "Scar" in node_counts and node_counts["Scar"] > 0:
                print("\n   📌 Sample SCARs in Neo4j:")
                result = session.run("""
                    MATCH (s:Scar)
                    RETURN s
                    LIMIT 3
                """)
                
                for record in result:
                    scar = dict(record["s"])
                    print(f"      {scar.get('scar_id', 'Unknown')}:")
                    print(f"         reason: {scar.get('reason', 'N/A')}")
                    print(f"         vault_id: {scar.get('vault_id', 'N/A')}")
            
            # Analyze relationships
            print("\n   🔗 Relationship Analysis:")
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            rel_counts = {}
            for record in result:
                rel_counts[record["rel_type"]] = record["count"]
            
            print(f"      Relationship counts: {rel_counts}")
            
            # Analyze INVOLVES relationships
            if "INVOLVES" in rel_counts and rel_counts["INVOLVES"] > 0:
                result = session.run("""
                    MATCH (s:Scar)-[r:INVOLVES]->(g:Geoid)
                    RETURN s.scar_id as scar, s.reason as reason, 
                           collect(g.geoid_id) as geoids
                    LIMIT 5
                """)
                
                print("\n      Sample SCAR->GEOID relationships:")
                for record in result:
                    print(f"         {record['scar']} ({record['reason']}) -> {record['geoids']}")
            
            # Graph statistics
            result = session.run("""
                MATCH (n)
                WITH count(n) as nodeCount
                MATCH ()-[r]->()
                WITH nodeCount, count(r) as relCount
                RETURN nodeCount, relCount, 
                       toFloat(relCount) / nodeCount as avgDegree
            """)
            
            stats = result.single()
            if stats:
                print(f"\n   📊 Graph Statistics:")
                print(f"      Total nodes: {stats['nodeCount']}")
                print(f"      Total relationships: {stats['relCount']}")
                print(f"      Average degree: {stats['avgDegree']:.2f}")
            
            analysis["nodes"] = node_counts
            analysis["relationships"] = rel_counts
            
    except ImportError:
        print("   ❌ Neo4j modules not available")
        analysis["status"] = "unavailable"
    except Exception as e:
        print(f"   ❌ Error analyzing Neo4j content: {e}")
        analysis["error"] = str(e)
    
    return analysis

def generate_insights(sqlite_analysis: Dict[str, Any], neo4j_analysis: Dict[str, Any]):
    """Generate insights from the analysis"""
    print("\n\n💡 INSIGHTS AND OBSERVATIONS:")
    
    patterns = sqlite_analysis.get("patterns", {})
    
    # Vault balance insight
    vault_dist = patterns.get("vault_distribution", {})
    if vault_dist:
        total_scars = sum(vault_dist.values())
        vault_a = vault_dist.get("vault_a", 0)
        vault_b = vault_dist.get("vault_b", 0)
        balance_ratio = min(vault_a, vault_b) / max(vault_a, vault_b) if max(vault_a, vault_b) > 0 else 0
        
        print(f"\n   🏦 Vault Balance Analysis:")
        print(f"      Vault A: {vault_a} SCARs ({vault_a/total_scars*100:.1f}%)")
        print(f"      Vault B: {vault_b} SCARs ({vault_b/total_scars*100:.1f}%)")
        print(f"      Balance Ratio: {balance_ratio:.2f} (1.0 = perfect balance)")
        
        if balance_ratio > 0.8:
            print("      ✅ Vaults are well-balanced")
        else:
            print("      ⚠️ Vault imbalance detected - may need rebalancing")
    
    # Semantic activity insight
    symbolic_types = patterns.get("symbolic_types", {})
    if symbolic_types:
        print(f"\n   🧠 Semantic Activity:")
        print(f"      Active symbolic types: {list(symbolic_types.keys())}")
        print(f"      Most common type: {max(symbolic_types, key=symbolic_types.get) if symbolic_types else 'None'}")
    
    # Geoid involvement insight
    geoid_involvement = patterns.get("geoid_involvement", {})
    if geoid_involvement:
        print(f"\n   🔗 Geoid Involvement:")
        highly_involved = [g for g, count in geoid_involvement.items() if count > 1]
        print(f"      Geoids in multiple SCARs: {len(highly_involved)}")
        if highly_involved:
            print(f"      Most involved: {highly_involved[:3]}")
    
    # System health insight
    print(f"\n   🏥 System Health Indicators:")
    
    # Check for recent activity
    recent_scars = len([s for s in sqlite_analysis.get("scars", {}).values() 
                       if "2025-06-16" in s.get("timestamp", "")])
    print(f"      Recent activity (today): {recent_scars} SCARs")
    
    # Check entropy trend
    entropy_changes = []
    for scar in sqlite_analysis.get("scars", {}).values():
        if scar.get("entropy_change") is not None:
            entropy_changes.append(scar["entropy_change"])
    
    if entropy_changes:
        avg_entropy_change = np.mean(entropy_changes)
        print(f"      Average entropy change: {avg_entropy_change:.3f}")
        if avg_entropy_change < 0:
            print("      ✅ System is reducing entropy (stabilizing)")
        else:
            print("      ⚠️ System entropy is increasing")
    
    # Neo4j sync status
    if neo4j_analysis.get("nodes", {}).get("Scar", 0) > 0:
        print("      ✅ Neo4j synchronization is active")
    else:
        print("      ⚠️ Neo4j may not be fully synchronized")

def main():
    """Main analysis function"""
    print("🚀 KIMERA SWM Deep Database Content Analysis")
    print("=" * 60)
    
    # Analyze SQLite content
    sqlite_analysis = analyze_sqlite_content()
    
    # Analyze Neo4j content
    neo4j_analysis = analyze_neo4j_content()
    
    # Generate insights
    generate_insights(sqlite_analysis, neo4j_analysis)
    
    # Save detailed report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "sqlite_analysis": sqlite_analysis,
        "neo4j_analysis": neo4j_analysis
    }
    
    with open("database_content_analysis.json", "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print("\n\n💾 Detailed report saved to: database_content_analysis.json")
    print("✅ Content analysis complete!")

if __name__ == "__main__":
    main()