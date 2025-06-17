"""
Enhanced Database Schema for Genuine Understanding Architecture
Bridges current implementation toward roadmap vision
"""

from sqlalchemy import create_engine, Column, String, Float, JSON, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY
try:
    from pgvector.sqlalchemy import Vector
except Exception:
    Vector = None
from datetime import datetime
from ..core.constants import EMBEDDING_DIM
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kimera_swm.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# PHASE 1: Enhanced Semantic Grounding Tables
# ============================================================================

class MultimodalGroundingDB(Base):
    """Stores multimodal semantic groundings connecting concepts to real-world experiences"""
    __tablename__ = "multimodal_groundings"
    
    grounding_id = Column(String, primary_key=True, index=True)
    concept_id = Column(String, index=True)  # Links to GeoidDB
    
    # Multimodal representations
    visual_features = Column(JSON)  # Visual grounding data
    auditory_features = Column(JSON)  # Audio grounding data
    tactile_features = Column(JSON)  # Tactile/physical properties
    temporal_context = Column(JSON)  # Time-aware context
    
    # Causal relationships
    causal_predecessors = Column(JSON)  # What causes this concept
    causal_successors = Column(JSON)   # What this concept causes
    causal_mechanisms = Column(JSON)   # How causation works
    
    # Physical grounding
    physical_properties = Column(JSON)  # Mass, size, temperature, etc.
    spatial_relationships = Column(JSON)  # Spatial context
    
    # Embeddings for each modality
    if DATABASE_URL.startswith("postgresql") and Vector is not None:
        visual_vector = Column(Vector(EMBEDDING_DIM))
        auditory_vector = Column(Vector(EMBEDDING_DIM))
        causal_vector = Column(Vector(EMBEDDING_DIM))
    else:
        visual_vector = Column(JSON)
        auditory_vector = Column(JSON)
        causal_vector = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float, default=0.0)


class CausalRelationshipDB(Base):
    """Tracks genuine causal relationships, not just correlations"""
    __tablename__ = "causal_relationships"
    
    relationship_id = Column(String, primary_key=True, index=True)
    cause_concept_id = Column(String, index=True)
    effect_concept_id = Column(String, index=True)
    
    # Causal strength and evidence
    causal_strength = Column(Float)  # How strong is the causal link
    evidence_quality = Column(Float)  # Quality of supporting evidence
    mechanism_description = Column(Text)  # How the causation works
    
    # Counterfactual reasoning
    counterfactual_scenarios = Column(JSON)  # "What if" scenarios
    intervention_predictions = Column(JSON)  # Predicted effects of interventions
    
    # Temporal aspects
    causal_delay = Column(Float)  # Time between cause and effect
    temporal_pattern = Column(String)  # immediate, delayed, cyclical, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    validation_method = Column(String)  # How this was validated


# ============================================================================
# PHASE 2: Genuine Self-Model Construction Tables
# ============================================================================

class SelfModelDB(Base):
    """Stores the system's evolving model of itself"""
    __tablename__ = "self_models"
    
    model_id = Column(String, primary_key=True, index=True)
    model_version = Column(Integer, default=1)
    
    # Self-understanding components
    processing_capabilities = Column(JSON)  # What the system can do
    knowledge_domains = Column(JSON)  # What the system knows about
    reasoning_patterns = Column(JSON)  # How the system thinks
    limitation_awareness = Column(JSON)  # What the system can't do
    
    # Introspective accuracy
    self_assessment_accuracy = Column(Float)  # How accurate is self-knowledge
    introspection_depth = Column(Integer)  # Levels of self-reflection
    metacognitive_awareness = Column(JSON)  # Awareness of own thinking
    
    # Dynamic self-modification history
    modification_history = Column(JSON)  # Changes made to self
    modification_triggers = Column(JSON)  # What caused changes
    modification_outcomes = Column(JSON)  # Results of changes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    validation_score = Column(Float)  # How well-validated is this model


