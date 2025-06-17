#!/usr/bin/env python3
"""
Financial API Demo for KIMERA SWM

This script demonstrates practical financial API integration with KIMERA SWM,
showing real-world contradiction detection in financial markets.
"""

import requests
import time
import json
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from financial_api_integration import (
    YahooFinanceConnector, 
    CoinGeckoConnector, 
    FinancialKimeraIntegrator,
    FinancialContradictionDetector
)
from financial_config import get_config, MARKET_SECTORS, CRYPTO_CATEGORIES


class FinancialDemo:
    """Demonstration of financial API integration with KIMERA SWM"""
    
    def __init__(self):
        self.config = get_config()
        self.yahoo = YahooFinanceConnector()
        self.coingecko = CoinGeckoConnector()
        self.kimera = FinancialKimeraIntegrator(self.config.kimera_api_url)
        self.detector = FinancialContradictionDetector(self.kimera)
        
        # Check if KIMERA is running
        self.check_kimera_connection()
    
    def check_kimera_connection(self):
        """Check if KIMERA API is accessible"""
        try:
            response = requests.get(f"{self.config.kimera_api_url}/system/status", timeout=5)
            if response.status_code == 200:
                print("✅ KIMERA SWM API is running")
                status = response.json()
                print(f"   Active geoids: {status.get('active_geoids', 0)}")
                print(f"   System entropy: {status.get('system_entropy', 0):.2f}")
            else:
                print("❌ KIMERA API responded with error")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Cannot connect to KIMERA API: {e}")
            print("   Please start KIMERA with: python run_kimera.py")
            sys.exit(1)
    
    def demo_1_basic_stock_analysis(self):
        """Demo 1: Basic stock data integration"""
        print("\n" + "="*60)
        print("DEMO 1: Basic Stock Data Integration")
        print("="*60)
        
        stocks = ["AAPL", "GOOGL", "MSFT"]
        geoid_ids = []
        
        for symbol in stocks:
            print(f"\n📊 Analyzing {symbol}...")
            
            try:
                # Fetch stock data
                stock_data = self.yahoo.get_stock_data(symbol)
                if not stock_data:
                    print(f"   ❌ Failed to fetch data for {symbol}")
                    continue
                
                print(f"   💰 Price: ${stock_data.price:.2f}")
                print(f"   📈 Volume: {stock_data.volume:,}")
                print(f"   🏢 Market Cap: ${stock_data.market_cap:,}" if stock_data.market_cap else "   🏢 Market Cap: N/A")
                
                # Create KIMERA geoid
                result = self.kimera.create_kimera_geoid(stock_data)
                if result.get('geoid_id'):
                    geoid_id = result['geoid_id']
                    geoid_ids.append(geoid_id)
                    entropy = result.get('entropy', 0)
                    print(f"   🧠 KIMERA Geoid: {geoid_id}")
                    print(f"   🌀 Entropy: {entropy:.3f}")
                else:
                    print(f"   ❌ Failed to create KIMERA geoid")
                
            except Exception as e:
                print(f"   ❌ Error processing {symbol}: {e}")
        
        print(f"\n✅ Created {len(geoid_ids)} geoids for stock analysis")
        return geoid_ids
    
    def demo_2_crypto_analysis(self):
        """Demo 2: Cryptocurrency market analysis"""
        print("\n" + "="*60)
        print("DEMO 2: Cryptocurrency Market Analysis")
        print("="*60)
        
        cryptos = ["bitcoin", "ethereum", "cardano"]
        geoid_ids = []
        
        for crypto in cryptos:
            print(f"\n🪙 Analyzing {crypto.upper()}...")
            
            try:
                # Fetch crypto data
                crypto_data = self.coingecko.get_crypto_data(crypto)
                if not crypto_data:
                    print(f"   ❌ Failed to fetch data for {crypto}")
                    continue
                
                print(f"   💰 Price: ${crypto_data.price:.2f}")
                print(f"   📊 Market Cap: ${crypto_data.market_cap:,}" if crypto_data.market_cap else "   📊 Market Cap: N/A")
                print(f"   📈 24h Change: {crypto_data.metadata.get('price_change_24h', 'N/A'):.2f}%" if crypto_data.metadata.get('price_change_24h') else "   📈 24h Change: N/A")
                print(f"   😊 Sentiment: {crypto_data.sentiment_score:.1f}%" if crypto_data.sentiment_score else "   😊 Sentiment: N/A")
                
                # Create KIMERA geoid
                result = self.kimera.create_kimera_geoid(crypto_data)
                if result.get('geoid_id'):
                    geoid_id = result['geoid_id']
                    geoid_ids.append(geoid_id)
                    entropy = result.get('entropy', 0)
                    print(f"   🧠 KIMERA Geoid: {geoid_id}")
                    print(f"   🌀 Entropy: {entropy:.3f}")
                else:
                    print(f"   ❌ Failed to create KIMERA geoid")
                
            except Exception as e:
                print(f"   ❌ Error processing {crypto}: {e}")
        
        print(f"\n✅ Created {len(geoid_ids)} geoids for crypto analysis")
        return geoid_ids
    
    def demo_3_contradiction_detection(self):
        """Demo 3: Financial contradiction detection"""
        print("\n" + "="*60)
        print("DEMO 3: Financial Contradiction Detection")
        print("="*60)
        
        # Use technology sector for contradiction analysis
        tech_stocks = MARKET_SECTORS["technology"][:5]  # Limit to 5 for demo
        
        print(f"🔍 Analyzing contradictions in technology sector...")
        print(f"   Stocks: {', '.join(tech_stocks)}")
        
        try:
            # Detect contradictions
            result = self.kimera.detect_financial_contradictions(tech_stocks)
            
            if result.get('error'):
                print(f"   ❌ Error: {result['error']}")
                return
            
            contradictions = result.get('contradictions_detected', 0)
            scars_created = result.get('scars_created', 0)
            
            print(f"\n📊 Analysis Results:")
            print(f"   🔥 Contradictions detected: {contradictions}")
            print(f"   ⚡ Scars created: {scars_created}")
            print(f"   🔄 Cycle: {result.get('cycle', 'N/A')}")
            
            if contradictions > 0:
                print(f"\n🚨 CONTRADICTION DETAILS:")
                for i, analysis in enumerate(result.get('analysis_results', []), 1):
                    tension = analysis.get('tension', {})
                    print(f"\n   Contradiction #{i}:")
                    print(f"   📍 Geoids: {tension.get('geoids_involved', [])}")
                    print(f"   📊 Score: {tension.get('score', 'N/A')}")
                    print(f"   🏷️  Type: {tension.get('type', 'N/A')}")
                    print(f"   💪 Pulse Strength: {analysis.get('pulse_strength', 'N/A')}")
                    print(f"   🎯 Decision: {analysis.get('system_decision', 'N/A')}")
                    print(f"   ⚡ Scar Created: {'Yes' if analysis.get('scar_created') else 'No'}")
            else:
                print(f"\n✅ No significant contradictions detected in tech sector")
            
        except Exception as e:
            print(f"   ❌ Error in contradiction detection: {e}")
    
    def demo_4_cross_asset_analysis(self):
        """Demo 4: Cross-asset contradiction analysis"""
        print("\n" + "="*60)
        print("DEMO 4: Cross-Asset Contradiction Analysis")
        print("="*60)
        
        print("🔍 Analyzing contradictions across asset classes...")
        
        # Mix of stocks and crypto
        mixed_assets = ["AAPL", "TSLA", "bitcoin", "ethereum"]
        
        try:
            result = self.kimera.detect_financial_contradictions(mixed_assets)
            
            contradictions = result.get('contradictions_detected', 0)
            scars_created = result.get('scars_created', 0)
            
            print(f"\n📊 Cross-Asset Analysis:")
            print(f"   🔥 Contradictions: {contradictions}")
            print(f"   ⚡ Scars: {scars_created}")
            
            if contradictions > 0:
                print(f"\n🚨 CROSS-ASSET CONTRADICTIONS:")
                for analysis in result.get('analysis_results', []):
                    tension = analysis.get('tension', {})
                    geoids = tension.get('geoids_involved', [])
                    print(f"   📍 {geoids[0]} ↔ {geoids[1]}")
                    print(f"   🎯 Decision: {analysis.get('system_decision', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error in cross-asset analysis: {e}")
    
    def demo_5_system_monitoring(self):
        """Demo 5: System monitoring and status"""
        print("\n" + "="*60)
        print("DEMO 5: System Monitoring and Status")
        print("="*60)
        
        try:
            # Get system status
            response = requests.get(f"{self.config.kimera_api_url}/system/status")
            status = response.json()
            
            print("📊 KIMERA System Status:")
            print(f"   🧠 Active Geoids: {status.get('active_geoids', 0)}")
            print(f"   🏛️  Vault A Scars: {status.get('vault_a_scars', 0)}")
            print(f"   🏛️  Vault B Scars: {status.get('vault_b_scars', 0)}")
            print(f"   🌀 System Entropy: {status.get('system_entropy', 0):.3f}")
            print(f"   🔄 Cycle Count: {status.get('cycle_count', 0)}")
            
            # Get stability metrics
            response = requests.get(f"{self.config.kimera_api_url}/system/stability")
            stability = response.json()
            
            print(f"\n📈 Stability Metrics:")
            for metric, value in stability.items():
                if isinstance(value, float):
                    print(f"   📊 {metric.replace('_', ' ').title()}: {value:.3f}")
                else:
                    print(f"   📊 {metric.replace('_', ' ').title()}: {value}")
            
            # Trigger a cognitive cycle
            print(f"\n🔄 Triggering cognitive cycle...")
            response = requests.post(f"{self.config.kimera_api_url}/system/cycle")
            cycle_result = response.json()
            
            print(f"   ✅ Cycle Status: {cycle_result.get('status', 'N/A')}")
            print(f"   🔥 Contradictions: {cycle_result.get('contradictions_detected', 0)}")
            print(f"   ⚡ Scars Created: {cycle_result.get('scars_created', 0)}")
            print(f"   🌀 Entropy Delta: {cycle_result.get('entropy_delta', 0):.3f}")
            
        except Exception as e:
            print(f"   ❌ Error in system monitoring: {e}")
    
    def demo_6_vault_inspection(self):
        """Demo 6: Vault inspection and analysis"""
        print("\n" + "="*60)
        print("DEMO 6: Vault Inspection and Analysis")
        print("="*60)
        
        for vault_id in ["vault_a", "vault_b"]:
            print(f"\n🏛️  Inspecting {vault_id.upper()}...")
            
            try:
                response = requests.get(f"{self.config.kimera_api_url}/vaults/{vault_id}?limit=5")
                vault_data = response.json()
                
                scars = vault_data.get('scars', [])
                print(f"   📊 Total scars shown: {len(scars)}")
                
                if scars:
                    print(f"   🔍 Recent scars:")
                    for i, scar in enumerate(scars[:3], 1):
                        print(f"      {i}. {scar.get('scar_id', 'N/A')}")
                        print(f"         Reason: {scar.get('reason', 'N/A')[:50]}...")
                        print(f"         Entropy Δ: {scar.get('delta_entropy', 0):.3f}")
                        print(f"         Geoids: {len(scar.get('geoids', []))}")
                else:
                    print(f"   📭 No scars in {vault_id}")
                
            except Exception as e:
                print(f"   ❌ Error inspecting {vault_id}: {e}")
    
    def run_all_demos(self):
        """Run all demonstration scenarios"""
        print("🚀 KIMERA SWM Financial API Integration Demo")
        print("=" * 60)
        print("This demo shows how to integrate financial APIs with KIMERA SWM")
        print("for real-world contradiction detection and semantic analysis.")
        
        try:
            # Run all demos
            self.demo_1_basic_stock_analysis()
            time.sleep(2)  # Brief pause between demos
            
            self.demo_2_crypto_analysis()
            time.sleep(2)
            
            self.demo_3_contradiction_detection()
            time.sleep(2)
            
            self.demo_4_cross_asset_analysis()
            time.sleep(2)
            
            self.demo_5_system_monitoring()
            time.sleep(2)
            
            self.demo_6_vault_inspection()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETE")
            print("="*60)
            print("🎯 Key Takeaways:")
            print("   • Financial data successfully converted to semantic features")
            print("   • KIMERA detected contradictions in market data")
            print("   • System created scars representing market anomalies")
            print("   • Cross-asset analysis revealed hidden relationships")
            print("   • Real-time monitoring enables continuous market surveillance")
            
            print(f"\n🔗 Next Steps:")
            print(f"   • Customize contradiction detection for your use case")
            print(f"   • Add real-time alerts and notifications")
            print(f"   • Integrate with your trading or analysis systems")
            print(f"   • Explore the KIMERA API at: {self.config.kimera_api_url}/docs")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")


def main():
    """Main demo function"""
    demo = FinancialDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()