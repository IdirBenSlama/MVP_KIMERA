#!/usr/bin/env python3
"""
Clear check of what mode we're actually using.
"""

import sys
import os
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_current_mode():
    """Check exactly what mode we're using."""
    print("🔍 CHECKING CURRENT EMBEDDING MODE...")
    
    # Check environment
    lightweight_env = os.getenv('LIGHTWEIGHT_EMBEDDING', 'Not Set')
    print(f"Environment LIGHTWEIGHT_EMBEDDING: {lightweight_env}")
    
    # Import and check the actual values
    from backend.core.embedding_utils import LIGHTWEIGHT_MODE, MODEL_NAME, encode_text
    from backend.core.constants import EMBEDDING_DIM
    
    print(f"LIGHTWEIGHT_MODE variable: {LIGHTWEIGHT_MODE}")
    print(f"MODEL_NAME: {MODEL_NAME}")
    print(f"EMBEDDING_DIM: {EMBEDDING_DIM}")
    
    # Test actual embedding generation
    print("\n🧠 TESTING ACTUAL EMBEDDING GENERATION:")
    test_text = "This is a test to see what model we're actually using."
    
    embedding = encode_text(test_text)
    
    print(f"Generated embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Calculate norm
    norm = sum(x*x for x in embedding) ** 0.5
    print(f"Embedding norm: {norm:.6f}")
    
    # Determine what we're actually using
    print("\n📊 ANALYSIS:")
    if LIGHTWEIGHT_MODE:
        print("❌ USING LIGHTWEIGHT MODE (hash-based random vectors)")
        print("   This is NOT the BGE model!")
        print("   This is for testing/development only")
    else:
        if norm > 0.99 and norm < 1.01:  # Normalized embeddings
            print("✅ USING FULL BGE-M3 MODEL")
            print("   Real semantic embeddings with normalization")
            print("   This is the actual migrated model!")
        else:
            print("⚠️  USING DUMMY/FALLBACK MODE")
            print("   Something went wrong with model loading")
    
    return LIGHTWEIGHT_MODE

if __name__ == "__main__":
    is_lightweight = check_current_mode()
    
    if is_lightweight:
        print("\n🚨 ISSUE: We're in lightweight mode!")
        print("To use the full BGE model, ensure LIGHTWEIGHT_EMBEDDING is not set to '1'")
    else:
        print("\n✅ GOOD: We're using the full BGE-M3 model!")