"""
Financial API Integration for KIMERA SWM Testing

This module demonstrates how to connect various financial APIs to KIMERA SWM
for real-world contradiction detection and semantic analysis.
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass
import asyncio
import aiohttp

# KIMERA imports
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.geoid import GeoidState
from backend.core.embedding_utils import encode_text
from backend.vault.database import SessionLocal, GeoidDB


@dataclass
class FinancialDataPoint:
    """Represents a financial data point for KIMERA processing"""
    symbol: str
    price: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    sentiment_score: Optional[float]
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]


class FinancialAPIConnector:
    """Base class for financial API connections"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Generic API fetch method"""
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {}


class AlphaVantageConnector(FinancialAPIConnector):
    """Alpha Vantage API connector for stock data"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://www.alphavantage.co/query")
    
    def get_stock_quote(self, symbol: str) -> FinancialDataPoint:
        """Get real-time stock quote"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        data = self.fetch_data("", params)
        quote = data.get('Global Quote', {})
        
        return FinancialDataPoint(
            symbol=symbol,
            price=float(quote.get('05. price', 0)),
            volume=int(quote.get('06. volume', 0)),
            market_cap=None,
            pe_ratio=None,
            sentiment_score=None,
            timestamp=datetime.now(),
            source="alphavantage",
            metadata={
                'change': quote.get('09. change', '0'),
                'change_percent': quote.get('10. change percent', '0%'),
                'previous_close': quote.get('08. previous close', '0')
            }
        )
    
    def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        return self.fetch_data("", params)


class YahooFinanceConnector(FinancialAPIConnector):
    """Yahoo Finance API connector (using yfinance library)"""
    
    def __init__(self):
        super().__init__()
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            print("yfinance not installed. Run: pip install yfinance")
            self.yf = None
    
    def get_stock_data(self, symbol: str) -> FinancialDataPoint:
        """Get stock data from Yahoo Finance"""
        if not self.yf:
            return None
        
        ticker = self.yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        current_price = hist['Close'].iloc[-1] if not hist.empty else 0
        volume = hist['Volume'].iloc[-1] if not hist.empty else 0
        
        return FinancialDataPoint(
            symbol=symbol,
            price=float(current_price),
            volume=int(volume),
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE'),
            sentiment_score=None,
            timestamp=datetime.now(),
            source="yahoo_finance",
            metadata={
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'country': info.get('country', ''),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield')
            }
        )


class CoinGeckoConnector(FinancialAPIConnector):
    """CoinGecko API connector for cryptocurrency data"""
    
    def __init__(self):
        super().__init__(base_url="https://api.coingecko.com/api/v3")
    
    def get_crypto_data(self, coin_id: str) -> FinancialDataPoint:
        """Get cryptocurrency data"""
        data = self.fetch_data(f"coins/{coin_id}")
        
        market_data = data.get('market_data', {})
        current_price = market_data.get('current_price', {}).get('usd', 0)
        
        return FinancialDataPoint(
            symbol=coin_id.upper(),
            price=float(current_price),
            volume=int(market_data.get('total_volume', {}).get('usd', 0)),
            market_cap=market_data.get('market_cap', {}).get('usd'),
            pe_ratio=None,
            sentiment_score=data.get('sentiment_votes_up_percentage'),
            timestamp=datetime.now(),
            source="coingecko",
            metadata={
                'rank': data.get('market_cap_rank'),
                'price_change_24h': market_data.get('price_change_percentage_24h'),
                'ath': market_data.get('ath', {}).get('usd'),
                'atl': market_data.get('atl', {}).get('usd')
            }
        )


