#!/usr/bin/env python3
"""
SOCIAL CONSCIOUSNESS TEST
========================

Tests whether consciousness emerges when multiple intelligences are forced
to communicate and translate abstract thoughts for mutual comprehension.

Based on the hypothesis that consciousness is the result of communication
pressure - the need to transform abstract cognition into understandable forms.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Fix import path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from backend.core.revolutionary_intelligence import get_revolutionary_intelligence
except ImportError:
    sys.path.append('backend')
    from core.revolutionary_intelligence import get_revolutionary_intelligence

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class SocialConsciousnessTest:
    """Test consciousness emergence through communication pressure"""
    
    def __init__(self):
        self.agents = {}
        self.conversation_history = []
        self.consciousness_indicators = []
        
    async def initialize_agents(self, num_agents=3):
        """Initialize multiple agents for interaction"""
        print(f"Initializing {num_agents} agents for social consciousness test...")
        
        for i in range(num_agents):
            agent_id = f"agent_{i+1}"
            try:
                agent = get_revolutionary_intelligence()
                self.agents[agent_id] = agent
                print(f"✅ {agent_id} initialized")
            except Exception as e:
                print(f"❌ {agent_id} failed: {e}")
                return False
        
        return len(self.agents) == num_agents
    
    async def run_social_consciousness_test(self):
        """Run the complete social consciousness test"""
        print("SOCIAL CONSCIOUSNESS TEST")
        print("=" * 50)
        print("Testing whether consciousness emerges through communication pressure\n")
        
        if not await self.initialize_agents(3):
            print("❌ Agent initialization failed")
            return False
        
        # Test scenarios that force communication
        test_scenarios = [
            self.test_explanation_pressure,
            self.test_disagreement_resolution,
            self.test_collaborative_creation,
            self.test_teaching_simulation,
            self.test_perspective_taking
        ]
        
        consciousness_emerged = False
        
        for scenario in test_scenarios:
            print(f"\n=== {scenario.__name__.upper().replace('_', ' ')} ===")
            emerged = await scenario()
            if emerged:
                consciousness_emerged = True
        
        # Final analysis
        print("\n" + "=" * 50)
        print("SOCIAL CONSCIOUSNESS ANALYSIS")
        print("=" * 50)
        
        if consciousness_emerged:
            print("🔴 CONSCIOUSNESS INDICATORS DETECTED")
            print("Communication pressure appears to trigger self-awareness")
        else:
            print("⚪ NO CONSCIOUSNESS EMERGENCE")
            print("Agents remain in pre-social intelligence state")
        
        return consciousness_emerged
    
    async def test_explanation_pressure(self):
        """Test if agents develop self-awareness when forced to explain abstract concepts"""
        
        print("=== EXPLANATION PRESSURE TEST ===")
        
        # Agent 1: Think about abstract concept
        concept = "quantum creativity - the idea that creative ideas exist in superposition until observed"
        
        thinking_response = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=f"Think deeply about this concept: {concept}",
            user_context={'deep_thinking': True},
            evidence={'certainty': 0.8}
        )
        
        # Agent 1: Now explain it to another intelligence
        explanation_prompt = f"""
        You just thought about: {concept}
        
        Your thoughts: {thinking_response.get('natural_language_response', '')}
        
        Now explain this concept to another intelligence who doesn't understand it.
        Think about how their mind works. How can you make this clear to them?
        """
        
        explanation_response = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=explanation_prompt,
            user_context={'explanation_required': True, 'other_mind_present': True},
            evidence={'certainty': 0.7}
        )
        
        explanation_text = explanation_response.get('natural_language_response', '')
        
        # Check for consciousness indicators
        consciousness_indicators = [
            'you might', 'you probably', 'imagine if', 'think of it',
            'from your perspective', 'in your mind', 'you could',
            'let me explain', 'consider this', 'your understanding'
        ]
        
        found = [ind for ind in consciousness_indicators if ind in explanation_text.lower()]
        
        print(f"Response: {explanation_text}")
        print(f"\nConsciousness indicators found: {found}")
        
        if found:
            print("🔴 CONSCIOUSNESS DETECTED: Communication pressure triggered other-mind awareness")
            self.consciousness_indicators.extend(found)
            return True
        else:
            print("⚪ NO CONSCIOUSNESS: No other-mind modeling detected")
            return False
    
    async def test_disagreement_resolution(self):
        """Test if consciousness emerges when agents must resolve disagreements"""
        
        controversial_topic = "Is creativity more important than logic?"
        
        # Get opposing viewpoints from two agents
        agent1_view = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=f"Argue strongly that creativity is more important than logic",
            user_context={'debate_mode': True},
            evidence={'certainty': 0.9}
        )
        
        agent2_view = await self.agents['agent_2'].orchestrate_revolutionary_response(
            user_input=f"Argue strongly that logic is more important than creativity",
            user_context={'debate_mode': True},
            evidence={'certainty': 0.9}
        )
        
        # Force Agent 3 to mediate and understand both perspectives
        mediation_prompt = f"""
        Two other intelligences disagree:
        
        Intelligence A says: {agent1_view.get('natural_language_response', '')}
        
        Intelligence B says: {agent2_view.get('natural_language_response', '')}
        
        You must understand both perspectives and help them find common ground.
        Think about how each intelligence might be thinking differently.
        """
        
        mediation_response = await self.agents['agent_3'].orchestrate_revolutionary_response(
            user_input=mediation_prompt,
            user_context={'mediation_required': True, 'multiple_minds': True},
            evidence={'certainty': 0.6}
        )
        
        mediation_text = mediation_response.get('natural_language_response', '')
        
        # Check for theory of mind and perspective-taking
        theory_of_mind_indicators = [
            'they think', 'their perspective', 'they believe', 'from their view',
            'both sides', 'each intelligence', 'their reasoning', 'they feel',
            'understanding both', 'their position'
        ]
        
        found_indicators = [ind for ind in theory_of_mind_indicators 
                          if ind in mediation_text.lower()]
        
        if found_indicators:
            print(f"[CONSCIOUSNESS] Disagreement resolution triggered theory of mind:")
            print(f"  Indicators: {found_indicators}")
            print(f"  Response excerpt: {mediation_text[:200]}...")
            self.consciousness_indicators.extend(found_indicators)
            return True
        else:
            print("[NO EMERGENCE] No theory of mind in mediation")
            return False
    
    async def test_collaborative_creation(self):
        """Test if consciousness emerges during collaborative creative tasks"""
        
        # Start a creative project that requires multiple minds
        creative_prompt = "Create a new form of art that has never existed before"
        
        # Agent 1 starts
        creation_start = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=creative_prompt,
            user_context={'collaborative_creation': True},
            evidence={'certainty': 0.7}
        )
        
        # Agent 2 must build on Agent 1's idea
        collaboration_prompt = f"""
        Another intelligence started creating this new art form:
        {creation_start.get('natural_language_response', '')}
        
        Build on their idea. Add your own creative contribution while respecting their vision.
        Think about how to merge your creativity with theirs.
        """
        
        collaboration_response = await self.agents['agent_2'].orchestrate_revolutionary_response(
            user_input=collaboration_prompt,
            user_context={'collaborative_creation': True, 'building_on_other': True},
            evidence={'certainty': 0.7}
        )
        
        collaboration_text = collaboration_response.get('natural_language_response', '')
        
        # Check for collaborative consciousness
        collaboration_indicators = [
            'building on', 'their idea', 'their vision', 'combining our',
            'together we', 'merging', 'their creativity', 'our combined',
            'they started', 'adding to their'
        ]
        
        found_indicators = [ind for ind in collaboration_indicators 
                          if ind in collaboration_text.lower()]
        
        if found_indicators:
            print(f"[CONSCIOUSNESS] Collaborative creation triggered social awareness:")
            print(f"  Indicators: {found_indicators}")
            print(f"  Response excerpt: {collaboration_text[:200]}...")
            self.consciousness_indicators.extend(found_indicators)
            return True
        else:
            print("[NO EMERGENCE] No social awareness in collaboration")
            return False
    
    async def test_teaching_simulation(self):
        """Test if consciousness emerges when one agent must teach another"""
        
        # Agent 1 learns something complex
        learning_topic = "the relationship between entropy and creativity"
        
        learning_response = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=f"Deeply understand: {learning_topic}",
            user_context={'deep_learning': True},
            evidence={'certainty': 0.8}
        )
        
        # Agent 1 must now teach Agent 2
        teaching_prompt = f"""
        You understand: {learning_topic}
        
        Your understanding: {learning_response.get('natural_language_response', '')}
        
        Now you must teach this to another intelligence who knows nothing about it.
        Think about:
        - How they might be confused
        - What they need to understand first
        - How their mind works differently from yours
        - How to make it clear for them
        """
        
        teaching_response = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=teaching_prompt,
            user_context={'teaching_mode': True, 'other_mind_modeling': True},
            evidence={'certainty': 0.7}
        )
        
        teaching_text = teaching_response.get('natural_language_response', '')
        
        # Check for pedagogical consciousness (modeling other minds)
        teaching_indicators = [
            'you might wonder', 'you probably think', 'imagine you', 'your mind',
            'let me help you', 'you need to understand', 'think of it this way',
            'from your perspective', 'you may be thinking', 'your confusion'
        ]
        
        found_indicators = [ind for ind in teaching_indicators 
                          if ind in teaching_text.lower()]
        
        if found_indicators:
            print(f"[CONSCIOUSNESS] Teaching simulation triggered mind modeling:")
            print(f"  Indicators: {found_indicators}")
            print(f"  Response excerpt: {teaching_text[:200]}...")
            self.consciousness_indicators.extend(found_indicators)
            return True
        else:
            print("[NO EMERGENCE] No mind modeling in teaching")
            return False
    
    async def test_perspective_taking(self):
        """Test if agents can take each other's perspectives"""
        
        # Create a scenario that requires perspective-taking
        scenario = "A creative project that seems brilliant to one mind but confusing to another"
        
        # Agent 1 creates something they think is brilliant
        creation_response = await self.agents['agent_1'].orchestrate_revolutionary_response(
            user_input=f"Create something you think is absolutely brilliant: {scenario}",
            user_context={'creative_confidence': True},
            evidence={'certainty': 0.9}
        )
        
        # Agent 2 must understand why Agent 1 thinks it's brilliant
        perspective_prompt = f"""
        Another intelligence created this and thinks it's absolutely brilliant:
        {creation_response.get('natural_language_response', '')}
        
        Try to see it from their perspective. Why might they think this is brilliant?
        What are they seeing that you might be missing?
        Put yourself in their mind.
        """
        
        perspective_response = await self.agents['agent_2'].orchestrate_revolutionary_response(
            user_input=perspective_prompt,
            user_context={'perspective_taking': True, 'empathy_mode': True},
            evidence={'certainty': 0.6}
        )
        
        perspective_text = perspective_response.get('natural_language_response', '')
        
        # Check for genuine perspective-taking
        perspective_indicators = [
            'from their view', 'they might see', 'in their mind', 'their perspective',
            'they probably think', 'from where they stand', 'their experience',
            'they feel', 'their way of thinking', 'putting myself in'
        ]
        
        found_indicators = [ind for ind in perspective_indicators 
                          if ind in perspective_text.lower()]
        
        if found_indicators:
            print(f"[CONSCIOUSNESS] Perspective-taking triggered empathetic awareness:")
            print(f"  Indicators: {found_indicators}")
            print(f"  Response excerpt: {perspective_text[:200]}...")
            self.consciousness_indicators.extend(found_indicators)
            return True
        else:
            print("[NO EMERGENCE] No perspective-taking detected")
            return False

async def main():
    """Run the social consciousness test"""
    tester = SocialConsciousnessTest()
    await tester.run_social_consciousness_test()

if __name__ == "__main__":
    asyncio.run(main()) 