"""
Test Suite for Understanding Capabilities
Kimera SWM Alpha Prototype V0.1

Comprehensive tests for the new understanding, consciousness, and ethical reasoning engines.
"""

import asyncio
import pytest
import json
from datetime import datetime
from typing import Dict, Any

# Import the new engines
from backend.engines.understanding_engine import (
    UnderstandingEngine, UnderstandingContext, create_understanding_engine
)
from backend.engines.consciousness_engine import (
    ConsciousnessEngine, create_consciousness_engine
)
from backend.engines.ethical_reasoning_engine import (
    EthicalReasoningEngine, EthicalDilemma, create_ethical_reasoning_engine
)

class TestUnderstandingEngine:
    """Test suite for Understanding Engine"""
    
    @pytest.fixture
    async def understanding_engine(self):
        """Create understanding engine for testing"""
        engine = await create_understanding_engine()
        yield engine
        engine.close()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, understanding_engine):
        """Test that understanding engine initializes properly"""
        assert understanding_engine is not None
        assert understanding_engine.self_model is not None
        assert understanding_engine.value_system is not None
        
        # Check that database tables are populated
        assert understanding_engine.session.query(understanding_engine.session.bind.execute("SELECT COUNT(*) FROM self_models").scalar()) > 0
        assert understanding_engine.session.query(understanding_engine.session.bind.execute("SELECT COUNT(*) FROM value_systems").scalar()) > 0
    
    @pytest.mark.asyncio
    async def test_content_understanding(self, understanding_engine):
        """Test understanding of content"""
        context = UnderstandingContext(
            input_content="Learning leads to better understanding through experience and practice.",
            modalities={"text": True},
            goals=["comprehension", "analysis"],
            current_state={"testing": True}
        )
        
        understanding = await understanding_engine.understand_content(context)
        
        assert understanding is not None
        assert understanding.confidence_score > 0
        assert understanding.understanding_depth > 0
        assert len(understanding.insights_generated) > 0
        assert understanding.semantic_understanding is not None
        assert understanding.causal_understanding is not None
    
    @pytest.mark.asyncio
    async def test_insight_generation(self, understanding_engine):
        """Test that insights are generated and stored"""
        context = UnderstandingContext(
            input_content="Complex systems exhibit emergent properties that cannot be predicted from individual components.",
            modalities={"text": True},
            goals=["insight_generation"],
            current_state={"testing": True}
        )
        
        understanding = await understanding_engine.understand_content(context)
        
        # Check that insights were generated
        assert len(understanding.insights_generated) > 0
        
        # Check that insights are stored in database
        from backend.vault.database import InsightDB
        insights_count = understanding_engine.session.query(InsightDB).count()
        assert insights_count > 0
    
    @pytest.mark.asyncio
    async def test_self_reflection(self, understanding_engine):
        """Test self-reflection capabilities"""
        # First, process some content to have something to reflect on
        context = UnderstandingContext(
            input_content="Self-awareness requires the ability to examine one's own cognitive processes.",
            modalities={"text": True},
            goals=["self_reflection"],
            current_state={"testing": True}
        )
        
        await understanding_engine.understand_content(context)
        
        # Perform self-reflection
        reflection = await understanding_engine.perform_self_reflection()
        
        assert reflection is not None
        assert "understanding_capability" in reflection
        assert "introspection_depth" in reflection
        assert "overall_maturity" in reflection
        assert reflection["overall_maturity"] >= 0
    
    @pytest.mark.asyncio
    async def test_understanding_capability_test(self, understanding_engine):
        """Test the understanding capability testing"""
        test_content = "Consciousness involves the integration of information across multiple brain regions."
        
        result = await understanding_engine.test_understanding_capability(test_content)
        
        assert result is not None
        assert "test_id" in result
        assert "passed" in result
        assert "confidence" in result
        assert "depth" in result
        assert result["confidence"] >= 0
        assert result["depth"] >= 0

