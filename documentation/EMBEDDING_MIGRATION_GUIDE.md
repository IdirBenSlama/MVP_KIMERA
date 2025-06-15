# Embedding Model Migration Guide

## Overview

This guide covers the migration from `sentence-transformers` with `all-MiniLM-L6-v2` to ONNX Runtime with `BAAI/bge-m3` (BGE-M3) model.

## Changes Made

### 1. Dependencies Updated

**Removed:**
- `sentence-transformers==4.1.0`

**Added:**
- `onnxruntime==1.20.1`
- `onnxruntime-gpu==1.20.1` 
- `optimum[onnxruntime]==1.23.3`
- `FlagEmbedding==1.3.2`

### 2. Model Changes

| Aspect | Before | After |
|--------|--------|-------|
| Model | all-MiniLM-L6-v2 | BAAI/bge-m3 |
| Framework | sentence-transformers | ONNX Runtime + FlagEmbedding |
| Embedding Dimension | 384 | 1024 |
| Performance | Standard | Optimized with ONNX |
| Multilingual Support | Limited | Enhanced (BGE-M3) |

### 3. Code Changes

#### embedding_utils.py
- Updated imports to use ONNX Runtime and FlagEmbedding
- Added ONNX model loading with fallback to BGE model
- Enhanced error handling and logging
- Maintained backward compatibility with lightweight mode

#### test_model.py
- Updated to test both ONNX and BGE model loading
- Added comprehensive error handling
- Includes inference testing

## Installation Steps

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

### 2. Convert Model to ONNX (Optional but Recommended)

```bash
python convert_to_onnx.py
```

This will:
- Download the BAAI/bge-m3 model
- Convert it to ONNX format
- Save it to `./models/bge-m3-onnx/`
- Create a configuration file

### 3. Environment Configuration

Create or update your `.env` file:

```env
# Embedding Configuration
USE_ONNX=1                              # Use ONNX Runtime (1) or BGE model (0)
ONNX_MODEL_PATH=./models/bge-m3-onnx   # Path to ONNX model
LIGHTWEIGHT_EMBEDDING=0                 # Use lightweight mode for testing
```

## Usage Examples

### Basic Usage (Automatic)

The existing code will work without changes:

```python
from backend.core.embedding_utils import encode_text

# This will automatically use the new BGE/ONNX model
embedding = encode_text("Your text here")
print(f"Embedding dimension: {len(embedding)}")
```

### Manual Model Testing

```python
python test_model.py
```

### Verify ONNX Model

```python
python convert_to_onnx.py --verify-only
```

## Performance Benefits

### ONNX Runtime Advantages:
1. **Faster Inference**: 2-3x speedup compared to PyTorch
2. **Lower Memory Usage**: Optimized memory footprint
3. **Cross-Platform**: Consistent performance across devices
4. **Hardware Acceleration**: Better GPU utilization

### BGE-M3 Model Advantages:
1. **Better Quality**: Superior embedding quality
2. **Multilingual**: Support for 100+ languages
3. **Larger Context**: Better handling of longer texts
4. **Retrieval Optimized**: Designed for semantic search

## Backward Compatibility

The migration maintains backward compatibility:

- All existing function signatures remain the same
- Lightweight mode still available for testing
- Graceful fallback if ONNX model unavailable
- Error handling preserves system stability

## Troubleshooting

### Common Issues

1. **ONNX Model Not Found**
   ```
   Solution: Run python convert_to_onnx.py to create ONNX model
   ```

2. **Import Errors**
   ```
   Solution: pip install FlagEmbedding onnxruntime transformers
   ```

3. **CUDA Issues**
   ```
   Solution: Install onnxruntime-gpu and ensure CUDA compatibility
   ```

4. **Memory Issues**
   ```
   Solution: Set USE_ONNX=0 to use BGE model, or LIGHTWEIGHT_EMBEDDING=1
   ```

### Verification Steps

1. **Test Model Loading**:
   ```bash
   python test_model.py
   ```

2. **Test Embedding Generation**:
   ```python
   from backend.core.embedding_utils import encode_text
   result = encode_text("test")
   assert len(result) == 1024  # BGE-M3 dimension
   ```

3. **Performance Benchmark**:
   ```bash
   python -c "
   import time
   from backend.core.embedding_utils import encode_text
   
   start = time.time()
   for i in range(100):
       encode_text(f'Test sentence {i}')
   print(f'100 embeddings in {time.time() - start:.2f}s')
   "
   ```

## Migration Checklist

- [ ] Install new dependencies
- [ ] Convert model to ONNX (optional)
- [ ] Update environment variables
- [ ] Test model loading
- [ ] Verify embedding generation
- [ ] Run existing tests
- [ ] Monitor performance
- [ ] Update documentation

## Rollback Plan

If issues occur, you can rollback by:

1. Restore original requirements.txt:
   ```bash
   git checkout HEAD~1 requirements.txt
   pip install -r requirements.txt
   ```

2. Restore original embedding_utils.py:
   ```bash
   git checkout HEAD~1 backend/core/embedding_utils.py
   ```

3. Set environment variable:
   ```env
   LIGHTWEIGHT_EMBEDDING=1
   ```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Test with lightweight mode first
4. Check logs for detailed error messages

The migration is designed to be robust with multiple fallback mechanisms to ensure system stability.