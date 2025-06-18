"""
Example: Integrating Phase 1 Semantic Grounding with KIMERA Workflows
Shows how to use the new semantic understanding capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.semantic_grounding import (
    EmbodiedSemanticEngine,
    IntentionalProcessor
)
from backend.semantic_grounding.intentional_processor import Goal, GoalPriority
from backend.vault.understanding_vault_manager import UnderstandingVaultManager
from backend.core.geoid import GeoidState
from backend.core.scar import ScarRecord
import numpy as np
from datetime import datetime


def demonstrate_semantic_understanding():
    """Demonstrate semantic understanding of a complex concept"""
    print("\n" + "="*80)
    print("🧠 KIMERA SEMANTIC UNDERSTANDING DEMONSTRATION")
    print("="*80)
    
    # Initialize components
    semantic_engine = EmbodiedSemanticEngine()
    understanding_vault = UnderstandingVaultManager()
    
    # Example 1: Understanding a complex concept
    print("\n📚 Example 1: Understanding 'thunderstorm'")
    
    # Ground the concept
    grounding = semantic_engine.process_concept("thunderstorm")
    
    print(f"\nGrounding confidence: {grounding.confidence:.2f}")
    print("\nMultimodal understanding:")
    
    if grounding.visual:
        print(f"  👁️ Visual: {grounding.visual.get('properties', {})}")
    
    if grounding.auditory:
        print(f"  👂 Auditory: {grounding.auditory.get('properties', {})}")
    
    if grounding.causal:
        print(f"  ⚡ Causal: causes={grounding.causal.get('causes', [])}, effects={grounding.causal.get('effects', [])}")
    
    if grounding.temporal:
        print(f"  ⏰ Temporal: {grounding.temporal.get('patterns', [])}")
    
    if grounding.physical:
        print(f"  ⚛️ Physical: state={grounding.physical.get('state', 'complex')}")
    
    # Store in understanding vault
    grounding_id = understanding_vault.create_multimodal_grounding(
        concept_id="thunderstorm",
        visual_features=grounding.visual,
        auditory_features=grounding.auditory,
        temporal_context=grounding.temporal,
        physical_properties=grounding.physical,
        confidence_score=grounding.confidence
    )
    
    print(f"\n✅ Stored grounding with ID: {grounding_id}")


def demonstrate_causal_understanding():
    """Demonstrate causal reasoning capabilities"""
    print("\n" + "="*80)
    print("⚡ CAUSAL UNDERSTANDING DEMONSTRATION")
    print("="*80)
    
    understanding_vault = UnderstandingVaultManager()
    
    # Establish causal relationships
    print("\n🔗 Establishing causal relationships:")
    
    # Rain causes wet ground
    rel1_id = understanding_vault.establish_causal_relationship(
        cause_concept_id="rain",
        effect_concept_id="wet_ground",
        causal_strength=0.9,
        mechanism_description="Water falls from sky and accumulates on ground",
        evidence_quality=0.95,
        temporal_delay=0.1  # Almost immediate
    )
    print(f"  - rain → wet_ground (ID: {rel1_id})")
    
    # Fire causes smoke
    rel2_id = understanding_vault.establish_causal_relationship(
        cause_concept_id="fire",
        effect_concept_id="smoke",
        causal_strength=0.85,
        mechanism_description="Combustion produces particulate matter",
        evidence_quality=0.9,
        temporal_delay=0.01  # Very quick
    )
    print(f"  - fire → smoke (ID: {rel2_id})")
    
    # Get causal chain
    print("\n📊 Causal chain for 'wet_ground':")
    chain = understanding_vault.get_causal_chain("wet_ground")
    print(f"  Causes: {chain['causes']}")
    print(f"  Effects: {chain['effects']}")


def demonstrate_goal_directed_processing():
    """Demonstrate intentional, goal-directed understanding"""
    print("\n" + "="*80)
    print("🎯 GOAL-DIRECTED PROCESSING DEMONSTRATION")
    print("="*80)
    
    processor = IntentionalProcessor()
    
    # Set a learning goal
    learning_goal = Goal(
        goal_id="understand_weather",
        description="Develop deep understanding of weather phenomena",
        priority=GoalPriority.HIGH,
        criteria={
            "concepts_understood": ["rain", "cloud", "storm", "wind"],
            "relationships_discovered": 10,
            "confidence_threshold": 0.8
        },
        metadata={
            "target_concepts": ["rain", "cloud", "storm", "wind", "temperature", "pressure"]
        }
    )
    
    processor.set_goal(learning_goal)
    print(f"\n📋 Goal set: {learning_goal.description}")
    
    # Process weather-related text with intention
    weather_text = """
    The storm clouds gather as atmospheric pressure drops. 
    Rain begins to fall, driven by strong winds. 
    Lightning flashes illuminate the darkening sky.
    """
    
    print(f"\n📖 Processing text: {weather_text[:50]}...")
    
    result = processor.process_with_intention(
        weather_text,
        current_goals=[learning_goal.goal_id],
        allow_exploration=True
    )
    
    print(f"\n📊 Processing results:")
    print(f"  - Strategy: {result.processing_strategy}")
    print(f"  - Confidence: {result.confidence:.2f}")
    print(f"  - Focused concepts: {list(result.focused_content.keys())}")
    print(f"  - Novel discoveries: {len(result.novel_discoveries)}")
    
    # Check goal progress
    status = processor.get_goal_status(learning_goal.goal_id)
    print(f"\n📈 Goal progress: {status['progress']:.1%}")


def demonstrate_understanding_evolution():
    """Demonstrate how understanding evolves over time"""
    print("\n" + "="*80)
    print("📈 UNDERSTANDING EVOLUTION DEMONSTRATION")
    print("="*80)
    
    understanding_vault = UnderstandingVaultManager()
    
    # Create initial self-model
    print("\n🤖 Creating self-model...")
    
    model_id = understanding_vault.update_self_model(
        processing_capabilities={
            "semantic_grounding": 0.8,
            "causal_reasoning": 0.7,
            "temporal_processing": 0.6
        },
        knowledge_domains={
            "physical_world": 0.7,
            "abstract_concepts": 0.5,
            "social_dynamics": 0.3
        },
        reasoning_patterns={
            "deductive": 0.8,
            "inductive": 0.6,
            "abductive": 0.5
        },
        limitation_awareness={
            "context_window": "limited",
            "real_world_interaction": "none",
            "consciousness": "simulated"
        },
        introspection_accuracy=0.7
    )
    
    print(f"✅ Self-model created: {model_id}")
    
    # Test understanding
    print("\n🧪 Testing understanding capabilities...")
    
    test_result = understanding_vault.test_understanding(
        test_type="compositional_semantics",
        test_description="Understanding 'red apple' compositionally",
        test_input={
            "components": ["red", "apple"],
            "context": "fruit description"
        },
        expected_output={
            "meaning": "apple with red color",
            "properties": ["edible", "fruit", "colored"]
        },
        actual_output={
            "meaning": "apple that is red",
            "properties": ["edible", "fruit", "colored", "sweet"]
        }
    )
    
    print(f"  Test passed: {test_result['passed']}")
    print(f"  Accuracy: {test_result['accuracy_score']:.2f}")
    print(f"  Understanding quality: {test_result['understanding_quality']:.2f}")
    
    # Get understanding metrics
    print("\n📊 Overall understanding metrics:")
    metrics = understanding_vault.get_understanding_metrics()
    
    print(f"\nComponents created:")
    for component, count in metrics['understanding_components'].items():
        print(f"  - {component}: {count}")
    
    print(f"\nRoadmap progress:")
    for phase, progress in metrics['roadmap_progress'].items():
        print(f"  - {phase}: {progress:.1%}")


def demonstrate_enhanced_scar_creation():
    """Show how to create understanding-enhanced SCARs"""
    print("\n" + "="*80)
    print("🔮 ENHANCED SCAR WITH UNDERSTANDING")
    print("="*80)
    
    understanding_vault = UnderstandingVaultManager()
    
    # Create a traditional SCAR
    traditional_scar = ScarRecord(
        scar_id=f"SCAR_DEMO_{datetime.now().timestamp()}",
        geoids=["concept_rain", "concept_wet"],
        reason="Causal relationship discovered",
        timestamp=datetime.now().isoformat(),
        resolved_by="semantic_grounding",
        pre_entropy=2.5,
        post_entropy=1.8,
        delta_entropy=-0.7,
        cls_angle=45.0,
        semantic_polarity=0.8,
        mutation_frequency=0.1,
        weight=1.5
    )
    
    # Enhance with understanding
    enhanced_id = understanding_vault.create_understanding_scar(
        traditional_scar=traditional_scar,
        understanding_depth=0.85,
        causal_understanding={
            "mechanism": "precipitation causes surface wetness",
            "strength": 0.9,
            "reversible": False
        },
        compositional_analysis={
            "components": ["rain", "ground", "wetness"],
            "emergence": "weather effect"
        },
        contextual_factors={
            "weather_conditions": "rainy",
            "surface_type": "various"
        },
        introspective_accuracy=0.8,
        value_implications={
            "practical": "seek shelter when raining",
            "safety": "slippery surfaces"
        }
    )
    
    print(f"✅ Created enhanced SCAR: {enhanced_id}")
    print("  - Has causal understanding")
    print("  - Includes compositional analysis")
    print("  - Contains value implications")


def main():
    """Run all demonstrations"""
    print("\n" + "🚀 "*20)
    print("KIMERA PHASE 1: SEMANTIC GROUNDING INTEGRATION EXAMPLES")
    print("🚀 "*20)
    
    # Run demonstrations
    demonstrate_semantic_understanding()
    demonstrate_causal_understanding()
    demonstrate_goal_directed_processing()
    demonstrate_understanding_evolution()
    demonstrate_enhanced_scar_creation()
    
    print("\n" + "="*80)
    print("✅ INTEGRATION EXAMPLES COMPLETED")
    print("="*80)
    
    print("\n💡 Key Takeaways:")
    print("1. Semantic grounding provides multimodal understanding of concepts")
    print("2. Causal reasoning goes beyond correlation to identify mechanisms")
    print("3. Goal-directed processing enables intentional learning")
    print("4. Understanding metrics track progress toward genuine comprehension")
    print("5. Enhanced SCARs incorporate semantic understanding")
    
    print("\n🔮 Next Steps:")
    print("1. Integrate semantic grounding into your KIMERA workflows")
    print("2. Use the UnderstandingVaultManager for persistence")
    print("3. Set learning goals for targeted understanding")
    print("4. Monitor understanding metrics over time")
    print("5. Prepare for Phase 2: Self-Model Construction")


if __name__ == "__main__":
    main()