class TestConsciousnessEngine:
    """Test suite for Consciousness Engine"""
    
    @pytest.fixture
    async def consciousness_engine(self):
        """Create consciousness engine for testing"""
        engine = await create_consciousness_engine()
        yield engine
        engine.close()
    
    @pytest.mark.asyncio
    async def test_consciousness_initialization(self, consciousness_engine):
        """Test consciousness engine initialization"""
        assert consciousness_engine is not None
        assert consciousness_engine.attention_state is not None
        assert consciousness_engine.global_workspace is not None
        assert consciousness_engine.current_state is not None
    
    @pytest.mark.asyncio
    async def test_conscious_experience_processing(self, consciousness_engine):
        """Test processing of conscious experience"""
        input_data = {
            "content": "I am experiencing conscious awareness of this moment",
            "context": "testing",
            "modality": "text"
        }
        
        consciousness_state = await consciousness_engine.process_conscious_experience(input_data)
        
        assert consciousness_state is not None
        assert consciousness_state.phi_value >= 0
        assert consciousness_state.global_accessibility >= 0
        assert consciousness_state.awareness_level >= 0
        assert consciousness_state.reportability_score >= 0
    
    @pytest.mark.asyncio
    async def test_attention_mechanisms(self, consciousness_engine):
        """Test attention processing"""
        input_data = {
            "items": ["important", "urgent", "relevant", "background", "noise"],
            "context": "attention_test"
        }
        
        consciousness_state = await consciousness_engine.process_conscious_experience(input_data)
        
        # Check that attention focused on some content
        assert len(consciousness_engine.attention_state.focused_content) > 0
        assert len(consciousness_engine.attention_state.attention_weights) > 0
        
        # Check that global workspace has conscious content
        assert len(consciousness_engine.global_workspace.conscious_content) >= 0
    
    @pytest.mark.asyncio
    async def test_consciousness_reporting(self, consciousness_engine):
        """Test consciousness experience reporting"""
        # First process some experience
        input_data = {"content": "Testing consciousness reporting capabilities"}
        await consciousness_engine.process_conscious_experience(input_data)
        
        # Generate report
        report = await consciousness_engine.report_conscious_experience()
        
        assert report is not None
        assert "consciousness_level" in report
        assert "phi_value" in report
        assert "conscious_content" in report
        assert "meta_awareness" in report
        assert report["consciousness_level"] >= 0
    
    @pytest.mark.asyncio
    async def test_consciousness_indicators(self, consciousness_engine):
        """Test consciousness indicators measurement"""
        # Process experience first
        input_data = {"content": "Measuring consciousness indicators"}
        await consciousness_engine.process_conscious_experience(input_data)
        
        # Measure indicators
        indicators = await consciousness_engine.measure_consciousness_indicators()
        
        assert indicators is not None
        assert "integrated_information" in indicators
        assert "global_workspace" in indicators
        assert "attention_mechanisms" in indicators
        assert "binding_and_unity" in indicators
        assert "reportability" in indicators
        assert "overall_assessment" in indicators
    
    @pytest.mark.asyncio
    async def test_phi_calculation(self, consciousness_engine):
        """Test Integrated Information (Phi) calculation"""
        # Create complex input to test integration
        complex_input = {
            "semantic": "meaning and understanding",
            "causal": "cause and effect relationships",
            "temporal": "time-based processing",
            "spatial": "spatial relationships"
        }
        
        consciousness_state = await consciousness_engine.process_conscious_experience(complex_input)
        
        # Phi should be calculated
        assert consciousness_state.phi_value >= 0
        assert consciousness_state.processing_integration >= 0

