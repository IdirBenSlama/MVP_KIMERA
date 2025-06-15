#!/usr/bin/env python3
"""
Test embedding functionality after BGE-M3 migration.
"""

import sys
import time
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_embedding_performance():
    """Test embedding performance with the new BGE-M3 model."""
    print("🧠 Testing BGE-M3 Embedding Performance...")
    
    from backend.core.embedding_utils import encode_text, initialize_embedding_model
    from backend.core.constants import EMBEDDING_DIM
    
    # Initialize model
    print("🔧 Initializing BGE-M3 model...")
    start_time = time.time()
    model = initialize_embedding_model()
    init_time = time.time() - start_time
    print(f"✅ Model initialized in {init_time:.2f}s")
    
    # Test various text complexities
    test_cases = [
        ("Simple", "The cat sat on the mat."),
        ("Technical", "Neural networks utilize backpropagation algorithms for gradient descent optimization in deep learning architectures."),
        ("Complex", "The semantic thermodynamic entropy pruning mechanism leverages contradictory insight synthesis to optimize cognitive coherence through spherical word methodology transformations."),
        ("Long", "In the realm of artificial intelligence and machine learning, the development of sophisticated natural language processing systems has revolutionized our understanding of computational linguistics. These systems, which incorporate advanced neural network architectures such as transformers, attention mechanisms, and recurrent neural networks, have demonstrated remarkable capabilities in tasks ranging from language translation and sentiment analysis to question answering and text generation. The underlying mathematical foundations of these systems rely heavily on concepts from linear algebra, calculus, and probability theory, enabling them to process and understand human language with unprecedented accuracy and nuance.")
    ]
    
    print(f"\n📊 Testing {len(test_cases)} different text complexities:")
    print(f"Expected embedding dimension: {EMBEDDING_DIM}")
    
    results = []
    for test_name, text in test_cases:
        print(f"\n🔍 Testing {test_name} text ({len(text)} chars)...")
        
        # Time the embedding generation
        start_time = time.time()
        embedding = encode_text(text)
        end_time = time.time()
        
        # Verify embedding
        assert len(embedding) == EMBEDDING_DIM, f"Expected {EMBEDDING_DIM} dims, got {len(embedding)}"
        assert all(isinstance(x, (int, float)) for x in embedding), "All values should be numeric"
        
        # Calculate metrics
        norm = sum(x*x for x in embedding) ** 0.5
        duration = end_time - start_time
        
        result = {
            'name': test_name,
            'text_length': len(text),
            'embedding_dim': len(embedding),
            'norm': norm,
            'duration': duration,
            'chars_per_sec': len(text) / duration
        }
        results.append(result)
        
        print(f"   ✅ Generated {len(embedding)}-dim embedding")
        print(f"   ⏱️  Duration: {duration:.3f}s ({result['chars_per_sec']:.1f} chars/s)")
        print(f"   📏 Norm: {norm:.6f}")
    
    # Performance summary
    print("\n📈 Performance Summary:")
    print("=" * 60)
    avg_duration = sum(r['duration'] for r in results) / len(results)
    avg_chars_per_sec = sum(r['chars_per_sec'] for r in results) / len(results)
    
    for result in results:
        print(f"   {result['name']:10} | {result['duration']:6.3f}s | {result['chars_per_sec']:8.1f} chars/s | norm: {result['norm']:.3f}")
    
    print("=" * 60)
    print(f"   Average    | {avg_duration:6.3f}s | {avg_chars_per_sec:8.1f} chars/s")
    
    # Test batch processing
    print("\n🚀 Testing batch processing...")
    batch_texts = [case[1] for case in test_cases] * 5  # 20 texts total
    
    start_time = time.time()
    batch_embeddings = [encode_text(text) for text in batch_texts]
    batch_duration = time.time() - start_time
    
    print(f"   ✅ Processed {len(batch_texts)} texts in {batch_duration:.3f}s")
    print(f"   ⚡ Throughput: {len(batch_texts)/batch_duration:.1f} texts/s")
    
    return True

if __name__ == "__main__":
    try:
        success = test_embedding_performance()
        if success:
            print("\n🎉 BGE-M3 embedding migration test completed successfully!")
            print("✅ All functionality working as expected")
        else:
            print("\n❌ Test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)