"""
Causal Reasoning Engine
Implements genuine causal understanding beyond mere correlation
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import networkx as nx
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class CausalRelation:
    """Represents a causal relationship between concepts"""
    cause: str
    effect: str
    mechanism: str
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidence_count: int
    temporal_lag: Optional[float] = None  # Time delay between cause and effect
    conditions: List[str] = None  # Conditions under which causation holds
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []


@dataclass
class CausalChain:
    """Represents a chain of causal relationships"""
    steps: List[CausalRelation]
    total_strength: float
    weakest_link: float
    
    def get_path(self) -> List[str]:
        """Get the path from initial cause to final effect"""
        if not self.steps:
            return []
        
        path = [self.steps[0].cause]
        for step in self.steps:
            path.append(step.effect)
        return path


class CausalReasoningEngine:
    """
    Engine for understanding and reasoning about causal relationships.
    Goes beyond correlation to identify actual causal mechanisms.
    """
    
    def __init__(self):
        # Causal knowledge graph
        self.causal_graph = nx.DiGraph()
        
        # Mechanism database
        self.mechanisms = {}
        
        # Temporal patterns
        self.temporal_patterns = defaultdict(list)
        
        # Counterfactual reasoning cache
        self.counterfactual_cache = {}
        
        # Initialize with basic causal knowledge
        self._init_causal_knowledge()
        
        logger.info("Causal Reasoning Engine initialized")
    
    def _init_causal_knowledge(self):
        """Initialize basic causal relationships and mechanisms"""
        # Physical causation
        self._add_causal_relation(
            "heat", "ice", "melting", "water",
            strength=0.95, confidence=1.0,
            conditions=["temperature > 0°C"]
        )
        self._add_causal_relation(
            "water", "freezing", "ice", "solidification",
            strength=0.95, confidence=1.0,
            conditions=["temperature < 0°C"]
        )
        self._add_causal_relation(
            "fire", "combustion", "smoke", "oxidation",
            strength=0.9, confidence=0.95,
            conditions=["oxygen present", "fuel available"]
        )
        self._add_causal_relation(
            "rain", "precipitation", "wet ground", "water absorption",
            strength=0.85, confidence=0.9,
            temporal_lag=0.1  # Quick effect
        )
        
        # Biological causation
        self._add_causal_relation(
            "sunlight", "photosynthesis", "plant growth", "energy conversion",
            strength=0.8, confidence=0.9,
            conditions=["chlorophyll present", "CO2 available"],
            temporal_lag=24.0  # Daily cycle
        )
        self._add_causal_relation(
            "exercise", "muscle stimulation", "increased heart rate", "oxygen demand",
            strength=0.9, confidence=0.95,
            temporal_lag=0.01  # Almost immediate
        )
        
        # Abstract causation
        self._add_causal_relation(
            "study", "knowledge acquisition", "understanding", "neural pathway formation",
            strength=0.7, confidence=0.8,
            temporal_lag=3600.0  # Hours to days
        )
        self._add_causal_relation(
            "practice", "skill reinforcement", "improvement", "motor memory",
            strength=0.75, confidence=0.85,
            conditions=["consistent repetition"],
            temporal_lag=86400.0  # Days
        )
    
    def _add_causal_relation(self, cause: str, mechanism: str, effect: str, 
                           process: str, strength: float, confidence: float,
                           conditions: List[str] = None, temporal_lag: float = None):
        """Add a causal relation to the knowledge base"""
        # Create relation object
        relation = CausalRelation(
            cause=cause,
            effect=effect,
            mechanism=mechanism,
            strength=strength,
            confidence=confidence,
            evidence_count=1,
            temporal_lag=temporal_lag,
            conditions=conditions or []
        )
        
        # Add to graph
        self.causal_graph.add_edge(
            cause, effect,
            relation=relation,
            weight=strength
        )
        
        # Store mechanism details
        self.mechanisms[mechanism] = {
            'process': process,
            'inputs': [cause],
            'outputs': [effect],
            'conditions': conditions or [],
            'temporal_lag': temporal_lag
        }
    
    def identify_causes_effects(self, concept: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Identify causal relationships for a concept.
        
        Args:
            concept: The concept to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing causes, effects, and mechanisms
        """
        logger.debug(f"Identifying causal relations for: {concept}")
        
        causes = []
        effects = []
        mechanisms = []
        
        # Find direct causes (predecessors in graph)
        if concept in self.causal_graph:
            for predecessor in self.causal_graph.predecessors(concept):
                edge_data = self.causal_graph[predecessor][concept]
                relation = edge_data.get('relation')
                if relation:
                    causes.append({
                        'cause': predecessor,
                        'mechanism': relation.mechanism,
                        'strength': relation.strength,
                        'conditions': relation.conditions
                    })
                    mechanisms.append(relation.mechanism)
            
            # Find direct effects (successors in graph)
            for successor in self.causal_graph.successors(concept):
                edge_data = self.causal_graph[concept][successor]
                relation = edge_data.get('relation')
                if relation:
                    effects.append({
                        'effect': successor,
                        'mechanism': relation.mechanism,
                        'strength': relation.strength,
                        'conditions': relation.conditions
                    })
                    mechanisms.append(relation.mechanism)
        
        # Infer additional relations from context
        if context:
            inferred = self._infer_causal_relations(concept, context)
            causes.extend(inferred.get('causes', []))
            effects.extend(inferred.get('effects', []))
            mechanisms.extend(inferred.get('mechanisms', []))
        
        # Calculate overall causal confidence
        confidence = self._calculate_causal_confidence(causes, effects)
        
        # Find causal chains
        chains = self._find_causal_chains(concept, max_depth=3)
        
        return {
            'causes': [c['cause'] for c in causes],
            'effects': [e['effect'] for e in effects],
            'mechanisms': list(set(mechanisms)),
            'causal_chains': chains,
            'confidence': confidence,
            'strength': np.mean([c['strength'] for c in causes + effects]) if causes or effects else 0.0,
            'detailed_causes': causes,
            'detailed_effects': effects
        }
    
    def _infer_causal_relations(self, concept: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Infer causal relations from context"""
        inferred_causes = []
        inferred_effects = []
        inferred_mechanisms = []
        
        # Check for temporal patterns
        if 'temporal_sequence' in context:
            sequence = context['temporal_sequence']
            # Handle single temporal index
            if isinstance(sequence, int):
                return {
                    'causes': inferred_causes,
                    'effects': inferred_effects,
                    'mechanisms': inferred_mechanisms
                }
            for i, item in enumerate(sequence):
                if item == concept and i > 0:
                    # Previous item might be a cause
                    potential_cause = sequence[i-1]
                    if self._is_plausible_cause(potential_cause, concept):
                        inferred_causes.append({
                            'cause': potential_cause,
                            'mechanism': 'temporal_precedence',
                            'strength': 0.6,
                            'conditions': ['temporal_sequence']
                        })
                
                if item == concept and i < len(sequence) - 1:
                    # Next item might be an effect
                    potential_effect = sequence[i+1]
                    if self._is_plausible_effect(concept, potential_effect):
                        inferred_effects.append({
                            'effect': potential_effect,
                            'mechanism': 'temporal_succession',
                            'strength': 0.6,
                            'conditions': ['temporal_sequence']
                        })
        
        # Check for co-occurrence patterns
        if 'co_occurrences' in context:
            for co_concept, frequency in context['co_occurrences'].items():
                if frequency > 0.7:  # High co-occurrence
                    # Determine causal direction based on domain knowledge
                    if self._is_plausible_cause(co_concept, concept):
                        inferred_causes.append({
                            'cause': co_concept,
                            'mechanism': 'high_correlation',
                            'strength': 0.5,
                            'conditions': ['frequent_co_occurrence']
                        })
        
        return {
            'causes': inferred_causes,
            'effects': inferred_effects,
            'mechanisms': inferred_mechanisms
        }
    
    def _is_plausible_cause(self, potential_cause: str, effect: str) -> bool:
        """Check if a causal relationship is plausible"""
        # Check if there's already a path in the graph
        if (potential_cause in self.causal_graph and 
            effect in self.causal_graph and
            nx.has_path(self.causal_graph, potential_cause, effect)):
            return True
        
        # Apply domain heuristics
        cause_keywords = ['trigger', 'cause', 'lead', 'result', 'create', 'generate']
        effect_keywords = ['result', 'effect', 'consequence', 'outcome', 'product']
        
        # Simple heuristic based on keywords
        for keyword in cause_keywords:
            if keyword in potential_cause.lower():
                return True
        
        return False
    
    def _is_plausible_effect(self, cause: str, potential_effect: str) -> bool:
        """Check if an effect relationship is plausible"""
        return self._is_plausible_cause(cause, potential_effect)
    
    def _calculate_causal_confidence(self, causes: List[Dict], effects: List[Dict]) -> float:
        """Calculate overall confidence in causal understanding"""
        if not causes and not effects:
            return 0.0
        
        all_strengths = []
        all_strengths.extend([c['strength'] for c in causes])
        all_strengths.extend([e['strength'] for e in effects])
        
        # Base confidence on average strength
        base_confidence = np.mean(all_strengths)
        
        # Boost confidence if we have both causes and effects
        if causes and effects:
            base_confidence = min(1.0, base_confidence * 1.2)
        
        # Reduce confidence if conditions are complex
        total_conditions = sum(len(c.get('conditions', [])) for c in causes + effects)
        if total_conditions > 5:
            base_confidence *= 0.9
        
        return base_confidence
    
    def _find_causal_chains(self, concept: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Find causal chains involving the concept"""
        chains = []
        
        if concept not in self.causal_graph:
            return chains
        
        # Find chains where concept is the effect
        for source in self.causal_graph.nodes():
            if source != concept:
                try:
                    paths = list(nx.all_simple_paths(
                        self.causal_graph, source, concept, cutoff=max_depth
                    ))
                    for path in paths:
                        if len(path) > 1:
                            chain = self._build_causal_chain(path)
                            if chain:
                                chains.append({
                                    'type': 'causes_of',
                                    'chain': chain,
                                    'path': chain.get_path()
                                })
                except nx.NetworkXNoPath:
                    continue
        
        # Find chains where concept is the cause
        for target in self.causal_graph.nodes():
            if target != concept:
                try:
                    paths = list(nx.all_simple_paths(
                        self.causal_graph, concept, target, cutoff=max_depth
                    ))
                    for path in paths:
                        if len(path) > 1:
                            chain = self._build_causal_chain(path)
                            if chain:
                                chains.append({
                                    'type': 'effects_of',
                                    'chain': chain,
                                    'path': chain.get_path()
                                })
                except nx.NetworkXNoPath:
                    continue
        
        return chains[:10]  # Limit to 10 most relevant chains
    
    def _build_causal_chain(self, path: List[str]) -> Optional[CausalChain]:
        """Build a causal chain from a path"""
        if len(path) < 2:
            return None
        
        steps = []
        strengths = []
        
        for i in range(len(path) - 1):
            cause = path[i]
            effect = path[i + 1]
            
            if self.causal_graph.has_edge(cause, effect):
                edge_data = self.causal_graph[cause][effect]
                relation = edge_data.get('relation')
                if relation:
                    steps.append(relation)
                    strengths.append(relation.strength)
        
        if not steps:
            return None
        
        return CausalChain(
            steps=steps,
            total_strength=np.prod(strengths),  # Multiplicative chain strength
            weakest_link=min(strengths)
        )
    
    def reason_counterfactually(self, 
                              concept: str,
                              intervention: Dict[str, Any],
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform counterfactual reasoning: "What if X had been different?"
        
        Args:
            concept: The concept to analyze
            intervention: The hypothetical change
            context: Optional context
            
        Returns:
            Predicted changes and their likelihood
        """
        logger.debug(f"Counterfactual reasoning for {concept} with intervention: {intervention}")
        
        # Check cache
        cache_key = f"{concept}_{str(intervention)}"
        if cache_key in self.counterfactual_cache:
            return self.counterfactual_cache[cache_key]
        
        predictions = {
            'direct_effects': [],
            'indirect_effects': [],
            'prevented_effects': [],
            'confidence': 0.0
        }
        
        # Analyze what would change
        if 'remove' in intervention:
            # What if this concept didn't exist?
            removed_concept = intervention['remove']
            
            # Find all effects that would be prevented
            if removed_concept in self.causal_graph:
                for successor in nx.descendants(self.causal_graph, removed_concept):
                    # Check if there are alternative paths
                    alt_paths = self._find_alternative_paths(removed_concept, successor)
                    
                    if not alt_paths:
                        predictions['prevented_effects'].append({
                            'effect': successor,
                            'certainty': 0.8,
                            'reason': f"No alternative cause for {successor}"
                        })
        
        if 'change' in intervention:
            # What if this property changed?
            change = intervention['change']
            property_name = change.get('property')
            new_value = change.get('value')
            
            # Propagate changes through causal network
            affected = self._propagate_change(concept, property_name, new_value)
            
            predictions['direct_effects'] = affected['direct']
            predictions['indirect_effects'] = affected['indirect']
        
        # Calculate confidence
        total_predictions = (len(predictions['direct_effects']) + 
                           len(predictions['indirect_effects']) + 
                           len(predictions['prevented_effects']))
        
        if total_predictions > 0:
            predictions['confidence'] = min(0.9, 0.3 + (total_predictions * 0.1))
        
        # Cache result
        self.counterfactual_cache[cache_key] = predictions
        
        return predictions
    
    def _find_alternative_paths(self, removed_node: str, target: str) -> List[List[str]]:
        """Find alternative causal paths that don't go through removed_node"""
        alternative_paths = []
        
        # Temporarily remove the node from a copy of the graph
        temp_graph = self.causal_graph.copy()
        temp_graph.remove_node(removed_node)
        
        # Find all nodes that could potentially cause the target
        for source in temp_graph.nodes():
            if source != target:
                try:
                    paths = nx.all_simple_paths(temp_graph, source, target, cutoff=5)
                    alternative_paths.extend(paths)
                except nx.NetworkXNoPath:
                    continue
        
        return alternative_paths
    
    def _propagate_change(self, concept: str, property_name: str, 
                         new_value: Any) -> Dict[str, List[Dict]]:
        """Propagate a change through the causal network"""
        affected = {
            'direct': [],
            'indirect': []
        }
        
        # Direct effects
        if concept in self.causal_graph:
            for successor in self.causal_graph.successors(concept):
                edge_data = self.causal_graph[concept][successor]
                relation = edge_data.get('relation')
                
                if relation:
                    # Check if this property change affects the causal relation
                    impact = self._assess_property_impact(
                        property_name, new_value, relation
                    )
                    
                    if impact > 0:
                        affected['direct'].append({
                            'concept': successor,
                            'impact': impact,
                            'mechanism': relation.mechanism,
                            'description': f"{property_name} change affects {relation.mechanism}"
                        })
            
            # Indirect effects (2-hop)
            for direct_effect in affected['direct']:
                successor = direct_effect['concept']
                if successor in self.causal_graph:
                    for indirect in self.causal_graph.successors(successor):
                        affected['indirect'].append({
                            'concept': indirect,
                            'impact': direct_effect['impact'] * 0.7,  # Diminished impact
                            'via': successor,
                            'description': f"Indirect effect via {successor}"
                        })
        
        return affected
    
    def _assess_property_impact(self, property_name: str, new_value: Any,
                              relation: CausalRelation) -> float:
        """Assess how a property change impacts a causal relation"""
        # Check if property is mentioned in conditions
        impact = 0.0
        
        for condition in relation.conditions:
            if property_name.lower() in condition.lower():
                # Property is relevant to this causal relation
                impact = 0.8
                
                # Adjust based on the nature of the change
                if 'temperature' in property_name and 'temperature' in condition:
                    # Temperature changes have strong effects
                    impact = 0.9
                elif 'presence' in property_name or 'absence' in property_name:
                    # Presence/absence has binary effect
                    impact = 1.0 if new_value else 0.0
        
        # If no specific condition match, use general heuristic
        if impact == 0.0:
            impact = 0.3 * relation.strength  # Proportional to relation strength
        
        return impact
    
    def explain_mechanism(self, cause: str, effect: str) -> Optional[str]:
        """
        Provide a detailed explanation of the causal mechanism.
        
        Args:
            cause: The cause concept
            effect: The effect concept
            
        Returns:
            Human-readable explanation of the mechanism
        """
        if not self.causal_graph.has_edge(cause, effect):
            return None
        
        edge_data = self.causal_graph[cause][effect]
        relation = edge_data.get('relation')
        
        if not relation:
            return None
        
        mechanism_details = self.mechanisms.get(relation.mechanism, {})
        
        explanation = f"Causal Mechanism: {cause} → {effect}\n"
        explanation += f"Mechanism: {relation.mechanism}\n"
        explanation += f"Process: {mechanism_details.get('process', 'Unknown')}\n"
        explanation += f"Strength: {relation.strength:.2f}\n"
        explanation += f"Confidence: {relation.confidence:.2f}\n"
        
        if relation.temporal_lag:
            explanation += f"Temporal Lag: {relation.temporal_lag} time units\n"
        
        if relation.conditions:
            explanation += f"Conditions Required:\n"
            for condition in relation.conditions:
                explanation += f"  - {condition}\n"
        
        return explanation
    
    def discover_new_causation(self, observations: List[Dict[str, Any]]) -> List[CausalRelation]:
        """
        Discover new causal relationships from observations.
        
        Args:
            observations: List of observed events with timestamps
            
        Returns:
            List of discovered causal relations
        """
        discovered = []
        
        # Sort observations by timestamp
        sorted_obs = sorted(observations, key=lambda x: x.get('timestamp', 0))
        
        # Look for temporal patterns
        for i in range(len(sorted_obs) - 1):
            current = sorted_obs[i]
            next_obs = sorted_obs[i + 1]
            
            # Check temporal proximity
            time_diff = next_obs.get('timestamp', 0) - current.get('timestamp', 0)
            
            if time_diff < 3600:  # Within an hour
                # Potential causal relationship
                cause_candidate = current.get('concept')
                effect_candidate = next_obs.get('concept')
                
                if cause_candidate and effect_candidate:
                    # Check if this pattern repeats
                    pattern_count = self._count_temporal_pattern(
                        sorted_obs, cause_candidate, effect_candidate, time_diff
                    )
                    
                    if pattern_count >= 3:  # Repeated at least 3 times
                        # Create new causal relation
                        new_relation = CausalRelation(
                            cause=cause_candidate,
                            effect=effect_candidate,
                            mechanism='temporal_regularity',
                            strength=min(0.7, pattern_count * 0.1),
                            confidence=min(0.8, pattern_count * 0.15),
                            evidence_count=pattern_count,
                            temporal_lag=time_diff
                        )
                        
                        discovered.append(new_relation)
                        
                        # Add to graph
                        self.causal_graph.add_edge(
                            cause_candidate, effect_candidate,
                            relation=new_relation,
                            weight=new_relation.strength
                        )
        
        return discovered
    
    def _count_temporal_pattern(self, observations: List[Dict], 
                              cause: str, effect: str, 
                              expected_lag: float) -> int:
        """Count how many times a temporal pattern occurs"""
        count = 0
        
        for i in range(len(observations) - 1):
            if (observations[i].get('concept') == cause and
                observations[i + 1].get('concept') == effect):
                
                time_diff = (observations[i + 1].get('timestamp', 0) - 
                           observations[i].get('timestamp', 0))
                
                # Allow 20% variance in temporal lag
                if abs(time_diff - expected_lag) / expected_lag < 0.2:
                    count += 1
        
        return count