#!/usr/bin/env python3
"""
Diagnose why Phase 4 (16 threads, 256 features, depth 5) causes the system to hang
"""
import os
import sys
import time
import json
import uuid
import psutil
import threading
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.api.main import app

# Force lightweight mode to see if that helps
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["DATABASE_URL"] = f"sqlite:///./diagnostic_test_{uuid.uuid4().hex[:8]}.db"

def create_test_payload(feature_count: int, depth: int):
    """Create a test payload matching Phase 4 characteristics"""
    
    def generate_nested(d):
        if d <= 0:
            return "x" * 32  # 32 character string
        return {
            f"level_{d}": generate_nested(d - 1),
            f"data_{d}": "x" * 32
        }
    
    return {
        "semantic_features": {f"feature_{i}": 0.5 for i in range(feature_count)},
        "symbolic_content": generate_nested(depth),
        "metadata": {
            "test_id": uuid.uuid4().hex,
            "timestamp": datetime.now().isoformat(),
            "depth": depth,
            "feature_count": feature_count
        }
    }

def measure_payload_size(payload):
    """Measure the size of a payload in bytes"""
    return len(json.dumps(payload).encode('utf-8'))

def test_single_request(feature_count, depth):
    """Test a single request with given parameters"""
    client = TestClient(app)
    payload = create_test_payload(feature_count, depth)
    payload_size = measure_payload_size(payload)
    
    print(f"\nTesting single request: {feature_count} features, depth {depth}")
    print(f"  Payload size: {payload_size:,} bytes ({payload_size/1024:.1f} KB)")
    
    start_time = time.time()
    try:
        response = client.post("/geoids", json=payload, timeout=30)
        duration = time.time() - start_time
        
        print(f"  Response: {response.status_code}")
        print(f"  Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            print("  ✅ Success")
        else:
            print(f"  ❌ Failed: {response.text[:200]}")
            
        return True, duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ Exception after {duration:.2f}s: {e}")
        return False, duration

def test_concurrent_requests(feature_count, depth, num_threads):
    """Test concurrent requests"""
    client = TestClient(app)
    results = []
    
    def worker(worker_id):
        payload = create_test_payload(feature_count, depth)
        start_time = time.time()
        try:
            response = client.post("/geoids", json=payload, timeout=30)
            duration = time.time() - start_time
            results.append({
                'worker_id': worker_id,
                'success': response.status_code == 200,
                'duration': duration,
                'status_code': response.status_code
            })
        except Exception as e:
            duration = time.time() - start_time
            results.append({
                'worker_id': worker_id,
                'success': False,
                'duration': duration,
                'error': str(e)
            })
    
    print(f"\nTesting {num_threads} concurrent requests: {feature_count} features, depth {depth}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads with timeout
    for t in threads:
        t.join(timeout=60)
    
    total_duration = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r.get('success', False))
    avg_duration = sum(r['duration'] for r in results) / len(results) if results else 0
    
    print(f"  Total duration: {total_duration:.2f}s")
    print(f"  Successful: {successful}/{num_threads}")
    print(f"  Average response time: {avg_duration:.2f}s")
    
    return results

def monitor_resources():
    """Monitor system resources"""
    process = psutil.Process()
    
    print("\nSystem Resources:")
    print(f"  CPU: {psutil.cpu_percent()}%")
    print(f"  Memory: {psutil.virtual_memory().percent}%")
    print(f"  Process Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"  Threads: {process.num_threads()}")

def main():
    print("=== PHASE 4 BOTTLENECK DIAGNOSIS ===\n")
    
    # Test progression
    test_cases = [
        # (features, depth, threads)
        (32, 2, 1),      # Phase 1 single
        (64, 3, 1),      # Phase 2 single
        (128, 4, 1),     # Phase 3 single
        (256, 5, 1),     # Phase 4 single - THE PROBLEM CASE
        (256, 5, 2),     # Phase 4 with 2 threads
        (256, 5, 4),     # Phase 4 with 4 threads
        (256, 5, 8),     # Phase 4 with 8 threads
        (256, 5, 16),    # Phase 4 full - WHERE IT HANGS
    ]
    
    for features, depth, threads in test_cases:
        monitor_resources()
        
        if threads == 1:
            success, duration = test_single_request(features, depth)
            if not success and features == 256:
                print("\n⚠️ Single request failed at Phase 4 parameters!")
                print("This indicates the issue is with the payload size/complexity, not concurrency.")
                break
        else:
            results = test_concurrent_requests(features, depth, threads)
            if len(results) < threads:
                print(f"\n⚠️ Only {len(results)}/{threads} threads completed!")
                print("This indicates a concurrency issue or resource exhaustion.")
                break
        
        time.sleep(2)
    
    print("\n=== DIAGNOSIS COMPLETE ===")
    
    # Final analysis
    print("\nPossible causes:")
    print("1. Payload size exceeds some internal buffer limit")
    print("2. Embedding model struggles with 256 features")
    print("3. Database transaction size limit")
    print("4. Memory pressure from large nested structures")
    print("5. Serialization/deserialization bottleneck")

if __name__ == "__main__":
    main()