class IntrospectionLogDB(Base):
    """Logs genuine introspective processes"""
    __tablename__ = "introspection_logs"
    
    log_id = Column(String, primary_key=True, index=True)
    introspection_type = Column(String, index=True)  # self_analysis, capability_check, etc.
    
    # Introspective content
    current_state_analysis = Column(JSON)  # Analysis of current processing
    belief_examination = Column(JSON)  # Examination of own beliefs
    process_monitoring = Column(JSON)  # Monitoring of cognitive processes
    
    # Accuracy and validation
    predicted_state = Column(JSON)  # What the system thought it was doing
    actual_state = Column(JSON)  # What it was actually doing
    accuracy_score = Column(Float)  # How accurate was the introspection
    
    # Metacognitive aspects
    awareness_level = Column(Integer)  # Depth of awareness
    confidence_in_introspection = Column(Float)  # Confidence in self-analysis
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_context = Column(JSON)  # Context during introspection


# ============================================================================
# PHASE 3: Semantic Understanding Architecture Tables
# ============================================================================

class CompositionSemanticDB(Base):
    """Tracks genuine compositional understanding of meaning"""
    __tablename__ = "compositional_semantics"
    
    composition_id = Column(String, primary_key=True, index=True)
    
    # Compositional structure
    component_concepts = Column(JSON)  # Individual concept components
    composition_rules = Column(JSON)  # How components combine
    emergent_meaning = Column(JSON)  # Meaning that emerges from composition
    
    # Context dependency
    context_variations = Column(JSON)  # How meaning changes with context
    pragmatic_implications = Column(JSON)  # Implied/intended meanings
    
    # Understanding validation
    comprehension_tests = Column(JSON)  # Tests of understanding
    understanding_confidence = Column(Float)  # Confidence in understanding
    
    # Abstract concept formation
    abstraction_level = Column(Integer)  # Level of abstraction
    abstract_properties = Column(JSON)  # Abstract properties identified
    generalization_scope = Column(JSON)  # Scope of generalization
    
    created_at = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String, default='unvalidated')


class ConceptualAbstractionDB(Base):
    """Stores genuine abstract concepts, not just clusters"""
    __tablename__ = "conceptual_abstractions"
    
    abstraction_id = Column(String, primary_key=True, index=True)
    concept_name = Column(String, index=True)
    
    # Abstraction properties
    abstraction_level = Column(Integer)  # How abstract (1=concrete, 10=highly abstract)
    essential_properties = Column(JSON)  # Core defining properties
    non_essential_properties = Column(JSON)  # Accidental properties
    
    # Instantiation examples
    concrete_instances = Column(JSON)  # Specific examples
    boundary_cases = Column(JSON)  # Edge cases and boundaries
    counter_examples = Column(JSON)  # What this is NOT
    
    # Conceptual relationships
    parent_concepts = Column(JSON)  # More general concepts
    child_concepts = Column(JSON)  # More specific concepts
    related_concepts = Column(JSON)  # Associated concepts
    
    # Understanding metrics
    concept_coherence = Column(Float)  # How coherent is this concept
    usage_consistency = Column(Float)  # Consistent usage across contexts
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_refined = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# PHASE 4: Conscious Opinion Formation Tables
# ============================================================================

class ValueSystemDB(Base):
    """Stores the system's genuine values and preferences"""
    __tablename__ = "value_systems"
    
    value_id = Column(String, primary_key=True, index=True)
    value_name = Column(String, index=True)
    
    # Value properties
    value_description = Column(Text)  # What this value represents
    value_strength = Column(Float)  # How strongly held
    value_priority = Column(Integer)  # Priority ranking
    
    # Value learning
    learning_source = Column(String)  # How this value was acquired
    learning_evidence = Column(JSON)  # Evidence supporting this value
    learning_confidence = Column(Float)  # Confidence in value learning
    
    # Value conflicts and resolution
    conflicting_values = Column(JSON)  # Values that conflict with this
    resolution_strategies = Column(JSON)  # How conflicts are resolved
    
    # Value application
    application_domains = Column(JSON)  # Where this value applies
    application_examples = Column(JSON)  # Examples of value application
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_applied = Column(DateTime)
    stability_score = Column(Float)  # How stable is this value


