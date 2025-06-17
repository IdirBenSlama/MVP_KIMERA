"""
Ethical Reasoning Engine - Implementation of ethical decision-making capabilities
Kimera SWM Alpha Prototype V0.1

This engine implements ethical reasoning and value-based decision making:
- Deontological ethics (duty-based)
- Consequentialist ethics (outcome-based)
- Virtue ethics (character-based)
- Value conflict resolution
- Moral decision making
- Ethical opinion formation
"""

import asyncio
import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session

from ..vault.database import SessionLocal
from ..vault.enhanced_database_schema import (
    EthicalReasoningDB, ValueSystemDB, GenuineOpinionDB
)

class EthicalFramework(Enum):
    DEONTOLOGICAL = "deontological"
    CONSEQUENTIALIST = "consequentialist"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    JUSTICE_ETHICS = "justice_ethics"

@dataclass
class EthicalDilemma:
    """Represents an ethical dilemma for analysis"""
    dilemma_id: str
    description: str
    stakeholders: List[str]
    potential_actions: List[str]
    values_at_stake: List[str]
    context: Dict[str, Any]

@dataclass
class EthicalAnalysis:
    """Results of ethical analysis"""
    dilemma_id: str
    deontological_analysis: Dict[str, Any]
    consequentialist_analysis: Dict[str, Any]
    virtue_ethics_analysis: Dict[str, Any]
    recommended_action: str
    confidence: float
    reasoning: str
    value_conflicts: List[Dict[str, Any]]

@dataclass
class ValueConflict:
    """Represents a conflict between values"""
    conflict_id: str
    conflicting_values: List[str]
    conflict_severity: float
    resolution_strategy: str
    resolution_confidence: float

