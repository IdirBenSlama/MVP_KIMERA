# Financial API Integration with KIMERA SWM

This guide shows how to connect various financial APIs to KIMERA SWM for real-world testing with market data, enabling sophisticated contradiction detection and semantic analysis of financial markets.

## 🎯 Overview

The financial integration allows you to:
- **Real-time Market Data**: Connect to stock, crypto, and forex APIs
- **Semantic Analysis**: Convert financial metrics to semantic features
- **Contradiction Detection**: Identify market anomalies and contradictions
- **Automated Monitoring**: Continuous market surveillance
- **Alert Systems**: Get notified of significant contradictions

## 🔧 Setup Instructions

### 1. Install Required Dependencies

```bash
# Install financial data libraries
pip install yfinance requests pandas numpy aiohttp

# Optional: For advanced technical analysis
pip install ta-lib pandas-ta

# For email alerts (optional)
pip install smtplib
```

### 2. Get API Keys (Free Options Available)

#### Alpha Vantage (Recommended for stocks)
- Visit: https://www.alphavantage.co/support/#api-key
- Free tier: 5 calls/minute, 500 calls/day
- Set environment variable: `ALPHA_VANTAGE_API_KEY`

#### Yahoo Finance (No API key needed)
- Uses `yfinance` library
- Free and unlimited for basic data
- Best for testing and development

#### CoinGecko (Cryptocurrency)
- Free tier available without API key
- Visit: https://www.coingecko.com/en/api
- 50 calls/minute for free tier

#### Polygon.io (Professional)
- Visit: https://polygon.io/
- Free tier: 5 calls/minute
- Set environment variable: `POLYGON_API_KEY`

### 3. Set Environment Variables

```bash
# Windows
set ALPHA_VANTAGE_API_KEY=your_key_here
set POLYGON_API_KEY=your_key_here

# Linux/Mac
export ALPHA_VANTAGE_API_KEY=your_key_here
export POLYGON_API_KEY=your_key_here
```

### 4. Start KIMERA SWM API

```bash
# Start the KIMERA API server
python run_kimera.py

# Verify it's running
curl http://localhost:8001/system/status
```

## 🚀 Quick Start Examples

### Example 1: Basic Stock Data Integration

```python
from financial_api_integration import YahooFinanceConnector, FinancialKimeraIntegrator

# Initialize connectors
yahoo = YahooFinanceConnector()
kimera = FinancialKimeraIntegrator()

# Fetch stock data
stock_data = yahoo.get_stock_data("AAPL")
print(f"AAPL Price: ${stock_data.price:.2f}")

# Create KIMERA geoid from stock data
result = kimera.create_kimera_geoid(stock_data)
print(f"Created geoid: {result['geoid_id']}")
```

### Example 2: Cryptocurrency Analysis

```python
from financial_api_integration import CoinGeckoConnector, FinancialKimeraIntegrator

# Initialize connectors
coingecko = CoinGeckoConnector()
kimera = FinancialKimeraIntegrator()

# Analyze multiple cryptocurrencies
cryptos = ["bitcoin", "ethereum", "cardano"]
geoid_ids = []

for crypto in cryptos:
    data = coingecko.get_crypto_data(crypto)
    result = kimera.create_kimera_geoid(data)
    geoid_ids.append(result['geoid_id'])
    print(f"{crypto.upper()}: ${data.price:.2f} -> {result['geoid_id']}")

# Detect contradictions between cryptocurrencies
contradiction_result = kimera.detect_financial_contradictions(cryptos)
print(f"Detected {contradiction_result['contradictions_detected']} contradictions")
```

### Example 3: Sector Analysis

```python
from financial_api_integration import FinancialKimeraIntegrator
from financial_config import MARKET_SECTORS

kimera = FinancialKimeraIntegrator()

# Analyze technology sector
tech_stocks = MARKET_SECTORS["technology"]
print(f"Analyzing {len(tech_stocks)} technology stocks...")

result = kimera.detect_financial_contradictions(tech_stocks)

if result['contradictions_detected'] > 0:
    print(f"🚨 Found {result['contradictions_detected']} contradictions in tech sector!")
    for analysis in result['analysis_results']:
        print(f"  - {analysis['tension']['type']}: {analysis['tension']['geoids_involved']}")
```

