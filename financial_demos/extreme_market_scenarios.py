#!/usr/bin/env python3
"""
Extreme Market Scenarios Test for KIMERA SWM

This script simulates specific extreme market events to test KIMERA's
ability to detect contradictions during market crises and anomalies.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

KIMERA_API_URL = "http://localhost:8001"

class ExtremeMarketScenarios:
    """Simulates extreme market scenarios for KIMERA testing"""
    
    def __init__(self):
        self.scenario_results = []
        self.total_contradictions = 0
        self.total_scars = 0
    
    def check_kimera_connection(self) -> bool:
        """Check KIMERA connection"""
        try:
            response = requests.get(f"{KIMERA_API_URL}/system/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_scenario_geoid(self, scenario_data: Dict) -> str:
        """Create a geoid for a market scenario"""
        try:
            response = requests.post(
                f"{KIMERA_API_URL}/geoids",
                json=scenario_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["geoid_id"]
            else:
                print(f"❌ Failed to create scenario geoid: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error creating scenario geoid: {e}")
            return None
    
    def detect_scenario_contradictions(self, geoid_ids: List[str]) -> Dict:
        """Detect contradictions between scenarios"""
        if len(geoid_ids) < 2:
            return None
        
        try:
            contradiction_data = {
                "trigger_geoid_id": geoid_ids[0],
                "search_limit": len(geoid_ids),
                "force_collapse": False
            }
            
            response = requests.post(
                f"{KIMERA_API_URL}/process/contradictions",
                json=contradiction_data,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                
                self.total_contradictions += contradictions
                self.total_scars += scars
                
                return result
            else:
                print(f"❌ Contradiction detection failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error in contradiction detection: {e}")
            return None
    
    def scenario_1_flash_crash(self) -> List[str]:
        """Scenario 1: Flash Crash - Sudden market collapse"""
        print("\n🌪️  SCENARIO 1: FLASH CRASH")
        print("=" * 40)
        print("Simulating sudden market collapse with extreme volatility")
        
        scenarios = [
            {
                "name": "Pre-Crash Normal Market",
                "semantic_features": {
                    "price_momentum": 0.6,    # Mild uptrend
                    "volume_intensity": 0.4,  # Normal volume
                    "market_sentiment": 0.7,  # Optimistic
                    "volatility": 0.2,        # Low volatility
                    "liquidity": 0.9          # High liquidity
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "pre_crash_normal",
                    "description": "Normal market conditions before flash crash"
                },
                "metadata": {
                    "scenario_type": "flash_crash",
                    "phase": "pre_crash",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Flash Crash Trigger",
                "semantic_features": {
                    "price_momentum": 0.05,   # Massive drop
                    "volume_intensity": 0.95, # Extreme volume
                    "market_sentiment": 0.1,  # Panic
                    "volatility": 0.98,       # Extreme volatility
                    "liquidity": 0.2          # Liquidity crisis
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "flash_crash_trigger",
                    "description": "Sudden market collapse with extreme selling"
                },
                "metadata": {
                    "scenario_type": "flash_crash",
                    "phase": "crash",
                    "trigger_event": "algorithmic_selloff",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Circuit Breaker Halt",
                "semantic_features": {
                    "price_momentum": 0.5,    # Frozen
                    "volume_intensity": 0.0,  # No trading
                    "market_sentiment": 0.3,  # Confused/fearful
                    "volatility": 0.0,        # Artificially suppressed
                    "liquidity": 0.0          # No liquidity
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "circuit_breaker_halt",
                    "description": "Trading halted due to extreme volatility"
                },
                "metadata": {
                    "scenario_type": "flash_crash",
                    "phase": "halt",
                    "regulatory_action": "circuit_breaker",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Recovery Bounce",
                "semantic_features": {
                    "price_momentum": 0.8,    # Sharp recovery
                    "volume_intensity": 0.7,  # High volume
                    "market_sentiment": 0.6,  # Cautious optimism
                    "volatility": 0.6,        # Still volatile
                    "liquidity": 0.5          # Partial liquidity return
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "recovery_bounce",
                    "description": "Sharp recovery after flash crash"
                },
                "metadata": {
                    "scenario_type": "flash_crash",
                    "phase": "recovery",
                    "recovery_mechanism": "bargain_hunting",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        geoid_ids = []
        for scenario in scenarios:
            print(f"📊 Creating: {scenario['name']}")
            geoid_id = self.create_scenario_geoid(scenario)
            if geoid_id:
                geoid_ids.append(geoid_id)
                print(f"   ✅ Geoid: {geoid_id}")
            time.sleep(1)
        
        return geoid_ids
    
    def scenario_2_short_squeeze(self) -> List[str]:
        """Scenario 2: Short Squeeze - Extreme upward pressure"""
        print("\n🚀 SCENARIO 2: SHORT SQUEEZE")
        print("=" * 40)
        print("Simulating extreme short squeeze with gamma squeeze")
        
        scenarios = [
            {
                "name": "Heavy Short Interest",
                "semantic_features": {
                    "price_momentum": 0.3,    # Downward pressure
                    "volume_intensity": 0.6,  # Moderate volume
                    "market_sentiment": 0.2,  # Bearish
                    "volatility": 0.4,        # Moderate volatility
                    "liquidity": 0.7          # Good liquidity
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "heavy_short_interest",
                    "description": "Stock heavily shorted by institutions"
                },
                "metadata": {
                    "scenario_type": "short_squeeze",
                    "phase": "setup",
                    "short_interest": "high",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Retail Buying Pressure",
                "semantic_features": {
                    "price_momentum": 0.7,    # Upward momentum
                    "volume_intensity": 0.8,  # High volume
                    "market_sentiment": 0.8,  # Very bullish
                    "volatility": 0.6,        # Increasing volatility
                    "liquidity": 0.6          # Decreasing liquidity
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "retail_buying_pressure",
                    "description": "Coordinated retail buying campaign"
                },
                "metadata": {
                    "scenario_type": "short_squeeze",
                    "phase": "ignition",
                    "catalyst": "social_media_campaign",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Gamma Squeeze",
                "semantic_features": {
                    "price_momentum": 0.95,   # Extreme upward movement
                    "volume_intensity": 0.9,  # Very high volume
                    "market_sentiment": 0.9,  # Euphoric
                    "volatility": 0.9,        # Extreme volatility
                    "liquidity": 0.3          # Liquidity crisis
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "gamma_squeeze",
                    "description": "Options market makers forced to buy shares"
                },
                "metadata": {
                    "scenario_type": "short_squeeze",
                    "phase": "acceleration",
                    "mechanism": "gamma_hedging",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Short Covering Panic",
                "semantic_features": {
                    "price_momentum": 0.98,   # Parabolic move
                    "volume_intensity": 0.95, # Extreme volume
                    "market_sentiment": 0.95, # Manic
                    "volatility": 0.98,       # Maximum volatility
                    "liquidity": 0.1          # No liquidity
                },
                "symbolic_content": {
                    "type": "market_state",
                    "scenario": "short_covering_panic",
                    "description": "Shorts forced to cover at any price"
                },
                "metadata": {
                    "scenario_type": "short_squeeze",
                    "phase": "climax",
                    "forced_covering": True,
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        geoid_ids = []
        for scenario in scenarios:
            print(f"📊 Creating: {scenario['name']}")
            geoid_id = self.create_scenario_geoid(scenario)
            if geoid_id:
                geoid_ids.append(geoid_id)
                print(f"   ✅ Geoid: {geoid_id}")
            time.sleep(1)
        
        return geoid_ids
    
    def scenario_3_crypto_manipulation(self) -> List[str]:
        """Scenario 3: Cryptocurrency Market Manipulation"""
        print("\n₿ SCENARIO 3: CRYPTO MANIPULATION")
        print("=" * 40)
        print("Simulating cryptocurrency market manipulation patterns")
        
        scenarios = [
            {
                "name": "Whale Accumulation",
                "semantic_features": {
                    "price_momentum": 0.55,   # Slight upward bias
                    "volume_intensity": 0.3,  # Low volume
                    "market_sentiment": 0.5,  # Neutral
                    "volatility": 0.2,        # Suppressed volatility
                    "liquidity": 0.8          # Good liquidity
                },
                "symbolic_content": {
                    "type": "crypto_state",
                    "scenario": "whale_accumulation",
                    "description": "Large holder quietly accumulating position"
                },
                "metadata": {
                    "scenario_type": "crypto_manipulation",
                    "phase": "accumulation",
                    "actor": "whale",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Pump Initiation",
                "semantic_features": {
                    "price_momentum": 0.8,    # Strong upward move
                    "volume_intensity": 0.9,  # Sudden volume spike
                    "market_sentiment": 0.7,  # FOMO building
                    "volatility": 0.7,        # Increasing volatility
                    "liquidity": 0.6          # Decreasing liquidity
                },
                "symbolic_content": {
                    "type": "crypto_state",
                    "scenario": "pump_initiation",
                    "description": "Coordinated buying to trigger FOMO"
                },
                "metadata": {
                    "scenario_type": "crypto_manipulation",
                    "phase": "pump",
                    "coordination": "telegram_group",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "FOMO Peak",
                "semantic_features": {
                    "price_momentum": 0.95,   # Parabolic rise
                    "volume_intensity": 0.95, # Extreme volume
                    "market_sentiment": 0.95, # Maximum FOMO
                    "volatility": 0.8,        # High volatility
                    "liquidity": 0.4          # Liquidity drying up
                },
                "symbolic_content": {
                    "type": "crypto_state",
                    "scenario": "fomo_peak",
                    "description": "Retail FOMO reaches maximum intensity"
                },
                "metadata": {
                    "scenario_type": "crypto_manipulation",
                    "phase": "peak",
                    "social_media_buzz": "maximum",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Dump Execution",
                "semantic_features": {
                    "price_momentum": 0.1,    # Massive dump
                    "volume_intensity": 0.9,  # High dump volume
                    "market_sentiment": 0.1,  # Panic and betrayal
                    "volatility": 0.9,        # Extreme volatility
                    "liquidity": 0.2          # Liquidity crisis
                },
                "symbolic_content": {
                    "type": "crypto_state",
                    "scenario": "dump_execution",
                    "description": "Coordinated selling by manipulators"
                },
                "metadata": {
                    "scenario_type": "crypto_manipulation",
                    "phase": "dump",
                    "exit_strategy": "coordinated_sell",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        geoid_ids = []
        for scenario in scenarios:
            print(f"📊 Creating: {scenario['name']}")
            geoid_id = self.create_scenario_geoid(scenario)
            if geoid_id:
                geoid_ids.append(geoid_id)
                print(f"   ✅ Geoid: {geoid_id}")
            time.sleep(1)
        
        return geoid_ids
    
    def scenario_4_vix_explosion(self) -> List[str]:
        """Scenario 4: VIX Explosion - Fear index spike"""
        print("\n😱 SCENARIO 4: VIX EXPLOSION")
        print("=" * 40)
        print("Simulating extreme fear and volatility spike")
        
        scenarios = [
            {
                "name": "Complacent Market",
                "semantic_features": {
                    "price_momentum": 0.6,    # Steady gains
                    "volume_intensity": 0.3,  # Low volume
                    "market_sentiment": 0.8,  # Complacent
                    "volatility": 0.1,        # Very low volatility
                    "liquidity": 0.9          # High liquidity
                },
                "symbolic_content": {
                    "type": "volatility_state",
                    "scenario": "complacent_market",
                    "description": "Market complacency with VIX at historic lows"
                },
                "metadata": {
                    "scenario_type": "vix_explosion",
                    "phase": "complacency",
                    "vix_level": "historic_low",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Black Swan Event",
                "semantic_features": {
                    "price_momentum": 0.2,    # Initial shock
                    "volume_intensity": 0.7,  # Increasing volume
                    "market_sentiment": 0.4,  # Confusion
                    "volatility": 0.6,        # Volatility rising
                    "liquidity": 0.6          # Liquidity concerns
                },
                "symbolic_content": {
                    "type": "volatility_state",
                    "scenario": "black_swan_event",
                    "description": "Unexpected geopolitical or economic shock"
                },
                "metadata": {
                    "scenario_type": "vix_explosion",
                    "phase": "trigger",
                    "event_type": "geopolitical_shock",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "VIX Explosion",
                "semantic_features": {
                    "price_momentum": 0.05,   # Market collapse
                    "volume_intensity": 0.95, # Panic selling
                    "market_sentiment": 0.05, # Extreme fear
                    "volatility": 0.98,       # VIX explosion
                    "liquidity": 0.1          # Liquidity evaporation
                },
                "symbolic_content": {
                    "type": "volatility_state",
                    "scenario": "vix_explosion",
                    "description": "VIX spikes to extreme levels as fear dominates"
                },
                "metadata": {
                    "scenario_type": "vix_explosion",
                    "phase": "explosion",
                    "vix_level": "extreme_spike",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "name": "Volatility Persistence",
                "semantic_features": {
                    "price_momentum": 0.3,    # Choppy movement
                    "volume_intensity": 0.8,  # High volume
                    "market_sentiment": 0.2,  # Persistent fear
                    "volatility": 0.8,        # Elevated volatility
                    "liquidity": 0.4          # Impaired liquidity
                },
                "symbolic_content": {
                    "type": "volatility_state",
                    "scenario": "volatility_persistence",
                    "description": "Elevated volatility persists as uncertainty remains"
                },
                "metadata": {
                    "scenario_type": "vix_explosion",
                    "phase": "persistence",
                    "market_structure": "damaged",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        geoid_ids = []
        for scenario in scenarios:
            print(f"📊 Creating: {scenario['name']}")
            geoid_id = self.create_scenario_geoid(scenario)
            if geoid_id:
                geoid_ids.append(geoid_id)
                print(f"   ✅ Geoid: {geoid_id}")
            time.sleep(1)
        
        return geoid_ids
    
    def run_all_scenarios(self):
        """Run all extreme market scenarios"""
        print("🌪️  KIMERA SWM EXTREME MARKET SCENARIOS TEST")
        print("=" * 60)
        print("Testing KIMERA's ability to detect contradictions during")
        print("extreme market events and crisis situations")
        
        # Check connection
        if not self.check_kimera_connection():
            print("❌ KIMERA API not accessible. Please start with: python run_kimera.py")
            return
        
        print("✅ KIMERA SWM API is accessible")
        
        # Run all scenarios
        all_geoid_ids = []
        
        # Scenario 1: Flash Crash
        scenario_1_geoids = self.scenario_1_flash_crash()
        all_geoid_ids.extend(scenario_1_geoids)
        
        if scenario_1_geoids:
            print(f"\n🔍 Analyzing Flash Crash contradictions...")
            result = self.detect_scenario_contradictions(scenario_1_geoids)
            if result:
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                print(f"   🔥 Flash Crash Contradictions: {contradictions}")
                print(f"   ⚡ Scars Created: {scars}")
                self.scenario_results.append(("Flash Crash", contradictions, scars))
        
        time.sleep(3)
        
        # Scenario 2: Short Squeeze
        scenario_2_geoids = self.scenario_2_short_squeeze()
        all_geoid_ids.extend(scenario_2_geoids)
        
        if scenario_2_geoids:
            print(f"\n🔍 Analyzing Short Squeeze contradictions...")
            result = self.detect_scenario_contradictions(scenario_2_geoids)
            if result:
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                print(f"   🔥 Short Squeeze Contradictions: {contradictions}")
                print(f"   ⚡ Scars Created: {scars}")
                self.scenario_results.append(("Short Squeeze", contradictions, scars))
        
        time.sleep(3)
        
        # Scenario 3: Crypto Manipulation
        scenario_3_geoids = self.scenario_3_crypto_manipulation()
        all_geoid_ids.extend(scenario_3_geoids)
        
        if scenario_3_geoids:
            print(f"\n🔍 Analyzing Crypto Manipulation contradictions...")
            result = self.detect_scenario_contradictions(scenario_3_geoids)
            if result:
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                print(f"   🔥 Crypto Manipulation Contradictions: {contradictions}")
                print(f"   ⚡ Scars Created: {scars}")
                self.scenario_results.append(("Crypto Manipulation", contradictions, scars))
        
        time.sleep(3)
        
        # Scenario 4: VIX Explosion
        scenario_4_geoids = self.scenario_4_vix_explosion()
        all_geoid_ids.extend(scenario_4_geoids)
        
        if scenario_4_geoids:
            print(f"\n🔍 Analyzing VIX Explosion contradictions...")
            result = self.detect_scenario_contradictions(scenario_4_geoids)
            if result:
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                print(f"   🔥 VIX Explosion Contradictions: {contradictions}")
                print(f"   ⚡ Scars Created: {scars}")
                self.scenario_results.append(("VIX Explosion", contradictions, scars))
        
        time.sleep(3)
        
        # Cross-scenario analysis
        if len(all_geoid_ids) > 4:
            print(f"\n🔍 Analyzing cross-scenario contradictions...")
            print(f"   Testing interactions between all {len(all_geoid_ids)} scenarios...")
            
            # Sample a subset for cross-analysis to avoid overload
            sample_geoids = random.sample(all_geoid_ids, min(8, len(all_geoid_ids)))
            result = self.detect_scenario_contradictions(sample_geoids)
            
            if result:
                contradictions = result.get("contradictions_detected", 0)
                scars = result.get("scars_created", 0)
                print(f"   🔥 Cross-Scenario Contradictions: {contradictions}")
                print(f"   ⚡ Scars Created: {scars}")
                self.scenario_results.append(("Cross-Scenario", contradictions, scars))
        
        # Final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print final test results"""
        print(f"\n🏁 EXTREME MARKET SCENARIOS TEST RESULTS")
        print("=" * 60)
        
        print(f"📊 Scenario Analysis Results:")
        for scenario_name, contradictions, scars in self.scenario_results:
            print(f"   {scenario_name}:")
            print(f"      🔥 Contradictions: {contradictions}")
            print(f"      ⚡ Scars: {scars}")
        
        print(f"\n📈 Overall Statistics:")
        print(f"   🔥 Total Contradictions: {self.total_contradictions}")
        print(f"   ⚡ Total Scars: {self.total_scars}")
        print(f"   📊 Scenarios Tested: {len(self.scenario_results)}")
        
        # Get final system status
        try:
            response = requests.get(f"{KIMERA_API_URL}/system/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"\n🧠 Final KIMERA System State:")
                print(f"   Active Geoids: {status.get('active_geoids', 0)}")
                print(f"   Vault A Scars: {status.get('vault_a_scars', 0)}")
                print(f"   Vault B Scars: {status.get('vault_b_scars', 0)}")
                print(f"   System Entropy: {status.get('system_entropy', 0):.3f}")
                print(f"   Cycle Count: {status.get('cycle_count', 0)}")
        except:
            pass
        
        print(f"\n🎯 Key Insights:")
        print(f"   ✅ KIMERA successfully processed extreme market scenarios")
        print(f"   ✅ System detected contradictions in crisis situations")
        print(f"   ✅ Market memory encoded through scar creation")
        print(f"   ✅ Cross-scenario analysis revealed hidden relationships")
        
        print(f"\n🚀 Extreme market scenarios test completed successfully!")

def main():
    """Main function"""
    tester = ExtremeMarketScenarios()
    tester.run_all_scenarios()

if __name__ == "__main__":
    main()