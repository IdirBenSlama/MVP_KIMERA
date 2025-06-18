"""
Embodied Semantic Engine
Core component for connecting abstract symbols to real-world experiences
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import logging

from ..core.geoid import GeoidState
from ..vault.vault_manager import VaultManager

logger = logging.getLogger(__name__)

@dataclass
class SemanticGrounding:
    """Represents a grounded semantic concept with multimodal connections"""
    concept: str
    visual: Optional[Dict[str, Any]] = None
    auditory: Optional[Dict[str, Any]] = None
    causal: Optional[Dict[str, Any]] = None
    temporal: Optional[Dict[str, Any]] = None
    physical: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'concept': self.concept,
            'visual': self.visual,
            'auditory': self.auditory,
            'causal': self.causal,
            'temporal': self.temporal,
            'physical': self.physical,
            'confidence': self.confidence,
            'timestamp': self.timestamp
        }
    
    def compute_grounding_strength(self) -> float:
        """Calculate overall grounding strength across modalities"""
        modality_scores = []
        
        if self.visual and self.visual.get('confidence', 0) > 0:
            modality_scores.append(self.visual['confidence'])
        if self.auditory and self.auditory.get('confidence', 0) > 0:
            modality_scores.append(self.auditory['confidence'])
        if self.causal and self.causal.get('confidence', 0) > 0:
            modality_scores.append(self.causal['confidence'])
        if self.temporal and self.temporal.get('confidence', 0) > 0:
            modality_scores.append(self.temporal['confidence'])
        if self.physical and self.physical.get('confidence', 0) > 0:
            modality_scores.append(self.physical['confidence'])
        
        if not modality_scores:
            return 0.0
        
        # Weighted average with bonus for multiple modalities
        base_score = np.mean(modality_scores)
        modality_bonus = min(0.3, len(modality_scores) * 0.05)
        
        return min(1.0, base_score + modality_bonus)


class EmbodiedSemanticEngine:
    """
    Engine for creating genuine semantic understanding through embodied grounding.
    Connects abstract concepts to multimodal experiences and physical reality.
    """
    
    def __init__(self, vault_manager: Optional[VaultManager] = None):
        self.vault_manager = vault_manager or VaultManager()
        
        # Initialize sub-engines (will be imported from separate modules)
        from .multimodal_processor import MultiModalProcessor
        from .causal_reasoning_engine import CausalReasoningEngine
        from .temporal_dynamics_engine import TemporalDynamicsEngine
        from .physical_grounding_system import PhysicalGroundingSystem
        
        self.multimodal_processor = MultiModalProcessor()
        self.causal_reasoner = CausalReasoningEngine()
        self.temporal_processor = TemporalDynamicsEngine()
        self.physical_grounding = PhysicalGroundingSystem()
        
        # Semantic memory for storing grounded concepts
        self.semantic_memory: Dict[str, SemanticGrounding] = {}
        
        # Cross-modal association matrix
        self.cross_modal_associations: Dict[Tuple[str, str], float] = {}
        
        logger.info("Embodied Semantic Engine initialized")
    
    def process_concept(self, 
                       concept: str, 
                       context: Optional[Dict[str, Any]] = None,
                       modalities: Optional[List[str]] = None) -> SemanticGrounding:
        """
        Process a concept through multiple modalities to create genuine understanding.
        
        Args:
            concept: The abstract concept to ground
            context: Optional context information
            modalities: Specific modalities to process (default: all)
        
        Returns:
            SemanticGrounding object with multimodal connections
        """
        logger.info(f"Processing concept: {concept}")
        
        # Check if we already have this concept grounded
        if concept in self.semantic_memory:
            existing = self.semantic_memory[concept]
            # Update with new context if provided
            if context:
                return self._update_grounding(existing, context)
            return existing
        
        # Process through each modality
        modalities = modalities or ['visual', 'auditory', 'causal', 'temporal', 'physical']
        
        grounding = SemanticGrounding(concept=concept)
        
        if 'visual' in modalities:
            grounding.visual = self._ground_visually(concept, context)
        
        if 'auditory' in modalities:
            grounding.auditory = self._ground_auditorily(concept, context)
        
        if 'causal' in modalities:
            grounding.causal = self._ground_causally(concept, context)
        
        if 'temporal' in modalities:
            grounding.temporal = self._ground_temporally(concept, context)
        
        if 'physical' in modalities:
            grounding.physical = self._ground_physically(concept, context)
        
        # Compute overall confidence
        grounding.confidence = grounding.compute_grounding_strength()
        
        # Store in semantic memory
        self.semantic_memory[concept] = grounding
        
        # Update cross-modal associations
        self._update_cross_modal_associations(grounding)
        
        # Persist to database
        self._persist_grounding(grounding)
        
        logger.info(f"Concept '{concept}' grounded with confidence: {grounding.confidence}")
        
        return grounding
    
    def _ground_visually(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ground concept in visual experience"""
        try:
            visual_features = self.multimodal_processor.ground_visually(concept, context)
            return {
                'features': visual_features,
                'confidence': visual_features.get('confidence', 0.0),
                'associations': visual_features.get('associations', []),
                'properties': {
                    'color': visual_features.get('color'),
                    'shape': visual_features.get('shape'),
                    'texture': visual_features.get('texture'),
                    'size': visual_features.get('size')
                }
            }
        except Exception as e:
            logger.error(f"Visual grounding failed for {concept}: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _ground_auditorily(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ground concept in auditory experience"""
        try:
            audio_features = self.multimodal_processor.ground_auditorily(concept, context)
            return {
                'features': audio_features,
                'confidence': audio_features.get('confidence', 0.0),
                'associations': audio_features.get('associations', []),
                'properties': {
                    'frequency': audio_features.get('frequency'),
                    'amplitude': audio_features.get('amplitude'),
                    'timbre': audio_features.get('timbre'),
                    'rhythm': audio_features.get('rhythm')
                }
            }
        except Exception as e:
            logger.error(f"Auditory grounding failed for {concept}: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _ground_causally(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ground concept in causal relationships"""
        try:
            causal_relations = self.causal_reasoner.identify_causes_effects(concept, context)
            return {
                'causes': causal_relations.get('causes', []),
                'effects': causal_relations.get('effects', []),
                'mechanisms': causal_relations.get('mechanisms', []),
                'confidence': causal_relations.get('confidence', 0.0),
                'causal_strength': causal_relations.get('strength', 0.0)
            }
        except Exception as e:
            logger.error(f"Causal grounding failed for {concept}: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _ground_temporally(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ground concept in temporal dynamics"""
        try:
            temporal_context = self.temporal_processor.contextualize(concept, context)
            return {
                'duration': temporal_context.get('duration'),
                'frequency': temporal_context.get('frequency'),
                'temporal_patterns': temporal_context.get('patterns', []),
                'lifecycle': temporal_context.get('lifecycle'),
                'confidence': temporal_context.get('confidence', 0.0)
            }
        except Exception as e:
            logger.error(f"Temporal grounding failed for {concept}: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _ground_physically(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ground concept in physical properties"""
        try:
            physical_properties = self.physical_grounding.map_properties(concept, context)
            return {
                'mass': physical_properties.get('mass'),
                'volume': physical_properties.get('volume'),
                'density': physical_properties.get('density'),
                'state': physical_properties.get('state'),
                'interactions': physical_properties.get('interactions', []),
                'constraints': physical_properties.get('constraints', []),
                'confidence': physical_properties.get('confidence', 0.0)
            }
        except Exception as e:
            logger.error(f"Physical grounding failed for {concept}: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _update_grounding(self, 
                         existing: SemanticGrounding, 
                         new_context: Dict[str, Any]) -> SemanticGrounding:
        """Update existing grounding with new context information"""
        # Create a copy to avoid modifying the original
        updated = SemanticGrounding(
            concept=existing.concept,
            visual=existing.visual.copy() if existing.visual else None,
            auditory=existing.auditory.copy() if existing.auditory else None,
            causal=existing.causal.copy() if existing.causal else None,
            temporal=existing.temporal.copy() if existing.temporal else None,
            physical=existing.physical.copy() if existing.physical else None,
            confidence=existing.confidence
        )
        
        # Update based on new context
        if new_context.get('update_visual'):
            updated.visual = self._ground_visually(existing.concept, new_context)
        
        if new_context.get('update_causal'):
            updated.causal = self._ground_causally(existing.concept, new_context)
        
        # Recompute confidence
        updated.confidence = updated.compute_grounding_strength()
        
        # Update in memory
        self.semantic_memory[existing.concept] = updated
        
        # Persist updates
        self._persist_grounding(updated)
        
        return updated
    
    def _update_cross_modal_associations(self, grounding: SemanticGrounding):
        """Update associations between different modalities for this concept"""
        modalities = []
        
        if grounding.visual and grounding.visual.get('confidence', 0) > 0.5:
            modalities.append('visual')
        if grounding.auditory and grounding.auditory.get('confidence', 0) > 0.5:
            modalities.append('auditory')
        if grounding.causal and grounding.causal.get('confidence', 0) > 0.5:
            modalities.append('causal')
        if grounding.temporal and grounding.temporal.get('confidence', 0) > 0.5:
            modalities.append('temporal')
        if grounding.physical and grounding.physical.get('confidence', 0) > 0.5:
            modalities.append('physical')
        
        # Create associations between all pairs of active modalities
        for i, mod1 in enumerate(modalities):
            for mod2 in modalities[i+1:]:
                key = (mod1, mod2)
                current_strength = self.cross_modal_associations.get(key, 0.0)
                # Strengthen association
                self.cross_modal_associations[key] = min(1.0, current_strength + 0.1)
    
    def _persist_grounding(self, grounding: SemanticGrounding):
        """Persist grounding to database"""
        try:
            # Store in Neo4j through vault manager
            if hasattr(self.vault_manager, 'store_semantic_grounding'):
                self.vault_manager.store_semantic_grounding(grounding.to_dict())
            
            # Also create a GeoidState for compatibility
            geoid = GeoidState(
                geoid_id=f"semantic_{grounding.concept}_{datetime.now().timestamp()}",
                semantic_state={'concept': grounding.concept, 'confidence': grounding.confidence},
                symbolic_state=grounding.to_dict(),
                metadata={
                    'type': 'semantic_grounding',
                    'timestamp': grounding.timestamp,
                    'modalities': list(grounding.to_dict().keys())
                }
            )
            
            # Store through vault manager
            if hasattr(self.vault_manager, 'insert_geoid'):
                self.vault_manager.insert_geoid(geoid)
            else:
                logger.debug("VaultManager doesn't support insert_geoid - skipping persistence")
            
        except Exception as e:
            logger.error(f"Failed to persist grounding: {e}")
    
    def get_grounding(self, concept: str) -> Optional[SemanticGrounding]:
        """Retrieve grounding for a concept"""
        return self.semantic_memory.get(concept)
    
    def get_related_concepts(self, 
                           concept: str, 
                           modality: Optional[str] = None,
                           threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        Find concepts related through specific modality or all modalities.
        
        Returns:
            List of (concept, similarity_score) tuples
        """
        if concept not in self.semantic_memory:
            return []
        
        base_grounding = self.semantic_memory[concept]
        related = []
        
        for other_concept, other_grounding in self.semantic_memory.items():
            if other_concept == concept:
                continue
            
            similarity = self._compute_similarity(base_grounding, other_grounding, modality)
            
            if similarity >= threshold:
                related.append((other_concept, similarity))
        
        # Sort by similarity
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related
    
    def _compute_similarity(self, 
                          grounding1: SemanticGrounding, 
                          grounding2: SemanticGrounding,
                          modality: Optional[str] = None) -> float:
        """Compute similarity between two groundings"""
        if modality:
            # Compare specific modality
            modal1 = getattr(grounding1, modality)
            modal2 = getattr(grounding2, modality)
            
            if not modal1 or not modal2:
                return 0.0
            
            # Simple feature comparison (would be more sophisticated in practice)
            return self._compare_modal_features(modal1, modal2)
        else:
            # Compare across all modalities
            similarities = []
            
            for mod in ['visual', 'auditory', 'causal', 'temporal', 'physical']:
                modal1 = getattr(grounding1, mod)
                modal2 = getattr(grounding2, mod)
                
                if modal1 and modal2:
                    sim = self._compare_modal_features(modal1, modal2)
                    similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.0
    
    def _compare_modal_features(self, features1: Dict, features2: Dict) -> float:
        """Compare features between two modality representations"""
        # Simplified comparison - in practice would use more sophisticated methods
        common_keys = set(features1.keys()) & set(features2.keys())
        
        if not common_keys:
            return 0.0
        
        similarities = []
        
        for key in common_keys:
            val1 = features1.get(key)
            val2 = features2.get(key)
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity
                diff = abs(val1 - val2)
                sim = 1.0 / (1.0 + diff)
                similarities.append(sim)
            elif val1 == val2:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return np.mean(similarities)
    
    def explain_grounding(self, concept: str) -> str:
        """Generate human-readable explanation of concept grounding"""
        grounding = self.semantic_memory.get(concept)
        
        if not grounding:
            return f"No grounding found for concept: {concept}"
        
        explanation = f"Concept: {concept}\n"
        explanation += f"Overall Confidence: {grounding.confidence:.2f}\n\n"
        
        if grounding.visual:
            explanation += "Visual Grounding:\n"
            if 'properties' in grounding.visual:
                props = grounding.visual['properties']
                explanation += f"  - Color: {props.get('color', 'unknown')}\n"
                explanation += f"  - Shape: {props.get('shape', 'unknown')}\n"
            explanation += f"  - Confidence: {grounding.visual.get('confidence', 0):.2f}\n\n"
        
        if grounding.causal:
            explanation += "Causal Grounding:\n"
            causes = grounding.causal.get('causes', [])
            effects = grounding.causal.get('effects', [])
            if causes:
                explanation += f"  - Causes: {', '.join(causes[:3])}\n"
            if effects:
                explanation += f"  - Effects: {', '.join(effects[:3])}\n"
            explanation += f"  - Confidence: {grounding.causal.get('confidence', 0):.2f}\n\n"
        
        if grounding.physical:
            explanation += "Physical Grounding:\n"
            explanation += f"  - State: {grounding.physical.get('state', 'unknown')}\n"
            explanation += f"  - Mass: {grounding.physical.get('mass', 'unknown')}\n"
            explanation += f"  - Confidence: {grounding.physical.get('confidence', 0):.2f}\n"
        
        return explanation