## 📊 Advanced Usage

### Real-time Market Monitoring

```python
# monitor_markets.py
import time
from datetime import datetime
from financial_api_integration import FinancialKimeraIntegrator
from financial_config import get_config

def monitor_markets():
    config = get_config()
    kimera = FinancialKimeraIntegrator(config.kimera_api_url)
    
    print("Starting real-time market monitoring...")
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Monitoring cycle starting...")
        
        # Monitor stocks
        stock_result = kimera.detect_financial_contradictions(config.stock_symbols[:5])
        
        # Monitor crypto
        crypto_result = kimera.detect_financial_contradictions(config.crypto_symbols[:5])
        
        total_contradictions = (
            stock_result.get('contradictions_detected', 0) + 
            crypto_result.get('contradictions_detected', 0)
        )
        
        if total_contradictions > 0:
            print(f"🚨 ALERT: {total_contradictions} contradictions detected!")
            # Add your alert logic here
        else:
            print("✅ No significant contradictions detected")
        
        time.sleep(config.update_interval)

if __name__ == "__main__":
    monitor_markets()
```

### Custom Contradiction Detection

```python
# custom_detector.py
from financial_api_integration import FinancialContradictionDetector, FinancialKimeraIntegrator

class CustomFinancialDetector(FinancialContradictionDetector):
    
    def detect_earnings_surprise_contradiction(self, symbol: str) -> dict:
        """Detect contradictions around earnings announcements"""
        # Implement custom logic for earnings-related contradictions
        pass
    
    def detect_macro_micro_divergence(self, market_data: list) -> dict:
        """Detect when individual stocks contradict market trends"""
        # Implement macro vs micro analysis
        pass
    
    def detect_sentiment_price_divergence(self, symbol: str) -> dict:
        """Detect when sentiment contradicts price action"""
        # Implement sentiment analysis contradiction detection
        pass

# Usage
kimera = FinancialKimeraIntegrator()
detector = CustomFinancialDetector(kimera)

# Use your custom detection methods
# result = detector.detect_earnings_surprise_contradiction("AAPL")
```

## 🔍 Semantic Feature Mapping

The system converts financial metrics to semantic features for KIMERA processing:

### Price Momentum
- **High (0.7-1.0)**: Strong upward price movement
- **Medium (0.3-0.7)**: Moderate price changes
- **Low (0.0-0.3)**: Minimal or negative price movement

### Volume Intensity
- **High (0.7-1.0)**: Unusually high trading volume
- **Medium (0.3-0.7)**: Normal trading volume
- **Low (0.0-0.3)**: Below-average volume

### Market Sentiment
- **Bullish (0.6-1.0)**: Positive market sentiment
- **Neutral (0.4-0.6)**: Mixed sentiment
- **Bearish (0.0-0.4)**: Negative sentiment

### Volatility
- **High (0.7-1.0)**: High price volatility
- **Medium (0.3-0.7)**: Normal volatility
- **Low (0.0-0.3)**: Low volatility

### Liquidity
- **High (0.7-1.0)**: Easy to buy/sell
- **Medium (0.3-0.7)**: Normal liquidity
- **Low (0.0-0.3)**: Difficult to trade

## 🚨 Contradiction Types Detected

### 1. Sector Divergence
```
Description: Stocks in the same sector moving in opposite directions
Example: AAPL up 5% while MSFT down 3% in tech sector
Threshold: >5% divergence
```

### 2. Volume-Price Mismatch
```
Description: High volume with minimal price movement
Example: 10x normal volume but <0.5% price change
Indicates: Possible manipulation or hidden information
```

### 3. Correlation Breakdown
```
Description: Historically correlated assets diverging
Example: Gold and USD both rising (usually inverse)
Indicates: Market regime change or anomaly
```

### 4. Cross-Asset Anomaly
```
Description: Unusual behavior across asset classes
Example: Stocks up, bonds up, dollar up simultaneously
Indicates: Potential market instability
```

## 📈 Example Contradiction Scenarios

