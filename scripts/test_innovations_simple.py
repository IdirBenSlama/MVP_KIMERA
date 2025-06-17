#!/usr/bin/env python3
"""
Simple test to verify innovation modules are working
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from innovations.quantum_batch_processor import process_geoids_quantum, get_quantum_metrics
from innovations.predictive_load_balancer import (
    ResourceState, WorkloadRequest,
    register_resource, get_load_balancing_decision,
    start_optimization_loop, stop_optimization_loop
)
from backend.core.geoid import GeoidState
import uuid

async def test_quantum_processor():
    print("Testing Quantum Batch Processor...")
    
    # Create a few test geoids
    geoids = []
    for i in range(5):
        geoid = GeoidState(
            geoid_id=uuid.uuid4().hex,
            semantic_state={f"feature_{j}": float(j) for j in range(10)},
            symbolic_state={"data": f"test_{i}"},
            metadata={"index": i}
        )
        geoids.append(geoid)
    
    print(f"Created {len(geoids)} test geoids")
    
    try:
        # Process with quantum batch processor
        result = await asyncio.wait_for(
            process_geoids_quantum(geoids),
            timeout=10.0
        )
        
        print(f"✅ Quantum processing successful!")
        print(f"   - Processed: {len(result.processed_geoids)} geoids")
        print(f"   - Coherence score: {result.coherence_score:.2f}")
        print(f"   - Processing time: {result.processing_time:.2f}s")
        print(f"   - Quantum efficiency: {result.quantum_efficiency:.2f}")
        
        # Get metrics
        metrics = get_quantum_metrics()
        print(f"\nQuantum Metrics:")
        for key, value in metrics.items():
            print(f"   - {key}: {value}")
            
    except asyncio.TimeoutError:
        print("❌ Quantum processing timed out!")
    except Exception as e:
        print(f"❌ Quantum processing failed: {e}")
        import traceback
        traceback.print_exc()

def test_load_balancer():
    print("\n\nTesting Predictive Load Balancer...")
    
    # Register a simple resource
    resource = ResourceState(
        resource_id="test_gpu",
        resource_type="gpu",
        utilization=0.3,
        capacity=100.0,
        temperature=50.0,
        power_consumption=100.0,
        latency=0.01,
        throughput=100.0,
        error_rate=0.0
    )
    register_resource(resource)
    print("✅ Resource registered")
    
    # Start optimization loop
    start_optimization_loop()
    print("✅ Optimization loop started")
    
    # Create a workload
    workload = WorkloadRequest(
        request_id="test_workload",
        complexity_score=0.5,
        resource_requirements={"gpu": 0.8},
        priority=5
    )
    
    # Get load balancing decision
    decision = get_load_balancing_decision(workload)
    print(f"✅ Load balancing decision: {decision.reasoning}")
    print(f"   - Confidence: {decision.confidence_score:.2f}")
    print(f"   - Predicted completion: {decision.predicted_completion_time:.2f}")
    
    # Stop optimization loop
    stop_optimization_loop()
    print("✅ Optimization loop stopped")

if __name__ == "__main__":
    print("=== INNOVATION MODULES TEST ===\n")
    
    # Test quantum processor
    asyncio.run(test_quantum_processor())
    
    # Test load balancer
    test_load_balancer()
    
    print("\n=== TEST COMPLETE ===")