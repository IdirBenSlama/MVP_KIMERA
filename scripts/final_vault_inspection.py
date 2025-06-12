#!/usr/bin/env python3
"""
Final Comprehensive Vault Inspection
====================================

Complete vault system inspection with proper error handling.
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

def inspect_vault_system():
    """Complete vault system inspection"""
    
    print("🏛️  KIMERA VAULT SYSTEM - FINAL INSPECTION")
    print("=" * 60)
    
    # Find database
    db_path = os.path.join(ROOT_DIR, "kimera_swm.db")
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    print(f"📁 Database: {db_path}")
    print(f"📊 Size: {os.path.getsize(db_path):,} bytes ({os.path.getsize(db_path)/1024/1024:.1f} MB)")
    print(f"🕐 Inspection: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schemas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n🗂️  Tables: {', '.join(tables)}")
        
        # Inspect scars table
        if "scars" in tables:
            print(f"\n🏛️  VAULT SCARS ANALYSIS")
            print("=" * 40)
            
            # Get scar statistics
            cursor.execute("SELECT COUNT(*) FROM scars;")
            total_scars = cursor.fetchone()[0]
            
            cursor.execute("SELECT vault_id, COUNT(*), SUM(weight), AVG(weight) FROM scars GROUP BY vault_id;")
            vault_stats = cursor.fetchall()
            
            print(f"📊 Total Scars: {total_scars}")
            
            vault_summary = {}
            for vault_id, count, total_weight, avg_weight in vault_stats:
                vault_summary[vault_id] = {
                    "count": count,
                    "total_weight": total_weight or 0,
                    "avg_weight": avg_weight or 0
                }
                print(f"\n🏛️  {vault_id.upper()}:")
                print(f"   Scars: {count}")
                print(f"   Total Weight: {total_weight:.2f}")
                print(f"   Average Weight: {avg_weight:.4f}")
            
            # Balance analysis
            vault_a_count = vault_summary.get("vault_a", {}).get("count", 0)
            vault_b_count = vault_summary.get("vault_b", {}).get("count", 0)
            imbalance = abs(vault_a_count - vault_b_count)
            
            print(f"\n⚖️  BALANCE ANALYSIS:")
            print(f"   Vault A: {vault_a_count} scars")
            print(f"   Vault B: {vault_b_count} scars")
            print(f"   Imbalance: {imbalance} scars")
            
            if imbalance == 0:
                balance_status = "🟢 PERFECT"
            elif imbalance <= 1:
                balance_status = "🟢 EXCELLENT"
            elif imbalance <= 5:
                balance_status = "🟡 GOOD"
            else:
                balance_status = "🔴 POOR"
            
            print(f"   Status: {balance_status}")
            
            # Recent scars
            print(f"\n📋 RECENT SCARS:")
            cursor.execute("SELECT scar_id, vault_id, reason, weight, timestamp FROM scars ORDER BY timestamp DESC LIMIT 5;")
            recent_scars = cursor.fetchall()
            
            for i, (scar_id, vault_id, reason, weight, timestamp) in enumerate(recent_scars, 1):
                print(f"   {i}. {scar_id} ({vault_id}) - {reason} [Weight: {weight:.2f}]")
                print(f"      {timestamp}")
            
            # Scar reasons distribution
            cursor.execute("SELECT reason, COUNT(*) FROM scars GROUP BY reason ORDER BY COUNT(*) DESC;")
            reasons = cursor.fetchall()
            
            print(f"\n📊 SCAR REASONS:")
            for reason, count in reasons:
                print(f"   {reason}: {count}")
            
            # Temporal analysis
            cursor.execute("SELECT DATE(timestamp) as date, COUNT(*) FROM scars GROUP BY DATE(timestamp) ORDER BY date DESC LIMIT 7;")
            daily_counts = cursor.fetchall()
            
            print(f"\n📅 DAILY SCAR CREATION (Last 7 days):")
            for date, count in daily_counts:
                print(f"   {date}: {count} scars")
        
        # Inspect geoids table
        if "geoids" in tables:
            print(f"\n🧠 GEOIDS ANALYSIS")
            print("=" * 40)
            
            # Get geoid table schema
            cursor.execute("PRAGMA table_info(geoids);")
            geoid_columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 Columns: {', '.join(geoid_columns)}")
            
            cursor.execute("SELECT COUNT(*) FROM geoids;")
            total_geoids = cursor.fetchone()[0]
            print(f"📊 Total Geoids: {total_geoids}")
            
            if total_geoids > 0:
                # Get recent geoids with available columns
                available_columns = ["geoid_id"]
                if "semantic_state" in geoid_columns:
                    available_columns.append("semantic_state")
                elif "semantic_features" in geoid_columns:
                    available_columns.append("semantic_features")
                
                if "symbolic_state" in geoid_columns:
                    available_columns.append("symbolic_state")
                elif "symbolic_content" in geoid_columns:
                    available_columns.append("symbolic_content")
                
                query = f"SELECT {', '.join(available_columns)} FROM geoids ORDER BY rowid DESC LIMIT 3;"
                cursor.execute(query)
                recent_geoids = cursor.fetchall()
                
                print(f"\n📋 RECENT GEOIDS (Last 3):")
                for i, geoid_data in enumerate(recent_geoids, 1):
                    geoid_id = geoid_data[0]
                    print(f"   {i}. {geoid_id}")
                    
                    # Show semantic features if available
                    if len(geoid_data) > 1 and geoid_data[1]:
                        try:
                            semantic = json.loads(geoid_data[1])
                            feature_count = len(semantic) if isinstance(semantic, dict) else 0
                            print(f"      Semantic features: {feature_count}")
                        except:
                            print(f"      Semantic data: {str(geoid_data[1])[:50]}...")
                    
                    # Show symbolic content if available
                    if len(geoid_data) > 2 and geoid_data[2]:
                        try:
                            symbolic = json.loads(geoid_data[2])
                            print(f"      Symbolic: {symbolic}")
                        except:
                            print(f"      Symbolic data: {str(geoid_data[2])[:50]}...")
        
        # System health assessment
        print(f"\n🏥 SYSTEM HEALTH ASSESSMENT")
        print("=" * 40)
        
        health_score = 100
        issues = []
        recommendations = []
        
        # Check vault balance
        if total_scars > 0:
            if imbalance == 0:
                print("✅ Vault balance: PERFECT")
            elif imbalance <= 1:
                print("✅ Vault balance: EXCELLENT")
            elif imbalance <= 5:
                print("⚠️  Vault balance: GOOD (minor imbalance)")
                health_score -= 10
                recommendations.append("Consider vault rebalancing")
            else:
                print("❌ Vault balance: POOR (significant imbalance)")
                health_score -= 30
                issues.append(f"Vault imbalance: {imbalance} scars")
                recommendations.append("Immediate vault rebalancing required")
        else:
            print("ℹ️  Vault balance: N/A (no scars)")
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM scars WHERE scar_id IS NULL OR vault_id IS NULL;")
        null_data = cursor.fetchone()[0]
        
        if null_data == 0:
            print("✅ Data integrity: GOOD")
        else:
            print(f"❌ Data integrity: ISSUES ({null_data} records with null data)")
            health_score -= 20
            issues.append(f"{null_data} scars with missing data")
        
        # Overall health
        if health_score >= 90:
            health_status = "🟢 EXCELLENT"
        elif health_score >= 70:
            health_status = "🟡 GOOD"
        elif health_score >= 50:
            health_status = "🟠 FAIR"
        else:
            health_status = "🔴 POOR"
        
        print(f"\n🎯 OVERALL HEALTH: {health_status} ({health_score}/100)")
        
        if issues:
            print(f"\n⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   - {rec}")
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS")
        print("=" * 40)
        print(f"Database Size: {os.path.getsize(db_path):,} bytes")
        print(f"Total Tables: {len(tables)}")
        print(f"Total Scars: {total_scars}")
        print(f"Total Geoids: {total_geoids if 'geoids' in tables else 'N/A'}")
        print(f"Vault Balance: {imbalance} scar difference")
        print(f"Health Score: {health_score}/100")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_vault_system()