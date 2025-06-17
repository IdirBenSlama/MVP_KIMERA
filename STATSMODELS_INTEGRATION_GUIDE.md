# Statsmodels Integration Guide for Kimera SWM

## Overview

This guide documents the comprehensive integration of statsmodels into the Kimera SWM (Semantic Working Memory) system. Statsmodels provides advanced statistical modeling, econometric analysis, and time series forecasting capabilities that enhance the system's analytical power.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Components](#core-components)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Advanced Features](#advanced-features)
6. [Integration with Existing System](#integration-with-existing-system)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)

## Installation and Setup

### Prerequisites

Statsmodels has been added to the project requirements:

```
statsmodels>=0.14.0,<0.16.0
```

### Installation

```bash
pip install -r requirements.txt
```

### Verification

Run the integration test to verify proper installation:

```bash
python test_statsmodels_integration.py
```

## Core Components

### 1. Statistical Modeling Engine (`backend/core/statistical_modeling.py`)

The main engine that coordinates all statistical modeling capabilities:

- **SemanticTimeSeriesAnalyzer**: Advanced time series analysis for entropy patterns
- **ContradictionRegressionAnalyzer**: Regression analysis for contradiction factors
- **SemanticEconometrics**: Econometric modeling of semantic markets
- **StatisticalModelingEngine**: Main coordinator class

### 2. Advanced Statistical Monitor (`backend/monitoring/advanced_statistical_monitor.py`)

Real-time statistical monitoring system:

- **StatisticalProcessController**: Statistical process control with control charts
- **PredictiveMonitor**: Forecasting and predictive analytics
- **AdvancedStatisticalMonitor**: Main monitoring coordinator

### 3. API Integration (`backend/api/main.py`)

RESTful API endpoints for accessing statistical capabilities.

## API Endpoints

### Statistical Capabilities

#### GET `/statistics/capabilities`
Get available statistical modeling capabilities.

**Response:**
```json
{
  "statsmodels_available": true,
  "capabilities": {
    "time_series_analysis": true,
    "regression_modeling": true,
    "econometric_analysis": true,
    "regime_detection": true,
    "forecasting": true
  },
  "supported_models": ["ARIMA", "VAR", "OLS Regression", ...]
}
```

### Time Series Analysis

#### POST `/statistics/analyze/entropy_series`
Analyze entropy time series data.

**Request:**
```json
{
  "entropy_data": [2.1, 2.3, 2.0, 2.4, 2.2],
  "timestamps": ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z", ...]
}
```

**Response:**
```json
{
  "model_type": "entropy_time_series",
  "statistics": {
    "mean": 2.2,
    "std": 0.15,
    "adf_statistic": -3.45,
    "adf_pvalue": 0.01,
    "is_stationary": true,
    "trend_strength": 0.02
  },
  "predictions": [2.25, 2.27, 2.24, 2.26, 2.23],
  "diagnostics": {
    "arima_successful": true,
    "data_points": 100
  }
}
```

### Regression Analysis

#### POST `/statistics/analyze/contradiction_factors`
Analyze factors contributing to contradiction detection.

**Request:**
```json
{
  "contradiction_scores": [0.3, 0.7, 0.2, 0.8, 0.5],
  "semantic_features": {
    "complexity": [0.4, 0.8, 0.3, 0.9, 0.6],
    "coherence": [0.7, 0.3, 0.8, 0.2, 0.5]
  }
}
```

**Response:**
```json
{
  "model_type": "contradiction_regression",
  "statistics": {
    "r_squared": 0.85,
    "adj_r_squared": 0.82,
    "f_statistic": 15.3,
    "f_pvalue": 0.001
  },
  "parameters": {
    "complexity_coef": 0.45,
    "complexity_pvalue": 0.02,
    "coherence_coef": -0.32,
    "coherence_pvalue": 0.05
  }
}
```

### Econometric Analysis

#### POST `/statistics/analyze/semantic_market`
Analyze semantic market dynamics.

**Request:**
```json
{
  "semantic_supply": [2.1, 2.3, 2.0, 2.4],
  "semantic_demand": [1.8, 2.1, 1.9, 2.2],
  "entropy_prices": [2.0, 2.2, 1.95, 2.3]
}
```

**Response:**
```json
{
  "model_type": "semantic_econometrics",
  "statistics": {
    "supply_price_elasticity": 0.65,
    "demand_price_elasticity": -0.42,
    "market_efficiency": 1.07,
    "supply_r_squared": 0.78,
    "demand_r_squared": 0.71
  }
}
```

### Comprehensive Analysis

#### POST `/statistics/analyze/comprehensive`
Perform comprehensive statistical analysis.

**Request:**
```json
{
  "entropy_history": [2.1, 2.3, 2.0, 2.4, 2.2],
  "timestamps": ["2024-01-01T00:00:00Z", ...],
  "contradiction_scores": [0.3, 0.7, 0.2, 0.8, 0.5],
  "semantic_features": {
    "complexity": [0.4, 0.8, 0.3, 0.9, 0.6]
  },
  "semantic_supply": [2.1, 2.3, 2.0, 2.4, 2.2],
  "semantic_demand": [1.8, 2.1, 1.9, 2.2, 2.0],
  "entropy_prices": [2.0, 2.2, 1.95, 2.3, 2.1]
}
```

### Statistical Monitoring

#### GET `/statistics/monitoring/status`
Get status of advanced statistical monitoring.

#### POST `/statistics/monitoring/start`
Start advanced statistical monitoring.

#### POST `/statistics/monitoring/stop`
Stop advanced statistical monitoring.

#### GET `/statistics/monitoring/alerts`
Get recent statistical alerts.

**Query Parameters:**
- `severity`: Filter by severity (low, medium, high, critical)
- `hours`: Time window in hours (default: 24)

#### GET `/statistics/monitoring/forecast/{metric_name}`
Get forecast for a specific metric.

### System Analysis

#### GET `/statistics/system/entropy_analysis`
Get real-time entropy analysis of the current system state.

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL for your Kimera SWM instance
base_url = "http://localhost:8000"

# Check statistical capabilities
response = requests.get(f"{base_url}/statistics/capabilities")
capabilities = response.json()
print(f"Statsmodels available: {capabilities['statsmodels_available']}")

# Analyze entropy time series
entropy_data = [2.1, 2.3, 2.0, 2.4, 2.2, 2.1, 2.5, 2.3]
response = requests.post(
    f"{base_url}/statistics/analyze/entropy_series",
    json={"entropy_data": entropy_data}
)
analysis = response.json()
print(f"Mean entropy: {analysis['statistics']['mean']:.3f}")
print(f"Is stationary: {analysis['statistics']['is_stationary']}")

# Start statistical monitoring
response = requests.post(f"{base_url}/statistics/monitoring/start")
print(f"Monitoring status: {response.json()['status']}")

# Get system entropy analysis
response = requests.get(f"{base_url}/statistics/system/entropy_analysis")
system_analysis = response.json()
print(f"Current system entropy: {system_analysis['current_system_entropy']}")
```

### JavaScript Client Example

```javascript
const baseUrl = 'http://localhost:8000';

// Check capabilities
async function checkCapabilities() {
    const response = await fetch(`${baseUrl}/statistics/capabilities`);
    const capabilities = await response.json();
    console.log('Statistical capabilities:', capabilities);
}

// Analyze contradiction factors
async function analyzeContradictions() {
    const data = {
        contradiction_scores: [0.3, 0.7, 0.2, 0.8, 0.5],
        semantic_features: {
            complexity: [0.4, 0.8, 0.3, 0.9, 0.6],
            coherence: [0.7, 0.3, 0.8, 0.2, 0.5]
        }
    };
    
    const response = await fetch(`${baseUrl}/statistics/analyze/contradiction_factors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    const analysis = await response.json();
    console.log('R-squared:', analysis.statistics.r_squared);
}

// Get monitoring alerts
async function getAlerts() {
    const response = await fetch(`${baseUrl}/statistics/monitoring/alerts?severity=high`);
    const alerts = await response.json();
    console.log(`Found ${alerts.total_alerts} high-severity alerts`);
}
```

## Advanced Features

### 1. Time Series Analysis

- **ARIMA Modeling**: Automatic parameter selection for entropy forecasting
- **Stationarity Testing**: Augmented Dickey-Fuller and KPSS tests
- **Seasonal Decomposition**: Trend, seasonal, and residual components
- **Regime Change Detection**: Structural break identification

### 2. Regression Modeling

- **Multiple Regression**: Analyze multiple semantic features simultaneously
- **Diagnostic Testing**: Durbin-Watson, outlier detection, influence measures
- **Model Selection**: Automatic feature selection and validation

### 3. Econometric Analysis

- **Supply and Demand Modeling**: Semantic market equilibrium analysis
- **Price Elasticity**: Measure responsiveness to entropy changes
- **Market Efficiency**: Assess semantic information market dynamics

### 4. Statistical Process Control

- **Control Charts**: 3-sigma control limits with warning zones
- **Anomaly Detection**: Statistical outlier identification
- **Process Capability**: Measure system stability and predictability

### 5. Predictive Analytics

- **Forecasting**: Multi-step ahead predictions with confidence intervals
- **Early Warning**: Predictive alerts for potential system issues
- **Trend Analysis**: Long-term pattern identification

## Integration with Existing System

### Entropy Monitoring Integration

The statsmodels integration seamlessly works with existing entropy monitoring:

```python
from backend.monitoring.entropy_monitor import EntropyMonitor
from backend.monitoring.advanced_statistical_monitor import initialize_advanced_monitoring

# Initialize with existing monitors
entropy_monitor = EntropyMonitor()
advanced_monitor = initialize_advanced_monitoring(entropy_monitor)

# Start advanced monitoring
advanced_monitor.start_monitoring()
```

### Native Math Compatibility

Statsmodels integration maintains full compatibility with native math implementations:

```python
from backend.core.native_math import NativeStats
from backend.core.statistical_modeling import analyze_entropy_time_series

# Native calculation
native_entropy = NativeStats.entropy([0.25, 0.25, 0.25, 0.25])

# Advanced analysis (falls back to native if statsmodels unavailable)
result = analyze_entropy_time_series([2.1, 2.3, 2.0, 2.4])
```

### Vault System Integration

Statistical analysis integrates with the vault system for SCAR analysis:

```python
# Analyze SCAR patterns
vault_manager = kimera_system['vault_manager']
scars = vault_manager.get_scars_from_vault("vault_a", limit=100)

# Extract contradiction scores and features
contradiction_scores = [scar.mutation_frequency for scar in scars]
semantic_features = {
    'entropy_delta': [scar.delta_entropy for scar in scars],
    'cls_angle': [scar.cls_angle for scar in scars]
}

# Analyze factors
result = analyze_contradiction_factors(contradiction_scores, semantic_features)
```

## Performance Considerations

### Memory Usage

- Statsmodels models are cached to avoid recomputation
- Large datasets are processed in chunks
- Memory-efficient algorithms are used for time series analysis

### Computational Complexity

- ARIMA fitting: O(n³) for parameter estimation
- Regression analysis: O(n²p) where p is number of features
- Control chart updates: O(1) amortized

### Optimization Tips

1. **Batch Processing**: Process multiple analyses together
2. **Caching**: Results are cached for repeated queries
3. **Fallback**: Native implementations used when statsmodels unavailable
4. **Async Processing**: Long-running analyses don't block API

### Performance Benchmarks

Based on test results:
- Native calculations: ~0.001s for 1000 data points
- Statsmodels ARIMA: ~0.1s for 100 data points
- Regression analysis: ~0.05s for 50 observations

## Troubleshooting

### Common Issues

#### 1. Statsmodels Not Available

**Error**: `ModuleNotFoundError: No module named 'statsmodels'`

**Solution**:
```bash
pip install statsmodels>=0.14.0
```

#### 2. Insufficient Data for Analysis

**Error**: Analysis returns basic fallback results

**Solution**: Ensure sufficient data points:
- Time series analysis: minimum 10 points
- Regression analysis: minimum 5 observations
- ARIMA modeling: minimum 20 points

#### 3. Convergence Issues

**Error**: ARIMA model fails to converge

**Solution**: 
- Check for missing values in data
- Ensure data is properly formatted
- Try different ARIMA parameters

#### 4. Memory Issues with Large Datasets

**Error**: Out of memory during analysis

**Solution**:
- Process data in smaller chunks
- Use sampling for very large datasets
- Increase system memory allocation

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis with detailed logging
result = analyze_entropy_time_series(entropy_data)
```

### Validation

Validate integration:

```bash
# Run comprehensive test suite
python test_statsmodels_integration.py

# Check specific functionality
python -c "from backend.core.statistical_modeling import statistical_engine; print(statistical_engine.get_model_summary())"
```

## Best Practices

### 1. Data Quality

- Ensure data is clean and properly formatted
- Handle missing values appropriately
- Validate data ranges and distributions

### 2. Model Selection

- Use appropriate models for your data characteristics
- Validate model assumptions
- Consider computational complexity vs. accuracy trade-offs

### 3. Monitoring

- Set up appropriate alert thresholds
- Monitor model performance over time
- Regularly validate forecasting accuracy

### 4. Integration

- Use fallback mechanisms for robustness
- Cache results for performance
- Implement proper error handling

## Future Enhancements

### Planned Features

1. **Advanced Time Series Models**: VAR, GARCH, state space models
2. **Machine Learning Integration**: Combine with scikit-learn models
3. **Bayesian Analysis**: Bayesian regression and time series
4. **Causal Inference**: Structural equation modeling
5. **Real-time Streaming**: Online learning and adaptation

### Extensibility

The statsmodels integration is designed to be extensible:

```python
# Add custom analysis
class CustomAnalyzer:
    def analyze(self, data):
        # Custom statsmodels analysis
        pass

# Register with engine
statistical_engine.register_analyzer('custom', CustomAnalyzer())
```

## Conclusion

The statsmodels integration significantly enhances Kimera SWM's analytical capabilities, providing:

- Advanced statistical modeling for semantic analysis
- Real-time monitoring with statistical process control
- Predictive analytics for proactive system management
- Econometric modeling of semantic markets
- Comprehensive time series analysis of entropy patterns

This integration maintains full backward compatibility while adding powerful new capabilities for understanding and optimizing semantic working memory systems.

For additional support or questions, refer to the test suite and example implementations provided in the codebase.