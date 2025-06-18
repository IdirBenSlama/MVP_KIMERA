# Cognitive Field Dynamics Development Guide

## Overview

This guide covers development practices, testing strategies, and extension patterns for the Cognitive Field Dynamics (CFD) system.

## Project Structure

```
backend/
├── engines/
│   └── cognitive_field_dynamics.py    # Core CFD engine
├── api/
│   └── cognitive_field_routes.py      # FastAPI endpoints
├── core/
│   └── cognitive_field_config.py      # Configuration parameters
tests/
├── integration/
│   └── test_cognitive_field_dynamics_api.py    # API tests
└── rigorous/
    └── test_cognitive_field_dynamics_logic.py  # Logic tests
```

## Development Environment Setup

### Prerequisites
```bash
# Python 3.10+
python --version

# Required packages
pip install -r requirements.txt
```

### Configuration
1. Copy configuration template:
```python
# backend/core/cognitive_field_config.py
@dataclass
class CognitiveFieldConfig:
    field_params: FieldParameters = field(default_factory=FieldParameters)
    wave_params: WaveParameters = field(default_factory=WaveParameters)
```

2. Adjust parameters for your use case:
```python
# Example: High-precision configuration
config = CognitiveFieldConfig()
config.wave_params.WAVE_THICKNESS = 0.05  # Tighter collision detection
config.wave_params.PROPAGATION_SPEED = 0.5  # Slower, more precise waves
```

## Testing Strategy

### 1. Rigorous Logic Tests

Location: `tests/rigorous/test_cognitive_field_dynamics_logic.py`

**Purpose**: Validate core conceptual integrity

```python
@pytest.mark.asyncio
async def test_wave_propagation_and_impact():
    """Ensures waves only affect fields they physically reach"""
    # Test that temporal causality is respected
    # Verify collision detection accuracy
    # Validate resonance amplification
```

**Key Tests**:
- `test_add_geoid`: Field creation and normalization
- `test_interaction_symmetry`: Mutual interactions are symmetric
- `test_resonance_amplification`: Resonant fields strengthen over time
- `test_wave_propagation_and_impact`: True wave physics

### 2. Integration Tests

Location: `tests/integration/test_cognitive_field_dynamics_api.py`

**Purpose**: Validate API functionality and data flow

```python
def test_find_semantic_neighbors(setup_geoids):
    """Test neighbor discovery through API"""
    response = client.post("/cognitive-fields/neighbors/find", 
                          json={"geoid_id": "TEST_GEOID_1"})
    assert response.status_code == 200
```

**Key Tests**:
- API endpoint functionality
- Database integration
- Error handling
- JSON serialization
- Performance under load

### 3. Running Tests

```bash
# Run all CFD tests
pytest tests/integration/test_cognitive_field_dynamics_api.py tests/rigorous/test_cognitive_field_dynamics_logic.py -v

# Run specific test categories
pytest tests/rigorous/ -v                    # Logic tests only
pytest tests/integration/ -v                 # API tests only

# Run with coverage
pytest --cov=backend.engines.cognitive_field_dynamics tests/
```

## Best Practices

### 1. Configuration Management

- **Externalize all parameters**: Never hardcode physics constants
- **Use environment-specific configs**: Development vs. production settings
- **Version configurations**: Track parameter changes over time
- **Validate configurations**: Ensure parameters are within reasonable ranges

### 2. Error Handling

```python
class FieldEvolutionError(Exception):
    """Base exception for field evolution errors"""
    pass

class WaveCollisionError(FieldEvolutionError):
    """Error in wave-field collision detection"""
    pass

class ResonanceCalculationError(FieldEvolutionError):
    """Error in resonance frequency calculation"""
    pass
```

### 3. Performance Optimization

- **Wave Management**: Implement amplitude cutoffs to remove weak waves
- **Spatial Indexing**: Use KDTree for efficient neighbor queries
- **Parallel Processing**: Process wave chunks in parallel
- **Memory Management**: Monitor field and wave counts

## Contributing Guidelines

### 1. Code Style

Follow the existing patterns:
- Use dataclasses for data structures
- Implement async methods for evolution
- Add comprehensive docstrings
- Include type hints
- Convert numpy types to Python types for JSON serialization

### 2. Testing Requirements

- **Test physics principles**: Verify conservation laws, causality, symmetry
- **Test edge cases**: Empty fields, single field, very large fields
- **Test parameter sensitivity**: Ensure robust behavior across parameter ranges
- **Test performance**: Monitor computational complexity and memory usage

### 3. Documentation Requirements

- **Architecture changes**: Update `cognitive_field_dynamics.md`
- **API changes**: Update `cognitive_field_api.md`
- **New features**: Add examples and usage patterns
- **Configuration changes**: Document new parameters

## Troubleshooting

### Common Issues

1. **Tests failing with numpy serialization errors**
   - Convert all numpy types to Python types: `float(numpy_value)`

2. **Wave propagation not working**
   - Check `WAVE_THICKNESS` parameter (try increasing to 0.1)
   - Verify collision detection logic

3. **Performance degradation**
   - Monitor wave count (implement amplitude cutoff)
   - Check field count (consider spatial indexing)

4. **Resonance not amplifying fields**
   - Verify resonance frequency calculation
   - Check `RESONANCE_EFFECT_STRENGTH` parameter
   - Ensure waves are reaching target fields

### Debug Commands

```bash
# Run single test with verbose output
pytest tests/rigorous/test_cognitive_field_dynamics_logic.py::test_wave_propagation_and_impact -v -s

# Run API tests with debug
pytest tests/integration/test_cognitive_field_dynamics_api.py -v --tb=long
```

This development guide provides the foundation for extending and maintaining the Cognitive Field Dynamics system while preserving its conceptual integrity and performance characteristics. 