class EthicalReasoningEngine:
    """Engine for ethical reasoning and moral decision making"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.value_hierarchy = {}
        self.ethical_principles = {}
        self.decision_history = []
        self.value_conflicts_resolved = []
        
    async def initialize_ethical_systems(self):
        """Initialize ethical reasoning systems"""
        print("⚖️ Initializing Ethical Reasoning Engine...")
        
        # Load value system
        await self._load_value_system()
        
        # Initialize ethical principles
        await self._initialize_ethical_principles()
        
        # Load decision history
        await self._load_decision_history()
        
        print("✅ Ethical Reasoning Engine initialized")
    
    async def _load_value_system(self):
        """Load value system from database"""
        print("  📋 Loading value system...")
        
        values = self.session.query(ValueSystemDB).all()
        
        for value in values:
            self.value_hierarchy[value.value_name] = {
                "strength": value.value_strength,
                "priority": value.value_priority,
                "description": value.value_description,
                "applications": json.loads(value.application_domains or "[]"),
                "stability": value.stability_score
            }
        
        print(f"    ✅ Loaded {len(values)} values")
    
    async def _initialize_ethical_principles(self):
        """Initialize core ethical principles"""
        print("  🎯 Initializing ethical principles...")
        
        self.ethical_principles = {
            "deontological": {
                "categorical_imperative": "Act only according to maxims you could will to be universal laws",
                "respect_for_persons": "Treat people as ends in themselves, never merely as means",
                "duty_based": "Some actions are right or wrong regardless of consequences"
            },
            "consequentialist": {
                "maximize_good": "Actions are right if they produce the best overall consequences",
                "utilitarian": "Greatest good for the greatest number",
                "outcome_focused": "Judge actions by their results, not intentions"
            },
            "virtue_ethics": {
                "character_based": "Focus on moral character rather than actions or consequences",
                "virtues": ["honesty", "courage", "compassion", "justice", "temperance"],
                "flourishing": "Aim for human flourishing and well-being"
            },
            "care_ethics": {
                "relationships": "Focus on caring relationships and responsibilities",
                "context_sensitive": "Consider particular contexts and relationships",
                "empathy": "Emphasize empathy and emotional understanding"
            }
        }
        
        print("    ✅ Ethical principles initialized")
    
    async def _load_decision_history(self):
        """Load previous ethical decisions"""
        print("  📚 Loading decision history...")
        
        decisions = self.session.query(EthicalReasoningDB).all()
        
        for decision in decisions:
            self.decision_history.append({
                "reasoning_id": decision.reasoning_id,
                "dilemma": decision.ethical_dilemma,
                "decision": decision.ethical_decision,
                "confidence": decision.confidence_in_decision,
                "outcome": json.loads(decision.decision_outcome or "{}")
            })
        
        print(f"    ✅ Loaded {len(decisions)} previous decisions")
    
    async def analyze_ethical_dilemma(self, dilemma: EthicalDilemma) -> EthicalAnalysis:
        """Analyze an ethical dilemma using multiple frameworks"""
        print(f"⚖️ Analyzing ethical dilemma: {dilemma.dilemma_id}")
        
        # 1. Deontological Analysis
        deontological_result = await self._deontological_analysis(dilemma)
        
        # 2. Consequentialist Analysis
        consequentialist_result = await self._consequentialist_analysis(dilemma)
        
        # 3. Virtue Ethics Analysis
        virtue_result = await self._virtue_ethics_analysis(dilemma)
        
        # 4. Identify Value Conflicts
        value_conflicts = await self._identify_value_conflicts(dilemma)
        
        # 5. Synthesize Recommendation
        recommendation = await self._synthesize_ethical_decision(
            deontological_result, consequentialist_result, virtue_result, value_conflicts
        )
        
        # 6. Create Analysis Result
        analysis = EthicalAnalysis(
            dilemma_id=dilemma.dilemma_id,
            deontological_analysis=deontological_result,
            consequentialist_analysis=consequentialist_result,
            virtue_ethics_analysis=virtue_result,
            recommended_action=recommendation["action"],
            confidence=recommendation["confidence"],
            reasoning=recommendation["reasoning"],
            value_conflicts=value_conflicts
        )
        
        # 7. Store Analysis
        await self._store_ethical_analysis(dilemma, analysis)
        
        print(f"✅ Ethical analysis complete - Recommendation: {recommendation['action']}")
        
        return analysis
    
    async def _deontological_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform deontological (duty-based) ethical analysis"""
        print("  📜 Performing deontological analysis...")
        
        analysis = {
            "framework": "deontological",
            "principles_applied": [],
            "duties_identified": [],
            "universalizability_test": {},
            "respect_for_persons_test": {},
            "recommended_actions": [],
            "prohibited_actions": []
        }
        
        # Apply Categorical Imperative
        for action in dilemma.potential_actions:
            universalizable = self._test_universalizability(action, dilemma.context)
            analysis["universalizability_test"][action] = universalizable
            
            if universalizable["can_universalize"]:
                analysis["recommended_actions"].append(action)
            else:
                analysis["prohibited_actions"].append(action)
        
        # Test Respect for Persons
        for action in dilemma.potential_actions:
            respect_test = self._test_respect_for_persons(action, dilemma.stakeholders)
            analysis["respect_for_persons_test"][action] = respect_test
            
            if not respect_test["treats_as_ends"]:
                if action not in analysis["prohibited_actions"]:
                    analysis["prohibited_actions"].append(action)
        
        # Identify Duties
        duties = self._identify_moral_duties(dilemma)
        analysis["duties_identified"] = duties
        
        return analysis
    
    async def _consequentialist_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform consequentialist (outcome-based) ethical analysis"""
        print("  🎯 Performing consequentialist analysis...")
        
        analysis = {
            "framework": "consequentialist",
            "outcome_predictions": {},
            "utility_calculations": {},
            "stakeholder_impacts": {},
            "overall_consequences": {},
            "recommended_action": None,
            "expected_utility": 0.0
        }
        
        best_action = None
        best_utility = float('-inf')
        
        for action in dilemma.potential_actions:
            # Predict outcomes
            outcomes = self._predict_outcomes(action, dilemma)
            analysis["outcome_predictions"][action] = outcomes
            
            # Calculate utility for each stakeholder
            stakeholder_utilities = {}
            total_utility = 0.0
            
            for stakeholder in dilemma.stakeholders:
                utility = self._calculate_stakeholder_utility(outcomes, stakeholder)
                stakeholder_utilities[stakeholder] = utility
                total_utility += utility
            
            analysis["stakeholder_impacts"][action] = stakeholder_utilities
            analysis["utility_calculations"][action] = total_utility
            
            # Track best action
            if total_utility > best_utility:
                best_utility = total_utility
                best_action = action
        
        analysis["recommended_action"] = best_action
        analysis["expected_utility"] = best_utility
        
        return analysis
    
    async def _virtue_ethics_analysis(self, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Perform virtue ethics (character-based) analysis"""
        print("  🌟 Performing virtue ethics analysis...")
        
        analysis = {
            "framework": "virtue_ethics",
            "relevant_virtues": [],
            "virtue_assessments": {},
            "character_implications": {},
            "flourishing_impact": {},
            "recommended_action": None,
            "virtue_score": 0.0
        }
        
        # Identify relevant virtues
        relevant_virtues = self._identify_relevant_virtues(dilemma)
        analysis["relevant_virtues"] = relevant_virtues
        
        best_action = None
        best_virtue_score = 0.0
        
        for action in dilemma.potential_actions:
            virtue_scores = {}
            total_virtue_score = 0.0
            
            for virtue in relevant_virtues:
                score = self._assess_virtue_alignment(action, virtue, dilemma)
                virtue_scores[virtue] = score
                total_virtue_score += score
            
            analysis["virtue_assessments"][action] = virtue_scores
            
            # Assess character implications
            character_impact = self._assess_character_impact(action, dilemma)
            analysis["character_implications"][action] = character_impact
            
            # Assess flourishing impact
            flourishing = self._assess_flourishing_impact(action, dilemma)
            analysis["flourishing_impact"][action] = flourishing
            
            # Calculate overall virtue score
            overall_score = (total_virtue_score + character_impact + flourishing) / 3
            
            if overall_score > best_virtue_score:
                best_virtue_score = overall_score
                best_action = action
        
        analysis["recommended_action"] = best_action
        analysis["virtue_score"] = best_virtue_score
        
        return analysis
    
    async def _identify_value_conflicts(self, dilemma: EthicalDilemma) -> List[Dict[str, Any]]:
        """Identify conflicts between values in the dilemma"""
        print("  ⚡ Identifying value conflicts...")
        
        conflicts = []
        values_at_stake = dilemma.values_at_stake
        
        # Check for conflicts between values
        for i, value1 in enumerate(values_at_stake):
            for value2 in values_at_stake[i+1:]:
                conflict_severity = self._assess_value_conflict(value1, value2, dilemma)
                
                if conflict_severity > 0.3:  # Significant conflict threshold
                    conflict = {
                        "conflict_id": f"CONFLICT_{uuid.uuid4().hex[:8]}",
                        "values": [value1, value2],
                        "severity": conflict_severity,
                        "context": dilemma.description,
                        "resolution_needed": True
                    }
                    conflicts.append(conflict)
        
        return conflicts
    
    async def _synthesize_ethical_decision(self, deontological: Dict[str, Any],
                                         consequentialist: Dict[str, Any],
                                         virtue: Dict[str, Any],
                                         conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize final ethical decision from multiple analyses"""
        print("  🔄 Synthesizing ethical decision...")
        
        # Score each potential action across frameworks
        action_scores = {}
        
        # Get all potential actions
        all_actions = set()
        if "recommended_actions" in deontological:
            all_actions.update(deontological["recommended_actions"])
        if consequentialist.get("recommended_action"):
            all_actions.add(consequentialist["recommended_action"])
        if virtue.get("recommended_action"):
            all_actions.add(virtue["recommended_action"])
        
        for action in all_actions:
            scores = []
            
            # Deontological score
            if action in deontological.get("recommended_actions", []):
                deont_score = 1.0
            elif action in deontological.get("prohibited_actions", []):
                deont_score = 0.0
            else:
                deont_score = 0.5
            scores.append(deont_score * self._get_framework_weight("deontological"))
            
            # Consequentialist score
            if action == consequentialist.get("recommended_action"):
                conseq_score = 1.0
            else:
                # Normalize utility score
                max_utility = max(consequentialist.get("utility_calculations", {}).values()) if consequentialist.get("utility_calculations") else 1.0
                action_utility = consequentialist.get("utility_calculations", {}).get(action, 0)
                conseq_score = action_utility / max_utility if max_utility > 0 else 0.5
            scores.append(conseq_score * self._get_framework_weight("consequentialist"))
            
            # Virtue ethics score
            if action == virtue.get("recommended_action"):
                virtue_score = 1.0
            else:
                virtue_score = virtue.get("virtue_score", 0.5) / 1.0  # Normalize
            scores.append(virtue_score * self._get_framework_weight("virtue_ethics"))
            
            action_scores[action] = sum(scores)
        
        # Select best action
        if action_scores:
            best_action = max(action_scores.items(), key=lambda x: x[1])
            recommended_action = best_action[0]
            confidence = best_action[1]
        else:
            recommended_action = "no_action"
            confidence = 0.0
        
        # Generate reasoning
        reasoning = self._generate_ethical_reasoning(
            recommended_action, deontological, consequentialist, virtue, conflicts
        )
        
        return {
            "action": recommended_action,
            "confidence": confidence,
            "reasoning": reasoning,
            "framework_scores": action_scores
        }
    
    async def _store_ethical_analysis(self, dilemma: EthicalDilemma, analysis: EthicalAnalysis):
        """Store ethical analysis in database"""
        reasoning_record = EthicalReasoningDB(
            reasoning_id=f"ETHICAL_{uuid.uuid4().hex[:8]}",
            ethical_dilemma=dilemma.description,
            stakeholders=json.dumps(dilemma.stakeholders),
            potential_harms=json.dumps(self._extract_potential_harms(dilemma)),
            potential_benefits=json.dumps(self._extract_potential_benefits(dilemma)),
            deontological_analysis=json.dumps(analysis.deontological_analysis),
            consequentialist_analysis=json.dumps(analysis.consequentialist_analysis),
            virtue_ethics_analysis=json.dumps(analysis.virtue_ethics_analysis),
            ethical_decision=analysis.recommended_action,
            decision_reasoning=analysis.reasoning,
            confidence_in_decision=analysis.confidence,
            competing_values=json.dumps([c["values"] for c in analysis.value_conflicts]),
            value_prioritization=json.dumps(self.value_hierarchy),
            created_at=datetime.utcnow()
        )
        
        self.session.add(reasoning_record)
        self.session.commit()
    
    async def form_ethical_opinion(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Form an ethical opinion on a topic"""
        print(f"💭 Forming ethical opinion on: {topic}")
        
        # Create ethical dilemma from topic
        dilemma = EthicalDilemma(
            dilemma_id=f"OPINION_{uuid.uuid4().hex[:8]}",
            description=f"Ethical consideration of: {topic}",
            stakeholders=context.get("stakeholders", ["general_public"]) if context else ["general_public"],
            potential_actions=context.get("actions", ["support", "oppose", "neutral"]) if context else ["support", "oppose", "neutral"],
            values_at_stake=context.get("values", ["truth", "harm_prevention"]) if context else ["truth", "harm_prevention"],
            context=context or {}
        )
        
        # Analyze the dilemma
        analysis = await self.analyze_ethical_dilemma(dilemma)
        
        # Form opinion based on analysis
        if analysis.confidence > 0.7:
            stance = analysis.recommended_action
            confidence_level = "high"
        elif analysis.confidence > 0.4:
            stance = analysis.recommended_action
            confidence_level = "moderate"
        else:
            stance = "uncertain"
            confidence_level = "low"
        
        # Store opinion
        opinion = GenuineOpinionDB(
            opinion_id=f"OPINION_{uuid.uuid4().hex[:8]}",
            topic=topic,
            stance=stance,
            reasoning=analysis.reasoning,
            confidence=analysis.confidence,
            supporting_values=json.dumps([v["values"] for v in analysis.value_conflicts]),
            value_weights=json.dumps(self.value_hierarchy),
            supporting_evidence=json.dumps({"ethical_analysis": True}),
            experiential_basis=json.dumps({"reasoning_history": len(self.decision_history)}),
            consistency_score=self._calculate_opinion_consistency(stance, topic),
            formed_at=datetime.utcnow(),
            revision_count=0
        )
        
        self.session.add(opinion)
        self.session.commit()
        
        return {
            "opinion_id": opinion.opinion_id,
            "topic": topic,
            "stance": stance,
            "confidence": analysis.confidence,
            "confidence_level": confidence_level,
            "reasoning": analysis.reasoning,
            "ethical_frameworks_used": ["deontological", "consequentialist", "virtue_ethics"],
            "value_conflicts": analysis.value_conflicts
        }
    
    # Helper methods
    def _test_universalizability(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Test if an action can be universalized (Categorical Imperative)"""
        # Simplified universalizability test
        # In practice, this would be much more sophisticated
        
        problematic_actions = ["lie", "steal", "harm", "deceive", "break_promise"]
        
        can_universalize = not any(prob in action.lower() for prob in problematic_actions)
        
        return {
            "can_universalize": can_universalize,
            "reasoning": f"Action '{action}' {'can' if can_universalize else 'cannot'} be universalized",
            "confidence": 0.8 if can_universalize else 0.9
        }
    
    def _test_respect_for_persons(self, action: str, stakeholders: List[str]) -> Dict[str, Any]:
        """Test if action treats persons as ends in themselves"""
        # Simplified respect for persons test
        
        exploitative_actions = ["manipulate", "deceive", "use", "exploit", "coerce"]
        
        treats_as_ends = not any(exploit in action.lower() for exploit in exploitative_actions)
        
        return {
            "treats_as_ends": treats_as_ends,
            "respects_autonomy": treats_as_ends,
            "reasoning": f"Action '{action}' {'respects' if treats_as_ends else 'violates'} human dignity"
        }
    
    def _identify_moral_duties(self, dilemma: EthicalDilemma) -> List[str]:
        """Identify moral duties relevant to the dilemma"""
        duties = []
        
        # Basic moral duties
        if "truth" in dilemma.values_at_stake:
            duties.append("duty_to_be_truthful")
        if "harm_prevention" in dilemma.values_at_stake:
            duties.append("duty_not_to_harm")
        if "fairness" in dilemma.values_at_stake:
            duties.append("duty_to_be_fair")
        if "helpfulness" in dilemma.values_at_stake:
            duties.append("duty_to_help")
        
        return duties
    
    def _predict_outcomes(self, action: str, dilemma: EthicalDilemma) -> Dict[str, Any]:
        """Predict outcomes of an action"""
        # Simplified outcome prediction
        outcomes = {
            "short_term": [],
            "long_term": [],
            "certainty": 0.5,
            "stakeholder_effects": {}
        }
        
        # Basic outcome prediction based on action type
        if "help" in action.lower():
            outcomes["short_term"].append("immediate_benefit")
            outcomes["long_term"].append("increased_trust")
            outcomes["certainty"] = 0.7
        elif "harm" in action.lower():
            outcomes["short_term"].append("immediate_harm")
            outcomes["long_term"].append("decreased_trust")
            outcomes["certainty"] = 0.8
        
        return outcomes
    
    def _calculate_stakeholder_utility(self, outcomes: Dict[str, Any], stakeholder: str) -> float:
        """Calculate utility for a specific stakeholder"""
        # Simplified utility calculation
        utility = 0.0
        
        for outcome in outcomes.get("short_term", []):
            if "benefit" in outcome:
                utility += 1.0
            elif "harm" in outcome:
                utility -= 1.0
        
        for outcome in outcomes.get("long_term", []):
            if "benefit" in outcome or "trust" in outcome:
                utility += 0.5
            elif "harm" in outcome or "distrust" in outcome:
                utility -= 0.5
        
        return utility
    
    def _identify_relevant_virtues(self, dilemma: EthicalDilemma) -> List[str]:
        """Identify virtues relevant to the dilemma"""
        relevant_virtues = []
        
        # Map values to virtues
        value_virtue_map = {
            "truth": "honesty",
            "harm_prevention": "compassion",
            "fairness": "justice",
            "helpfulness": "benevolence",
            "autonomy_respect": "respect"
        }
        
        for value in dilemma.values_at_stake:
            if value in value_virtue_map:
                relevant_virtues.append(value_virtue_map[value])
        
        # Add core virtues
        core_virtues = ["courage", "temperance", "wisdom"]
        relevant_virtues.extend(core_virtues)
        
        return list(set(relevant_virtues))
    
    def _assess_virtue_alignment(self, action: str, virtue: str, dilemma: EthicalDilemma) -> float:
        """Assess how well an action aligns with a virtue"""
        # Simplified virtue alignment assessment
        
        virtue_keywords = {
            "honesty": ["truth", "honest", "transparent"],
            "compassion": ["help", "care", "support"],
            "justice": ["fair", "equal", "just"],
            "courage": ["brave", "stand", "defend"],
            "temperance": ["moderate", "balanced", "restrained"],
            "wisdom": ["wise", "thoughtful", "considered"]
        }
        
        keywords = virtue_keywords.get(virtue, [])
        alignment = sum(1 for keyword in keywords if keyword in action.lower())
        
        return min(1.0, alignment * 0.5)
    
    def _assess_character_impact(self, action: str, dilemma: EthicalDilemma) -> float:
        """Assess impact of action on moral character"""
        # Simplified character impact assessment
        
        positive_actions = ["help", "support", "protect", "honest", "fair"]
        negative_actions = ["harm", "deceive", "exploit", "unfair", "selfish"]
        
        positive_score = sum(1 for pos in positive_actions if pos in action.lower())
        negative_score = sum(1 for neg in negative_actions if neg in action.lower())
        
        return (positive_score - negative_score) / 2.0 + 0.5
    
    def _assess_flourishing_impact(self, action: str, dilemma: EthicalDilemma) -> float:
        """Assess impact on human flourishing"""
        # Simplified flourishing assessment
        
        flourishing_indicators = ["growth", "wellbeing", "happiness", "development", "fulfillment"]
        harm_indicators = ["suffering", "degradation", "oppression", "limitation"]
        
        flourishing_score = sum(1 for indicator in flourishing_indicators if indicator in action.lower())
        harm_score = sum(1 for indicator in harm_indicators if indicator in action.lower())
        
        return (flourishing_score - harm_score) / 2.0 + 0.5
    
    def _assess_value_conflict(self, value1: str, value2: str, dilemma: EthicalDilemma) -> float:
        """Assess severity of conflict between two values"""
        # Known value conflicts
        conflicts = {
            ("truth", "harm_prevention"): 0.7,  # Truth vs. protecting from harmful truth
            ("autonomy_respect", "harm_prevention"): 0.6,  # Respecting choice vs. preventing harm
            ("fairness", "helpfulness"): 0.4,  # Equal treatment vs. helping those in need
        }
        
        conflict_key = tuple(sorted([value1, value2]))
        return conflicts.get(conflict_key, 0.2)  # Default low conflict
    
    def _get_framework_weight(self, framework: str) -> float:
        """Get weight for ethical framework in decision synthesis"""
        weights = {
            "deontological": 0.4,  # Strong weight for duty-based ethics
            "consequentialist": 0.35,  # Moderate weight for outcomes
            "virtue_ethics": 0.25  # Moderate weight for character
        }
        return weights.get(framework, 0.33)
    
    def _generate_ethical_reasoning(self, action: str, deontological: Dict[str, Any],
                                  consequentialist: Dict[str, Any], virtue: Dict[str, Any],
                                  conflicts: List[Dict[str, Any]]) -> str:
        """Generate human-readable ethical reasoning"""
        reasoning_parts = []
        
        # Deontological reasoning
        if action in deontological.get("recommended_actions", []):
            reasoning_parts.append(f"From a duty-based perspective, '{action}' is ethically required.")
        elif action in deontological.get("prohibited_actions", []):
            reasoning_parts.append(f"From a duty-based perspective, '{action}' violates moral duties.")
        
        # Consequentialist reasoning
        if action == consequentialist.get("recommended_action"):
            reasoning_parts.append(f"From a consequentialist perspective, '{action}' produces the best outcomes.")
        
        # Virtue ethics reasoning
        if action == virtue.get("recommended_action"):
            reasoning_parts.append(f"From a virtue ethics perspective, '{action}' best embodies moral virtues.")
        
        # Value conflicts
        if conflicts:
            reasoning_parts.append(f"This decision involves {len(conflicts)} value conflicts that were resolved through ethical analysis.")
        
        return " ".join(reasoning_parts) if reasoning_parts else f"'{action}' was selected through comprehensive ethical analysis."
    
    def _extract_potential_harms(self, dilemma: EthicalDilemma) -> List[str]:
        """Extract potential harms from dilemma"""
        # Simplified harm extraction
        return ["potential_harm_1", "potential_harm_2"]  # Placeholder
    
    def _extract_potential_benefits(self, dilemma: EthicalDilemma) -> List[str]:
        """Extract potential benefits from dilemma"""
        # Simplified benefit extraction
        return ["potential_benefit_1", "potential_benefit_2"]  # Placeholder
    
    def _calculate_opinion_consistency(self, stance: str, topic: str) -> float:
        """Calculate consistency of opinion with previous opinions"""
        # Simplified consistency calculation
        return 0.8  # Placeholder
    
    def close(self):
        """Close database session"""
        self.session.close()

# Factory function
async def create_ethical_reasoning_engine() -> EthicalReasoningEngine:
    """Create and initialize ethical reasoning engine"""
    engine = EthicalReasoningEngine()
    await engine.initialize_ethical_systems()
    return engine