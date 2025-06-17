#!/usr/bin/env python3
"""
Test script to verify the embedding model migration from sentence-transformers to ONNX Runtime + BGE.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embedding_import():
    """Test that we can import the embedding utilities."""
    try:
        from backend.core.embedding_utils import encode_text, initialize_embedding_model
        logger.info("✅ Successfully imported embedding utilities")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import embedding utilities: {e}")
        return False

def test_model_initialization():
    """Test model initialization."""
    try:
        from backend.core.embedding_utils import initialize_embedding_model
        model = initialize_embedding_model()
        logger.info("✅ Model initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {e}")
        return False

def test_embedding_generation():
    """Test embedding generation with various inputs."""
    try:
        from backend.core.embedding_utils import encode_text
        from backend.core.constants import EMBEDDING_DIM
        
        test_cases = [
            "This is a simple test sentence.",
            "A more complex sentence with technical terms like neural networks and embeddings.",
            "Short text.",
            "A very long sentence that contains multiple clauses and should test the model's ability to handle longer inputs while maintaining semantic coherence and producing meaningful embeddings.",
            "Multilingual test: Hello, Bonjour, Hola, Guten Tag, こんにちは"
        ]
        
        results = []
        for i, text in enumerate(test_cases):
            start_time = time.time()
            embedding = encode_text(text)
            end_time = time.time()
            
            # Verify embedding properties
            assert isinstance(embedding, list), f"Embedding should be a list, got {type(embedding)}"
            assert len(embedding) == EMBEDDING_DIM, f"Expected dimension {EMBEDDING_DIM}, got {len(embedding)}"
            assert all(isinstance(x, (int, float)) for x in embedding), "All embedding values should be numeric"
            
            results.append({
                'text': text[:50] + "..." if len(text) > 50 else text,
                'dimension': len(embedding),
                'time': end_time - start_time,
                'norm': sum(x*x for x in embedding) ** 0.5
            })
            
            logger.info(f"✅ Test case {i+1}: {results[-1]['text']} - "
                       f"dim={results[-1]['dimension']}, "
                       f"time={results[-1]['time']:.3f}s, "
                       f"norm={results[-1]['norm']:.3f}")
        
        return True, results
        
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return False, []

def test_performance_benchmark():
    """Run a simple performance benchmark."""
    try:
        from backend.core.embedding_utils import encode_text
        
        test_text = "This is a benchmark test sentence for measuring embedding performance."
        num_iterations = 50
        
        logger.info(f"Running performance benchmark with {num_iterations} iterations...")
        
        start_time = time.time()
        for i in range(num_iterations):
            embedding = encode_text(f"{test_text} Iteration {i}")
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        throughput = num_iterations / total_time
        
        logger.info(f"✅ Performance benchmark completed:")
        logger.info(f"   Total time: {total_time:.3f}s")
        logger.info(f"   Average time per embedding: {avg_time:.3f}s")
        logger.info(f"   Throughput: {throughput:.1f} embeddings/second")
        
        return True, {
            'total_time': total_time,
            'avg_time': avg_time,
            'throughput': throughput
        }
        
    except Exception as e:
        logger.error(f"❌ Performance benchmark failed: {e}")
        return False, {}

def test_configuration_modes():
    """Test different configuration modes."""
    try:
        # Test lightweight mode
        os.environ['LIGHTWEIGHT_EMBEDDING'] = '1'
        from backend.core.embedding_utils import encode_text
        
        # Force reload the module to pick up environment changes
        import importlib
        import backend.core.embedding_utils
        importlib.reload(backend.core.embedding_utils)
        
        embedding = backend.core.embedding_utils.encode_text("Test lightweight mode")
        logger.info(f"✅ Lightweight mode test passed - dimension: {len(embedding)}")
        
        # Reset to normal mode
        os.environ['LIGHTWEIGHT_EMBEDDING'] = '0'
        importlib.reload(backend.core.embedding_utils)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration mode test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting embedding migration tests...")
    
    tests = [
        ("Import Test", test_embedding_import),
        ("Model Initialization", test_model_initialization),
        ("Embedding Generation", lambda: test_embedding_generation()[0]),
        ("Performance Benchmark", lambda: test_performance_benchmark()[0]),
        ("Configuration Modes", test_configuration_modes),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n📊 Test Summary:")
    logger.info(f"   Passed: {passed}/{total}")
    logger.info(f"   Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 All tests passed! Migration successful.")
        
        # Run detailed embedding test for final verification
        logger.info("\n🔍 Running detailed embedding analysis...")
        success, embedding_results = test_embedding_generation()
        if success:
            logger.info("📈 Embedding Analysis Results:")
            for result in embedding_results:
                logger.info(f"   {result}")
        
        # Run performance benchmark for final metrics
        logger.info("\n⚡ Running final performance benchmark...")
        success, perf_results = test_performance_benchmark()
        if success:
            logger.info("📊 Final Performance Metrics:")
            for key, value in perf_results.items():
                logger.info(f"   {key}: {value}")
                
        return True
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)