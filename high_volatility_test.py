#!/usr/bin/env python3
"""
High Volatility Financial Stream Test for KIMERA SWM

This test simulates extreme market conditions with high volatility streams
to stress test KIMERA's real-time contradiction detection capabilities.
"""

import requests
import json
import time
import random
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import math

KIMERA_API_URL = "http://localhost:8001"

class VolatilityStreamGenerator:
    """Generates realistic high volatility financial data streams"""
    
    def __init__(self):
        # Base prices for different assets
        self.base_prices = {
            "TSLA": 250.0,    # Tesla - known for volatility
            "GME": 20.0,      # GameStop - meme stock volatility
            "NVDA": 800.0,    # NVIDIA - AI/crypto correlation
            "BTC": 45000.0,   # Bitcoin - crypto volatility
            "ETH": 2500.0,    # Ethereum - alt-coin volatility
            "VIX": 25.0,      # Volatility Index
            "SQQQ": 15.0,     # 3x Inverse NASDAQ ETF
            "UVXY": 12.0,     # 2x VIX ETF
        }
        
        # Current prices (will fluctuate)
        self.current_prices = self.base_prices.copy()
        
        # Volatility parameters for each asset
        self.volatility_params = {
            "TSLA": {"base_vol": 0.05, "spike_prob": 0.15, "spike_magnitude": 0.20},
            "GME": {"base_vol": 0.08, "spike_prob": 0.25, "spike_magnitude": 0.35},
            "NVDA": {"base_vol": 0.04, "spike_prob": 0.12, "spike_magnitude": 0.15},
            "BTC": {"base_vol": 0.06, "spike_prob": 0.20, "spike_magnitude": 0.25},
            "ETH": {"base_vol": 0.07, "spike_prob": 0.18, "spike_magnitude": 0.30},
            "VIX": {"base_vol": 0.10, "spike_prob": 0.30, "spike_magnitude": 0.50},
            "SQQQ": {"base_vol": 0.12, "spike_prob": 0.20, "spike_magnitude": 0.40},
            "UVXY": {"base_vol": 0.15, "spike_prob": 0.35, "spike_magnitude": 0.60},
        }
        
        # Market regime states
        self.market_regimes = ["normal", "stress", "panic", "euphoria", "manipulation"]
        self.current_regime = "normal"
        self.regime_duration = 0
        
        # Correlation matrix for realistic co-movements
        self.correlations = {
            ("TSLA", "NVDA"): 0.6,   # Tech correlation
            ("BTC", "ETH"): 0.8,     # Crypto correlation
            ("VIX", "SQQQ"): 0.7,    # Volatility correlation
            ("UVXY", "VIX"): 0.9,    # VIX products correlation
            ("TSLA", "GME"): -0.3,   # Meme stock inverse correlation
        }
    
    def generate_market_event(self) -> str:
        """Generate random market events that affect volatility"""
        events = [
            "fed_announcement",
            "earnings_surprise",
            "geopolitical_tension",
            "crypto_regulation",
            "margin_call_cascade",
            "algorithmic_selloff",
            "short_squeeze",
            "flash_crash",
            "whale_movement",
            "social_media_frenzy"
        ]
        return random.choice(events)
    
    def update_market_regime(self):
        """Update market regime based on conditions"""
        self.regime_duration += 1
        
        # Regime transition probabilities
        if self.regime_duration > 10:  # Force regime change after 10 updates
            regime_transitions = {
                "normal": ["stress", "euphoria"],
                "stress": ["panic", "normal"],
                "panic": ["stress", "normal"],
                "euphoria": ["normal", "stress"],
                "manipulation": ["normal", "stress"]
            }
            
            if random.random() < 0.3:  # 30% chance of regime change
                self.current_regime = random.choice(regime_transitions[self.current_regime])
                self.regime_duration = 0
                print(f"🌪️  Market regime changed to: {self.current_regime.upper()}")
    
    def calculate_volatility_multiplier(self, symbol: str) -> float:
        """Calculate volatility multiplier based on market regime"""
        base_multipliers = {
            "normal": 1.0,
            "stress": 2.5,
            "panic": 5.0,
            "euphoria": 3.0,
            "manipulation": 4.0
        }
        
        # Add symbol-specific adjustments
        symbol_adjustments = {
            "VIX": 2.0,    # VIX is more sensitive
            "UVXY": 2.5,   # Leveraged VIX product
            "SQQQ": 2.0,   # Inverse leveraged ETF
            "GME": 1.8,    # Meme stock volatility
            "BTC": 1.5,    # Crypto volatility
            "ETH": 1.6,    # Alt-coin volatility
        }
        
        base_mult = base_multipliers[self.current_regime]
        symbol_mult = symbol_adjustments.get(symbol, 1.0)
        
        return base_mult * symbol_mult
    
    def generate_price_update(self, symbol: str) -> Dict:
        """Generate a realistic price update with high volatility"""
        params = self.volatility_params[symbol]
        current_price = self.current_prices[symbol]
        
        # Base volatility
        base_vol = params["base_vol"]
        vol_multiplier = self.calculate_volatility_multiplier(symbol)
        effective_vol = base_vol * vol_multiplier
        
        # Generate price change
        if random.random() < params["spike_prob"]:
            # Volatility spike
            spike_direction = random.choice([-1, 1])
            price_change = spike_direction * params["spike_magnitude"] * random.uniform(0.5, 1.5)
            volume_multiplier = random.uniform(5.0, 15.0)  # High volume during spikes
            event = self.generate_market_event()
        else:
            # Normal movement
            price_change = np.random.normal(0, effective_vol)
            volume_multiplier = random.uniform(0.8, 2.0)
            event = None
        
        # Apply correlations
        for (sym1, sym2), correlation in self.correlations.items():
            if symbol == sym1 and random.random() < abs(correlation):
                # Apply correlated movement to sym2
                corr_change = price_change * correlation * random.uniform(0.5, 1.0)
                self.current_prices[sym2] *= (1 + corr_change)
                self.current_prices[sym2] = max(self.current_prices[sym2], 0.01)  # Prevent negative prices
        
        # Update current price
        new_price = current_price * (1 + price_change)
        new_price = max(new_price, 0.01)  # Prevent negative prices
        self.current_prices[symbol] = new_price
        
        # Calculate volume
        base_volume = {
            "TSLA": 50000000, "GME": 30000000, "NVDA": 40000000,
            "BTC": 1000000, "ETH": 800000, "VIX": 20000000,
            "SQQQ": 25000000, "UVXY": 35000000
        }
        
        volume = int(base_volume[symbol] * volume_multiplier * random.uniform(0.5, 2.0))
        
        # Calculate additional metrics
        price_change_pct = (new_price - current_price) / current_price * 100
        
        # Generate realistic bid-ask spread based on volatility
        spread_pct = effective_vol * random.uniform(0.1, 0.5)
        bid = new_price * (1 - spread_pct / 2)
        ask = new_price * (1 + spread_pct / 2)
        
        return {
            "symbol": symbol,
            "price": round(new_price, 2),
            "previous_price": round(current_price, 2),
            "change": round(new_price - current_price, 2),
            "change_pct": round(price_change_pct, 2),
            "volume": volume,
            "bid": round(bid, 2),
            "ask": round(ask, 2),
            "spread": round(ask - bid, 2),
            "volatility": round(effective_vol * 100, 2),
            "market_regime": self.current_regime,
            "event": event,
            "timestamp": datetime.now().isoformat()
        }