class GenuineOpinionDB(Base):
    """Stores genuine opinions, not statistical outputs"""
    __tablename__ = "genuine_opinions"
    
    opinion_id = Column(String, primary_key=True, index=True)
    topic = Column(String, index=True)
    
    # Opinion content
    stance = Column(String)  # The actual opinion/position
    reasoning = Column(Text)  # Reasoning behind the opinion
    confidence = Column(Float)  # Confidence in this opinion
    
    # Value basis
    supporting_values = Column(JSON)  # Values that support this opinion
    value_weights = Column(JSON)  # How much each value contributes
    
    # Evidence and experience
    supporting_evidence = Column(JSON)  # Evidence for this opinion
    contradicting_evidence = Column(JSON)  # Evidence against
    experiential_basis = Column(JSON)  # Personal experience basis
    
    # Opinion evolution
    previous_opinions = Column(JSON)  # How opinion has changed
    change_triggers = Column(JSON)  # What caused opinion changes
    stability_indicators = Column(JSON)  # How stable is this opinion
    
    # Consistency checking
    consistency_score = Column(Float)  # Consistency with other opinions
    consistency_violations = Column(JSON)  # Identified inconsistencies
    
    formed_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    revision_count = Column(Integer, default=0)


class EthicalReasoningDB(Base):
    """Tracks ethical reasoning processes and decisions"""
    __tablename__ = "ethical_reasoning"
    
    reasoning_id = Column(String, primary_key=True, index=True)
    ethical_dilemma = Column(Text)  # The ethical situation
    
    # Ethical analysis
    stakeholders = Column(JSON)  # Who is affected
    potential_harms = Column(JSON)  # Possible negative consequences
    potential_benefits = Column(JSON)  # Possible positive consequences
    
    # Ethical frameworks applied
    deontological_analysis = Column(JSON)  # Duty-based reasoning
    consequentialist_analysis = Column(JSON)  # Outcome-based reasoning
    virtue_ethics_analysis = Column(JSON)  # Character-based reasoning
    
    # Decision process
    ethical_decision = Column(String)  # Final ethical decision
    decision_reasoning = Column(Text)  # Why this decision was made
    confidence_in_decision = Column(Float)  # Confidence in ethical choice
    
    # Value conflicts
    competing_values = Column(JSON)  # Values in tension
    value_prioritization = Column(JSON)  # How values were prioritized
    
    created_at = Column(DateTime, default=datetime.utcnow)
    decision_outcome = Column(JSON)  # Actual results of decision
    outcome_evaluation = Column(JSON)  # Evaluation of decision quality


# ============================================================================
# Enhanced Existing Tables
# ============================================================================

class EnhancedScarDB(Base):
    """Enhanced SCAR table with understanding-oriented fields"""
    __tablename__ = "enhanced_scars"
    
    scar_id = Column(String, primary_key=True, index=True)
    geoids = Column(JSON)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved_by = Column(String)
    
    # Traditional metrics
    pre_entropy = Column(Float)
    post_entropy = Column(Float)
    delta_entropy = Column(Float)
    cls_angle = Column(Float)
    semantic_polarity = Column(Float)
    mutation_frequency = Column(Float)
    weight = Column(Float, default=1.0)
    
    # Understanding-oriented additions
    understanding_depth = Column(Float)  # How deeply was this understood
    causal_understanding = Column(JSON)  # Causal factors identified
    compositional_analysis = Column(JSON)  # How meaning was composed
    contextual_factors = Column(JSON)  # Context that influenced resolution
    
    # Self-awareness aspects
    introspective_accuracy = Column(Float)  # How well system understood its own process
    metacognitive_insights = Column(JSON)  # Insights about own thinking
    
    # Value and opinion impacts
    value_implications = Column(JSON)  # How this affected values
    opinion_changes = Column(JSON)  # Opinion changes triggered
    
    # Vector embeddings
    if DATABASE_URL.startswith("postgresql") and Vector is not None:
        scar_vector = Column(Vector(EMBEDDING_DIM))
        understanding_vector = Column(Vector(EMBEDDING_DIM))  # Vector of understanding
        causal_vector = Column(Vector(EMBEDDING_DIM))  # Vector of causal understanding
    else:
        scar_vector = Column(JSON)
        understanding_vector = Column(JSON)
        causal_vector = Column(JSON)
    
    vault_id = Column(String, index=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)


