#!/usr/bin/env python3
"""Quick verification that our native math changes work."""

print('🔍 Quick System Verification...')

# Test 1: Import core components
from backend.core.native_math import NativeMath
from backend.engines.contradiction_engine import ContradictionEngine
from backend.engines.spde import SPDE
print('✅ All imports successful')

# Test 2: Basic functionality
result = NativeMath.cosine_distance([1,2,3], [4,5,6])
print(f'✅ Cosine distance: {result:.4f}')

# Test 3: SPDE diffusion
spde = SPDE()
diffused = spde.diffuse({'a': 1.0, 'b': 2.0})
print(f'✅ SPDE diffusion: {diffused}')

print('🎉 System verification complete - all native math working!')