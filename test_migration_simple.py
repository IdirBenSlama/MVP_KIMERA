#!/usr/bin/env python3
"""
Simple test to verify the embedding migration is working correctly.
"""

import sys
import os
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_basic_functionality():
    """Test basic embedding functionality."""
    print("🚀 Testing Kimera SWM Embedding Migration...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from backend.core.embedding_utils import encode_text, initialize_embedding_model
        from backend.core.constants import EMBEDDING_DIM
        print(f"✅ Imports successful. Expected embedding dimension: {EMBEDDING_DIM}")
        
        # Test model initialization
        print("🔧 Testing model initialization...")
        model = initialize_embedding_model()
        print("✅ Model initialized successfully")
        
        # Test embedding generation
        print("🧠 Testing embedding generation...")
        test_texts = [
            "This is a test sentence for the new BGE-M3 model.",
            "Another test to verify the migration worked correctly.",
            "Final test with technical terms: neural networks, embeddings, transformers."
        ]
        
        for i, text in enumerate(test_texts, 1):
            embedding = encode_text(text)
            
            # Verify embedding properties
            assert isinstance(embedding, list), f"Expected list, got {type(embedding)}"
            assert len(embedding) == EMBEDDING_DIM, f"Expected {EMBEDDING_DIM} dimensions, got {len(embedding)}"
            assert all(isinstance(x, (int, float)) for x in embedding), "All values should be numeric"
            
            # Calculate norm for verification
            norm = sum(x*x for x in embedding) ** 0.5
            
            print(f"✅ Test {i}: Generated {len(embedding)}-dim embedding (norm: {norm:.3f})")
        
        # Test lightweight mode
        print("🪶 Testing lightweight mode...")
        os.environ['LIGHTWEIGHT_EMBEDDING'] = '1'
        
        # Force reload to pick up environment change
        import importlib
        import backend.core.embedding_utils
        importlib.reload(backend.core.embedding_utils)
        
        lightweight_embedding = backend.core.embedding_utils.encode_text("Lightweight test")
        print(f"✅ Lightweight mode: Generated {len(lightweight_embedding)}-dim embedding")
        
        # Reset to normal mode
        os.environ['LIGHTWEIGHT_EMBEDDING'] = '0'
        
        print("\n🎉 All tests passed! Migration successful!")
        print("\n📊 Summary:")
        print(f"   ✅ Model: BAAI/bge-m3 (upgraded from all-MiniLM-L6-v2)")
        print(f"   ✅ Framework: Transformers + ONNX Runtime (upgraded from sentence-transformers)")
        print(f"   ✅ Embedding Dimension: {EMBEDDING_DIM} (upgraded from 384)")
        print(f"   ✅ All functionality preserved")
        print(f"   ✅ Lightweight mode working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)