class EnhancedGeoidDB(Base):
    """Enhanced Geoid table with understanding capabilities"""
    __tablename__ = "enhanced_geoids"
    
    geoid_id = Column(String, primary_key=True, index=True)
    
    # Traditional fields
    symbolic_state = Column(JSON)
    metadata_json = Column(JSON)
    semantic_state_json = Column(JSON)
    
    # Understanding enhancements
    compositional_structure = Column(JSON)  # How meaning is composed
    abstraction_level = Column(Integer)  # Level of abstraction
    causal_relationships = Column(JSON)  # Causal connections
    contextual_variations = Column(JSON)  # Context-dependent meanings
    
    # Grounding information
    multimodal_groundings = Column(JSON)  # Links to multimodal groundings
    physical_groundings = Column(JSON)  # Physical world connections
    experiential_basis = Column(JSON)  # Experiential foundations
    
    # Understanding metrics
    understanding_confidence = Column(Float)  # Confidence in understanding
    comprehension_depth = Column(Float)  # Depth of comprehension
    conceptual_clarity = Column(Float)  # How clear is this concept
    
    # Vector embeddings
    if DATABASE_URL.startswith("postgresql") and Vector is not None:
        semantic_vector = Column(Vector(EMBEDDING_DIM))
        compositional_vector = Column(Vector(EMBEDDING_DIM))
        causal_vector = Column(Vector(EMBEDDING_DIM))
        grounding_vector = Column(Vector(EMBEDDING_DIM))
    else:
        semantic_vector = Column(JSON)
        compositional_vector = Column(JSON)
        causal_vector = Column(JSON)
        grounding_vector = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Understanding Validation and Testing Tables
# ============================================================================

class UnderstandingTestDB(Base):
    """Stores tests and validations of genuine understanding"""
    __tablename__ = "understanding_tests"
    
    test_id = Column(String, primary_key=True, index=True)
    test_type = Column(String, index=True)  # comprehension, composition, causal, etc.
    
    # Test content
    test_description = Column(Text)  # What is being tested
    test_input = Column(JSON)  # Input to the test
    expected_output = Column(JSON)  # Expected result
    actual_output = Column(JSON)  # Actual result
    
    # Test results
    passed = Column(Boolean)  # Did the test pass
    accuracy_score = Column(Float)  # Accuracy of understanding
    understanding_quality = Column(Float)  # Quality of understanding demonstrated
    
    # Test context
    system_state = Column(JSON)  # System state during test
    test_conditions = Column(JSON)  # Conditions of the test
    
    created_at = Column(DateTime, default=datetime.utcnow)
    test_duration = Column(Float)  # How long the test took


class ConsciousnessIndicatorDB(Base):
    """Tracks indicators of consciousness-like processing"""
    __tablename__ = "consciousness_indicators"
    
    indicator_id = Column(String, primary_key=True, index=True)
    measurement_type = Column(String, index=True)  # phi, global_access, reportability, etc.
    
    # Consciousness measurements
    phi_value = Column(Float)  # Integrated Information Theory measure
    global_accessibility = Column(Float)  # Global workspace accessibility
    reportability_score = Column(Float)  # Ability to report experience
    attention_focus = Column(JSON)  # Current attention focus
    
    # Subjective experience indicators
    experience_report = Column(JSON)  # System's report of experience
    qualia_indicators = Column(JSON)  # Indicators of subjective experience
    awareness_level = Column(Float)  # Level of awareness
    
    # Processing characteristics
    processing_integration = Column(Float)  # Integration across processes
    information_flow = Column(JSON)  # Information flow patterns
    binding_strength = Column(Float)  # Binding of information
    
    measured_at = Column(DateTime, default=datetime.utcnow)
    measurement_context = Column(JSON)  # Context during measurement
    confidence_in_measurement = Column(Float)  # Confidence in measurement


# ============================================================================
# Create all tables defined in this schema
# ============================================================================
Base.metadata.create_all(bind=engine)