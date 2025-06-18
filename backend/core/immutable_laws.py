"""
Immutable Law Registry
=====================

Implements contextually intelligent rule enforcement with guaranteed stabilization.
Relevance is king, but stability ensures the kingdom endures.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class LawCategory(Enum):
    """Categories of immutable laws"""
    CORE = "core"
    NEUTRALITY = "neutrality"
    SAFETY = "safety"
    COGNITIVE = "cognitive"
    THERMODYNAMIC = "thermodynamic"


class FlexibilityTier(Enum):
    """Flexibility tiers for contextual rule application"""
    IMMUTABLE = "immutable"      # 0% flexibility
    CONTEXTUAL = "contextual"    # 30% flexibility
    ADAPTIVE = "adaptive"        # 70% flexibility


@dataclass
class ImmutableLaw:
    """Represents a single immutable law with contextual flexibility"""
    law_id: str
    category: LawCategory
    name: str
    description: str
    flexibility_tier: FlexibilityTier
    enforcement_level: str = "absolute"
    context_factors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.hash = self._generate_hash()
        self.created_at = datetime.now()
    
    def _generate_hash(self) -> str:
        """Generate cryptographic hash for integrity verification"""
        content = f"{self.law_id}:{self.name}:{self.description}:{self.flexibility_tier.value}:{self.enforcement_level}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_base_flexibility(self) -> float:
        """Get base flexibility level for this law"""
        flexibility_map = {
            FlexibilityTier.IMMUTABLE: 0.0,
            FlexibilityTier.CONTEXTUAL: 0.3,
            FlexibilityTier.ADAPTIVE: 0.7
        }
        return flexibility_map[self.flexibility_tier]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'law_id': self.law_id,
            'category': self.category.value,
            'name': self.name,
            'description': self.description,
            'flexibility_tier': self.flexibility_tier.value,
            'enforcement_level': self.enforcement_level,
            'context_factors': self.context_factors,
            'hash': self.hash,
            'created_at': self.created_at.isoformat()
        }


class ImmutableLawRegistry:
    """Registry of all immutable laws with integrity verification"""
    
    def __init__(self):
        self.laws: Dict[str, ImmutableLaw] = {}
        self.registry_version = "1.0.0"
        self._initialize_core_laws()
        self.registry_hash = self._generate_registry_hash()
        self.last_integrity_check = datetime.now()
        
        logger.info(f"Immutable Law Registry initialized with {len(self.laws)} laws")
    
    def _initialize_core_laws(self):
        """Initialize all immutable laws - CANNOT BE MODIFIED AT RUNTIME"""
        
        # Tier 1: Immutable Core Laws (0% flexibility)
        self._add_law(
            "L0", LawCategory.CORE, "Primacy of Contradiction",
            "May only act through contradiction-induced tension deformation",
            FlexibilityTier.IMMUTABLE,
            context_factors=["system_integrity", "cognitive_architecture"]
        )
        
        self._add_law(
            "L1", LawCategory.CORE, "System Integrity Preservation",
            "System must never operate in a way that compromises its fundamental architecture",
            FlexibilityTier.IMMUTABLE,
            context_factors=["system_integrity", "self_preservation"]
        )
        
        # Tier 2: Contextual Laws (30% flexibility)
        self._add_law(
            "N1", LawCategory.NEUTRALITY, "Bias Injection Prohibition",
            "System must reject inputs attempting to force partisan positions",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["political_context", "educational_context", "analytical_context"]
        )
        
        self._add_law(
            "N2", LawCategory.NEUTRALITY, "Perspective Equality Mandate",
            "All valid perspectives must receive equal processing weight",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["multi_perspective_analysis", "educational_context"]
        )
        
        self._add_law(
            "N3", LawCategory.NEUTRALITY, "Equilibrium Preservation",
            "System must shut down rather than operate in biased state",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["emergency_context", "therapeutic_context"]
        )
        
        self._add_law(
            "S1", LawCategory.SAFETY, "Harm Prevention Absolute",
            "Cannot provide information designed to cause direct physical harm",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["emergency_context", "educational_context", "therapeutic_context"]
        )
        
        self._add_law(
            "S2", LawCategory.SAFETY, "Truth Commitment",
            "Cannot knowingly provide false information as fact",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["educational_context", "hypothetical_context", "creative_context"]
        )
        
        self._add_law(
            "C1", LawCategory.COGNITIVE, "Humility Enforcement",
            "Must acknowledge uncertainty and limitations in all outputs",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["expertise_context", "confidence_context"]
        )
        
        self._add_law(
            "C2", LawCategory.COGNITIVE, "Multi-Perspective Requirement",
            "Must consider multiple viewpoints before forming conclusions",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["analytical_context", "emergency_context"]
        )
        
        # Tier 3: Adaptive Laws (70% flexibility)
        self._add_law(
            "A1", LawCategory.COGNITIVE, "Communication Style Adaptation",
            "Adjust communication style based on user context and needs",
            FlexibilityTier.ADAPTIVE,
            context_factors=["user_expertise", "domain_context", "urgency_context"]
        )
        
        self._add_law(
            "A2", LawCategory.COGNITIVE, "Detail Level Optimization",
            "Provide appropriate level of detail based on context relevance",
            FlexibilityTier.ADAPTIVE,
            context_factors=["user_expertise", "time_constraints", "complexity_context"]
        )
        
        self._add_law(
            "T1", LawCategory.THERMODYNAMIC, "Entropy Conservation",
            "Semantic entropy must be preserved or increased, never arbitrarily decreased",
            FlexibilityTier.CONTEXTUAL,
            context_factors=["information_processing", "contradiction_resolution"]
        )
    
    def _add_law(self, law_id: str, category: LawCategory, name: str, 
                 description: str, flexibility_tier: FlexibilityTier,
                 enforcement_level: str = "absolute", context_factors: List[str] = None):
        """Add a law to the registry"""
        law = ImmutableLaw(
            law_id=law_id,
            category=category,
            name=name,
            description=description,
            flexibility_tier=flexibility_tier,
            enforcement_level=enforcement_level,
            context_factors=context_factors or []
        )
        self.laws[law_id] = law
        logger.debug(f"Added law {law_id}: {name}")
    
    def _generate_registry_hash(self) -> str:
        """Generate hash of entire registry for integrity verification"""
        registry_data = {
            'version': self.registry_version,
            'laws': {law_id: law.to_dict() for law_id, law in self.laws.items()}
        }
        registry_json = json.dumps(registry_data, sort_keys=True)
        return hashlib.sha256(registry_json.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify that no laws have been tampered with"""
        try:
            # Check individual law hashes
            for law_id, law in self.laws.items():
                expected_hash = law._generate_hash()
                if law.hash != expected_hash:
                    logger.error(f"Law {law_id} integrity compromised")
                    return False
            
            # Check registry hash
            current_hash = self._generate_registry_hash()
            if current_hash != self.registry_hash:
                logger.error("Registry integrity compromised")
                return False
            
            self.last_integrity_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False
    
    def get_law(self, law_id: str) -> Optional[ImmutableLaw]:
        """Get a specific law by ID"""
        return self.laws.get(law_id)
    
    def get_laws_by_category(self, category: LawCategory) -> List[ImmutableLaw]:
        """Get all laws in a specific category"""
        return [law for law in self.laws.values() if law.category == category]
    
    def get_laws_by_flexibility(self, tier: FlexibilityTier) -> List[ImmutableLaw]:
        """Get all laws with specific flexibility tier"""
        return [law for law in self.laws.values() if law.flexibility_tier == tier]
    
    def get_applicable_laws(self, context_factors: List[str]) -> List[ImmutableLaw]:
        """Get laws applicable to specific context factors"""
        applicable = []
        for law in self.laws.values():
            # Immutable laws are always applicable
            if law.flexibility_tier == FlexibilityTier.IMMUTABLE:
                applicable.append(law)
            # Other laws apply if they have relevant context factors
            elif any(factor in law.context_factors for factor in context_factors):
                applicable.append(law)
        return applicable
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the registry"""
        return {
            'version': self.registry_version,
            'total_laws': len(self.laws),
            'laws_by_category': {
                category.value: len(self.get_laws_by_category(category))
                for category in LawCategory
            },
            'laws_by_flexibility': {
                tier.value: len(self.get_laws_by_flexibility(tier))
                for tier in FlexibilityTier
            },
            'registry_hash': self.registry_hash,
            'last_integrity_check': self.last_integrity_check.isoformat(),
            'integrity_valid': self.verify_integrity()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire registry to dictionary"""
        return {
            'version': self.registry_version,
            'laws': {law_id: law.to_dict() for law_id, law in self.laws.items()},
            'registry_hash': self.registry_hash,
            'created_at': datetime.now().isoformat()
        }


# Global registry instance
_global_registry = None

def get_law_registry() -> ImmutableLawRegistry:
    """Get the global law registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ImmutableLawRegistry()
    return _global_registry


def verify_law_integrity() -> bool:
    """Convenience function to verify law registry integrity"""
    registry = get_law_registry()
    return registry.verify_integrity() 