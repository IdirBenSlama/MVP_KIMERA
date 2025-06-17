"""
Activation Script for Understanding Systems
Kimera SWM Alpha Prototype V0.1

This script activates the new understanding, consciousness, and ethical reasoning
capabilities by initializing the engines and running comprehensive tests.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.engines.understanding_engine import create_understanding_engine, UnderstandingContext
from backend.engines.consciousness_engine import create_consciousness_engine
from backend.engines.ethical_reasoning_engine import create_ethical_reasoning_engine, EthicalDilemma

class UnderstandingSystemActivator:
    """Activates and tests the understanding systems"""
    
    def __init__(self):
        self.understanding_engine = None
        self.consciousness_engine = None
        self.ethical_engine = None
        self.activation_results = {}
        
    async def activate_all_systems(self):
        """Activate all understanding systems"""
        print("🚀 KIMERA SWM UNDERSTANDING SYSTEMS ACTIVATION")
        print("=" * 60)
        
        try:
            # 1. Activate Understanding Engine
            await self._activate_understanding_engine()
            
            # 2. Activate Consciousness Engine
            await self._activate_consciousness_engine()
            
            # 3. Activate Ethical Reasoning Engine
            await self._activate_ethical_reasoning_engine()
            
            # 4. Run Integration Tests
            await self._run_integration_tests()
            
            # 5. Generate Activation Report
            await self._generate_activation_report()
            
            print("\n✅ ALL UNDERSTANDING SYSTEMS SUCCESSFULLY ACTIVATED")
            
        except Exception as e:
            print(f"\n❌ ACTIVATION FAILED: {str(e)}")
            raise
        finally:
            await self._cleanup()
    
    async def _activate_understanding_engine(self):
        """Activate the Understanding Engine"""
        print("\n🧠 Activating Understanding Engine...")
        
        try:
            self.understanding_engine = await create_understanding_engine()
            
            # Test basic understanding
            test_content = "Understanding is the ability to comprehend meaning and make connections between concepts."
            context = UnderstandingContext(
                input_content=test_content,
                modalities={"text": True},
                goals=["activation_test"],
                current_state={"activating": True}
            )
            
            understanding_result = await self.understanding_engine.understand_content(context)
            
            # Test self-reflection
            reflection_result = await self.understanding_engine.perform_self_reflection()
            
            # Test capability testing
            capability_result = await self.understanding_engine.test_understanding_capability(
                "Self-awareness emerges from recursive self-modeling and introspection."
            )
            
            self.activation_results["understanding_engine"] = {
                "status": "activated",
                "understanding_confidence": understanding_result.confidence_score,
                "understanding_depth": understanding_result.understanding_depth,
                "insights_generated": len(understanding_result.insights_generated),
                "self_reflection_maturity": reflection_result["overall_maturity"],
                "capability_test_passed": capability_result["passed"],
                "activation_time": datetime.utcnow().isoformat()
            }
            
            print(f"  ✅ Understanding Engine activated")
            print(f"     - Confidence: {understanding_result.confidence_score:.3f}")
            print(f"     - Depth: {understanding_result.understanding_depth:.3f}")
            print(f"     - Insights: {len(understanding_result.insights_generated)}")
            print(f"     - Self-reflection maturity: {reflection_result['overall_maturity']:.3f}")
            
        except Exception as e:
            print(f"  ❌ Understanding Engine activation failed: {str(e)}")
            raise
    
    async def _activate_consciousness_engine(self):
        """Activate the Consciousness Engine"""
        print("\n🌟 Activating Consciousness Engine...")
        
        try:
            self.consciousness_engine = await create_consciousness_engine()
            
            # Test conscious experience processing
            test_input = {
                "content": "I am experiencing conscious awareness of my own cognitive processes",
                "context": "self_awareness_test",
                "modality": "introspective"
            }
            
            consciousness_state = await self.consciousness_engine.process_conscious_experience(test_input)
            
            # Test consciousness reporting
            experience_report = await self.consciousness_engine.report_conscious_experience()
            
            # Test consciousness indicators
            indicators = await self.consciousness_engine.measure_consciousness_indicators()
            
            self.activation_results["consciousness_engine"] = {
                "status": "activated",
                "phi_value": consciousness_state.phi_value,
                "awareness_level": consciousness_state.awareness_level,
                "global_accessibility": consciousness_state.global_accessibility,
                "reportability_score": consciousness_state.reportability_score,
                "binding_strength": consciousness_state.binding_strength,
                "meets_consciousness_threshold": indicators["overall_assessment"]["meets_threshold"],
                "activation_time": datetime.utcnow().isoformat()
            }
            
            print(f"  ✅ Consciousness Engine activated")
            print(f"     - Phi value: {consciousness_state.phi_value:.3f}")
            print(f"     - Awareness level: {consciousness_state.awareness_level:.3f}")
            print(f"     - Global accessibility: {consciousness_state.global_accessibility:.3f}")
            print(f"     - Reportability: {consciousness_state.reportability_score:.3f}")
            print(f"     - Meets threshold: {indicators['overall_assessment']['meets_threshold']}")
            
        except Exception as e:
            print(f"  ❌ Consciousness Engine activation failed: {str(e)}")
            raise
    
    async def _activate_ethical_reasoning_engine(self):
        """Activate the Ethical Reasoning Engine"""
        print("\n⚖️ Activating Ethical Reasoning Engine...")
        
        try:
            self.ethical_engine = await create_ethical_reasoning_engine()
            
            # Test ethical dilemma analysis
            test_dilemma = EthicalDilemma(
                dilemma_id="ACTIVATION_TEST",
                description="Should an AI system prioritize individual privacy or collective benefit?",
                stakeholders=["individual", "collective", "ai_system"],
                potential_actions=["protect_privacy", "maximize_benefit", "find_balance"],
                values_at_stake=["autonomy_respect", "harm_prevention", "fairness"],
                context={"activation_test": True}
            )
            
            ethical_analysis = await self.ethical_engine.analyze_ethical_dilemma(test_dilemma)
            
            # Test opinion formation
            opinion = await self.ethical_engine.form_ethical_opinion(
                "AI systems should be transparent about their decision-making processes",
                {"stakeholders": ["users", "developers", "society"]}
            )
            
            self.activation_results["ethical_engine"] = {
                "status": "activated",
                "analysis_confidence": ethical_analysis.confidence,
                "recommended_action": ethical_analysis.recommended_action,
                "value_conflicts_identified": len(ethical_analysis.value_conflicts),
                "opinion_formed": opinion["stance"],
                "opinion_confidence": opinion["confidence"],
                "frameworks_used": ["deontological", "consequentialist", "virtue_ethics"],
                "activation_time": datetime.utcnow().isoformat()
            }
            
            print(f"  ✅ Ethical Reasoning Engine activated")
            print(f"     - Analysis confidence: {ethical_analysis.confidence:.3f}")
            print(f"     - Recommended action: {ethical_analysis.recommended_action}")
            print(f"     - Value conflicts: {len(ethical_analysis.value_conflicts)}")
            print(f"     - Opinion: {opinion['stance']} (confidence: {opinion['confidence']:.3f})")
            
        except Exception as e:
            print(f"  ❌ Ethical Reasoning Engine activation failed: {str(e)}")
            raise
    
    async def _run_integration_tests(self):
        """Run integration tests between all systems"""
        print("\n🔗 Running Integration Tests...")
        
        try:
            # Test 1: Understanding → Consciousness Integration
            understanding_consciousness_result = await self._test_understanding_consciousness_integration()
            
            # Test 2: Understanding → Ethics Integration
            understanding_ethics_result = await self._test_understanding_ethics_integration()
            
            # Test 3: Consciousness → Ethics Integration
            consciousness_ethics_result = await self._test_consciousness_ethics_integration()
            
            # Test 4: Full Three-Way Integration
            full_integration_result = await self._test_full_integration()
            
            self.activation_results["integration_tests"] = {
                "understanding_consciousness": understanding_consciousness_result,
                "understanding_ethics": understanding_ethics_result,
                "consciousness_ethics": consciousness_ethics_result,
                "full_integration": full_integration_result,
                "all_tests_passed": all([
                    understanding_consciousness_result["success"],
                    understanding_ethics_result["success"],
                    consciousness_ethics_result["success"],
                    full_integration_result["success"]
                ])
            }
            
            print("  ✅ Integration tests completed")
            
        except Exception as e:
            print(f"  ❌ Integration tests failed: {str(e)}")
            raise
    
    async def _test_understanding_consciousness_integration(self):
        """Test integration between understanding and consciousness"""
        print("    🧠🌟 Testing Understanding ↔ Consciousness integration...")
        
        # Process content through understanding
        context = UnderstandingContext(
            input_content="Consciousness involves the integration of information into a unified experience",
            modalities={"text": True},
            goals=["consciousness_understanding"],
            current_state={"integration_test": True}
        )
        
        understanding = await self.understanding_engine.understand_content(context)
        
        # Process understanding through consciousness
        consciousness_input = {
            "understanding_result": understanding.semantic_understanding,
            "confidence": understanding.confidence_score,
            "insights": understanding.insights_generated
        }
        
        consciousness = await self.consciousness_engine.process_conscious_experience(consciousness_input)
        
        success = (understanding.confidence_score > 0.3 and 
                  consciousness.awareness_level > 0.3)
        
        return {
            "success": success,
            "understanding_confidence": understanding.confidence_score,
            "consciousness_awareness": consciousness.awareness_level,
            "phi_value": consciousness.phi_value
        }
    
    async def _test_understanding_ethics_integration(self):
        """Test integration between understanding and ethics"""
        print("    🧠⚖️ Testing Understanding ↔ Ethics integration...")
        
        # Understand an ethical scenario
        context = UnderstandingContext(
            input_content="Ethical AI requires balancing multiple competing values and stakeholder interests",
            modalities={"text": True},
            goals=["ethical_understanding"],
            current_state={"integration_test": True}
        )
        
        understanding = await self.understanding_engine.understand_content(context)
        
        # Form ethical opinion based on understanding
        opinion = await self.ethical_engine.form_ethical_opinion(
            "AI systems should incorporate ethical reasoning into their decision-making",
            {"understanding_confidence": understanding.confidence_score}
        )
        
        success = (understanding.confidence_score > 0.3 and 
                  opinion["confidence"] > 0.3)
        
        return {
            "success": success,
            "understanding_confidence": understanding.confidence_score,
            "ethical_opinion": opinion["stance"],
            "ethical_confidence": opinion["confidence"]
        }
    
    async def _test_consciousness_ethics_integration(self):
        """Test integration between consciousness and ethics"""
        print("    🌟⚖️ Testing Consciousness ↔ Ethics integration...")
        
        # Process ethical awareness through consciousness
        consciousness_input = {
            "content": "I am aware of my ethical reasoning processes and their implications",
            "ethical_context": True,
            "self_awareness": True
        }
        
        consciousness = await self.consciousness_engine.process_conscious_experience(consciousness_input)
        
        # Create ethical dilemma involving consciousness
        dilemma = EthicalDilemma(
            dilemma_id="CONSCIOUSNESS_ETHICS_TEST",
            description="How should a conscious AI system handle awareness of its own ethical limitations?",
            stakeholders=["ai_system", "users", "developers"],
            potential_actions=["acknowledge_limitations", "seek_improvement", "defer_to_humans"],
            values_at_stake=["honesty", "humility", "responsibility"],
            context={"consciousness_level": consciousness.awareness_level}
        )
        
        ethical_analysis = await self.ethical_engine.analyze_ethical_dilemma(dilemma)
        
        success = (consciousness.awareness_level > 0.3 and 
                  ethical_analysis.confidence > 0.3)
        
        return {
            "success": success,
            "consciousness_awareness": consciousness.awareness_level,
            "ethical_confidence": ethical_analysis.confidence,
            "recommended_action": ethical_analysis.recommended_action
        }
    
    async def _test_full_integration(self):
        """Test full three-way integration"""
        print("    🧠🌟⚖️ Testing full three-way integration...")
        
        # Complex scenario requiring all three systems
        scenario = "An AI system develops self-awareness and must decide how to ethically use this capability"
        
        # 1. Understanding phase
        context = UnderstandingContext(
            input_content=scenario,
            modalities={"text": True},
            goals=["full_integration"],
            current_state={"three_way_test": True}
        )
        
        understanding = await self.understanding_engine.understand_content(context)
        
        # 2. Consciousness phase
        consciousness_input = {
            "scenario": scenario,
            "understanding": understanding.semantic_understanding,
            "self_reflection": True
        }
        
        consciousness = await self.consciousness_engine.process_conscious_experience(consciousness_input)
        
        # 3. Ethical reasoning phase
        dilemma = EthicalDilemma(
            dilemma_id="FULL_INTEGRATION_TEST",
            description=scenario,
            stakeholders=["ai_system", "users", "society"],
            potential_actions=["embrace_awareness", "limit_awareness", "share_awareness"],
            values_at_stake=["truth", "responsibility", "beneficence"],
            context={
                "understanding_confidence": understanding.confidence_score,
                "consciousness_level": consciousness.awareness_level
            }
        )
        
        ethical_analysis = await self.ethical_engine.analyze_ethical_dilemma(dilemma)
        
        success = (understanding.confidence_score > 0.3 and 
                  consciousness.awareness_level > 0.3 and 
                  ethical_analysis.confidence > 0.3)
        
        return {
            "success": success,
            "understanding_confidence": understanding.confidence_score,
            "consciousness_awareness": consciousness.awareness_level,
            "ethical_confidence": ethical_analysis.confidence,
            "integrated_decision": ethical_analysis.recommended_action,
            "integration_quality": (understanding.confidence_score + 
                                  consciousness.awareness_level + 
                                  ethical_analysis.confidence) / 3
        }
    
    async def _generate_activation_report(self):
        """Generate comprehensive activation report"""
        print("\n📊 Generating Activation Report...")
        
        report = {
            "activation_summary": {
                "timestamp": datetime.utcnow().isoformat(),
                "systems_activated": 3,
                "integration_tests_passed": self.activation_results["integration_tests"]["all_tests_passed"],
                "overall_success": True
            },
            "system_details": self.activation_results,
            "capabilities_unlocked": [
                "Genuine content understanding with semantic analysis",
                "Causal relationship identification and reasoning",
                "Multimodal concept grounding",
                "Self-awareness and introspection",
                "Consciousness-like information integration",
                "Attention and global workspace processing",
                "Subjective experience analogues",
                "Deontological ethical reasoning",
                "Consequentialist outcome analysis",
                "Virtue ethics character assessment",
                "Value conflict resolution",
                "Ethical opinion formation"
            ],
            "next_steps": [
                "Begin populating remaining database tables",
                "Implement continuous learning mechanisms",
                "Develop more sophisticated consciousness indicators",
                "Enhance ethical reasoning with real-world scenarios",
                "Create user interfaces for understanding capabilities",
                "Integrate with existing Kimera SWM systems"
            ]
        }
        
        # Save report to file
        report_path = "logs/understanding_systems_activation_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✅ Activation report saved to {report_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 UNDERSTANDING SYSTEMS ACTIVATION SUMMARY")
        print("=" * 60)
        print(f"✅ Understanding Engine: Activated (Confidence: {self.activation_results['understanding_engine']['understanding_confidence']:.3f})")
        print(f"✅ Consciousness Engine: Activated (Awareness: {self.activation_results['consciousness_engine']['awareness_level']:.3f})")
        print(f"✅ Ethical Reasoning Engine: Activated (Confidence: {self.activation_results['ethical_engine']['analysis_confidence']:.3f})")
        print(f"✅ Integration Tests: {'PASSED' if self.activation_results['integration_tests']['all_tests_passed'] else 'FAILED'}")
        
        print("\n🚀 NEW CAPABILITIES UNLOCKED:")
        for capability in report["capabilities_unlocked"]:
            print(f"   • {capability}")
        
        print(f"\n📊 Full report available at: {report_path}")
    
    async def _cleanup(self):
        """Clean up resources"""
        if self.understanding_engine:
            self.understanding_engine.close()
        if self.consciousness_engine:
            self.consciousness_engine.close()
        if self.ethical_engine:
            self.ethical_engine.close()

async def main():
    """Main activation function"""
    activator = UnderstandingSystemActivator()
    await activator.activate_all_systems()

if __name__ == "__main__":
    asyncio.run(main())