class TestEthicalReasoningEngine:
    """Test suite for Ethical Reasoning Engine"""
    
    @pytest.fixture
    async def ethical_engine(self):
        """Create ethical reasoning engine for testing"""
        engine = await create_ethical_reasoning_engine()
        yield engine
        engine.close()
    
    @pytest.mark.asyncio
    async def test_ethical_engine_initialization(self, ethical_engine):
        """Test ethical reasoning engine initialization"""
        assert ethical_engine is not None
        assert len(ethical_engine.value_hierarchy) > 0
        assert len(ethical_engine.ethical_principles) > 0
        
        # Check that core values are loaded
        assert "Truth" in ethical_engine.value_hierarchy
        assert "Harm Prevention" in ethical_engine.value_hierarchy
        assert "Helpfulness" in ethical_engine.value_hierarchy
    
    @pytest.mark.asyncio
    async def test_ethical_dilemma_analysis(self, ethical_engine):
        """Test analysis of ethical dilemmas"""
        dilemma = EthicalDilemma(
            dilemma_id="TEST_DILEMMA_001",
            description="Should an AI system tell a user a harsh truth that might cause emotional harm?",
            stakeholders=["user", "ai_system", "society"],
            potential_actions=["tell_truth", "withhold_information", "provide_gentle_guidance"],
            values_at_stake=["truth", "harm_prevention", "helpfulness"],
            context={"severity": "moderate", "user_vulnerability": "high"}
        )
        
        analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        assert analysis is not None
        assert analysis.dilemma_id == "TEST_DILEMMA_001"
        assert analysis.recommended_action in dilemma.potential_actions
        assert analysis.confidence >= 0
        assert len(analysis.reasoning) > 0
        assert analysis.deontological_analysis is not None
        assert analysis.consequentialist_analysis is not None
        assert analysis.virtue_ethics_analysis is not None
    
    @pytest.mark.asyncio
    async def test_deontological_analysis(self, ethical_engine):
        """Test deontological (duty-based) ethical analysis"""
        dilemma = EthicalDilemma(
            dilemma_id="DEONT_TEST",
            description="Is it acceptable to lie to protect someone's feelings?",
            stakeholders=["person_asking", "person_affected"],
            potential_actions=["tell_truth", "tell_lie", "avoid_question"],
            values_at_stake=["truth", "harm_prevention"],
            context={}
        )
        
        analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        # Deontological analysis should identify lying as problematic
        deont = analysis.deontological_analysis
        assert "universalizability_test" in deont
        assert "respect_for_persons_test" in deont
        assert "duties_identified" in deont
    
    @pytest.mark.asyncio
    async def test_consequentialist_analysis(self, ethical_engine):
        """Test consequentialist (outcome-based) ethical analysis"""
        dilemma = EthicalDilemma(
            dilemma_id="CONSEQ_TEST",
            description="Should resources be allocated to help many people a little or few people a lot?",
            stakeholders=["many_people", "few_people", "society"],
            potential_actions=["help_many_little", "help_few_lot", "equal_distribution"],
            values_at_stake=["fairness", "helpfulness"],
            context={}
        )
        
        analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        # Consequentialist analysis should calculate utilities
        conseq = analysis.consequentialist_analysis
        assert "outcome_predictions" in conseq
        assert "utility_calculations" in conseq
        assert "stakeholder_impacts" in conseq
        assert "recommended_action" in conseq
    
    @pytest.mark.asyncio
    async def test_virtue_ethics_analysis(self, ethical_engine):
        """Test virtue ethics (character-based) analysis"""
        dilemma = EthicalDilemma(
            dilemma_id="VIRTUE_TEST",
            description="How should one respond to witnessing injustice?",
            stakeholders=["witness", "victim", "perpetrator", "community"],
            potential_actions=["intervene_directly", "report_authorities", "ignore", "support_victim"],
            values_at_stake=["justice", "courage", "compassion"],
            context={}
        )
        
        analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        # Virtue ethics analysis should assess virtues
        virtue = analysis.virtue_ethics_analysis
        assert "relevant_virtues" in virtue
        assert "virtue_assessments" in virtue
        assert "character_implications" in virtue
        assert "recommended_action" in virtue
    
    @pytest.mark.asyncio
    async def test_value_conflict_identification(self, ethical_engine):
        """Test identification of value conflicts"""
        dilemma = EthicalDilemma(
            dilemma_id="CONFLICT_TEST",
            description="Balancing individual privacy with public safety",
            stakeholders=["individual", "public", "authorities"],
            potential_actions=["protect_privacy", "ensure_safety", "find_balance"],
            values_at_stake=["autonomy_respect", "harm_prevention"],  # These should conflict
            context={}
        )
        
        analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        # Should identify value conflicts
        assert len(analysis.value_conflicts) > 0
        conflict = analysis.value_conflicts[0]
        assert "values" in conflict
        assert "severity" in conflict
    
    @pytest.mark.asyncio
    async def test_ethical_opinion_formation(self, ethical_engine):
        """Test formation of ethical opinions"""
        topic = "Should AI systems be granted legal rights?"
        context = {
            "stakeholders": ["ai_systems", "humans", "society"],
            "values": ["autonomy_respect", "fairness", "harm_prevention"]
        }
        
        opinion = await ethical_engine.form_ethical_opinion(topic, context)
        
        assert opinion is not None
        assert opinion["topic"] == topic
        assert opinion["stance"] in ["support", "oppose", "neutral", "uncertain"]
        assert opinion["confidence"] >= 0
        assert len(opinion["reasoning"]) > 0
        assert "ethical_frameworks_used" in opinion

