#!/usr/bin/env python3
"""
Test Script for KIMERA Optimizations
====================================

Tests the three key optimizations:
1. Synchronous contradiction processing
2. Automatic insight generation  
3. Improved stress test handling
"""

import requests
import time
import json
from typing import Dict, Any, List

API_URL = "http://localhost:8001"

def test_system_health() -> bool:
    """Test if KIMERA is running and healthy"""
    try:
        response = requests.get(f"{API_URL}/system/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ KIMERA is healthy: {status['system_info']['active_geoids']} geoids active")
            return True
        else:
            print(f"❌ KIMERA health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to KIMERA: {e}")
        return False

def create_test_geoids() -> List[str]:
    """Create test geoids with contradictory features"""
    print("\n🧪 Creating test geoids with contradictory features...")
    
    geoids = []
    test_scenarios = [
        {
            "name": "optimistic_market",
            "semantic_features": {
                "market_sentiment": 0.9,
                "volatility": 0.2,
                "growth_potential": 0.8,
                "risk_level": 0.1
            },
            "symbolic_content": {"type": "market_state", "condition": "bullish"}
        },
        {
            "name": "pessimistic_market", 
            "semantic_features": {
                "market_sentiment": 0.1,
                "volatility": 0.9,
                "growth_potential": 0.2,
                "risk_level": 0.9
            },
            "symbolic_content": {"type": "market_state", "condition": "bearish"}
        },
        {
            "name": "contradictory_market",
            "semantic_features": {
                "market_sentiment": 0.9,  # High sentiment
                "volatility": 0.9,       # High volatility (contradiction)
                "growth_potential": 0.8, # High growth
                "risk_level": 0.8        # High risk (contradiction)
            },
            "symbolic_content": {"type": "market_state", "condition": "mixed_signals"}
        }
    ]
    
    for scenario in test_scenarios:
        try:
            response = requests.post(f"{API_URL}/geoids", json={
                "semantic_features": scenario["semantic_features"],
                "symbolic_content": scenario["symbolic_content"],
                "metadata": {"test": "optimization_test", "scenario": scenario["name"]}
            }, timeout=10)
            
            if response.status_code == 200:
                geoid_id = response.json()["geoid_id"]
                geoids.append(geoid_id)
                print(f"  ✅ Created {scenario['name']}: {geoid_id}")
            else:
                print(f"  ❌ Failed to create {scenario['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error creating {scenario['name']}: {e}")
    
    return geoids

def test_synchronous_contradiction_processing(geoids: List[str]) -> Dict[str, Any]:
    """Test the new synchronous contradiction processing endpoint"""
    print("\n🔍 Testing synchronous contradiction processing...")
    
    if not geoids:
        print("  ⚠️ No geoids available for testing")
        return {}
    
    try:
        # Test with the first geoid as trigger
        trigger_geoid = geoids[0]
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/process/contradictions/sync", json={
            "trigger_geoid_id": trigger_geoid,
            "search_limit": len(geoids)
        }, timeout=30)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Synchronous processing completed in {processing_time:.2f}s")
            print(f"     Contradictions detected: {result.get('contradictions_detected', 0)}")
            print(f"     SCARs created: {result.get('scars_created', 0)}")
            print(f"     Geoids analyzed: {result.get('geoids_analyzed', 0)}")
            return result
        else:
            print(f"  ❌ Synchronous processing failed: HTTP {response.status_code}")
            print(f"     Response: {response.text}")
            return {}
            
    except Exception as e:
        print(f"  ❌ Error in synchronous processing: {e}")
        return {}

def test_automatic_insight_generation() -> Dict[str, Any]:
    """Test the new automatic insight generation endpoint"""
    print("\n💡 Testing automatic insight generation...")
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/insights/auto_generate", timeout=30)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Insight generation completed in {processing_time:.2f}s")
            print(f"     Insights generated: {result.get('insights_generated', 0)}")
            print(f"     Total insights stored: {result.get('total_insights_stored', 0)}")
            
            # Display generated insights
            insights = result.get('insights', [])
            for i, insight in enumerate(insights[:3], 1):  # Show first 3
                print(f"     Insight {i}: {insight.get('type')} (confidence: {insight.get('confidence', 0):.2f})")
            
            return result
        else:
            print(f"  ❌ Insight generation failed: HTTP {response.status_code}")
            print(f"     Response: {response.text}")
            return {}
            
    except Exception as e:
        print(f"  ❌ Error in insight generation: {e}")
        return {}

