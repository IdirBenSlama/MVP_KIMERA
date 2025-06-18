"""
Multimodal Processor
Handles integration of multiple sensory modalities for semantic grounding
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModalityFeatures:
    """Features extracted from a specific modality"""
    modality: str
    raw_features: np.ndarray
    processed_features: Dict[str, Any]
    confidence: float
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MultiModalProcessor:
    """
    Processes and integrates information from multiple sensory modalities
    to create rich, grounded representations of concepts.
    """
    
    def __init__(self):
        # Visual processing parameters
        self.visual_features = {
            'colors': ['red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'gray'],
            'shapes': ['round', 'square', 'triangular', 'irregular', 'linear', 'curved'],
            'textures': ['smooth', 'rough', 'soft', 'hard', 'fuzzy', 'metallic'],
            'sizes': ['tiny', 'small', 'medium', 'large', 'huge']
        }
        
        # Auditory processing parameters
        self.auditory_features = {
            'frequencies': {'low': (20, 250), 'mid': (250, 2000), 'high': (2000, 20000)},
            'amplitudes': ['quiet', 'moderate', 'loud'],
            'timbres': ['pure', 'harmonic', 'noisy', 'complex'],
            'rhythms': ['steady', 'irregular', 'pulsing', 'continuous']
        }
        
        # Concept-to-feature mappings (simplified knowledge base)
        self._init_concept_mappings()
        
        # Cross-modal correspondence rules
        self._init_cross_modal_rules()
        
        logger.info("MultiModal Processor initialized")
    
    def _init_concept_mappings(self):
        """Initialize basic concept-to-feature mappings"""
        # This would be learned from data in a real system
        self.concept_visual_map = {
            'apple': {
                'color': ['red', 'green', 'yellow'],
                'shape': ['round'],
                'texture': ['smooth'],
                'size': ['small', 'medium']
            },
            'car': {
                'color': ['black', 'white', 'red', 'blue', 'gray'],
                'shape': ['curved', 'linear'],
                'texture': ['metallic', 'smooth'],
                'size': ['large', 'huge']
            },
            'water': {
                'color': ['blue', 'transparent'],
                'shape': ['irregular'],
                'texture': ['smooth', 'flowing'],
                'size': ['variable']
            },
            'fire': {
                'color': ['red', 'yellow', 'orange'],
                'shape': ['irregular', 'flickering'],
                'texture': ['intangible'],
                'size': ['variable']
            }
        }
        
        self.concept_auditory_map = {
            'car': {
                'frequency': 'low',
                'amplitude': 'loud',
                'timbre': 'complex',
                'rhythm': 'steady'
            },
            'water': {
                'frequency': 'mid',
                'amplitude': 'moderate',
                'timbre': 'noisy',
                'rhythm': 'continuous'
            },
            'fire': {
                'frequency': 'mid',
                'amplitude': 'moderate',
                'timbre': 'noisy',
                'rhythm': 'irregular'
            },
            'bird': {
                'frequency': 'high',
                'amplitude': 'moderate',
                'timbre': 'harmonic',
                'rhythm': 'pulsing'
            }
        }
    
    def _init_cross_modal_rules(self):
        """Initialize cross-modal correspondence rules"""
        self.cross_modal_rules = {
            'size_to_frequency': {
                'tiny': 'high',
                'small': 'high',
                'medium': 'mid',
                'large': 'low',
                'huge': 'low'
            },
            'color_to_temperature': {
                'red': 'hot',
                'orange': 'warm',
                'yellow': 'warm',
                'blue': 'cold',
                'white': 'neutral',
                'black': 'neutral'
            },
            'texture_to_timbre': {
                'smooth': 'pure',
                'rough': 'noisy',
                'soft': 'harmonic',
                'hard': 'complex',
                'metallic': 'complex'
            }
        }
    
    def ground_visually(self, concept: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ground a concept in visual features.
        
        Args:
            concept: The concept to ground
            context: Optional context information
            
        Returns:
            Dictionary of visual features and associations
        """
        logger.debug(f"Visual grounding for concept: {concept}")
        
        # Check if we have direct mapping
        if concept.lower() in self.concept_visual_map:
            features = self.concept_visual_map[concept.lower()]
            confidence = 0.9
        else:
            # Try to infer from context or use defaults
            features = self._infer_visual_features(concept, context)
            confidence = 0.5
        
        # Generate visual feature vector
        feature_vector = self._encode_visual_features(features)
        
        # Find visual associations
        associations = self._find_visual_associations(concept, features)
        
        return {
            'features': features,
            'feature_vector': feature_vector.tolist(),
            'associations': associations,
            'confidence': confidence,
            'color': features.get('color', ['unknown'])[0],
            'shape': features.get('shape', ['unknown'])[0],
            'texture': features.get('texture', ['unknown'])[0],
            'size': features.get('size', ['unknown'])[0]
        }
    
    def ground_auditorily(self, concept: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ground a concept in auditory features.
        
        Args:
            concept: The concept to ground
            context: Optional context information
            
        Returns:
            Dictionary of auditory features and associations
        """
        logger.debug(f"Auditory grounding for concept: {concept}")
        
        # Check if we have direct mapping
        if concept.lower() in self.concept_auditory_map:
            features = self.concept_auditory_map[concept.lower()]
            confidence = 0.9
        else:
            # Try to infer from context or cross-modal correspondence
            features = self._infer_auditory_features(concept, context)
            confidence = 0.5
        
        # Generate auditory feature vector
        feature_vector = self._encode_auditory_features(features)
        
        # Find auditory associations
        associations = self._find_auditory_associations(concept, features)
        
        # Convert frequency to Hz range
        freq_range = self.auditory_features['frequencies'].get(
            features.get('frequency', 'mid'), 
            (250, 2000)
        )
        
        return {
            'features': features,
            'feature_vector': feature_vector.tolist(),
            'associations': associations,
            'confidence': confidence,
            'frequency': freq_range,
            'amplitude': features.get('amplitude', 'moderate'),
            'timbre': features.get('timbre', 'complex'),
            'rhythm': features.get('rhythm', 'steady')
        }
    
    def integrate_modalities(self, 
                           visual_features: Dict[str, Any],
                           auditory_features: Dict[str, Any],
                           other_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Integrate features from multiple modalities into a unified representation.
        
        Args:
            visual_features: Visual modality features
            auditory_features: Auditory modality features
            other_features: Additional modality features
            
        Returns:
            Integrated multimodal representation
        """
        # Extract feature vectors
        visual_vec = np.array(visual_features.get('feature_vector', []))
        auditory_vec = np.array(auditory_features.get('feature_vector', []))
        
        # Compute cross-modal consistency
        consistency = self._compute_cross_modal_consistency(visual_features, auditory_features)
        
        # Create integrated representation
        if visual_vec.size > 0 and auditory_vec.size > 0:
            # Concatenate and normalize
            integrated_vec = np.concatenate([visual_vec, auditory_vec])
            integrated_vec = integrated_vec / (np.linalg.norm(integrated_vec) + 1e-8)
        else:
            integrated_vec = np.zeros(128)  # Default size
        
        # Merge associations
        all_associations = []
        all_associations.extend(visual_features.get('associations', []))
        all_associations.extend(auditory_features.get('associations', []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_associations = []
        for item in all_associations:
            if item not in seen:
                seen.add(item)
                unique_associations.append(item)
        
        return {
            'integrated_vector': integrated_vec.tolist(),
            'modality_features': {
                'visual': visual_features,
                'auditory': auditory_features
            },
            'cross_modal_consistency': consistency,
            'associations': unique_associations,
            'confidence': (visual_features.get('confidence', 0) + 
                         auditory_features.get('confidence', 0)) / 2
        }
    
    def _infer_visual_features(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Infer visual features when direct mapping is not available"""
        features = {}
        
        # Use context if available
        if context:
            if 'color' in context:
                features['color'] = [context['color']]
            if 'size' in context:
                features['size'] = [context['size']]
        
        # Apply heuristics based on concept analysis
        concept_lower = concept.lower()
        
        # Size heuristics
        if any(word in concept_lower for word in ['tiny', 'micro', 'mini']):
            features['size'] = ['tiny']
        elif any(word in concept_lower for word in ['small', 'little']):
            features['size'] = ['small']
        elif any(word in concept_lower for word in ['large', 'big', 'giant']):
            features['size'] = ['large']
        elif any(word in concept_lower for word in ['huge', 'massive']):
            features['size'] = ['huge']
        else:
            features['size'] = ['medium']
        
        # Color heuristics
        for color in self.visual_features['colors']:
            if color in concept_lower:
                features['color'] = [color]
                break
        
        if 'color' not in features:
            features['color'] = ['gray']  # Default
        
        # Shape heuristics
        if any(word in concept_lower for word in ['round', 'circle', 'sphere', 'ball']):
            features['shape'] = ['round']
        elif any(word in concept_lower for word in ['square', 'box', 'cube']):
            features['shape'] = ['square']
        else:
            features['shape'] = ['irregular']
        
        # Texture defaults
        features['texture'] = ['smooth']
        
        return features
    
    def _infer_auditory_features(self, concept: str, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Infer auditory features using cross-modal correspondence"""
        features = {}
        
        # First check if we have visual features to use cross-modal rules
        if context and 'visual_features' in context:
            visual = context['visual_features']
            
            # Size to frequency mapping
            if 'size' in visual:
                size = visual['size'][0] if isinstance(visual['size'], list) else visual['size']
                features['frequency'] = self.cross_modal_rules['size_to_frequency'].get(size, 'mid')
            
            # Texture to timbre mapping
            if 'texture' in visual:
                texture = visual['texture'][0] if isinstance(visual['texture'], list) else visual['texture']
                features['timbre'] = self.cross_modal_rules['texture_to_timbre'].get(texture, 'complex')
        
        # Apply concept-based heuristics
        concept_lower = concept.lower()
        
        # Amplitude heuristics
        if any(word in concept_lower for word in ['quiet', 'soft', 'whisper']):
            features['amplitude'] = 'quiet'
        elif any(word in concept_lower for word in ['loud', 'noisy', 'roar']):
            features['amplitude'] = 'loud'
        else:
            features['amplitude'] = 'moderate'
        
        # Rhythm heuristics
        if any(word in concept_lower for word in ['steady', 'constant', 'regular']):
            features['rhythm'] = 'steady'
        elif any(word in concept_lower for word in ['irregular', 'random', 'chaotic']):
            features['rhythm'] = 'irregular'
        else:
            features['rhythm'] = 'continuous'
        
        # Fill in defaults
        if 'frequency' not in features:
            features['frequency'] = 'mid'
        if 'timbre' not in features:
            features['timbre'] = 'complex'
        
        return features
    
    def _encode_visual_features(self, features: Dict[str, List[str]]) -> np.ndarray:
        """Encode visual features into a numerical vector"""
        vector = np.zeros(64)  # 64-dimensional visual feature vector
        
        # Encode color (first 8 dimensions)
        for i, color in enumerate(self.visual_features['colors']):
            if color in features.get('color', []):
                vector[i] = 1.0
        
        # Encode shape (next 6 dimensions)
        for i, shape in enumerate(self.visual_features['shapes']):
            if shape in features.get('shape', []):
                vector[8 + i] = 1.0
        
        # Encode texture (next 6 dimensions)
        for i, texture in enumerate(self.visual_features['textures']):
            if texture in features.get('texture', []):
                vector[14 + i] = 1.0
        
        # Encode size (next 5 dimensions)
        for i, size in enumerate(self.visual_features['sizes']):
            if size in features.get('size', []):
                vector[20 + i] = 1.0
        
        # Add some random variation in remaining dimensions
        vector[25:] = np.random.randn(39) * 0.1
        
        return vector
    
    def _encode_auditory_features(self, features: Dict[str, str]) -> np.ndarray:
        """Encode auditory features into a numerical vector"""
        vector = np.zeros(64)  # 64-dimensional auditory feature vector
        
        # Encode frequency (first 3 dimensions)
        freq_map = {'low': 0, 'mid': 1, 'high': 2}
        freq_idx = freq_map.get(features.get('frequency', 'mid'), 1)
        vector[freq_idx] = 1.0
        
        # Encode amplitude (next 3 dimensions)
        amp_map = {'quiet': 0, 'moderate': 1, 'loud': 2}
        amp_idx = amp_map.get(features.get('amplitude', 'moderate'), 1)
        vector[3 + amp_idx] = 1.0
        
        # Encode timbre (next 4 dimensions)
        timbre_map = {'pure': 0, 'harmonic': 1, 'noisy': 2, 'complex': 3}
        timbre_idx = timbre_map.get(features.get('timbre', 'complex'), 3)
        vector[6 + timbre_idx] = 1.0
        
        # Encode rhythm (next 4 dimensions)
        rhythm_map = {'steady': 0, 'irregular': 1, 'pulsing': 2, 'continuous': 3}
        rhythm_idx = rhythm_map.get(features.get('rhythm', 'steady'), 0)
        vector[10 + rhythm_idx] = 1.0
        
        # Add frequency spectrum simulation
        if features.get('frequency') == 'low':
            vector[14:24] = np.exp(-np.linspace(0, 5, 10))  # Low frequency emphasis
        elif features.get('frequency') == 'high':
            vector[14:24] = np.exp(-np.linspace(5, 0, 10))  # High frequency emphasis
        else:
            vector[14:24] = np.exp(-np.abs(np.linspace(-2.5, 2.5, 10)))  # Mid frequency
        
        # Add some random variation
        vector[24:] = np.random.randn(40) * 0.1
        
        return vector
    
    def _find_visual_associations(self, concept: str, features: Dict[str, List[str]]) -> List[str]:
        """Find concepts with similar visual features"""
        associations = []
        
        for other_concept, other_features in self.concept_visual_map.items():
            if other_concept == concept.lower():
                continue
            
            # Count matching features
            matches = 0
            total = 0
            
            for feature_type in ['color', 'shape', 'texture', 'size']:
                if feature_type in features and feature_type in other_features:
                    concept_values = features[feature_type]
                    other_values = other_features[feature_type]
                    
                    # Check for overlap
                    if any(v in other_values for v in concept_values):
                        matches += 1
                    total += 1
            
            if total > 0 and matches / total >= 0.5:
                associations.append(other_concept)
        
        return associations[:5]  # Return top 5 associations
    
    def _find_auditory_associations(self, concept: str, features: Dict[str, str]) -> List[str]:
        """Find concepts with similar auditory features"""
        associations = []
        
        for other_concept, other_features in self.concept_auditory_map.items():
            if other_concept == concept.lower():
                continue
            
            # Count matching features
            matches = 0
            
            for feature_type in ['frequency', 'amplitude', 'timbre', 'rhythm']:
                if features.get(feature_type) == other_features.get(feature_type):
                    matches += 1
            
            if matches >= 2:  # At least 2 matching features
                associations.append(other_concept)
        
        return associations[:5]  # Return top 5 associations
    
    def _compute_cross_modal_consistency(self, 
                                       visual_features: Dict[str, Any],
                                       auditory_features: Dict[str, Any]) -> float:
        """Compute consistency between visual and auditory features"""
        consistency_score = 0.0
        checks = 0
        
        # Check size-frequency correspondence
        if 'size' in visual_features and 'frequency' in auditory_features:
            visual_size = visual_features['size']
            expected_freq = self.cross_modal_rules['size_to_frequency'].get(visual_size)
            
            if expected_freq and expected_freq == auditory_features['frequency']:
                consistency_score += 1.0
            checks += 1
        
        # Check texture-timbre correspondence
        if 'texture' in visual_features and 'timbre' in auditory_features:
            visual_texture = visual_features['texture']
            expected_timbre = self.cross_modal_rules['texture_to_timbre'].get(visual_texture)
            
            if expected_timbre and expected_timbre == auditory_features['timbre']:
                consistency_score += 1.0
            checks += 1
        
        return consistency_score / max(checks, 1)