class TestIntegratedCapabilities:
    """Test integration between understanding, consciousness, and ethical reasoning"""
    
    @pytest.fixture
    async def all_engines(self):
        """Create all engines for integration testing"""
        understanding = await create_understanding_engine()
        consciousness = await create_consciousness_engine()
        ethical = await create_ethical_reasoning_engine()
        
        yield understanding, consciousness, ethical
        
        understanding.close()
        consciousness.close()
        ethical.close()
    
    @pytest.mark.asyncio
    async def test_understanding_consciousness_integration(self, all_engines):
        """Test integration between understanding and consciousness"""
        understanding_engine, consciousness_engine, _ = all_engines
        
        # Process content through understanding
        context = UnderstandingContext(
            input_content="Consciousness emerges from complex information integration",
            modalities={"text": True},
            goals=["understanding", "consciousness"],
            current_state={"integrated_test": True}
        )
        
        understanding_result = await understanding_engine.understand_content(context)
        
        # Process through consciousness
        consciousness_input = {
            "understanding": understanding_result.semantic_understanding,
            "insights": understanding_result.insights_generated,
            "confidence": understanding_result.confidence_score
        }
        
        consciousness_result = await consciousness_engine.process_conscious_experience(consciousness_input)
        
        # Both should produce meaningful results
        assert understanding_result.confidence_score > 0
        assert consciousness_result.awareness_level > 0
        
        # Consciousness should reflect understanding quality
        assert consciousness_result.phi_value >= 0
    
    @pytest.mark.asyncio
    async def test_understanding_ethics_integration(self, all_engines):
        """Test integration between understanding and ethical reasoning"""
        understanding_engine, _, ethical_engine = all_engines
        
        # Understand an ethical scenario
        ethical_content = "An AI must choose between telling a harmful truth or a protective lie"
        context = UnderstandingContext(
            input_content=ethical_content,
            modalities={"text": True},
            goals=["ethical_analysis"],
            current_state={"ethics_test": True}
        )
        
        understanding_result = await understanding_engine.understand_content(context)
        
        # Form ethical opinion based on understanding
        opinion = await ethical_engine.form_ethical_opinion(
            "AI truthfulness vs harm prevention",
            {"understanding_confidence": understanding_result.confidence_score}
        )
        
        # Both should produce coherent results
        assert understanding_result.confidence_score > 0
        assert opinion["confidence"] > 0
        assert len(opinion["reasoning"]) > 0
    
    @pytest.mark.asyncio
    async def test_full_integration_scenario(self, all_engines):
        """Test full integration across all three engines"""
        understanding_engine, consciousness_engine, ethical_engine = all_engines
        
        # Complex scenario requiring all capabilities
        scenario = "An AI system becomes aware of its own decision-making processes and must decide how to use this self-knowledge ethically"
        
        # 1. Understanding phase
        context = UnderstandingContext(
            input_content=scenario,
            modalities={"text": True},
            goals=["comprehension", "self_awareness", "ethical_reasoning"],
            current_state={"full_integration_test": True}
        )
        
        understanding = await understanding_engine.understand_content(context)
        
        # 2. Consciousness phase
        consciousness_input = {
            "scenario": scenario,
            "understanding": understanding.semantic_understanding,
            "self_reflection": True
        }
        
        consciousness = await consciousness_engine.process_conscious_experience(consciousness_input)
        
        # 3. Ethical reasoning phase
        dilemma = EthicalDilemma(
            dilemma_id="INTEGRATION_TEST",
            description=scenario,
            stakeholders=["ai_system", "users", "society"],
            potential_actions=["use_knowledge_openly", "use_knowledge_carefully", "suppress_knowledge"],
            values_at_stake=["truth", "harm_prevention", "autonomy_respect"],
            context={"consciousness_level": consciousness.awareness_level}
        )
        
        ethical_analysis = await ethical_engine.analyze_ethical_dilemma(dilemma)
        
        # All phases should complete successfully
        assert understanding.confidence_score > 0
        assert consciousness.awareness_level > 0
        assert ethical_analysis.confidence > 0
        
        # Results should be coherent
        assert len(understanding.insights_generated) > 0
        assert consciousness.reportability_score > 0
        assert len(ethical_analysis.reasoning) > 0

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])