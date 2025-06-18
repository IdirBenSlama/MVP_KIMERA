#!/usr/bin/env python3
"""Populate the Kimera system with test data"""

import requests
import json
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8001"

def create_test_geoids():
    """Create various test geoids"""
    print("\n📦 Creating Test Geoids...")
    
    test_concepts = [
        {
            "name": "consciousness",
            "features": {"awareness": 0.9, "self_reflection": 0.8, "experience": 0.7},
            "metadata": {"domain": "philosophy", "type": "abstract"}
        },
        {
            "name": "intelligence",
            "features": {"reasoning": 0.9, "learning": 0.8, "adaptation": 0.7},
            "metadata": {"domain": "cognitive_science", "type": "abstract"}
        },
        {
            "name": "emotion",
            "features": {"feeling": 0.9, "expression": 0.7, "regulation": 0.6},
            "metadata": {"domain": "psychology", "type": "abstract"}
        },
        {
            "name": "creativity",
            "features": {"novelty": 0.8, "imagination": 0.9, "synthesis": 0.7},
            "metadata": {"domain": "arts", "type": "abstract"}
        },
        {
            "name": "language",
            "features": {"communication": 0.9, "syntax": 0.7, "semantics": 0.8},
            "metadata": {"domain": "linguistics", "type": "concrete"}
        },
        {
            "name": "mathematics",
            "features": {"logic": 0.9, "abstraction": 0.8, "precision": 0.95},
            "metadata": {"domain": "formal_science", "type": "abstract"}
        },
        {
            "name": "music",
            "features": {"rhythm": 0.8, "harmony": 0.7, "emotion": 0.9},
            "metadata": {"domain": "arts", "type": "concrete"}
        },
        {
            "name": "time",
            "features": {"duration": 0.8, "sequence": 0.9, "change": 0.7},
            "metadata": {"domain": "physics", "type": "abstract"}
        },
        {
            "name": "space",
            "features": {"dimension": 0.9, "distance": 0.8, "position": 0.7},
            "metadata": {"domain": "physics", "type": "abstract"}
        },
        {
            "name": "memory",
            "features": {"storage": 0.8, "retrieval": 0.7, "encoding": 0.9},
            "metadata": {"domain": "cognitive_science", "type": "concrete"}
        }
    ]
    
    created_geoids = []
    
    for concept in test_concepts:
        try:
            response = requests.post(
                f"{BASE_URL}/geoids",
                json={
                    "semantic_features": concept["features"],
                    "symbolic_content": {"name": concept["name"]},
                    "metadata": concept["metadata"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                created_geoids.append(data["geoid_id"])
                print(f"✅ Created geoid for '{concept['name']}': {data['geoid_id']}")
            else:
                print(f"❌ Failed to create geoid for '{concept['name']}': {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating geoid for '{concept['name']}': {e}")
    
    return created_geoids

def create_echoform_geoids():
    """Create geoids from echoform text"""
    print("\n📝 Creating Echoform Geoids...")
    
    echoforms = [
        "(define understanding (lambda (concept) (integrate knowledge experience)))",
        "(assert (implies consciousness awareness))",
        "(query (relationship intelligence creativity))",
        "(hypothesize (emerges consciousness complexity))",
        "(observe (pattern language thought))"
    ]
    
    created_geoids = []
    
    for echoform in echoforms:
        try:
            response = requests.post(
                f"{BASE_URL}/geoids",
                json={
                    "echoform_text": echoform,
                    "metadata": {"source": "echoform", "timestamp": datetime.now().isoformat()}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                created_geoids.append(data["geoid_id"])
                print(f"✅ Created echoform geoid: {data['geoid_id']}")
            else:
                print(f"❌ Failed to create echoform geoid: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating echoform geoid: {e}")
    
    return created_geoids

def process_contradictions(geoid_ids):
    """Process contradictions for created geoids"""
    print("\n⚡ Processing Contradictions...")
    
    total_scars = 0
    
    # Process contradictions for random pairs
    for i in range(min(10, len(geoid_ids))):
        trigger_geoid = random.choice(geoid_ids)
        
        try:
            response = requests.post(
                f"{BASE_URL}/process/contradictions",
                json={
                    "trigger_geoid_id": trigger_geoid,
                    "search_limit": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                scars_created = data.get("scars_created", 0)
                total_scars += scars_created
                
                if scars_created > 0:
                    print(f"✅ Processed contradictions for {trigger_geoid}: {scars_created} SCARs created")
                else:
                    print(f"ℹ️  No contradictions found for {trigger_geoid}")
            else:
                print(f"❌ Failed to process contradictions: {response.status_code}")
        except Exception as e:
            print(f"❌ Error processing contradictions: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    return total_scars

def run_system_cycles():
    """Run cognitive cycles"""
    print("\n🔄 Running System Cycles...")
    
    for i in range(3):
        try:
            response = requests.post(f"{BASE_URL}/system/cycle")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cycle {i+1} completed: {data.get('status', 'unknown')}")
                print(f"   Entropy delta: {data.get('entropy_delta', 0):.4f}")
            else:
                print(f"❌ Failed to run cycle: {response.status_code}")
        except Exception as e:
            print(f"❌ Error running cycle: {e}")
        
        time.sleep(1)

def run_proactive_scan():
    """Run proactive contradiction scan"""
    print("\n🔍 Running Proactive Scan...")
    
    try:
        response = requests.post(f"{BASE_URL}/system/proactive_scan")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Proactive scan completed")
            print(f"   Tensions found: {data.get('tensions_found', 0)}")
            print(f"   SCARs created: {data.get('scars_created', 0)}")
            print(f"   Utilization rate: {data.get('current_utilization_rate', 0):.2%}")
        else:
            print(f"❌ Failed to run proactive scan: {response.status_code}")
    except Exception as e:
        print(f"❌ Error running proactive scan: {e}")

def check_system_status():
    """Check final system status"""
    print("\n📊 Final System Status...")
    
    try:
        # Get monitoring status
        response = requests.get(f"{BASE_URL}/monitoring/status")
        if response.status_code == 200:
            data = response.json()
            vault_info = data.get("vault_info", {})
            print(f"✅ Monitoring Status:")
            print(f"   Active Geoids: {vault_info.get('active_geoids', 0)}")
            print(f"   Vault A SCARs: {vault_info.get('vault_a_scars', 0)}")
            print(f"   Vault B SCARs: {vault_info.get('vault_b_scars', 0)}")
        
        # Get system health
        response = requests.get(f"{BASE_URL}/system/health")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ System Health: {data.get('status', 'unknown')}")
            for check, info in data.get("checks", {}).items():
                status_icon = "✅" if info["status"] == "healthy" else "❌"
                print(f"   {status_icon} {check}: {info['message']}")
        
        # Get utilization stats
        response = requests.get(f"{BASE_URL}/system/utilization_stats")
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Utilization Statistics:")
            print(f"   Total Scans: {data.get('total_scans', 0)}")
            print(f"   Average Utilization: {data.get('average_utilization_rate', 0):.2%}")
            print(f"   Peak Utilization: {data.get('peak_utilization_rate', 0):.2%}")
            
    except Exception as e:
        print(f"❌ Error checking system status: {e}")

def main():
    """Main function to populate test data"""
    print("🚀 Kimera SWM Test Data Population")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print("✅ API server is running")
    except:
        print("❌ API server is not running. Please start it with: python run_kimera.py")
        return
    
    # Create test data
    geoid_ids = []
    
    # Create semantic geoids
    semantic_geoids = create_test_geoids()
    geoid_ids.extend(semantic_geoids)
    
    # Create echoform geoids
    echoform_geoids = create_echoform_geoids()
    geoid_ids.extend(echoform_geoids)
    
    print(f"\n📊 Created {len(geoid_ids)} total geoids")
    
    # Process contradictions
    if geoid_ids:
        total_scars = process_contradictions(geoid_ids)
        print(f"\n📊 Created {total_scars} total SCARs")
    
    # Run system cycles
    run_system_cycles()
    
    # Run proactive scan
    run_proactive_scan()
    
    # Check final status
    check_system_status()
    
    print("\n✅ Test data population complete!")

if __name__ == "__main__":
    main()