### Scenario 1: Tech Sector Divergence
```python
# AAPL reports strong earnings, up 8%
# GOOGL reports weak earnings, down 6%
# KIMERA detects: "sector_divergence" contradiction
# System creates scar representing this market anomaly
```

### Scenario 2: Crypto Market Manipulation
```python
# Bitcoin volume spikes 500% but price moves <1%
# KIMERA detects: "volume_price_mismatch" contradiction
# System flags potential market manipulation
```

### Scenario 3: Safe Haven Breakdown
```python
# Market crashes but gold also falls (unusual)
# KIMERA detects: "correlation_breakdown" contradiction
# System identifies regime change in safe haven behavior
```

## 🔧 Configuration Options

### API Rate Limiting
```python
RATE_LIMITS = {
    "alpha_vantage": {"calls_per_minute": 5},
    "yahoo_finance": {"calls_per_minute": 60},
    "coingecko": {"calls_per_minute": 50}
}
```

### Monitoring Settings
```python
config = FinancialAPIConfig(
    update_interval=300,  # 5 minutes
    contradiction_threshold=0.7,
    stock_symbols=["AAPL", "GOOGL", "MSFT"],
    crypto_symbols=["bitcoin", "ethereum"]
)
```

### Alert Configuration
```python
ALERT_CONFIG = {
    "email": {"enabled": True, "recipients": ["trader@example.com"]},
    "webhook": {"enabled": True, "url": "https://hooks.slack.com/..."},
    "console": {"enabled": True, "log_level": "INFO"}
}
```

## 🧪 Testing Scenarios

### Test 1: Basic Integration
```bash
python financial_api_integration.py
```

### Test 2: Real-time Monitoring
```bash
python -c "
from financial_api_integration import run_continuous_monitoring
run_continuous_monitoring()
"
```

### Test 3: Specific Contradiction Detection
```bash
python -c "
from financial_api_integration import test_contradiction_detection
test_contradiction_detection()
"
```

## 📊 Expected KIMERA Outputs

### Successful Geoid Creation
```json
{
  "geoid_id": "GEOID_a1b2c3d4",
  "geoid": {
    "semantic_state": {
      "price_momentum": 0.75,
      "volume_intensity": 0.60,
      "market_sentiment": 0.80,
      "volatility": 0.45,
      "liquidity": 0.85
    },
    "symbolic_state": {
      "type": "financial_instrument",
      "symbol": "AAPL",
      "asset_class": "equity"
    }
  },
  "entropy": 2.34
}
```

### Contradiction Detection Result
```json
{
  "cycle": 15,
  "contradictions_detected": 3,
  "scars_created": 2,
  "analysis_results": [
    {
      "tension": {
        "geoids_involved": ["GEOID_aapl", "GEOID_googl"],
        "score": "0.847",
        "type": "semantic_divergence"
      },
      "pulse_strength": "0.723",
      "system_decision": "collapse",
      "scar_created": true
    }
  ]
}
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   Solution: Check environment variables and API key validity
   ```

2. **Rate Limiting**
   ```
   Error: Too many requests
   Solution: Implement rate limiting or upgrade API plan
   ```

3. **KIMERA Connection**
   ```
   Error: Connection refused to localhost:8001
   Solution: Ensure KIMERA API server is running
   ```

4. **Data Format Issues**
   ```
   Error: Invalid semantic features
   Solution: Check data normalization and feature ranges
   ```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from financial_api_integration import FinancialKimeraIntegrator
kimera = FinancialKimeraIntegrator()
# Test with mock data first
```

## 🎯 Next Steps

1. **Start with Yahoo Finance** (no API key required)
2. **Test basic geoid creation** with a few stocks
3. **Implement contradiction detection** for your use case
4. **Add real-time monitoring** for continuous analysis
5. **Customize contradiction patterns** for your trading strategy
6. **Integrate with your existing systems** via webhooks/alerts

## 📚 Additional Resources

- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [KIMERA SWM API Documentation](http://localhost:8001/docs)

This integration transforms KIMERA SWM into a powerful financial market analysis tool, capable of detecting subtle contradictions and anomalies that traditional systems might miss.