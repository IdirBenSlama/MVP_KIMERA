#!/usr/bin/env python3
"""
KIMERA SWM Real Market Case Study
Using Alpha Vantage API for live financial data analysis

This case study demonstrates:
1. Real-time market data ingestion
2. Semantic contradiction detection in financial markets
3. Cross-asset correlation analysis
4. Volatility pattern recognition
5. Market sentiment analysis through KIMERA's cognitive architecture
"""

import asyncio
import aiohttp
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_market_case_study.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Represents a single market data point"""
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    change_percent: float
    volatility: float
    rsi: Optional[float] = None
    macd: Optional[float] = None
    
@dataclass
class ContradictionEvent:
    """Represents a detected market contradiction"""
    event_id: str
    timestamp: datetime
    contradiction_type: str
    severity: str
    description: str
    affected_assets: List[str]
    confidence_score: float
    semantic_features: Dict[str, float]
    
@dataclass
class CaseStudyResults:
    """Results of the case study analysis"""
    study_period: Tuple[datetime, datetime]
    total_data_points: int
    contradictions_detected: int
    market_events_identified: int
    correlation_breakdowns: int
    volatility_spikes: int
    semantic_insights: List[Dict]
    performance_metrics: Dict[str, float]

class AlphaVantageClient:
    """Client for Alpha Vantage API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.session = None
        self.rate_limit_delay = 12  # Alpha Vantage free tier: 5 calls per minute
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> Dict:
        """Get intraday stock data"""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
            await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
            return data
    
    async def get_daily_data(self, symbol: str) -> Dict:
        """Get daily stock data"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
            await asyncio.sleep(self.rate_limit_delay)
            return data
    
    async def get_technical_indicators(self, symbol: str, indicator: str, **kwargs) -> Dict:
        """Get technical indicators"""
        params = {
            "function": indicator,
            "symbol": symbol,
            "apikey": self.api_key,
            **kwargs
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            data = await response.json()
            await asyncio.sleep(self.rate_limit_delay)
            return data

class KimeraFinancialAnalyzer:
    """KIMERA-powered financial market analyzer"""
    
    def __init__(self, alpha_vantage_key: str, kimera_api_url: str = "http://localhost:8001"):
        self.av_key = alpha_vantage_key
        self.kimera_url = kimera_api_url
        self.market_data: Dict[str, List[MarketDataPoint]] = {}
        self.contradictions: List[ContradictionEvent] = []
        self.correlation_matrix = None
        
    async def collect_market_data(self, symbols: List[str]) -> None:
        """Collect real market data for analysis"""
        logger.info(f"Collecting market data for {len(symbols)} symbols...")
        
        async with AlphaVantageClient(self.av_key) as client:
            for symbol in symbols:
                try:
                    logger.info(f"Fetching data for {symbol}...")
                    
                    # Get daily data
                    daily_data = await client.get_daily_data(symbol)
                    
                    if "Time Series (Daily)" not in daily_data:
                        logger.warning(f"No daily data for {symbol}: {daily_data}")
                        continue
                    
                    # Get RSI
                    rsi_data = await client.get_technical_indicators(
                        symbol, "RSI", interval="daily", time_period=14, series_type="close"
                    )
                    
                    # Get MACD
                    macd_data = await client.get_technical_indicators(
                        symbol, "MACD", interval="daily", series_type="close"
                    )
                    
                    # Process and store data
                    self.market_data[symbol] = self._process_market_data(
                        symbol, daily_data, rsi_data, macd_data
                    )
                    
                    logger.info(f"Processed {len(self.market_data[symbol])} data points for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error collecting data for {symbol}: {e}")
                    continue
    
    def _process_market_data(self, symbol: str, daily_data: Dict, rsi_data: Dict, macd_data: Dict) -> List[MarketDataPoint]:
        """Process raw market data into structured format"""
        data_points = []
        
        time_series = daily_data.get("Time Series (Daily)", {})
        rsi_series = rsi_data.get("Technical Analysis: RSI", {})
        macd_series = macd_data.get("Technical Analysis: MACD", {})
        
        # Get last 30 days of data
        sorted_dates = sorted(time_series.keys(), reverse=True)[:30]
        
        for i, date_str in enumerate(sorted_dates):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                daily_info = time_series[date_str]
                
                # Calculate price change
                current_price = float(daily_info["4. close"])
                if i < len(sorted_dates) - 1:
                    prev_price = float(time_series[sorted_dates[i + 1]]["4. close"])
                    change_percent = ((current_price - prev_price) / prev_price) * 100
                else:
                    change_percent = 0.0
                
                # Calculate volatility (high-low range as percentage of close)
                high_price = float(daily_info["2. high"])
                low_price = float(daily_info["3. low"])
                volatility = ((high_price - low_price) / current_price) * 100
                
                # Get technical indicators
                rsi_value = None
                if date_str in rsi_series:
                    rsi_value = float(rsi_series[date_str]["RSI"])
                
                macd_value = None
                if date_str in macd_series:
                    macd_value = float(macd_series[date_str]["MACD"])
                
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=date_obj,
                    price=current_price,
                    volume=int(daily_info["5. volume"]),
                    change_percent=change_percent,
                    volatility=volatility,
                    rsi=rsi_value,
                    macd=macd_value
                )
                
                data_points.append(data_point)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing data point for {symbol} on {date_str}: {e}")
                continue
        
        return data_points
    
    async def analyze_correlations(self) -> np.ndarray:
        """Analyze correlations between assets"""
        logger.info("Analyzing asset correlations...")
        
        if not self.market_data:
            logger.warning("No market data available for correlation analysis")
            return np.array([])
        
        # Create price matrix
        symbols = list(self.market_data.keys())
        price_data = {}
        
        for symbol in symbols:
            prices = [dp.price for dp in self.market_data[symbol]]
            price_data[symbol] = prices
        
        # Create DataFrame and calculate correlation
        df = pd.DataFrame(price_data)
        self.correlation_matrix = df.corr().values
        
        logger.info(f"Calculated correlation matrix for {len(symbols)} assets")
        return self.correlation_matrix
    
    async def detect_contradictions(self) -> List[ContradictionEvent]:
        """Detect market contradictions using KIMERA's cognitive architecture"""
        logger.info("Detecting market contradictions...")
        
        contradictions = []
        
        # 1. Sector Divergence Analysis
        contradictions.extend(await self._detect_sector_divergence())
        
        # 2. Volume-Price Contradictions
        contradictions.extend(await self._detect_volume_price_contradictions())
        
        # 3. Technical Indicator Divergences
        contradictions.extend(await self._detect_technical_divergences())
        
        # 4. Correlation Breakdowns
        contradictions.extend(await self._detect_correlation_breakdowns())
        
        # 5. Cross-Asset Anomalies
        contradictions.extend(await self._detect_cross_asset_anomalies())
        
        self.contradictions = contradictions
        logger.info(f"Detected {len(contradictions)} market contradictions")
        
        return contradictions
    
    async def _detect_sector_divergence(self) -> List[ContradictionEvent]:
        """Detect divergences within market sectors"""
        contradictions = []
        
        # Define tech sector stocks from our data
        tech_stocks = [symbol for symbol in self.market_data.keys() 
                      if symbol in ["AAPL", "GOOGL", "MSFT", "NVDA", "AMD", "INTC", "META"]]
        
        if len(tech_stocks) < 2:
            return contradictions
        
        # Calculate average performance for each day
        for date_idx in range(min(len(self.market_data[stock]) for stock in tech_stocks)):
            daily_changes = []
            for stock in tech_stocks:
                if date_idx < len(self.market_data[stock]):
                    daily_changes.append(self.market_data[stock][date_idx].change_percent)
            
            if len(daily_changes) < 2:
                continue
            
            # Check for significant divergence
            max_change = max(daily_changes)
            min_change = min(daily_changes)
            divergence = abs(max_change - min_change)
            
            if divergence > 5.0:  # 5% divergence threshold
                timestamp = self.market_data[tech_stocks[0]][date_idx].timestamp
                
                contradiction = ContradictionEvent(
                    event_id=f"sector_div_{timestamp.strftime('%Y%m%d')}",
                    timestamp=timestamp,
                    contradiction_type="sector_divergence",
                    severity="medium" if divergence < 10 else "high",
                    description=f"Tech sector divergence: {divergence:.2f}% spread",
                    affected_assets=tech_stocks,
                    confidence_score=min(divergence / 15.0, 1.0),
                    semantic_features={
                        "divergence_magnitude": divergence / 20.0,
                        "sector_coherence": 1.0 - (divergence / 20.0),
                        "market_stress": divergence / 15.0
                    }
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    async def _detect_volume_price_contradictions(self) -> List[ContradictionEvent]:
        """Detect volume-price contradictions"""
        contradictions = []
        
        for symbol, data_points in self.market_data.items():
            for dp in data_points:
                # Calculate volume intensity (normalized)
                avg_volume = np.mean([d.volume for d in data_points])
                volume_intensity = dp.volume / avg_volume if avg_volume > 0 else 0
                
                # Check for high volume with low price movement
                if volume_intensity > 1.5 and abs(dp.change_percent) < 0.5:
                    contradiction = ContradictionEvent(
                        event_id=f"vol_price_{symbol}_{dp.timestamp.strftime('%Y%m%d')}",
                        timestamp=dp.timestamp,
                        contradiction_type="volume_price_mismatch",
                        severity="medium",
                        description=f"{symbol}: High volume ({volume_intensity:.2f}x) with minimal price movement ({dp.change_percent:.2f}%)",
                        affected_assets=[symbol],
                        confidence_score=min(volume_intensity / 3.0, 1.0),
                        semantic_features={
                            "volume_intensity": min(volume_intensity / 3.0, 1.0),
                            "price_momentum": abs(dp.change_percent) / 5.0,
                            "market_confusion": volume_intensity / 2.0
                        }
                    )
                    contradictions.append(contradiction)
        
        return contradictions
    
    async def _detect_technical_divergences(self) -> List[ContradictionEvent]:
        """Detect technical indicator divergences"""
        contradictions = []
        
        for symbol, data_points in self.market_data.items():
            for dp in data_points:
                if dp.rsi is None or dp.macd is None:
                    continue
                
                # RSI-Price divergence
                if dp.rsi > 70 and dp.change_percent < -2:  # Overbought but falling
                    contradiction = ContradictionEvent(
                        event_id=f"rsi_div_{symbol}_{dp.timestamp.strftime('%Y%m%d')}",
                        timestamp=dp.timestamp,
                        contradiction_type="technical_divergence",
                        severity="medium",
                        description=f"{symbol}: RSI overbought ({dp.rsi:.1f}) but price declining ({dp.change_percent:.2f}%)",
                        affected_assets=[symbol],
                        confidence_score=0.7,
                        semantic_features={
                            "technical_stress": (dp.rsi - 50) / 50,
                            "price_momentum": dp.change_percent / 10.0,
                            "divergence_strength": 0.7
                        }
                    )
                    contradictions.append(contradiction)
                
                elif dp.rsi < 30 and dp.change_percent > 2:  # Oversold but rising
                    contradiction = ContradictionEvent(
                        event_id=f"rsi_div_{symbol}_{dp.timestamp.strftime('%Y%m%d')}",
                        timestamp=dp.timestamp,
                        contradiction_type="technical_divergence",
                        severity="medium",
                        description=f"{symbol}: RSI oversold ({dp.rsi:.1f}) but price rising ({dp.change_percent:.2f}%)",
                        affected_assets=[symbol],
                        confidence_score=0.7,
                        semantic_features={
                            "technical_stress": (50 - dp.rsi) / 50,
                            "price_momentum": dp.change_percent / 10.0,
                            "divergence_strength": 0.7
                        }
                    )
                    contradictions.append(contradiction)
        
        return contradictions
    
    async def _detect_correlation_breakdowns(self) -> List[ContradictionEvent]:
        """Detect correlation breakdowns between historically correlated assets"""
        contradictions = []
        
        if self.correlation_matrix is None:
            await self.analyze_correlations()
        
        if self.correlation_matrix.size == 0:
            return contradictions
        
        symbols = list(self.market_data.keys())
        
        # Look for correlation breakdowns
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                correlation = self.correlation_matrix[i, j]
                
                # If correlation is unexpectedly low for related assets
                if correlation < 0.3 and symbols[i] in ["AAPL", "GOOGL", "MSFT"] and symbols[j] in ["AAPL", "GOOGL", "MSFT"]:
                    contradiction = ContradictionEvent(
                        event_id=f"corr_breakdown_{symbols[i]}_{symbols[j]}",
                        timestamp=datetime.now(),
                        contradiction_type="correlation_breakdown",
                        severity="high",
                        description=f"Correlation breakdown between {symbols[i]} and {symbols[j]}: {correlation:.3f}",
                        affected_assets=[symbols[i], symbols[j]],
                        confidence_score=1.0 - abs(correlation),
                        semantic_features={
                            "correlation_strength": abs(correlation),
                            "market_fragmentation": 1.0 - abs(correlation),
                            "systemic_risk": 0.8
                        }
                    )
                    contradictions.append(contradiction)
        
        return contradictions
    
    async def _detect_cross_asset_anomalies(self) -> List[ContradictionEvent]:
        """Detect anomalies across different asset classes"""
        contradictions = []
        
        # Calculate market-wide volatility spike
        all_volatilities = []
        for data_points in self.market_data.values():
            all_volatilities.extend([dp.volatility for dp in data_points])
        
        if not all_volatilities:
            return contradictions
        
        avg_volatility = np.mean(all_volatilities)
        volatility_threshold = avg_volatility * 2
        
        # Group by date and check for market-wide anomalies
        date_volatilities = {}
        for symbol, data_points in self.market_data.items():
            for dp in data_points:
                date_key = dp.timestamp.strftime('%Y-%m-%d')
                if date_key not in date_volatilities:
                    date_volatilities[date_key] = []
                date_volatilities[date_key].append(dp.volatility)
        
        for date_str, volatilities in date_volatilities.items():
            avg_daily_vol = np.mean(volatilities)
            
            if avg_daily_vol > volatility_threshold:
                contradiction = ContradictionEvent(
                    event_id=f"market_anomaly_{date_str}",
                    timestamp=datetime.strptime(date_str, '%Y-%m-%d'),
                    contradiction_type="cross_asset_anomaly",
                    severity="high",
                    description=f"Market-wide volatility spike: {avg_daily_vol:.2f}% (threshold: {volatility_threshold:.2f}%)",
                    affected_assets=list(self.market_data.keys()),
                    confidence_score=min(avg_daily_vol / (volatility_threshold * 2), 1.0),
                    semantic_features={
                        "volatility_intensity": avg_daily_vol / 10.0,
                        "market_stress": min(avg_daily_vol / volatility_threshold, 1.0),
                        "systemic_risk": 0.9
                    }
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    async def send_to_kimera(self, contradiction: ContradictionEvent) -> bool:
        """Send contradiction data to KIMERA for processing"""
        try:
            # Create geoid for the contradiction
            geoid_data = {
                "semantic_features": contradiction.semantic_features,
                "symbolic_content": {
                    "type": "financial_contradiction",
                    "contradiction_type": contradiction.contradiction_type,
                    "severity": contradiction.severity,
                    "description": contradiction.description,
                    "affected_assets": contradiction.affected_assets,
                    "timestamp": contradiction.timestamp.isoformat()
                },
                "metadata": {
                    "source": "real_market_case_study",
                    "confidence": contradiction.confidence_score,
                    "event_id": contradiction.event_id
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.kimera_url}/geoids", json=geoid_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Sent contradiction {contradiction.event_id} to KIMERA: {result.get('geoid_id')}")
                        return True
                    else:
                        logger.error(f"Failed to send to KIMERA: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending to KIMERA: {e}")
            return False
    
    async def generate_case_study_report(self) -> CaseStudyResults:
        """Generate comprehensive case study report"""
        logger.info("Generating case study report...")
        
        # Calculate metrics
        total_data_points = sum(len(data) for data in self.market_data.values())
        contradictions_by_type = {}
        
        for contradiction in self.contradictions:
            if contradiction.contradiction_type not in contradictions_by_type:
                contradictions_by_type[contradiction.contradiction_type] = 0
            contradictions_by_type[contradiction.contradiction_type] += 1
        
        # Generate semantic insights
        semantic_insights = []
        
        if self.contradictions:
            # Analyze contradiction patterns
            severity_distribution = {}
            for contradiction in self.contradictions:
                if contradiction.severity not in severity_distribution:
                    severity_distribution[contradiction.severity] = 0
                severity_distribution[contradiction.severity] += 1
            
            semantic_insights.append({
                "insight_type": "contradiction_severity_analysis",
                "data": severity_distribution,
                "description": "Distribution of contradiction severities detected"
            })
            
            # Analyze temporal patterns
            contradiction_dates = [c.timestamp.date() for c in self.contradictions]
            unique_dates = list(set(contradiction_dates))
            daily_counts = {date: contradiction_dates.count(date) for date in unique_dates}
            
            semantic_insights.append({
                "insight_type": "temporal_contradiction_pattern",
                "data": {str(k): v for k, v in daily_counts.items()},
                "description": "Daily contradiction occurrence patterns"
            })
        
        # Performance metrics
        performance_metrics = {
            "data_collection_success_rate": len(self.market_data) / 10,  # Assuming 10 target symbols
            "contradiction_detection_rate": len(self.contradictions) / max(total_data_points, 1),
            "average_confidence_score": np.mean([c.confidence_score for c in self.contradictions]) if self.contradictions else 0,
            "correlation_analysis_coverage": 1.0 if self.correlation_matrix is not None else 0.0
        }
        
        # Determine study period
        all_timestamps = []
        for data_points in self.market_data.values():
            all_timestamps.extend([dp.timestamp for dp in data_points])
        
        study_period = (min(all_timestamps), max(all_timestamps)) if all_timestamps else (datetime.now(), datetime.now())
        
        results = CaseStudyResults(
            study_period=study_period,
            total_data_points=total_data_points,
            contradictions_detected=len(self.contradictions),
            market_events_identified=len([c for c in self.contradictions if c.severity == "high"]),
            correlation_breakdowns=len([c for c in self.contradictions if c.contradiction_type == "correlation_breakdown"]),
            volatility_spikes=len([c for c in self.contradictions if c.contradiction_type == "cross_asset_anomaly"]),
            semantic_insights=semantic_insights,
            performance_metrics=performance_metrics
        )
        
        return results

async def run_real_market_case_study():
    """Run the complete real market case study"""
    logger.info("Starting KIMERA Real Market Case Study")
    logger.info("=" * 60)
    
    # Configuration
    ALPHA_VANTAGE_KEY = "X5GCHUJSY20536ID"
    SYMBOLS = ["AAPL", "GOOGL", "MSFT", "NVDA", "AMD", "TSLA", "META", "AMZN", "NFLX", "INTC"]
    
    # Initialize analyzer
    analyzer = KimeraFinancialAnalyzer(ALPHA_VANTAGE_KEY)
    
    try:
        # Step 1: Collect real market data
        logger.info("Step 1: Collecting real market data...")
        await analyzer.collect_market_data(SYMBOLS)
        
        if not analyzer.market_data:
            logger.error("No market data collected. Exiting.")
            return
        
        # Step 2: Analyze correlations
        logger.info("Step 2: Analyzing asset correlations...")
        await analyzer.analyze_correlations()
        
        # Step 3: Detect contradictions
        logger.info("Step 3: Detecting market contradictions...")
        contradictions = await analyzer.detect_contradictions()
        
        # Step 4: Send significant contradictions to KIMERA
        logger.info("Step 4: Sending contradictions to KIMERA...")
        high_confidence_contradictions = [c for c in contradictions if c.confidence_score > 0.6]
        
        for contradiction in high_confidence_contradictions[:5]:  # Limit to top 5
            await analyzer.send_to_kimera(contradiction)
            await asyncio.sleep(1)  # Rate limiting
        
        # Step 5: Generate comprehensive report
        logger.info("Step 5: Generating case study report...")
        results = await analyzer.generate_case_study_report()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"real_market_case_study_results_{timestamp}.json"
        
        # Convert results to JSON-serializable format
        results_dict = asdict(results)
        results_dict['study_period'] = [
            results.study_period[0].isoformat(),
            results.study_period[1].isoformat()
        ]
        
        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "=" * 60)
        print("KIMERA REAL MARKET CASE STUDY RESULTS")
        print("=" * 60)
        print(f"Study Period: {results.study_period[0].strftime('%Y-%m-%d')} to {results.study_period[1].strftime('%Y-%m-%d')}")
        print(f"Total Data Points Analyzed: {results.total_data_points:,}")
        print(f"Market Contradictions Detected: {results.contradictions_detected}")
        print(f"High-Severity Market Events: {results.market_events_identified}")
        print(f"Correlation Breakdowns: {results.correlation_breakdowns}")
        print(f"Volatility Spikes: {results.volatility_spikes}")
        print(f"Data Collection Success Rate: {results.performance_metrics['data_collection_success_rate']:.1%}")
        print(f"Average Confidence Score: {results.performance_metrics['average_confidence_score']:.3f}")
        print(f"\nDetailed results saved to: {results_file}")
        
        # Print top contradictions
        if contradictions:
            print(f"\nTop {min(5, len(contradictions))} Contradictions Detected:")
            print("-" * 60)
            
            sorted_contradictions = sorted(contradictions, key=lambda x: x.confidence_score, reverse=True)
            for i, contradiction in enumerate(sorted_contradictions[:5], 1):
                print(f"{i}. {contradiction.description}")
                print(f"   Type: {contradiction.contradiction_type} | Severity: {contradiction.severity}")
                print(f"   Confidence: {contradiction.confidence_score:.3f} | Assets: {', '.join(contradiction.affected_assets[:3])}")
                print(f"   Date: {contradiction.timestamp.strftime('%Y-%m-%d')}")
                print()
        
        logger.info("Case study completed successfully!")
        
    except Exception as e:
        logger.error(f"Case study failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_real_market_case_study())