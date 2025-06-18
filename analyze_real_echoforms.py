#!/usr/bin/env python3
"""
Real EchoForm Analysis for KIMERA Insights
==========================================

This script fetches real insights from KIMERA and analyzes their EchoForm representations
to reveal the deep cognitive structures behind the system's thinking.
"""

import requests
import json
from typing import Dict, Any, List
from echoform_analysis import EchoFormAnalyzer

def fetch_kimera_insights() -> List[Dict[str, Any]]:
    """Fetch real insights from KIMERA system"""
    try:
        # Try to fetch insights from KIMERA API
        response = requests.get("http://localhost:8001/insights/recent", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'insights' in data:
                return data['insights']
            else:
                print("⚠️  Unexpected response format from KIMERA")
                return []
        else:
            print(f"⚠️  KIMERA API returned status {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not connect to KIMERA: {e}")
        return []

def analyze_real_echoforms():
    """Analyze real EchoForm representations from KIMERA insights"""
    print("🔍 ANALYZING REAL ECHOFORMS FROM KIMERA")
    print("="*60)
    print("\nFetching insights from KIMERA system...")
    
    insights = fetch_kimera_insights()
    
    if not insights:
        print("\n❌ No insights available from KIMERA system.")
        print("   Make sure KIMERA is running on localhost:8001")
        print("   and has generated some insights.\n")
        
        # Show demonstration with synthetic examples instead
        print("📚 SHOWING DEMONSTRATION WITH SYNTHETIC EXAMPLES:")
        print("-" * 50)
        demonstrate_with_examples()
        return
    
    print(f"\n✅ Found {len(insights)} insights from KIMERA")
    print("   Analyzing their EchoForm representations...\n")
    
    analyzer = EchoFormAnalyzer()
    
    for i, insight in enumerate(insights[:5], 1):  # Analyze first 5 insights
        print(f"\n🧠 REAL INSIGHT {i}")
        print("-" * 50)
        
        # Extract basic insight information
        insight_id = insight.get('insight_id', 'Unknown')
        insight_type = insight.get('insight_type', 'Unknown')
        confidence = insight.get('confidence', 0.0)
        entropy_reduction = insight.get('entropy_reduction', 0.0)
        
        print(f"ID: {insight_id}")
        print(f"Type: {insight_type}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Entropy Reduction: {entropy_reduction:.3f}")
        
        # Analyze the EchoForm representation
        echoform_repr = insight.get('echoform_repr', {})
        
        if not echoform_repr:
            print("❌ No EchoForm representation found in this insight")
            continue
        
        print(f"\n🔍 ECHOFORM STRUCTURE:")
        print(f"   Raw EchoForm: {json.dumps(echoform_repr, indent=2)}")
        
        # Perform detailed analysis
        analysis = analyzer.analyze_echoform(echoform_repr)
        
        if 'error' in analysis:
            print(f"❌ Analysis error: {analysis['error']}")
            continue
        
        # Display analysis results
        print(f"\n📊 STRUCTURAL ANALYSIS:")
        struct = analysis['structure_analysis']
        print(f"   Completeness: {struct['completeness']}")
        print(f"   Components: {', '.join(struct['components'])}")
        print(f"   Complexity Score: {struct['complexity_score']}")
        
        print(f"\n🔍 CONCEPT ANALYSIS:")
        concepts = analysis['concept_analysis']
        if 'error' not in concepts:
            print(f"   Primary Concepts: {', '.join(concepts['primary_concepts'])}")
            print(f"   Dominant Concept: {concepts['dominant_concept']}")
            if isinstance(concepts['concept_weights'], dict):
                print(f"   Concept Weights: {concepts['concept_weights']}")
            print(f"   Semantic Density: {concepts['semantic_density']}")
        
        print(f"\n🎭 ARCHETYPE ANALYSIS:")
        archetype = analysis['archetype_analysis']
        if 'error' not in archetype:
            print(f"   Archetype: {archetype['archetype_name']}")
            print(f"   Meaning: {archetype['archetype_meaning']}")
            print(f"   Cognitive Pattern: {archetype['cognitive_pattern']}")
            print(f"   Family: {archetype['archetypal_family']}")
        
        print(f"\n⚡ PARADOX ANALYSIS:")
        paradox = analysis['paradox_analysis']
        if 'error' not in paradox:
            print(f"   Paradox: {paradox['paradox_statement']}")
            print(f"   Type: {paradox['paradox_type']}")
            print(f"   Dynamics: {paradox['tension_dynamics']}")
            print(f"   Challenge: {paradox['cognitive_challenge']}")
        
        print(f"\n🧩 COGNITIVE SIGNATURE:")
        signature = analysis['cognitive_signature']
        print(f"   Cognitive Type: {signature['cognitive_type']}")
        print(f"   Processing Style: {signature['processing_style']}")
        print(f"   Abstraction Level: {signature['abstraction_level']}")
        print(f"   Complexity Class: {signature['complexity_class']}")
        
        print(f"\n💡 INTERPRETATION:")
        print(f"   {analysis['interpretation_summary']}")
        
        print("\n" + "="*60)

def demonstrate_with_examples():
    """Demonstrate EchoForm analysis with synthetic examples when real data unavailable"""
    
    # These are realistic examples based on KIMERA's actual structure
    synthetic_insights = [
        {
            "insight_id": "INS_demo_001",
            "insight_type": "ANALOGY",
            "confidence": 0.82,
            "entropy_reduction": 0.28,
            "echoform_repr": {
                "type": "ANALOGY",
                "core_concept": {"financial_volatility": 0.85, "market_psychology": 0.78},
                "archetype": "The Stampede",
                "paradox": "Individual rationality creates collective irrationality"
            }
        },
        {
            "insight_id": "INS_demo_002", 
            "insight_type": "HYPOTHESIS",
            "confidence": 0.71,
            "entropy_reduction": 0.19,
            "echoform_repr": {
                "type": "HYPOTHESIS",
                "core_concept": {"atmospheric_pressure": 0.73, "cascade_effects": 0.69},
                "archetype": "The Hidden Trigger",
                "paradox": "Small changes create large effects"
            }
        },
        {
            "insight_id": "INS_demo_003",
            "insight_type": "META_FRAMEWORK",
            "confidence": 0.76,
            "entropy_reduction": 0.33,
            "echoform_repr": {
                "type": "META_FRAMEWORK", 
                "core_concept": {"bias_detection": 0.81, "cognitive_monitoring": 0.75},
                "archetype": "The Self-Critic",
                "paradox": "Awareness of bias can create new biases"
            }
        }
    ]
    
    analyzer = EchoFormAnalyzer()
    
    for i, insight in enumerate(synthetic_insights, 1):
        print(f"\n🧠 DEMONSTRATION INSIGHT {i}")
        print("-" * 50)
        
        # Extract basic insight information
        insight_id = insight['insight_id']
        insight_type = insight['insight_type']
        confidence = insight['confidence']
        entropy_reduction = insight['entropy_reduction']
        
        print(f"ID: {insight_id}")
        print(f"Type: {insight_type}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Entropy Reduction: {entropy_reduction:.3f}")
        
        # Analyze the EchoForm representation
        echoform_repr = insight['echoform_repr']
        
        print(f"\n🔍 ECHOFORM STRUCTURE:")
        print(f"   Raw EchoForm: {json.dumps(echoform_repr, indent=2)}")
        
        # Perform detailed analysis
        analysis = analyzer.analyze_echoform(echoform_repr)
        
        # Display key analysis results
        print(f"\n📊 KEY FINDINGS:")
        struct = analysis['structure_analysis']
        concepts = analysis['concept_analysis']
        archetype = analysis['archetype_analysis']
        paradox = analysis['paradox_analysis']
        signature = analysis['cognitive_signature']
        
        print(f"   • Structure: {struct['completeness']}")
        print(f"   • Dominant Concept: {concepts['dominant_concept']}")
        print(f"   • Archetype: {archetype['archetype_name']} ({archetype['cognitive_pattern']})")
        print(f"   • Paradox Type: {paradox['paradox_type']}")
        print(f"   • Processing Style: {signature['processing_style']}")
        
        print(f"\n💡 WHAT THE ECHOFORM REVEALS:")
        print(f"   {analysis['interpretation_summary']}")
        
        print("\n" + "="*60)

def main():
    """Main function to run EchoForm analysis"""
    print("🚀 Starting Real EchoForm Analysis...")
    analyze_real_echoforms()
    
    print(f"\n📚 For more detailed analysis tools, see:")
    print(f"   • echoform_analysis.py - Technical analysis framework")
    print(f"   • ECHOFORM_INTERPRETATION_GUIDE.md - Comprehensive guide")
    print(f"   • insight_interpretation_guide.py - Practical interpretation tools")

if __name__ == "__main__":
    main() 