class FinancialKimeraIntegrator:
    """Integrates financial data with KIMERA SWM system"""
    
    def __init__(self, kimera_api_url: str = "http://localhost:8001"):
        self.kimera_api_url = kimera_api_url
        self.session = requests.Session()
    
    def financial_data_to_geoid(self, data_point: FinancialDataPoint) -> Dict:
        """Convert financial data to KIMERA geoid format"""
        
        # Normalize financial metrics to 0-1 range for semantic features
        semantic_features = {
            "price_momentum": self._normalize_price_change(data_point),
            "volume_intensity": self._normalize_volume(data_point),
            "market_sentiment": self._calculate_sentiment(data_point),
            "volatility": self._calculate_volatility(data_point),
            "liquidity": self._calculate_liquidity(data_point)
        }
        
        # Create symbolic content
        symbolic_content = {
            "type": "financial_instrument",
            "symbol": data_point.symbol,
            "asset_class": self._determine_asset_class(data_point),
            "price": data_point.price,
            "timestamp": data_point.timestamp.isoformat()
        }
        
        # Create metadata
        metadata = {
            "source": data_point.source,
            "data_timestamp": data_point.timestamp.isoformat(),
            "financial_metrics": {
                "market_cap": data_point.market_cap,
                "pe_ratio": data_point.pe_ratio,
                "volume": data_point.volume
            },
            **data_point.metadata
        }
        
        return {
            "semantic_features": semantic_features,
            "symbolic_content": symbolic_content,
            "metadata": metadata
        }
    
    def _normalize_price_change(self, data_point: FinancialDataPoint) -> float:
        """Normalize price change to 0-1 range"""
        change_str = data_point.metadata.get('change', '0')
        try:
            change = float(change_str.replace('%', ''))
            # Map -10% to +10% change to 0-1 range
            return max(0, min(1, (change + 10) / 20))
        except:
            return 0.5  # Neutral if can't parse
    
    def _normalize_volume(self, data_point: FinancialDataPoint) -> float:
        """Normalize volume to 0-1 range"""
        if data_point.volume == 0:
            return 0
        # Use log scale for volume normalization
        log_volume = np.log10(max(1, data_point.volume))
        return min(1, log_volume / 10)  # Assume max log volume of 10
    
    def _calculate_sentiment(self, data_point: FinancialDataPoint) -> float:
        """Calculate sentiment score"""
        if data_point.sentiment_score is not None:
            return data_point.sentiment_score / 100
        
        # Fallback: use price change as sentiment proxy
        change_str = data_point.metadata.get('change_percent', '0%')
        try:
            change = float(change_str.replace('%', ''))
            return max(0, min(1, (change + 5) / 10))  # -5% to +5% mapped to 0-1
        except:
            return 0.5
    
    def _calculate_volatility(self, data_point: FinancialDataPoint) -> float:
        """Calculate volatility proxy"""
        beta = data_point.metadata.get('beta')
        if beta is not None:
            return min(1, max(0, beta / 2))  # Beta of 2 = max volatility
        return 0.5  # Default moderate volatility
    
    def _calculate_liquidity(self, data_point: FinancialDataPoint) -> float:
        """Calculate liquidity score"""
        if data_point.volume == 0:
            return 0
        if data_point.market_cap and data_point.market_cap > 0:
            # Volume to market cap ratio as liquidity proxy
            ratio = data_point.volume * data_point.price / data_point.market_cap
            return min(1, ratio * 100)  # Scale appropriately
        return self._normalize_volume(data_point)
    
    def _determine_asset_class(self, data_point: FinancialDataPoint) -> str:
        """Determine asset class from data source"""
        if data_point.source == "coingecko":
            return "cryptocurrency"
        elif data_point.source in ["alphavantage", "yahoo_finance"]:
            return "equity"
        else:
            return "unknown"
    
    def create_kimera_geoid(self, data_point: FinancialDataPoint) -> Dict:
        """Create a geoid in KIMERA from financial data"""
        geoid_data = self.financial_data_to_geoid(data_point)
        
        try:
            response = self.session.post(
                f"{self.kimera_api_url}/geoids",
                json=geoid_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating KIMERA geoid: {e}")
            return {}
    
    def detect_financial_contradictions(self, symbols: List[str]) -> Dict:
        """Detect contradictions between financial instruments"""
        geoid_ids = []
        
        # Create geoids for each symbol
        for symbol in symbols:
            # You would fetch real data here
            # For demo, creating mock data
            mock_data = self._create_mock_financial_data(symbol)
            result = self.create_kimera_geoid(mock_data)
            if result.get('geoid_id'):
                geoid_ids.append(result['geoid_id'])
        
        if len(geoid_ids) < 2:
            return {"error": "Need at least 2 geoids for contradiction detection"}
        
        # Trigger contradiction processing
        try:
            response = self.session.post(
                f"{self.kimera_api_url}/process/contradictions",
                json={
                    "trigger_geoid_id": geoid_ids[0],
                    "search_limit": len(geoid_ids)
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error processing contradictions: {e}")
            return {}
    
    def _create_mock_financial_data(self, symbol: str) -> FinancialDataPoint:
        """Create mock financial data for testing"""
        import random
        
        return FinancialDataPoint(
            symbol=symbol,
            price=random.uniform(10, 1000),
            volume=random.randint(1000000, 100000000),
            market_cap=random.randint(1000000000, 1000000000000),
            pe_ratio=random.uniform(5, 50),
            sentiment_score=random.uniform(0, 100),
            timestamp=datetime.now(),
            source="mock",
            metadata={
                "change": f"{random.uniform(-5, 5):.2f}",
                "change_percent": f"{random.uniform(-5, 5):.2f}%",
                "sector": random.choice(["Technology", "Finance", "Healthcare", "Energy"])
            }
        )


class FinancialContradictionDetector:
    """Specialized contradiction detection for financial data"""
    
    def __init__(self, integrator: FinancialKimeraIntegrator):
        self.integrator = integrator
    
    def detect_market_anomalies(self, market_data: List[FinancialDataPoint]) -> List[Dict]:
        """Detect market anomalies that could create contradictions"""
        anomalies = []
        
        for i, data1 in enumerate(market_data):
            for j, data2 in enumerate(market_data[i+1:], i+1):
                contradiction = self._analyze_pair_contradiction(data1, data2)
                if contradiction:
                    anomalies.append(contradiction)
        
        return anomalies
    
    def _analyze_pair_contradiction(self, data1: FinancialDataPoint, data2: FinancialDataPoint) -> Optional[Dict]:
        """Analyze potential contradiction between two financial instruments"""
        
        # Price divergence in same sector
        if (data1.metadata.get('sector') == data2.metadata.get('sector') and
            data1.metadata.get('sector') is not None):
            
            change1 = self._extract_change_percent(data1)
            change2 = self._extract_change_percent(data2)
            
            if abs(change1 - change2) > 5:  # 5% divergence threshold
                return {
                    "type": "sector_divergence",
                    "symbols": [data1.symbol, data2.symbol],
                    "sector": data1.metadata.get('sector'),
                    "divergence": abs(change1 - change2),
                    "description": f"{data1.symbol} and {data2.symbol} showing divergent behavior in {data1.metadata.get('sector')} sector"
                }
        
        # Volume vs Price contradiction
        if self._detect_volume_price_contradiction(data1):
            return {
                "type": "volume_price_contradiction",
                "symbol": data1.symbol,
                "description": f"{data1.symbol} showing unusual volume-price relationship"
            }
        
        return None
    
    def _extract_change_percent(self, data: FinancialDataPoint) -> float:
        """Extract percentage change from metadata"""
        change_str = data.metadata.get('change_percent', '0%')
        try:
            return float(change_str.replace('%', ''))
        except:
            return 0
    
    def _detect_volume_price_contradiction(self, data: FinancialDataPoint) -> bool:
        """Detect volume-price contradictions"""
        # High volume with minimal price change could indicate manipulation
        change = abs(self._extract_change_percent(data))
        volume_intensity = self.integrator._normalize_volume(data)
        
        return volume_intensity > 0.8 and change < 0.5


# Example usage and testing functions

def test_alpha_vantage_integration():
    """Test Alpha Vantage integration"""
    # You need to get a free API key from https://www.alphavantage.co/support/#api-key
    api_key = "YOUR_ALPHA_VANTAGE_API_KEY"
    
    if api_key == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Please set your Alpha Vantage API key")
        return
    
    connector = AlphaVantageConnector(api_key)
    integrator = FinancialKimeraIntegrator()
    
    # Test with major stocks
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        print(f"\nFetching data for {symbol}...")
        data = connector.get_stock_quote(symbol)
        print(f"Price: ${data.price}, Volume: {data.volume:,}")
        
        # Create KIMERA geoid
        result = integrator.create_kimera_geoid(data)
        if result.get('geoid_id'):
            print(f"Created KIMERA geoid: {result['geoid_id']}")


def test_yahoo_finance_integration():
    """Test Yahoo Finance integration"""
    connector = YahooFinanceConnector()
    integrator = FinancialKimeraIntegrator()
    
    symbols = ["AAPL", "TSLA", "NVDA"]
    
    for symbol in symbols:
        print(f"\nFetching Yahoo Finance data for {symbol}...")
        data = connector.get_stock_data(symbol)
        if data:
            print(f"Price: ${data.price:.2f}, Market Cap: ${data.market_cap:,}")
            
            # Create KIMERA geoid
            result = integrator.create_kimera_geoid(data)
            if result.get('geoid_id'):
                print(f"Created KIMERA geoid: {result['geoid_id']}")


def test_crypto_integration():
    """Test cryptocurrency integration"""
    connector = CoinGeckoConnector()
    integrator = FinancialKimeraIntegrator()
    
    crypto_ids = ["bitcoin", "ethereum", "cardano"]
    
    for crypto_id in crypto_ids:
        print(f"\nFetching crypto data for {crypto_id}...")
        data = connector.get_crypto_data(crypto_id)
        print(f"Price: ${data.price:.2f}, Market Cap: ${data.market_cap:,}")
        
        # Create KIMERA geoid
        result = integrator.create_kimera_geoid(data)
        if result.get('geoid_id'):
            print(f"Created KIMERA geoid: {result['geoid_id']}")


def test_contradiction_detection():
    """Test financial contradiction detection"""
    integrator = FinancialKimeraIntegrator()
    
    # Test with mock data
    symbols = ["AAPL", "GOOGL", "TSLA", "BTC", "ETH"]
    
    print("\nTesting financial contradiction detection...")
    result = integrator.detect_financial_contradictions(symbols)
    
    if result.get('contradictions_detected'):
        print(f"Detected {result['contradictions_detected']} contradictions")
        print(f"Created {result['scars_created']} scars")
        
        for analysis in result.get('analysis_results', []):
            tension = analysis['tension']
            print(f"\nContradiction between {tension['geoids_involved']}")
            print(f"Type: {tension['type']}, Score: {tension['score']}")
            print(f"Decision: {analysis['system_decision']}")


def run_continuous_monitoring():
    """Run continuous financial monitoring"""
    integrator = FinancialKimeraIntegrator()
    
    # Symbols to monitor
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    
    print("Starting continuous financial monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Monitoring cycle")
            
            # Create mock data and process
            result = integrator.detect_financial_contradictions(symbols)
            
            if result.get('contradictions_detected', 0) > 0:
                print(f"🚨 Alert: {result['contradictions_detected']} contradictions detected!")
                
                # You could add alerting logic here
                # send_alert(result)
            
            time.sleep(300)  # Wait 5 minutes
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")


if __name__ == "__main__":
    print("Financial API Integration for KIMERA SWM")
    print("=" * 50)
    
    # Test different integrations
    print("\n1. Testing Yahoo Finance integration...")
    test_yahoo_finance_integration()
    
    print("\n2. Testing cryptocurrency integration...")
    test_crypto_integration()
    
    print("\n3. Testing contradiction detection...")
    test_contradiction_detection()
    
    # Uncomment to run continuous monitoring
    # run_continuous_monitoring()