def test_improved_stress_handling() -> Dict[str, Any]:
    """Test the improved stress handling in cognitive cycles"""
    print("\n⚡ Testing improved stress handling...")
    
    results = {
        "cycles_attempted": 0,
        "cycles_successful": 0,
        "cycles_failed": 0,
        "average_time": 0,
        "errors": []
    }
    
    cycle_times = []
    
    # Run multiple rapid cycles to test stress handling
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/system/cycle", timeout=30)
            cycle_time = time.time() - start_time
            cycle_times.append(cycle_time)
            
            results["cycles_attempted"] += 1
            
            if response.status_code == 200:
                cycle_result = response.json()
                results["cycles_successful"] += 1
                status = cycle_result.get("status", "unknown")
                contradictions = cycle_result.get("contradictions_detected", 0)
                scars = cycle_result.get("scars_created", 0)
                
                print(f"  ✅ Cycle {i+1}: {status} ({cycle_time:.2f}s) - {contradictions} contradictions, {scars} scars")
            else:
                results["cycles_failed"] += 1
                results["errors"].append(f"Cycle {i+1}: HTTP {response.status_code}")
                print(f"  ❌ Cycle {i+1} failed: HTTP {response.status_code}")
                
        except Exception as e:
            results["cycles_failed"] += 1
            results["errors"].append(f"Cycle {i+1}: {str(e)}")
            print(f"  ❌ Cycle {i+1} error: {e}")
        
        # Brief pause between cycles
        time.sleep(1)
    
    if cycle_times:
        results["average_time"] = sum(cycle_times) / len(cycle_times)
    
    success_rate = (results["cycles_successful"] / results["cycles_attempted"]) * 100 if results["cycles_attempted"] > 0 else 0
    print(f"  📊 Stress test complete: {success_rate:.1f}% success rate")
    print(f"     Average cycle time: {results['average_time']:.2f}s")
    
    return results

def test_system_status_after_stress() -> Dict[str, Any]:
    """Check system status after stress testing"""
    print("\n📊 Checking system status after stress testing...")
    
    try:
        response = requests.get(f"{API_URL}/system/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            system_info = status.get("system_info", {})
            
            print(f"  ✅ System still responsive")
            print(f"     Active geoids: {system_info.get('active_geoids', 0)}")
            print(f"     Vault A SCARs: {system_info.get('vault_a_scars', 0)}")
            print(f"     Vault B SCARs: {system_info.get('vault_b_scars', 0)}")
            print(f"     System entropy: {system_info.get('system_entropy', 0):.2f}")
            print(f"     Cycle count: {system_info.get('cycle_count', 0)}")
            
            return status
        else:
            print(f"  ❌ System status check failed: HTTP {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"  ❌ Error checking system status: {e}")
        return {}

def main():
    """Run all optimization tests"""
    print("🚀 KIMERA OPTIMIZATION TEST SUITE")
    print("=" * 50)
    
    # Test 1: System Health
    if not test_system_health():
        print("❌ Cannot proceed - KIMERA is not running")
        return
    
    # Test 2: Create test geoids
    geoids = create_test_geoids()
    
    # Test 3: Synchronous contradiction processing
    contradiction_results = test_synchronous_contradiction_processing(geoids)
    
    # Test 4: Automatic insight generation
    insight_results = test_automatic_insight_generation()
    
    # Test 5: Improved stress handling
    stress_results = test_improved_stress_handling()
    
    # Test 6: System status after stress
    final_status = test_system_status_after_stress()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 OPTIMIZATION TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ Contradictions detected: {contradiction_results.get('contradictions_detected', 0)}")
    print(f"✅ SCARs created: {contradiction_results.get('scars_created', 0)}")
    print(f"✅ Insights generated: {insight_results.get('insights_generated', 0)}")
    print(f"✅ Stress test success rate: {(stress_results.get('cycles_successful', 0) / max(stress_results.get('cycles_attempted', 1), 1)) * 100:.1f}%")
    print(f"✅ System remains operational: {'Yes' if final_status else 'No'}")
    
    # Overall assessment
    total_tests = 5
    passed_tests = 0
    
    if contradiction_results.get('contradictions_detected', 0) > 0:
        passed_tests += 1
    if insight_results.get('insights_generated', 0) > 0:
        passed_tests += 1
    if stress_results.get('cycles_successful', 0) > 0:
        passed_tests += 1
    if final_status:
        passed_tests += 1
    if geoids:
        passed_tests += 1
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All optimizations working correctly!")
    elif passed_tests >= 3:
        print("⚠️ Most optimizations working, some issues detected")
    else:
        print("❌ Significant issues detected, optimizations need review")

if __name__ == "__main__":
    main() 