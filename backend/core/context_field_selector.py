"""
Context Field Selector
=====================

Provides granular control over which semantic fields are processed and included
in outputs during ingestion and processing phases. This optimizes performance
and allows users to focus on specific aspects of semantic analysis.
"""

from typing import Dict, List, Set, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FieldCategory(Enum):
    """Categories of semantic fields that can be selected/filtered"""
    SEMANTIC_STATE = "semantic_state"
    SYMBOLIC_STATE = "symbolic_state"
    EMBEDDING_VECTOR = "embedding_vector"
    METADATA = "metadata"
    ECHOFORM = "echoform"
    THERMODYNAMIC = "thermodynamic"
    CONTRADICTION = "contradiction"
    INSIGHT = "insight"
    TEMPORAL = "temporal"
    MULTIMODAL = "multimodal"


class ProcessingLevel(Enum):
    """Levels of processing intensity"""
    MINIMAL = "minimal"      # Basic semantic features only
    STANDARD = "standard"    # Standard processing
    ENHANCED = "enhanced"    # Full processing with all features
    CUSTOM = "custom"        # User-defined field selection


@dataclass
class ContextFieldConfig:
    """Configuration for context field selection"""
    
    # Processing level
    processing_level: ProcessingLevel = ProcessingLevel.STANDARD
    
    # Specific field categories to include/exclude
    included_categories: Set[FieldCategory] = field(default_factory=set)
    excluded_categories: Set[FieldCategory] = field(default_factory=set)
    
    # Specific field names to include/exclude
    included_fields: Set[str] = field(default_factory=set)
    excluded_fields: Set[str] = field(default_factory=set)
    
    # Output formatting options
    include_confidence_scores: bool = True
    include_processing_metadata: bool = True
    include_timestamps: bool = True
    
    # Performance optimization flags
    skip_expensive_calculations: bool = False
    limit_embedding_dimensions: Optional[int] = None
    max_semantic_features: Optional[int] = None
    
    # Context-specific settings
    domain_focus: Optional[str] = None  # e.g., "financial", "scientific", "creative"
    language_priority: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration and set defaults"""
        if self.processing_level != ProcessingLevel.CUSTOM:
            self._set_level_defaults()
        
        # Ensure included/excluded don't conflict
        conflicts = self.included_categories & self.excluded_categories
        if conflicts:
            logger.warning(f"Conflicting category selections removed: {conflicts}")
            self.excluded_categories -= conflicts
    
    def _set_level_defaults(self):
        """Set default field selections based on processing level"""
        if self.processing_level == ProcessingLevel.MINIMAL:
            self.included_categories = {
                FieldCategory.SEMANTIC_STATE,
                FieldCategory.METADATA
            }
            self.skip_expensive_calculations = True
            self.max_semantic_features = 50
            
        elif self.processing_level == ProcessingLevel.STANDARD:
            self.included_categories = {
                FieldCategory.SEMANTIC_STATE,
                FieldCategory.SYMBOLIC_STATE,
                FieldCategory.EMBEDDING_VECTOR,
                FieldCategory.METADATA,
                FieldCategory.THERMODYNAMIC
            }
            self.max_semantic_features = 200
            
        elif self.processing_level == ProcessingLevel.ENHANCED:
            self.included_categories = set(FieldCategory)  # Include all
            # No limits for enhanced processing


class ContextFieldSelector:
    """
    Main class for context field selection and filtering.
    Provides granular control over semantic processing and output generation.
    """
    
    def __init__(self, config: Optional[ContextFieldConfig] = None):
        self.config = config or ContextFieldConfig()
        self.processing_stats = {
            'fields_processed': 0,
            'fields_filtered': 0,
            'processing_time': 0.0,
            'last_update': datetime.now()
        }
        logger.info(f"Context Field Selector initialized with {self.config.processing_level.value} level")
    
    def should_process_category(self, category: FieldCategory) -> bool:
        """Determine if a field category should be processed"""
        # Check exclusions first
        if category in self.config.excluded_categories:
            return False
        
        # Check inclusions
        if self.config.included_categories:
            return category in self.config.included_categories
        
        # Default: process all categories not explicitly excluded
        return True
    
    def should_process_field(self, field_name: str) -> bool:
        """Determine if a specific field should be processed"""
        # Check exclusions first
        if field_name in self.config.excluded_fields:
            return False
        
        # Check inclusions
        if self.config.included_fields:
            return field_name in self.config.included_fields
        
        # Default: process all fields not explicitly excluded
        return True
    
    def filter_semantic_state(self, semantic_state: Dict[str, Any]) -> Dict[str, Any]:
        """Filter semantic state based on field selection"""
        if not self.should_process_category(FieldCategory.SEMANTIC_STATE):
            return {}
        
        filtered_state = {}
        processed_count = 0
        
        for field_name, value in semantic_state.items():
            if self.should_process_field(field_name):
                # Apply feature limits if configured
                if (self.config.max_semantic_features and 
                    processed_count >= self.config.max_semantic_features):
                    break
                
                filtered_state[field_name] = value
                processed_count += 1
            else:
                self.processing_stats['fields_filtered'] += 1
        
        self.processing_stats['fields_processed'] += processed_count
        return filtered_state
    
    def filter_embedding_vector(self, embedding: List[float]) -> List[float]:
        """Filter and potentially reduce embedding vector dimensions"""
        if not self.should_process_category(FieldCategory.EMBEDDING_VECTOR):
            return []
        
        if not embedding:
            return embedding
        
        # Apply dimension limits if configured
        if self.config.limit_embedding_dimensions:
            limit = min(self.config.limit_embedding_dimensions, len(embedding))
            return embedding[:limit]
        
        return embedding
    
    def filter_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Filter metadata based on configuration"""
        if not self.should_process_category(FieldCategory.METADATA):
            return {}
        
        filtered_metadata = {}
        
        for key, value in metadata.items():
            if self.should_process_field(key):
                filtered_metadata[key] = value
            else:
                self.processing_stats['fields_filtered'] += 1
        
        # Add processing metadata if requested
        if self.config.include_processing_metadata:
            filtered_metadata['processing_config'] = {
                'level': self.config.processing_level.value,
                'timestamp': datetime.now().isoformat(),
                'fields_processed': self.processing_stats['fields_processed'],
                'fields_filtered': self.processing_stats['fields_filtered']
            }
        
        return filtered_metadata
    
    def should_calculate_thermodynamics(self) -> bool:
        """Determine if thermodynamic calculations should be performed"""
        if self.config.skip_expensive_calculations:
            return False
        
        return self.should_process_category(FieldCategory.THERMODYNAMIC)
    
    def should_detect_contradictions(self) -> bool:
        """Determine if contradiction detection should be performed"""
        if self.config.skip_expensive_calculations:
            return False
        
        return self.should_process_category(FieldCategory.CONTRADICTION)
    
    def should_generate_insights(self) -> bool:
        """Determine if insight generation should be performed"""
        return self.should_process_category(FieldCategory.INSIGHT)
    
    def should_process_multimodal(self) -> bool:
        """Determine if multimodal processing should be performed"""
        if self.config.skip_expensive_calculations:
            return False
        
        return self.should_process_category(FieldCategory.MULTIMODAL)
    
    def apply_domain_focus(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply domain-specific filtering and enhancement"""
        if not self.config.domain_focus:
            return data
        
        domain = self.config.domain_focus.lower()
        
        # Domain-specific field prioritization
        domain_priorities = {
            'financial': ['market_', 'price_', 'volatility_', 'risk_'],
            'scientific': ['hypothesis_', 'evidence_', 'theory_', 'experiment_'],
            'creative': ['narrative_', 'aesthetic_', 'emotional_', 'artistic_'],
            'technical': ['system_', 'performance_', 'architecture_', 'optimization_']
        }
        
        if domain in domain_priorities:
            priority_prefixes = domain_priorities[domain]
            
            # Boost relevance of domain-specific fields
            for key in list(data.keys()):
                if any(key.startswith(prefix) for prefix in priority_prefixes):
                    # Mark as high priority for processing
                    if isinstance(data[key], (int, float)):
                        data[f"{key}_priority"] = data[key] * 1.2
        
        return data
    
    def create_filtered_output(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create filtered output based on configuration"""
        start_time = datetime.now()
        
        filtered_output = {}
        
        # Filter each category
        if 'semantic_state' in raw_data:
            filtered_output['semantic_state'] = self.filter_semantic_state(
                raw_data['semantic_state']
            )
        
        if 'symbolic_state' in raw_data and self.should_process_category(FieldCategory.SYMBOLIC_STATE):
            filtered_output['symbolic_state'] = raw_data['symbolic_state']
        
        if 'embedding_vector' in raw_data:
            filtered_output['embedding_vector'] = self.filter_embedding_vector(
                raw_data['embedding_vector']
            )
        
        if 'metadata' in raw_data:
            filtered_output['metadata'] = self.filter_metadata(raw_data['metadata'])
        
        # Apply domain focus if configured
        if self.config.domain_focus:
            filtered_output = self.apply_domain_focus(filtered_output)
        
        # Add confidence scores if requested
        if self.config.include_confidence_scores:
            filtered_output['confidence'] = self._calculate_confidence(filtered_output)
        
        # Add timestamp if requested
        if self.config.include_timestamps:
            filtered_output['processed_at'] = datetime.now().isoformat()
        
        # Update processing statistics
        processing_time = (datetime.now() - start_time).total_seconds()
        self.processing_stats['processing_time'] += processing_time
        self.processing_stats['last_update'] = datetime.now()
        
        return filtered_output
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness and quality"""
        total_possible = len(FieldCategory)
        categories_present = 0
        
        for category in FieldCategory:
            category_key = category.value
            if category_key in data and data[category_key]:
                categories_present += 1
        
        base_confidence = categories_present / total_possible
        
        # Adjust based on processing level
        level_multipliers = {
            ProcessingLevel.MINIMAL: 0.7,
            ProcessingLevel.STANDARD: 0.9,
            ProcessingLevel.ENHANCED: 1.0,
            ProcessingLevel.CUSTOM: 0.8
        }
        
        multiplier = level_multipliers.get(self.config.processing_level, 0.8)
        return min(1.0, base_confidence * multiplier)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing statistics"""
        return {
            'config': {
                'processing_level': self.config.processing_level.value,
                'included_categories': [cat.value for cat in self.config.included_categories],
                'excluded_categories': [cat.value for cat in self.config.excluded_categories],
                'domain_focus': self.config.domain_focus,
                'skip_expensive_calculations': self.config.skip_expensive_calculations
            },
            'statistics': self.processing_stats.copy(),
            'performance': {
                'avg_processing_time': self.processing_stats['processing_time'] / max(1, self.processing_stats['fields_processed']),
                'filter_efficiency': self.processing_stats['fields_filtered'] / max(1, self.processing_stats['fields_processed'] + self.processing_stats['fields_filtered'])
            }
        }


# Convenience functions for common configurations
def create_minimal_selector() -> ContextFieldSelector:
    """Create selector for minimal processing (fastest)"""
    config = ContextFieldConfig(processing_level=ProcessingLevel.MINIMAL)
    return ContextFieldSelector(config)


def create_standard_selector() -> ContextFieldSelector:
    """Create selector for standard processing (balanced)"""
    config = ContextFieldConfig(processing_level=ProcessingLevel.STANDARD)
    return ContextFieldSelector(config)


def create_enhanced_selector() -> ContextFieldSelector:
    """Create selector for enhanced processing (most comprehensive)"""
    config = ContextFieldConfig(processing_level=ProcessingLevel.ENHANCED)
    return ContextFieldSelector(config)


def create_domain_selector(domain: str) -> ContextFieldSelector:
    """Create selector optimized for specific domain"""
    config = ContextFieldConfig(
        processing_level=ProcessingLevel.STANDARD,
        domain_focus=domain
    )
    return ContextFieldSelector(config)


def create_performance_selector() -> ContextFieldSelector:
    """Create selector optimized for performance"""
    config = ContextFieldConfig(
        processing_level=ProcessingLevel.MINIMAL,
        skip_expensive_calculations=True,
        max_semantic_features=25,
        limit_embedding_dimensions=128,
        include_processing_metadata=False
    )
    return ContextFieldSelector(config) 