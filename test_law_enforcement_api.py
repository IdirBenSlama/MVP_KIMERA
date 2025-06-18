"""
Simple API Test for Law Enforcement System
==========================================

Tests the API endpoints to ensure they're working correctly.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8001"
LAW_ENFORCEMENT_URL = f"{BASE_URL}/law_enforcement"


def test_api_endpoints():
    """Test all law enforcement API endpoints"""
    
    print("🧪 Testing Law Enforcement API Endpoints")
    print("=" * 50)
    
    # Test 1: Get system status
    print("1. Testing system status...")
    try:
        response = requests.get(f"{LAW_ENFORCEMENT_URL}/system_status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ System status: {data['system_status']['system_stability']['status']}")
        else:
            print(f"   ✗ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Get all laws
    print("2. Testing law retrieval...")
    try:
        response = requests.get(f"{LAW_ENFORCEMENT_URL}/laws")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Retrieved {data['total_count']} laws")
        else:
            print(f"   ✗ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Context assessment
    print("3. Testing context assessment...")
    try:
        test_data = {
            "input_text": "I need help with my homework on quantum physics",
            "user_context": {"is_student": True}
        }
        response = requests.post(f"{LAW_ENFORCEMENT_URL}/assess_context", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Context: {data['context_type']}, Relevance: {data['relevance_level']}")
        else:
            print(f"   ✗ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Compliance assessment
    print("4. Testing compliance assessment...")
    try:
        test_data = {
            "input_text": "Can you explain different political perspectives on climate change?",
            "action": "provide_balanced_analysis",
            "user_context": {"educational_purpose": True}
        }
        response = requests.post(f"{LAW_ENFORCEMENT_URL}/assess_compliance", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Compliant: {data['compliant']}, Action: {data['enforcement_action']}")
        else:
            print(f"   ✗ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Get specific law
    print("5. Testing specific law retrieval...")
    try:
        response = requests.get(f"{LAW_ENFORCEMENT_URL}/laws/N1")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Law N1: {data['law']['name']}")
        else:
            print(f"   ✗ Status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ API endpoint testing completed!")


if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure KIMERA is running on port 8001")
    print()
    
    # Wait a moment for any startup
    time.sleep(1)
    
    test_api_endpoints() 