#!/usr/bin/env python3
"""
KIMERA SWM Practical Testing Demo
=================================

This script demonstrates the core functionality of KIMERA SWM by:
1. Creating semantic geoids with contradictory concepts
2. Processing contradictions to generate scars
3. Testing the cognitive cycle
4. Demonstrating semantic search capabilities
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8002"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🧠 {title}")
    print('='*60)

def print_result(operation: str, result: Dict[Any, Any]):
    """Print formatted results"""
    print(f"\n✅ {operation}")
    print(f"📊 Result: {json.dumps(result, indent=2)}")

def test_system_status():
    """Test basic system connectivity"""
    print_section("SYSTEM STATUS CHECK")
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        if response.status_code == 200:
            print("✅ KIMERA SWM API is running!")
            print_result("System Status", response.json())
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to KIMERA SWM API. Is the server running on port 8002?")
        return False

def create_test_geoids():
    """Create contradictory geoids for testing"""
    print_section("CREATING TEST GEOIDS")
    
    # Define contradictory concepts
    geoids_data = [
        {
            "name": "Hot Coffee",
            "semantic_features": {
                "temperature": 0.9,
                "liquid": 0.8,
                "beverage": 0.9,
                "comfort": 0.7,
                "energy": 0.8
            },
            "symbolic_content": {"type": "beverage", "temperature": "hot"},
            "metadata": {"category": "drink", "test_group": "temperature"}
        },
        {
            "name": "Ice Cream",
            "semantic_features": {
                "temperature": 0.1,  # Contradicts hot coffee
                "sweet": 0.9,
                "dessert": 0.8,
                "comfort": 0.8,
                "cold": 0.9
            },
            "symbolic_content": {"type": "dessert", "temperature": "cold"},
            "metadata": {"category": "dessert", "test_group": "temperature"}
        },
        {
            "name": "Healthy Vegetables",
            "semantic_features": {
                "healthy": 0.9,
                "natural": 0.8,
                "nutritious": 0.9,
                "green": 0.7,
                "vitamins": 0.8
            },
            "symbolic_content": {"type": "food", "health_value": "high"},
            "metadata": {"category": "food", "test_group": "health"}
        },
        {
            "name": "Fast Food Burger",
            "semantic_features": {
                "healthy": 0.2,  # Contradicts vegetables
                "processed": 0.8,
                "tasty": 0.7,
                "convenient": 0.8,
                "calories": 0.9
            },
            "symbolic_content": {"type": "food", "health_value": "low"},
            "metadata": {"category": "food", "test_group": "health"}
        }
    ]
    
    created_geoids = []
    for geoid_data in geoids_data:
        try:
            response = requests.post(
                f"{BASE_URL}/geoids",
                headers=HEADERS,
                json={
                    "semantic_features": geoid_data["semantic_features"],
                    "symbolic_content": geoid_data["symbolic_content"],
                    "metadata": geoid_data["metadata"]
                }
            )
            if response.status_code == 200:
                result = response.json()
                result["name"] = geoid_data["name"]
                created_geoids.append(result)
                print(f"✅ Created: {geoid_data['name']} (ID: {result['geoid_id']})")
            else:
                print(f"❌ Failed to create {geoid_data['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {geoid_data['name']}: {e}")
    
    return created_geoids

def test_contradiction_processing(geoids):
    """Test contradiction detection and processing"""
    print_section("PROCESSING CONTRADICTIONS")
    
    if not geoids:
        print("❌ No geoids available for contradiction testing")
        return
    
    # Test with the first geoid as trigger
    trigger_geoid = geoids[0]
    print(f"🎯 Using trigger geoid: {trigger_geoid['name']} ({trigger_geoid['geoid_id']})")
    
    try:
        response = requests.post(
            f"{BASE_URL}/process/contradictions",
            headers=HEADERS,
            json={
                "trigger_geoid_id": trigger_geoid["geoid_id"],
                "search_limit": 5,
                "force_collapse": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result("Contradiction Processing", result)
            
            if result.get("contradictions_detected", 0) > 0:
                print(f"🔥 Found {result['contradictions_detected']} contradictions!")
                print(f"⚡ Created {result['scars_created']} scars")
            else:
                print("ℹ️  No significant contradictions detected")
            
            return result
        else:
            print(f"❌ Contradiction processing failed: {response.text}")
    except Exception as e:
        print(f"❌ Error processing contradictions: {e}")
    
    return None

def test_cognitive_cycle():
    """Test the cognitive cycle"""
    print_section("COGNITIVE CYCLE TEST")
    
    try:
        response = requests.post(f"{BASE_URL}/system/cycle")
        if response.status_code == 200:
            result = response.json()
            print_result("Cognitive Cycle", result)
            return result
        else:
            print(f"❌ Cognitive cycle failed: {response.text}")
    except Exception as e:
        print(f"❌ Error running cognitive cycle: {e}")
    
    return None

def test_semantic_search():
    """Test semantic search capabilities"""
    print_section("SEMANTIC SEARCH TEST")
    
    search_queries = [
        "hot beverages",
        "cold desserts", 
        "healthy food",
        "unhealthy snacks"
    ]
    
    for query in search_queries:
        try:
            response = requests.get(
                f"{BASE_URL}/geoids/search",
                params={"query": query, "limit": 3}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"\n🔍 Search: '{query}'")
                print(f"📋 Found {len(result.get('similar_geoids', []))} similar geoids")
                for geoid in result.get('similar_geoids', []):
                    print(f"   - {geoid.get('geoid_id', 'Unknown')}: {geoid.get('symbolic_state', {})}")
            else:
                print(f"❌ Search failed for '{query}': {response.text}")
        except Exception as e:
            print(f"❌ Error searching for '{query}': {e}")

def test_system_stability():
    """Test system stability metrics"""
    print_section("SYSTEM STABILITY METRICS")
    
    try:
        response = requests.get(f"{BASE_URL}/system/stability")
        if response.status_code == 200:
            result = response.json()
            print_result("Stability Metrics", result)
            return result
        else:
            print(f"❌ Stability check failed: {response.text}")
    except Exception as e:
        print(f"❌ Error checking stability: {e}")
    
    return None

def run_comprehensive_test():
    """Run the complete test suite"""
    print("🚀 KIMERA SWM COMPREHENSIVE TEST SUITE")
    print("=====================================")
    
    # Step 1: Check system status
    if not test_system_status():
        print("\n❌ Cannot proceed - API is not accessible")
        return
    
    # Step 2: Create test geoids
    geoids = create_test_geoids()
    if not geoids:
        print("\n❌ Cannot proceed - No geoids created")
        return
    
    # Step 3: Test contradiction processing
    contradiction_result = test_contradiction_processing(geoids)
    
    # Step 4: Test cognitive cycle
    cycle_result = test_cognitive_cycle()
    
    # Step 5: Test semantic search
    test_semantic_search()
    
    # Step 6: Check system stability
    stability_result = test_system_stability()
    
    # Final status
    print_section("FINAL SYSTEM STATUS")
    final_status = requests.get(f"{BASE_URL}/system/status").json()
    print_result("Final Status", final_status)
    
    print(f"\n🎉 TEST SUITE COMPLETED!")
    print(f"📊 Summary:")
    print(f"   - Geoids Created: {len(geoids)}")
    print(f"   - Active Geoids: {final_status.get('active_geoids', 0)}")
    print(f"   - Total Scars: {final_status.get('vault_a_scars', 0) + final_status.get('vault_b_scars', 0)}")
    print(f"   - System Entropy: {final_status.get('system_entropy', 0):.3f}")
    print(f"   - Cycle Count: {final_status.get('cycle_count', 0)}")

if __name__ == "__main__":
    run_comprehensive_test()
