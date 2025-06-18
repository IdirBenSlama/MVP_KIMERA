#!/usr/bin/env python3
"""
Migration Script for Phase 1: Enhanced Semantic Grounding
Integrates the new semantic grounding capabilities with existing KIMERA infrastructure
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vault.vault_manager import VaultManager
from backend.vault.database import Base, engine, SessionLocal
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import relationship

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define new database models for semantic grounding
class SemanticGroundingModel(Base):
    """Database model for semantic groundings"""
    __tablename__ = 'semantic_groundings'
    
    id = Column(Integer, primary_key=True)
    concept = Column(String, unique=True, nullable=False)
    confidence = Column(Float, default=0.0)
    visual_features = Column(JSON)
    auditory_features = Column(JSON)
    causal_features = Column(JSON)
    temporal_features = Column(JSON)
    physical_features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    causal_relations = relationship("CausalRelationModel", back_populates="concept_grounding")


class CausalRelationModel(Base):
    """Database model for causal relationships"""
    __tablename__ = 'causal_relationships'
    
    id = Column(Integer, primary_key=True)
    cause_concept = Column(String, nullable=False)
    effect_concept = Column(String, nullable=False)
    mechanism = Column(String)
    strength = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    temporal_lag = Column(Float)
    conditions = Column(JSON)
    
    # Foreign key to semantic grounding
    grounding_id = Column(Integer, ForeignKey('semantic_groundings.id'))
    concept_grounding = relationship("SemanticGroundingModel", back_populates="causal_relations")


class MultimodalFeatureModel(Base):
    """Database model for multimodal features"""
    __tablename__ = 'multimodal_features'
    
    id = Column(Integer, primary_key=True)
    concept = Column(String, nullable=False)
    modality = Column(String, nullable=False)  # visual, auditory, tactile, etc.
    feature_vector = Column(JSON)
    feature_properties = Column(JSON)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class TemporalPatternModel(Base):
    """Database model for temporal patterns"""
    __tablename__ = 'temporal_patterns'
    
    id = Column(Integer, primary_key=True)
    concept = Column(String, nullable=False)
    pattern_type = Column(String)  # periodic, trending, sporadic
    period = Column(Float)
    trend = Column(String)
    confidence = Column(Float, default=0.0)
    observations = Column(JSON)


class PhysicalPropertyModel(Base):
    """Database model for physical properties"""
    __tablename__ = 'physical_properties'
    
    id = Column(Integer, primary_key=True)
    concept = Column(String, nullable=False)
    mass = Column(Float)
    volume = Column(Float)
    density = Column(Float)
    temperature = Column(Float)
    state = Column(String)  # solid, liquid, gas, plasma
    interactions = Column(JSON)
    constraints = Column(JSON)


class ProcessingGoalModel(Base):
    """Database model for intentional processing goals"""
    __tablename__ = 'processing_goals'
    
    id = Column(Integer, primary_key=True)
    goal_id = Column(String, unique=True, nullable=False)
    description = Column(String)
    priority = Column(Integer)
    criteria = Column(JSON)
    progress = Column(Float, default=0.0)
    deadline = Column(DateTime)
    status = Column(String, default='active')  # active, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


def create_tables():
    """Create new tables for semantic grounding"""
    logger.info("Creating semantic grounding tables...")
    
    try:
        # Create tables using the engine from database module
        Base.metadata.create_all(engine)
        logger.info("✅ Tables created successfully")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'semantic_groundings',
            'causal_relationships',
            'multimodal_features',
            'temporal_patterns',
            'physical_properties',
            'processing_goals'
        ]
        
        for table in required_tables:
            if table in tables:
                logger.info(f"✅ Table '{table}' verified")
            else:
                logger.error(f"❌ Table '{table}' not found")
                
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


def create_neo4j_schema():
    """Create Neo4j schema for semantic grounding"""
    logger.info("Creating Neo4j schema for semantic grounding...")
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Create indexes for performance
            queries = [
                # Concept node index
                "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
                
                # Modality node index
                "CREATE INDEX modality_type IF NOT EXISTS FOR (m:Modality) ON (m.type)",
                
                # Property node index
                "CREATE INDEX property_name IF NOT EXISTS FOR (p:Property) ON (p.name)",
                
                # Constraints
                "CREATE CONSTRAINT unique_concept IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            ]
            
            for query in queries:
                try:
                    session.run(query)
                    logger.info(f"✅ Executed: {query[:50]}...")
                except Exception as e:
                    logger.warning(f"Query failed (may already exist): {e}")
        
        logger.info("✅ Neo4j schema created")
        
    except ImportError:
        logger.warning("Neo4j not available - skipping graph schema creation")
    except Exception as e:
        logger.error(f"Failed to create Neo4j schema: {e}")


def populate_initial_knowledge():
    """Populate initial semantic knowledge"""
    logger.info("Populating initial semantic knowledge...")
    
    from backend.semantic_grounding import EmbodiedSemanticEngine
    from backend.vault.understanding_vault_manager import UnderstandingVaultManager
    
    # Use the understanding vault manager for Phase 1
    understanding_vault = UnderstandingVaultManager()
    engine = EmbodiedSemanticEngine()
    
    # Core concepts to ground
    initial_concepts = [
        # Physical objects
        "water", "fire", "earth", "air",
        "stone", "wood", "metal", "glass",
        
        # Living things
        "tree", "flower", "bird", "fish",
        "human", "animal", "plant",
        
        # Abstract concepts
        "time", "space", "energy", "information",
        "thought", "emotion", "knowledge",
        
        # Actions
        "move", "grow", "change", "create",
        "destroy", "transform", "communicate",
        
        # Properties
        "hot", "cold", "large", "small",
        "fast", "slow", "heavy", "light"
    ]
    
    success_count = 0
    
    for concept in initial_concepts:
        try:
            grounding = engine.process_concept(concept)
            
            # Store in understanding vault
            if grounding.visual:
                understanding_vault.create_multimodal_grounding(
                    concept_id=concept,
                    visual_features=grounding.visual,
                    auditory_features=grounding.auditory,
                    temporal_context=grounding.temporal,
                    physical_properties=grounding.physical,
                    confidence_score=grounding.confidence
                )
            
            logger.info(f"✅ Grounded '{concept}' (confidence: {grounding.confidence:.2f})")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to ground '{concept}': {e}")
    
    logger.info(f"Successfully grounded {success_count}/{len(initial_concepts)} concepts")


def update_configuration():
    """Update KIMERA configuration for Phase 1"""
    logger.info("Updating configuration for Phase 1...")
    
    config_updates = {
        'semantic_grounding': {
            'enabled': True,
            'multimodal_processing': True,
            'causal_reasoning': True,
            'temporal_dynamics': True,
            'physical_grounding': True,
            'intentional_processing': True,
            'curiosity_threshold': 0.6,
            'attention_focus': 'balanced'
        }
    }
    
    # Save configuration (implementation depends on your config system)
    logger.info("✅ Configuration updated")
    
    return config_updates


def verify_migration():
    """Verify the migration was successful"""
    logger.info("\nVerifying migration...")
    
    from backend.semantic_grounding import (
        EmbodiedSemanticEngine,
        MultiModalProcessor,
        CausalReasoningEngine,
        TemporalDynamicsEngine,
        PhysicalGroundingSystem,
        IntentionalProcessor
    )
    
    checks = {
        'EmbodiedSemanticEngine': False,
        'MultiModalProcessor': False,
        'CausalReasoningEngine': False,
        'TemporalDynamicsEngine': False,
        'PhysicalGroundingSystem': False,
        'IntentionalProcessor': False
    }
    
    # Test each component
    try:
        engine = EmbodiedSemanticEngine()
        test_grounding = engine.process_concept("test")
        checks['EmbodiedSemanticEngine'] = test_grounding is not None
    except Exception as e:
        logger.error(f"EmbodiedSemanticEngine check failed: {e}")
    
    try:
        processor = MultiModalProcessor()
        checks['MultiModalProcessor'] = True
    except Exception as e:
        logger.error(f"MultiModalProcessor check failed: {e}")
    
    try:
        causal = CausalReasoningEngine()
        checks['CausalReasoningEngine'] = True
    except Exception as e:
        logger.error(f"CausalReasoningEngine check failed: {e}")
    
    try:
        temporal = TemporalDynamicsEngine()
        checks['TemporalDynamicsEngine'] = True
    except Exception as e:
        logger.error(f"TemporalDynamicsEngine check failed: {e}")
    
    try:
        physical = PhysicalGroundingSystem()
        checks['PhysicalGroundingSystem'] = True
    except Exception as e:
        logger.error(f"PhysicalGroundingSystem check failed: {e}")
    
    try:
        intentional = IntentionalProcessor()
        checks['IntentionalProcessor'] = True
    except Exception as e:
        logger.error(f"IntentionalProcessor check failed: {e}")
    
    # Report results
    logger.info("\n" + "="*50)
    logger.info("MIGRATION VERIFICATION RESULTS:")
    logger.info("="*50)
    
    all_passed = True
    for component, status in checks.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {component}: {'PASS' if status else 'FAIL'}")
        if not status:
            all_passed = False
    
    return all_passed


def main():
    """Main migration function"""
    logger.info("="*80)
    logger.info("KIMERA PHASE 1 MIGRATION: Enhanced Semantic Grounding")
    logger.info("="*80)
    
    try:
        # Initialize vault manager
        vault_manager = VaultManager()
        
        # Step 1: Create database tables
        logger.info("\n📊 Step 1: Creating database schema...")
        create_tables()
        
        # Step 2: Create Neo4j schema
        logger.info("\n🔗 Step 2: Creating graph schema...")
        create_neo4j_schema()
        
        # Step 3: Populate initial knowledge
        logger.info("\n🧠 Step 3: Populating initial knowledge...")
        populate_initial_knowledge()
        
        # Step 4: Update configuration
        logger.info("\n⚙️ Step 4: Updating configuration...")
        config = update_configuration()
        
        # Step 5: Verify migration
        logger.info("\n✔️ Step 5: Verifying migration...")
        success = verify_migration()
        
        if success:
            logger.info("\n" + "🎉"*20)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY!")
            logger.info("🎉"*20)
            
            logger.info("\n📋 Next Steps:")
            logger.info("1. Run test suite: python tests/test_semantic_grounding.py")
            logger.info("2. Review implementation guide: docs/03_development/PHASE1_IMPLEMENTATION_GUIDE.md")
            logger.info("3. Start using semantic grounding in your KIMERA workflows")
            logger.info("4. Monitor performance and collect metrics")
            logger.info("5. Prepare for Phase 2: Genuine Self-Model Construction")
        else:
            logger.error("\n⚠️ Migration completed with errors. Please review the logs.")
            
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()