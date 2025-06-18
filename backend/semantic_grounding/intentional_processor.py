"""
Intentional Processor
Implements goal-oriented and curiosity-driven semantic processing
"""

import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from collections import defaultdict
import heapq

logger = logging.getLogger(__name__)

class GoalPriority(Enum):
    """Priority levels for goals"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKGROUND = 1

class AttentionFocus(Enum):
    """Types of attention focus"""
    GOAL_DIRECTED = "goal_directed"
    EXPLORATORY = "exploratory"
    REACTIVE = "reactive"
    BALANCED = "balanced"

@dataclass
class Goal:
    """Represents a processing goal"""
    goal_id: str
    description: str
    priority: GoalPriority
    criteria: Dict[str, Any]  # Success criteria
    deadline: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0
    sub_goals: List['Goal'] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # IDs of dependent goals
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_complete(self) -> bool:
        """Check if goal is complete"""
        return self.progress >= 1.0
    
    def is_overdue(self) -> bool:
        """Check if goal is past deadline"""
        if self.deadline:
            return datetime.now() > self.deadline
        return False

@dataclass
class AttentionState:
    """Current state of attention system"""
    focus_type: AttentionFocus
    current_targets: List[str]  # Concepts currently attended to
    attention_weights: Dict[str, float]  # Concept -> attention weight
    saliency_map: Dict[str, float]  # Concept -> saliency score
    inhibited_concepts: Set[str]  # Temporarily suppressed concepts
    
    def get_top_attended(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top N attended concepts"""
        sorted_attention = sorted(
            self.attention_weights.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_attention[:n]

@dataclass
class CuriositySignal:
    """Represents a curiosity-driven exploration signal"""
    target: str  # What to explore
    novelty_score: float  # How novel/interesting
    uncertainty: float  # How uncertain we are
    expected_information_gain: float
    exploration_type: str  # 'feature', 'relation', 'pattern'
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IntentionalUnderstanding:
    """Result of intentional processing"""
    focused_content: Dict[str, Any]
    novel_discoveries: List[Dict[str, Any]]
    goal_relevance: Dict[str, float]  # Goal ID -> relevance score
    attention_trace: List[AttentionState]
    processing_strategy: str
    confidence: float


class IntentionalProcessor:
    """
    Processor for goal-oriented and curiosity-driven semantic understanding.
    Moves beyond reactive processing to intentional, directed comprehension.
    """
    
    def __init__(self):
        # Goal management
        self.goals: Dict[str, Goal] = {}
        self.goal_queue: List[Tuple[float, str]] = []  # Priority queue (priority, goal_id)
        
        # Attention system
        self.attention_state = AttentionState(
            focus_type=AttentionFocus.BALANCED,
            current_targets=[],
            attention_weights={},
            saliency_map={},
            inhibited_concepts=set()
        )
        
        # Curiosity engine
        self.curiosity_threshold = 0.6
        self.novelty_memory: Dict[str, List[float]] = defaultdict(list)  # Track novelty over time
        self.exploration_history: List[CuriositySignal] = []
        
        # Meta-learning components
        self.learning_strategies: Dict[str, float] = {
            'depth_first': 0.5,
            'breadth_first': 0.5,
            'analogy_based': 0.5,
            'contrast_based': 0.5
        }
        
        # Performance tracking
        self.goal_success_rate: Dict[str, float] = defaultdict(float)
        self.strategy_effectiveness: Dict[str, float] = defaultdict(float)
        
        logger.info("Intentional Processor initialized")
    
    def set_goal(self, goal: Goal) -> str:
        """
        Set a new processing goal.
        
        Args:
            goal: The goal to set
            
        Returns:
            Goal ID
        """
        self.goals[goal.goal_id] = goal
        
        # Add to priority queue
        priority_value = -goal.priority.value  # Negative for max heap behavior
        heapq.heappush(self.goal_queue, (priority_value, goal.goal_id))
        
        logger.info(f"Set goal: {goal.description} (Priority: {goal.priority.name})")
        
        return goal.goal_id
    
    def process_with_intention(self, 
                             input_data: Any,
                             current_goals: Optional[List[str]] = None,
                             allow_exploration: bool = True) -> IntentionalUnderstanding:
        """
        Process input with specific goals and intentions.
        
        Args:
            input_data: Data to process
            current_goals: Specific goal IDs to focus on (None = use priority queue)
            allow_exploration: Whether to allow curiosity-driven exploration
            
        Returns:
            IntentionalUnderstanding with focused results
        """
        logger.debug("Processing with intention")
        
        # Determine active goals
        if current_goals is None:
            current_goals = self._select_active_goals()
        
        # Update attention based on goals
        self._update_attention_for_goals(current_goals, input_data)
        
        # Goal-directed processing
        focused_content = self._goal_directed_attention(input_data, current_goals)
        
        # Curiosity-driven exploration
        novel_discoveries = []
        if allow_exploration:
            curiosity_signals = self._identify_novelty(input_data)
            novel_discoveries = self._explore_curiosities(curiosity_signals)
        
        # Assess goal relevance
        goal_relevance = self._assess_goal_relevance(focused_content, current_goals)
        
        # Update goal progress
        self._update_goal_progress(current_goals, goal_relevance)
        
        # Determine processing strategy used
        strategy = self._determine_strategy(current_goals, allow_exploration)
        
        # Calculate confidence
        confidence = self._calculate_processing_confidence(
            focused_content, novel_discoveries, goal_relevance
        )
        
        return IntentionalUnderstanding(
            focused_content=focused_content,
            novel_discoveries=novel_discoveries,
            goal_relevance=goal_relevance,
            attention_trace=[self.attention_state],  # Simplified - would track over time
            processing_strategy=strategy,
            confidence=confidence
        )
    
    def _select_active_goals(self, max_goals: int = 3) -> List[str]:
        """Select active goals based on priority and constraints"""
        active_goals = []
        
        # Clean up completed goals from queue
        self._cleanup_goal_queue()
        
        # Get top priority goals
        temp_queue = []
        while len(active_goals) < max_goals and self.goal_queue:
            priority, goal_id = heapq.heappop(self.goal_queue)
            temp_queue.append((priority, goal_id))
            
            goal = self.goals.get(goal_id)
            if goal and not goal.is_complete() and not goal.is_overdue():
                # Check dependencies
                if self._dependencies_satisfied(goal):
                    active_goals.append(goal_id)
        
        # Restore queue
        for item in temp_queue:
            heapq.heappush(self.goal_queue, item)
        
        return active_goals
    
    def _cleanup_goal_queue(self):
        """Remove completed or expired goals from queue"""
        cleaned_queue = []
        
        while self.goal_queue:
            priority, goal_id = heapq.heappop(self.goal_queue)
            goal = self.goals.get(goal_id)
            
            if goal and not goal.is_complete() and not goal.is_overdue():
                cleaned_queue.append((priority, goal_id))
        
        self.goal_queue = cleaned_queue
        heapq.heapify(self.goal_queue)
    
    def _dependencies_satisfied(self, goal: Goal) -> bool:
        """Check if all dependencies for a goal are satisfied"""
        for dep_id in goal.dependencies:
            dep_goal = self.goals.get(dep_id)
            if dep_goal and not dep_goal.is_complete():
                return False
        return True
    
    def _update_attention_for_goals(self, goal_ids: List[str], input_data: Any):
        """Update attention state based on active goals"""
        # Reset attention weights
        self.attention_state.attention_weights.clear()
        
        # Analyze input to identify concepts
        concepts = self._extract_concepts(input_data)
        
        # Calculate relevance to each goal
        for concept in concepts:
            total_relevance = 0.0
            
            for goal_id in goal_ids:
                goal = self.goals.get(goal_id)
                if goal:
                    relevance = self._calculate_concept_goal_relevance(concept, goal)
                    total_relevance += relevance * goal.priority.value
            
            if total_relevance > 0:
                self.attention_state.attention_weights[concept] = total_relevance
        
        # Update saliency map
        self._update_saliency_map(concepts)
        
        # Set attention focus type
        if len(goal_ids) > 0:
            self.attention_state.focus_type = AttentionFocus.GOAL_DIRECTED
        else:
            self.attention_state.focus_type = AttentionFocus.EXPLORATORY
    
    def _extract_concepts(self, input_data: Any) -> List[str]:
        """Extract concepts from input data"""
        concepts = []
        
        if isinstance(input_data, str):
            # Simple word extraction (would use NLP in practice)
            words = input_data.lower().split()
            concepts = [w for w in words if len(w) > 3]  # Simple filter
        elif isinstance(input_data, dict):
            # Extract from dictionary keys and values
            for key, value in input_data.items():
                concepts.append(str(key))
                if isinstance(value, str):
                    concepts.extend(value.lower().split())
        elif isinstance(input_data, list):
            # Process each item
            for item in input_data:
                concepts.extend(self._extract_concepts(item))
        
        return list(set(concepts))  # Remove duplicates
    
    def _calculate_concept_goal_relevance(self, concept: str, goal: Goal) -> float:
        """Calculate how relevant a concept is to a goal"""
        relevance = 0.0
        
        # Check if concept appears in goal description
        if concept.lower() in goal.description.lower():
            relevance += 0.5
        
        # Check criteria
        for criterion_key, criterion_value in goal.criteria.items():
            if concept.lower() in str(criterion_key).lower():
                relevance += 0.3
            if concept.lower() in str(criterion_value).lower():
                relevance += 0.2
        
        # Check metadata
        if 'target_concepts' in goal.metadata:
            if concept in goal.metadata['target_concepts']:
                relevance += 0.8
        
        return min(1.0, relevance)
    
    def _update_saliency_map(self, concepts: List[str]):
        """Update saliency scores for concepts"""
        for concept in concepts:
            # Base saliency on attention weight
            base_saliency = self.attention_state.attention_weights.get(concept, 0.0)
            
            # Boost for novelty
            novelty = self._calculate_novelty(concept)
            
            # Combine factors
            saliency = base_saliency * 0.7 + novelty * 0.3
            
            # Apply inhibition
            if concept in self.attention_state.inhibited_concepts:
                saliency *= 0.1
            
            self.attention_state.saliency_map[concept] = saliency
    
    def _goal_directed_attention(self, input_data: Any, 
                               goal_ids: List[str]) -> Dict[str, Any]:
        """Apply goal-directed attention to process input"""
        focused_content = {}
        
        # Get top attended concepts
        top_concepts = self.attention_state.get_top_attended(10)
        
        # Process each concept with goal context
        for concept, attention_weight in top_concepts:
            if attention_weight > 0.1:  # Attention threshold
                concept_analysis = {
                    'concept': concept,
                    'attention_weight': attention_weight,
                    'goal_connections': {}
                }
                
                # Analyze concept in context of each goal
                for goal_id in goal_ids:
                    goal = self.goals.get(goal_id)
                    if goal:
                        connection = self._analyze_concept_for_goal(concept, goal, input_data)
                        if connection:
                            concept_analysis['goal_connections'][goal_id] = connection
                
                focused_content[concept] = concept_analysis
        
        return focused_content
    
    def _analyze_concept_for_goal(self, concept: str, goal: Goal, 
                                context: Any) -> Optional[Dict[str, Any]]:
        """Analyze how a concept relates to a specific goal"""
        analysis = {
            'relevance': self._calculate_concept_goal_relevance(concept, goal),
            'contribution': 'unknown',
            'evidence': []
        }
        
        # Determine contribution type
        if 'target_concepts' in goal.metadata:
            if concept in goal.metadata['target_concepts']:
                analysis['contribution'] = 'direct_target'
                analysis['evidence'].append('Listed as target concept')
        
        # Check if concept helps satisfy criteria
        for criterion, target_value in goal.criteria.items():
            if concept.lower() in str(criterion).lower():
                analysis['contribution'] = 'criterion_related'
                analysis['evidence'].append(f'Related to criterion: {criterion}')
        
        # Only return if there's meaningful contribution
        if analysis['relevance'] > 0.2:
            return analysis
        
        return None
    
    def _identify_novelty(self, input_data: Any) -> List[CuriositySignal]:
        """Identify novel or interesting patterns worth exploring"""
        curiosity_signals = []
        
        concepts = self._extract_concepts(input_data)
        
        for concept in concepts:
            novelty_score = self._calculate_novelty(concept)
            
            if novelty_score > self.curiosity_threshold:
                # Estimate information gain
                info_gain = self._estimate_information_gain(concept)
                
                signal = CuriositySignal(
                    target=concept,
                    novelty_score=novelty_score,
                    uncertainty=1.0 - len(self.novelty_memory[concept]) * 0.1,
                    expected_information_gain=info_gain,
                    exploration_type='feature'
                )
                
                curiosity_signals.append(signal)
        
        # Sort by expected information gain
        curiosity_signals.sort(key=lambda x: x.expected_information_gain, reverse=True)
        
        return curiosity_signals[:5]  # Top 5 curiosities
    
    def _calculate_novelty(self, concept: str) -> float:
        """Calculate novelty score for a concept"""
        # Check history
        if concept not in self.novelty_memory:
            return 0.9  # Very novel
        
        # Calculate based on recency and frequency
        occurrences = len(self.novelty_memory[concept])
        recency = self.novelty_memory[concept][-1] if occurrences > 0 else 0
        
        # Less novel if seen frequently or recently
        frequency_factor = 1.0 / (1.0 + occurrences * 0.1)
        recency_factor = min(1.0, (datetime.now().timestamp() - recency) / 3600)  # Hours
        
        return frequency_factor * 0.6 + recency_factor * 0.4
    
    def _estimate_information_gain(self, concept: str) -> float:
        """Estimate potential information gain from exploring a concept"""
        # Simplified estimation based on:
        # - Novelty
        # - Number of unknown relations
        # - Potential goal relevance
        
        base_gain = self._calculate_novelty(concept) * 0.5
        
        # Boost if related to active goals
        goal_boost = 0.0
        for goal_id, goal in self.goals.items():
            if not goal.is_complete():
                relevance = self._calculate_concept_goal_relevance(concept, goal)
                goal_boost = max(goal_boost, relevance * 0.3)
        
        return min(1.0, base_gain + goal_boost)
    
    def _explore_curiosities(self, curiosity_signals: List[CuriositySignal]) -> List[Dict[str, Any]]:
        """Explore curious patterns and concepts"""
        discoveries = []
        
        for signal in curiosity_signals[:3]:  # Explore top 3
            discovery = {
                'concept': signal.target,
                'novelty_score': signal.novelty_score,
                'exploration_type': signal.exploration_type,
                'findings': {}
            }
            
            # Simulate exploration (would involve actual investigation in practice)
            if signal.exploration_type == 'feature':
                discovery['findings']['new_features'] = self._discover_features(signal.target)
            elif signal.exploration_type == 'relation':
                discovery['findings']['new_relations'] = self._discover_relations(signal.target)
            elif signal.exploration_type == 'pattern':
                discovery['findings']['new_patterns'] = self._discover_patterns(signal.target)
            
            # Update novelty memory
            self.novelty_memory[signal.target].append(datetime.now().timestamp())
            
            # Record exploration
            self.exploration_history.append(signal)
            
            discoveries.append(discovery)
        
        return discoveries
    
    def _discover_features(self, concept: str) -> List[str]:
        """Discover new features of a concept (simulated)"""
        # In practice, this would involve actual feature extraction
        possible_features = [
            'has_color', 'has_shape', 'has_size', 'has_texture',
            'is_animate', 'is_natural', 'is_artificial', 'is_abstract'
        ]
        
        # Simulate discovery based on concept
        discovered = []
        if 'color' in concept.lower():
            discovered.append('has_color')
        if any(word in concept.lower() for word in ['animal', 'person', 'creature']):
            discovered.append('is_animate')
        
        # Random discovery for simulation
        import random
        if random.random() > 0.5:
            discovered.append(random.choice(possible_features))
        
        return discovered
    
    def _discover_relations(self, concept: str) -> List[Dict[str, str]]:
        """Discover new relations involving a concept (simulated)"""
        # In practice, this would involve knowledge graph exploration
        relations = []
        
        # Simulate some relations
        if 'water' in concept.lower():
            relations.append({'relation': 'composed_of', 'target': 'hydrogen'})
            relations.append({'relation': 'composed_of', 'target': 'oxygen'})
        
        return relations
    
    def _discover_patterns(self, concept: str) -> List[str]:
        """Discover patterns involving a concept (simulated)"""
        # In practice, this would involve pattern mining
        patterns = []
        
        if 'day' in concept.lower():
            patterns.append('follows_night')
            patterns.append('24_hour_cycle')
        
        return patterns
    
    def _assess_goal_relevance(self, focused_content: Dict[str, Any], 
                             goal_ids: List[str]) -> Dict[str, float]:
        """Assess how relevant the processed content is to each goal"""
        relevance_scores = {}
        
        for goal_id in goal_ids:
            goal = self.goals.get(goal_id)
            if not goal:
                continue
            
            total_relevance = 0.0
            relevance_count = 0
            
            # Check each focused concept
            for concept, analysis in focused_content.items():
                if goal_id in analysis.get('goal_connections', {}):
                    connection = analysis['goal_connections'][goal_id]
                    total_relevance += connection['relevance']
                    relevance_count += 1
            
            # Average relevance
            if relevance_count > 0:
                relevance_scores[goal_id] = total_relevance / relevance_count
            else:
                relevance_scores[goal_id] = 0.0
        
        return relevance_scores
    
    def _update_goal_progress(self, goal_ids: List[str], 
                            relevance_scores: Dict[str, float]):
        """Update progress on goals based on processing results"""
        for goal_id in goal_ids:
            goal = self.goals.get(goal_id)
            if not goal:
                continue
            
            relevance = relevance_scores.get(goal_id, 0.0)
            
            # Simple progress update (would be more sophisticated in practice)
            progress_increment = relevance * 0.1  # 10% max per processing
            goal.progress = min(1.0, goal.progress + progress_increment)
            
            # Track success rate
            if goal.is_complete():
                self.goal_success_rate[goal_id] = 1.0
            
            logger.debug(f"Goal '{goal.description}' progress: {goal.progress:.2%}")
    
    def _determine_strategy(self, goal_ids: List[str], 
                          allow_exploration: bool) -> str:
        """Determine which processing strategy was used"""
        if not goal_ids:
            return "pure_exploration"
        elif not allow_exploration:
            return "pure_goal_directed"
        elif len(goal_ids) == 1:
            return "focused_goal_with_exploration"
        else:
            return "multi_goal_balanced"
    
    def _calculate_processing_confidence(self, focused_content: Dict[str, Any],
                                       novel_discoveries: List[Dict[str, Any]],
                                       goal_relevance: Dict[str, float]) -> float:
        """Calculate confidence in the intentional processing results"""
        confidence_factors = []
        
        # Factor 1: Attention coverage
        if focused_content:
            avg_attention = np.mean([
                item['attention_weight'] 
                for item in focused_content.values()
            ])
            confidence_factors.append(avg_attention)
        
        # Factor 2: Goal relevance
        if goal_relevance:
            avg_relevance = np.mean(list(goal_relevance.values()))
            confidence_factors.append(avg_relevance)
        
        # Factor 3: Discovery quality
        if novel_discoveries:
            avg_novelty = np.mean([d['novelty_score'] for d in novel_discoveries])
            confidence_factors.append(avg_novelty * 0.5)  # Weight down
        
        # Combine factors
        if confidence_factors:
            return np.mean(confidence_factors)
        else:
            return 0.5  # Default medium confidence
    
    def get_goal_status(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a goal"""
        goal = self.goals.get(goal_id)
        if not goal:
            return None
        
        return {
            'goal_id': goal_id,
            'description': goal.description,
            'priority': goal.priority.name,
            'progress': goal.progress,
            'is_complete': goal.is_complete(),
            'is_overdue': goal.is_overdue(),
            'deadline': goal.deadline.isoformat() if goal.deadline else None,
            'sub_goals': [g.goal_id for g in goal.sub_goals],
            'dependencies': goal.dependencies
        }
    
    def get_attention_summary(self) -> Dict[str, Any]:
        """Get summary of current attention state"""
        return {
            'focus_type': self.attention_state.focus_type.value,
            'top_attended': self.attention_state.get_top_attended(5),
            'num_targets': len(self.attention_state.current_targets),
            'num_inhibited': len(self.attention_state.inhibited_concepts),
            'total_concepts': len(self.attention_state.attention_weights)
        }
    
    def adjust_curiosity_threshold(self, new_threshold: float):
        """Adjust the threshold for curiosity-driven exploration"""
        self.curiosity_threshold = max(0.0, min(1.0, new_threshold))
        logger.info(f"Curiosity threshold adjusted to: {self.curiosity_threshold}")
    
    def inhibit_concept(self, concept: str, duration: Optional[float] = None):
        """Temporarily inhibit attention to a concept"""
        self.attention_state.inhibited_concepts.add(concept)
        
        if duration:
            # Schedule removal of inhibition (simplified - would use proper scheduling)
            logger.info(f"Inhibiting '{concept}' for {duration} seconds")
        else:
            logger.info(f"Inhibiting '{concept}' indefinitely")
    
    def release_inhibition(self, concept: str):
        """Release inhibition on a concept"""
        self.attention_state.inhibited_concepts.discard(concept)
        logger.info(f"Released inhibition on '{concept}'")