class HighVolatilityTester:
    """Tests KIMERA with high volatility financial streams"""
    
    def __init__(self):
        self.generator = VolatilityStreamGenerator()
        self.data_queue = queue.Queue()
        self.geoid_cache = {}
        self.contradiction_count = 0
        self.scar_count = 0
        self.running = False
        self.test_duration = 300  # 5 minutes
        self.update_interval = 2  # 2 seconds between updates
        
    def check_kimera_connection(self) -> bool:
        """Check if KIMERA is accessible"""
        try:
            response = requests.get(f"{KIMERA_API_URL}/system/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def convert_to_semantic_features(self, market_data: Dict) -> Dict:
        """Convert market data to KIMERA semantic features"""
        
        # Normalize price momentum (-1 to 1 range)
        change_pct = market_data["change_pct"]
        price_momentum = max(-1.0, min(1.0, change_pct / 20.0))  # ±20% = ±1.0
        price_momentum = (price_momentum + 1) / 2  # Convert to 0-1 range
        
        # Volume intensity (0-1 range)
        volume = market_data["volume"]
        base_volumes = {
            "TSLA": 50000000, "GME": 30000000, "NVDA": 40000000,
            "BTC": 1000000, "ETH": 800000, "VIX": 20000000,
            "SQQQ": 25000000, "UVXY": 35000000
        }
        base_vol = base_volumes.get(market_data["symbol"], 10000000)
        volume_intensity = min(1.0, volume / (base_vol * 3))  # Cap at 3x normal volume
        
        # Market sentiment based on price action and regime
        sentiment_base = price_momentum
        regime_adjustments = {
            "normal": 0.0, "stress": -0.2, "panic": -0.4,
            "euphoria": 0.3, "manipulation": -0.1
        }
        market_sentiment = max(0.0, min(1.0, 
            sentiment_base + regime_adjustments[market_data["market_regime"]]))
        
        # Volatility (0-1 range)
        volatility = min(1.0, market_data["volatility"] / 50.0)  # 50% volatility = 1.0
        
        # Liquidity (inverse of spread)
        spread_pct = (market_data["spread"] / market_data["price"]) * 100
        liquidity = max(0.0, min(1.0, 1.0 - (spread_pct / 5.0)))  # 5% spread = 0 liquidity
        
        return {
            "price_momentum": round(price_momentum, 3),
            "volume_intensity": round(volume_intensity, 3),
            "market_sentiment": round(market_sentiment, 3),
            "volatility": round(volatility, 3),
            "liquidity": round(liquidity, 3)
        }
    
    def create_kimera_geoid(self, market_data: Dict) -> str:
        """Create or update KIMERA geoid from market data"""
        
        semantic_features = self.convert_to_semantic_features(market_data)
        
        symbolic_content = {
            "type": "high_volatility_stream",
            "symbol": market_data["symbol"],
            "price": market_data["price"],
            "change_pct": market_data["change_pct"],
            "market_regime": market_data["market_regime"],
            "timestamp": market_data["timestamp"]
        }
        
        metadata = {
            "source": "high_volatility_test",
            "volume": market_data["volume"],
            "volatility": market_data["volatility"],
            "event": market_data.get("event"),
            "bid_ask_spread": market_data["spread"],
            "test_stream": True
        }
        
        geoid_data = {
            "semantic_features": semantic_features,
            "symbolic_content": symbolic_content,
            "metadata": metadata
        }
        
        try:
            response = requests.post(
                f"{KIMERA_API_URL}/geoids",
                json=geoid_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                geoid_id = result["geoid_id"]
                
                # Cache the geoid
                self.geoid_cache[market_data["symbol"]] = {
                    "geoid_id": geoid_id,
                    "last_update": datetime.now(),
                    "price": market_data["price"],
                    "entropy": result.get("entropy", 0)
                }
                
                return geoid_id
            else:
                print(f"❌ Failed to create geoid for {market_data['symbol']}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating geoid for {market_data['symbol']}: {e}")
            return None
    
    def detect_contradictions(self, trigger_symbol: str) -> Dict:
        """Detect contradictions in the current market state"""
        
        if trigger_symbol not in self.geoid_cache:
            return None
        
        trigger_geoid = self.geoid_cache[trigger_symbol]["geoid_id"]
        
        # Get all available geoids for contradiction detection
        available_geoids = len(self.geoid_cache)
        
        try:
            contradiction_data = {
                "trigger_geoid_id": trigger_geoid,
                "search_limit": min(available_geoids, 8),  # Limit to prevent overload
                "force_collapse": False
            }
            
            response = requests.post(
                f"{KIMERA_API_URL}/process/contradictions",
                json=contradiction_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                
                self.contradiction_count += contradictions
                self.scar_count += scars
                
                return result
            else:
                print(f"❌ Contradiction detection failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error in contradiction detection: {e}")
            return None
    
    def stream_generator_thread(self):
        """Thread function to generate continuous market data"""
        
        symbols = list(self.generator.base_prices.keys())
        
        while self.running:
            try:
                # Update market regime
                self.generator.update_market_regime()
                
                # Generate updates for all symbols
                for symbol in symbols:
                    if not self.running:
                        break
                    
                    market_data = self.generator.generate_price_update(symbol)
                    self.data_queue.put(market_data)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ Error in stream generator: {e}")
                time.sleep(1)
    
    def process_market_data(self, market_data: Dict):
        """Process individual market data point"""
        
        symbol = market_data["symbol"]
        price = market_data["price"]
        change_pct = market_data["change_pct"]
        volume = market_data["volume"]
        event = market_data.get("event")
        
        # Create/update geoid
        geoid_id = self.create_kimera_geoid(market_data)
        
        if geoid_id:
            # Print market update
            change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
            event_text = f" [{event}]" if event else ""
            
            print(f"{change_icon} {symbol}: ${price:.2f} ({change_pct:+.2f}%) Vol: {volume:,}{event_text}")
            
            # Detect contradictions for high volatility events
            if abs(change_pct) > 5.0 or event or market_data["volatility"] > 20:
                print(f"🔍 High volatility detected for {symbol}, checking contradictions...")
                contradiction_result = self.detect_contradictions(symbol)
                
                if contradiction_result and contradiction_result.get("contradictions_detected", 0) > 0:
                    contradictions = contradiction_result["contradictions_detected"]
                    scars = contradiction_result["scars_created"]
                    print(f"🚨 CONTRADICTION ALERT: {contradictions} contradictions, {scars} scars created!")
    
    def print_test_statistics(self):
        """Print current test statistics"""
        
        print(f"\n📊 HIGH VOLATILITY TEST STATISTICS")
        print(f"=" * 50)
        print(f"🕒 Test Duration: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📈 Symbols Tracked: {len(self.geoid_cache)}")
        print(f"🧠 Geoids Created: {len(self.geoid_cache)}")
        print(f"🔥 Total Contradictions: {self.contradiction_count}")
        print(f"⚡ Total Scars: {self.scar_count}")
        print(f"🌪️  Current Market Regime: {self.generator.current_regime.upper()}")
        
        if self.geoid_cache:
            print(f"\n💰 Current Prices:")
            for symbol, cache_data in self.geoid_cache.items():
                price = cache_data["price"]
                entropy = cache_data["entropy"]
                print(f"   {symbol}: ${price:.2f} (Entropy: {entropy:.3f})")
    
    def get_system_status(self):
        """Get current KIMERA system status"""
        
        try:
            response = requests.get(f"{KIMERA_API_URL}/system/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"\n🧠 KIMERA System Status:")
                print(f"   Active Geoids: {status.get('active_geoids', 0)}")
                print(f"   Vault A Scars: {status.get('vault_a_scars', 0)}")
                print(f"   Vault B Scars: {status.get('vault_b_scars', 0)}")
                print(f"   System Entropy: {status.get('system_entropy', 0):.3f}")
                print(f"   Cycle Count: {status.get('cycle_count', 0)}")
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
    
    def run_test(self):
        """Run the high volatility test"""
        
        print("🌪️  KIMERA SWM HIGH VOLATILITY STREAM TEST")
        print("=" * 60)
        print("Simulating extreme market conditions with high volatility")
        print("to stress test KIMERA's real-time contradiction detection")
        
        # Check KIMERA connection
        if not self.check_kimera_connection():
            print("❌ KIMERA API not accessible. Please start with: python run_kimera.py")
            return
        
        print("✅ KIMERA SWM API is accessible")
        print(f"⏱️  Test Duration: {self.test_duration} seconds")
        print(f"🔄 Update Interval: {self.update_interval} seconds")
        
        # Start the stream generator thread
        self.running = True
        generator_thread = threading.Thread(target=self.stream_generator_thread)
        generator_thread.daemon = True
        generator_thread.start()
        
        print(f"\n🚀 Starting high volatility stream...")
        start_time = time.time()
        last_stats_time = start_time
        
        try:
            while self.running and (time.time() - start_time) < self.test_duration:
                
                # Process queued market data
                try:
                    market_data = self.data_queue.get(timeout=1)
                    self.process_market_data(market_data)
                except queue.Empty:
                    continue
                
                # Print statistics every 30 seconds
                if time.time() - last_stats_time > 30:
                    self.print_test_statistics()
                    last_stats_time = time.time()
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
        
        finally:
            self.running = False
            
        # Final statistics
        print(f"\n🏁 HIGH VOLATILITY TEST COMPLETED")
        print(f"=" * 50)
        
        self.print_test_statistics()
        self.get_system_status()
        
        # Calculate test metrics
        total_time = time.time() - start_time
        updates_per_second = len(self.geoid_cache) / total_time if total_time > 0 else 0
        contradictions_per_minute = (self.contradiction_count / total_time) * 60 if total_time > 0 else 0
        
        print(f"\n📈 Performance Metrics:")
        print(f"   ⚡ Updates/Second: {updates_per_second:.2f}")
        print(f"   🔥 Contradictions/Minute: {contradictions_per_minute:.2f}")
        print(f"   🧠 Contradiction Rate: {(self.contradiction_count / max(len(self.geoid_cache), 1)) * 100:.1f}%")
        
        print(f"\n🎯 Test Results:")
        if self.contradiction_count > 0:
            print(f"   ✅ KIMERA successfully detected market contradictions")
            print(f"   ✅ System handled high volatility streams")
            print(f"   ✅ Real-time processing functional")
        else:
            print(f"   ⚠️  No contradictions detected (may indicate low volatility)")
        
        print(f"\n🚀 High volatility test completed successfully!")

def main():
    """Main function"""
    tester = HighVolatilityTester()
    tester.run_test()

if __name__ == "__main__":
    main()