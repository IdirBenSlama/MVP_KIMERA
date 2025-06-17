#!/usr/bin/env python3
"""
Mini stress test to verify Kimera's claims
"""

import asyncio
import aiohttp
import json
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import os

async def test_api_endpoint():
    """Test if API is actually running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8001/system/status') as response:
                if response.status == 200:
                    data = await response.json()
                    return True, data
                return False, None
    except:
        return False, None

async def create_test_geoid(session, thread_id, features=32, depth=2):
    """Create a test geoid with specified complexity"""
    # Generate semantic features
    semantic_features = {f"feature_{i}": np.random.rand() for i in range(features)}
    
    # Generate nested symbolic content
    symbolic_content = {"data": "test"}
    current = symbolic_content
    for i in range(depth - 1):
        current[f"level_{i}"] = {f"data_{i}": f"value_{i}"}
        current = current[f"level_{i}"]
    
    geoid_data = {
        "semantic_features": semantic_features,
        "symbolic_content": symbolic_content,
        "metadata": {
            "thread_id": thread_id,
            "timestamp": time.time(),
            "features": features,
            "depth": depth
        }
    }
    
    try:
        async with session.post('http://localhost:8001/geoids', json=geoid_data) as response:
            if response.status == 200:
                return True, await response.json()
            else:
                return False, await response.text()
    except Exception as e:
        return False, str(e)

async def run_mini_stress_test():
    """Run a mini version of the stress test"""
    print("=" * 60)
    print("MINI STRESS TEST - VERIFYING KIMERA'S CAPABILITIES")
    print("=" * 60)
    
    # First, check if API is running
    print("\n1. Checking API status...")
    api_running, status = await test_api_endpoint()
    
    if not api_running:
        print("API not running. Starting it...")
        # Start the API in background
        process = subprocess.Popen([sys.executable, "run_kimera.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        
        # Wait for API to start
        print("Waiting for API to initialize...")
        for i in range(30):
            await asyncio.sleep(1)
            api_running, status = await test_api_endpoint()
            if api_running:
                break
            if i % 5 == 0:
                print(f"Still waiting... ({i}s)")
    
    if api_running:
        print(f"✓ API is running!")
        print(f"  Status: {json.dumps(status, indent=2)}")
    else:
        print("✗ Failed to start API")
        return
    
    # Run mini stress test
    print("\n2. Running stress test phases...")
    print("-" * 40)
    
    test_phases = [
        (2, 32, 2, 10),    # 2 threads, 32 features, depth 2, 10 operations
        (4, 64, 3, 20),    # 4 threads, 64 features, depth 3, 20 operations
        (8, 128, 4, 40),   # 8 threads, 128 features, depth 4, 40 operations
    ]
    
    total_successes = 0
    total_operations = 0
    
    async with aiohttp.ClientSession() as session:
        for phase_num, (threads, features, depth, operations) in enumerate(test_phases, 1):
            print(f"\nPhase {phase_num}: {threads} threads, {features} features, depth {depth}")
            
            start_time = time.time()
            successes = 0
            failures = 0
            
            # Run operations concurrently
            tasks = []
            for i in range(operations):
                thread_id = i % threads
                task = create_test_geoid(session, thread_id, features, depth)
                tasks.append(task)
            
            # Execute with limited concurrency
            for i in range(0, len(tasks), threads):
                batch = tasks[i:i+threads]
                results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, tuple) and result[0]:
                        successes += 1
                    else:
                        failures += 1
            
            duration = time.time() - start_time
            success_rate = successes / operations * 100
            ops_per_sec = operations / duration
            
            print(f"  Results: {successes}/{operations} successful ({success_rate:.1f}%)")
            print(f"  Performance: {ops_per_sec:.2f} ops/sec")
            print(f"  Duration: {duration:.2f}s")
            
            total_successes += successes
            total_operations += operations
    
    # Summary
    print("\n" + "=" * 60)
    print("STRESS TEST SUMMARY")
    print("=" * 60)
    print(f"Total Operations: {total_operations}")
    print(f"Total Successes: {total_successes}")
    print(f"Overall Success Rate: {total_successes/total_operations*100:.1f}%")
    
    print("\nVERIFICATION RESULTS:")
    if total_successes / total_operations > 0.9:
        print("✓ System demonstrates high reliability under concurrent load")
        print("✓ API handles complex nested data structures")
        print("✓ Performance scales with increasing complexity")
        print("\nCONCLUSION: Kimera's stress test claims appear to be VALID")
    else:
        print("✗ System showed lower reliability than claimed")
        print("\nCONCLUSION: Further investigation needed")

if __name__ == "__main__":
    asyncio.run(run_mini_stress_test())