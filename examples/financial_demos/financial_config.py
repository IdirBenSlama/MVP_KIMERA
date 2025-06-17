"""
Configuration and setup for Financial API Integration with KIMERA SWM
"""

import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FinancialAPIConfig:
    """Configuration for financial API connections"""
    
    # API Keys (set these as environment variables)
    alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    polygon_key: str = os.getenv("POLYGON_API_KEY", "")
    finnhub_key: str = os.getenv("FINNHUB_API_KEY", "")
    
    # KIMERA connection
    kimera_api_url: str = "http://localhost:8001"
    
    # Monitoring settings
    update_interval: int = 300  # 5 minutes
    contradiction_threshold: float = 0.7
    
    # Asset lists for monitoring
    stock_symbols: List[str] = None
    crypto_symbols: List[str] = None
    forex_pairs: List[str] = None
    
    def __post_init__(self):
        if self.stock_symbols is None:
            self.stock_symbols = [
                "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
                "NVDA", "META", "NFLX", "AMD", "INTC"
            ]
        
        if self.crypto_symbols is None:
            self.crypto_symbols = [
                "bitcoin", "ethereum", "cardano", "polkadot", "chainlink",
                "litecoin", "stellar", "dogecoin", "solana", "avalanche-2"
            ]
        
        if self.forex_pairs is None:
            self.forex_pairs = [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"
            ]


# Market sectors for contradiction analysis
MARKET_SECTORS = {
    "technology": ["AAPL", "GOOGL", "MSFT", "NVDA", "AMD", "INTC", "META"],
    "automotive": ["TSLA", "F", "GM", "NIO", "RIVN"],
    "finance": ["JPM", "BAC", "WFC", "GS", "MS"],
    "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
    "energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
    "retail": ["AMZN", "WMT", "TGT", "COST", "HD"]
}

# Cryptocurrency categories
CRYPTO_CATEGORIES = {
    "layer1": ["bitcoin", "ethereum", "cardano", "solana", "avalanche-2"],
    "defi": ["uniswap", "aave", "compound-governance-token", "maker"],
    "oracle": ["chainlink", "band-protocol", "api3"],
    "storage": ["filecoin", "storj", "siacoin"],
    "privacy": ["monero", "zcash", "dash"]
}

# Financial indicators for semantic mapping
FINANCIAL_INDICATORS = {
    "momentum": ["RSI", "MACD", "Stochastic", "Williams %R"],
    "trend": ["SMA", "EMA", "Bollinger Bands", "Ichimoku"],
    "volume": ["OBV", "Volume Profile", "VWAP", "Accumulation/Distribution"],
    "volatility": ["ATR", "VIX", "Standard Deviation", "Beta"]
}

# Contradiction patterns to detect
CONTRADICTION_PATTERNS = {
    "sector_divergence": {
        "description": "Stocks in same sector moving in opposite directions",
        "threshold": 5.0,  # 5% divergence
        "severity": "medium"
    },
    "volume_price_mismatch": {
        "description": "High volume with minimal price movement",
        "threshold": 0.8,  # Volume intensity > 0.8, price change < 0.5%
        "severity": "high"
    },
    "correlation_breakdown": {
        "description": "Historically correlated assets diverging",
        "threshold": 0.3,  # Correlation drops below 0.3
        "severity": "high"
    },
    "fundamental_technical_divergence": {
        "description": "Technical indicators contradicting fundamental data",
        "threshold": 0.6,
        "severity": "medium"
    },
    "cross_asset_anomaly": {
        "description": "Unusual behavior across asset classes",
        "threshold": 0.7,
        "severity": "high"
    }
}

# Semantic feature mappings for financial data
SEMANTIC_MAPPINGS = {
    "price_momentum": {
        "positive_range": (0.6, 1.0),
        "neutral_range": (0.4, 0.6),
        "negative_range": (0.0, 0.4)
    },
    "volume_intensity": {
        "high_range": (0.7, 1.0),
        "medium_range": (0.3, 0.7),
        "low_range": (0.0, 0.3)
    },
    "market_sentiment": {
        "bullish_range": (0.6, 1.0),
        "neutral_range": (0.4, 0.6),
        "bearish_range": (0.0, 0.4)
    },
    "volatility": {
        "high_range": (0.7, 1.0),
        "medium_range": (0.3, 0.7),
        "low_range": (0.0, 0.3)
    },
    "liquidity": {
        "high_range": (0.7, 1.0),
        "medium_range": (0.3, 0.7),
        "low_range": (0.0, 0.3)
    }
}

# Alert configurations
ALERT_CONFIG = {
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": os.getenv("EMAIL_USERNAME", ""),
        "password": os.getenv("EMAIL_PASSWORD", ""),
        "recipients": []
    },
    "webhook": {
        "enabled": False,
        "url": os.getenv("WEBHOOK_URL", ""),
        "headers": {"Content-Type": "application/json"}
    },
    "console": {
        "enabled": True,
        "log_level": "INFO"
    }
}

# Rate limiting for API calls
RATE_LIMITS = {
    "alpha_vantage": {
        "calls_per_minute": 5,
        "calls_per_day": 500
    },
    "yahoo_finance": {
        "calls_per_minute": 60,
        "calls_per_day": 2000
    },
    "coingecko": {
        "calls_per_minute": 50,
        "calls_per_day": 10000
    },
    "polygon": {
        "calls_per_minute": 5,
        "calls_per_day": 1000
    }
}

def get_config() -> FinancialAPIConfig:
    """Get the financial API configuration"""
    return FinancialAPIConfig()

def validate_config(config: FinancialAPIConfig) -> Dict[str, bool]:
    """Validate the configuration"""
    validation = {
        "alpha_vantage_key": bool(config.alpha_vantage_key),
        "kimera_connection": True,  # Will be tested at runtime
        "stock_symbols": len(config.stock_symbols) > 0,
        "crypto_symbols": len(config.crypto_symbols) > 0
    }
    return validation

def print_config_status():
    """Print configuration status"""
    config = get_config()
    validation = validate_config(config)
    
    print("Financial API Configuration Status:")
    print("=" * 40)
    
    for key, status in validation.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {key.replace('_', ' ').title()}: {status}")
    
    print(f"\nMonitoring {len(config.stock_symbols)} stocks")
    print(f"Monitoring {len(config.crypto_symbols)} cryptocurrencies")
    print(f"Update interval: {config.update_interval} seconds")
    print(f"KIMERA API URL: {config.kimera_api_url}")

if __name__ == "__main__":
    print_config_status()