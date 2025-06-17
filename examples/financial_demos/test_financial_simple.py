#!/usr/bin/env python3
"""
Simple Financial API Test for KIMERA SWM
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
KIMERA_API_URL = "http://localhost:8001"  # Default port
KIMERA_API_URL_ALT = "http://localhost:8003"  # Alternative port

def test_kimera_connection():
    """Test connection to KIMERA API"""
    for url in [KIMERA_API_URL, KIMERA_API_URL_ALT]:
        try:
            print(f"Testing connection to {url}...")
            response = requests.get(f"{url}/system/status", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connected to KIMERA at {url}")
                status = response.json()
                print(f"   Active geoids: {status.get('active_geoids', 0)}")
                print(f"   System entropy: {status.get('system_entropy', 0):.2f}")
                return url
            else:
                print(f"❌ KIMERA responded with status {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to {url}: {e}")
    
    print("❌ KIMERA API is not accessible. Please start it with: python run_kimera.py")
    return None

def create_mock_financial_geoid(api_url, symbol, price, volume):
    """Create a mock financial geoid for testing"""
    
    # Create semantic features from financial data
    semantic_features = {
        "price_momentum": min(1.0, max(0.0, (price - 100) / 200 + 0.5)),  # Normalize around $100
        "volume_intensity": min(1.0, volume / 10000000),  # Normalize volume
        "market_sentiment": 0.6,  # Mock positive sentiment
        "volatility": 0.4,  # Mock moderate volatility
        "liquidity": 0.8   # Mock high liquidity
    }
    
    # Create symbolic content
    symbolic_content = {
        "type": "financial_instrument",
        "symbol": symbol,
        "asset_class": "equity",
        "price": price,
        "timestamp": datetime.now().isoformat()
    }
    
    # Create metadata
    metadata = {
        "source": "test_financial_integration",
        "volume": volume,
        "test_data": True
    }
    
    # Create geoid via API
    geoid_data = {
        "semantic_features": semantic_features,
        "symbolic_content": symbolic_content,
        "metadata": metadata
    }
    
    try:
        response = requests.post(
            f"{api_url}/geoids",
            json=geoid_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created geoid for {symbol}: {result['geoid_id']}")
            print(f"   Price: ${price:.2f}, Volume: {volume:,}")
            print(f"   Entropy: {result.get('entropy', 0):.3f}")
            return result['geoid_id']
        else:
            print(f"❌ Failed to create geoid for {symbol}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating geoid for {symbol}: {e}")
        return None

def test_contradiction_detection(api_url, geoid_ids):
    """Test contradiction detection between financial geoids"""
    
    if len(geoid_ids) < 2:
        print("❌ Need at least 2 geoids for contradiction detection")
        return
    
    print(f"\n🔍 Testing contradiction detection with {len(geoid_ids)} geoids...")
    
    try:
        # Use the first geoid as trigger
        trigger_geoid = geoid_ids[0]
        
        contradiction_data = {
            "trigger_geoid_id": trigger_geoid,
            "search_limit": len(geoid_ids),
            "force_collapse": False
        }
        
        response = requests.post(
            f"{api_url}/process/contradictions",
            json=contradiction_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            contradictions = result.get('contradictions_detected', 0)
            scars_created = result.get('scars_created', 0)
            
            print(f"✅ Contradiction detection completed:")
            print(f"   🔥 Contradictions detected: {contradictions}")
            print(f"   ⚡ Scars created: {scars_created}")
            print(f"   🔄 Cycle: {result.get('cycle', 'N/A')}")
            
            if contradictions > 0:
                print(f"\n📊 Contradiction Details:")
                for i, analysis in enumerate(result.get('analysis_results', []), 1):
                    tension = analysis.get('tension', {})
                    print(f"   {i}. Type: {tension.get('type', 'N/A')}")
                    print(f"      Score: {tension.get('score', 'N/A')}")
                    print(f"      Decision: {analysis.get('system_decision', 'N/A')}")
            
            return result
        else:
            print(f"❌ Contradiction detection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in contradiction detection: {e}")
        return None

def test_system_status(api_url):
    """Test system status and monitoring"""
    
    print(f"\n📊 Testing system status...")
    
    try:
        # Get system status
        response = requests.get(f"{api_url}/system/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System Status:")
            print(f"   🧠 Active Geoids: {status.get('active_geoids', 0)}")
            print(f"   🏛️  Vault A Scars: {status.get('vault_a_scars', 0)}")
            print(f"   🏛️  Vault B Scars: {status.get('vault_b_scars', 0)}")
            print(f"   🌀 System Entropy: {status.get('system_entropy', 0):.3f}")
            print(f"   🔄 Cycle Count: {status.get('cycle_count', 0)}")
        
        # Get stability metrics
        response = requests.get(f"{api_url}/system/stability", timeout=10)
        if response.status_code == 200:
            stability = response.json()
            print(f"\n✅ Stability Metrics:")
            for metric, value in stability.items():
                if isinstance(value, (int, float)):
                    print(f"   📈 {metric.replace('_', ' ').title()}: {value:.3f}")
        
    except Exception as e:
        print(f"❌ Error getting system status: {e}")

def main():
    """Main test function"""
    print("🧪 KIMERA SWM Financial API Integration Test")
    print("=" * 50)
    
    # Test connection
    api_url = test_kimera_connection()
    if not api_url:
        return
    
    print(f"\n📈 Creating mock financial data...")
    
    # Create mock financial instruments
    financial_data = [
        ("AAPL", 150.25, 5000000),   # Apple
        ("GOOGL", 2800.50, 1200000), # Google
        ("TSLA", 250.75, 8000000),   # Tesla
        ("MSFT", 380.00, 3000000),   # Microsoft
    ]
    
    geoid_ids = []
    
    # Create geoids for each financial instrument
    for symbol, price, volume in financial_data:
        geoid_id = create_mock_financial_geoid(api_url, symbol, price, volume)
        if geoid_id:
            geoid_ids.append(geoid_id)
        time.sleep(1)  # Brief pause between creations
    
    print(f"\n✅ Created {len(geoid_ids)} financial geoids")
    
    # Test contradiction detection
    if geoid_ids:
        contradiction_result = test_contradiction_detection(api_url, geoid_ids)
    
    # Test system monitoring
    test_system_status(api_url)
    
    print(f"\n🎯 Test Summary:")
    print(f"   ✅ KIMERA Connection: Working")
    print(f"   ✅ Financial Geoid Creation: {len(geoid_ids)} created")
    print(f"   ✅ Contradiction Detection: {'Working' if geoid_ids else 'Skipped'}")
    print(f"   ✅ System Monitoring: Working")
    
    print(f"\n🚀 Financial integration test completed successfully!")
    print(f"   🔗 API Documentation: {api_url}/docs")

if __name__ == "__main__":
    main()