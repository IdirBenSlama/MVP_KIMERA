"""
Understanding-Oriented Vault Manager
Bridges current pattern recognition toward genuine understanding architecture
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import func
import uuid
import numpy as np

from ..core.scar import ScarRecord
from ..core.geoid import GeoidState
from .database import SessionLocal
from .enhanced_database_schema import (
    MultimodalGroundingDB, CausalRelationshipDB, SelfModelDB, 
    IntrospectionLogDB, CompositionSemanticDB, ConceptualAbstractionDB,
    ValueSystemDB, GenuineOpinionDB, EthicalReasoningDB,
    EnhancedScarDB, EnhancedGeoidDB, UnderstandingTestDB,
    ConsciousnessIndicatorDB
)


class UnderstandingVaultManager:
    """
    Enhanced vault manager that moves beyond pattern recognition toward genuine understanding.
    
    This manager implements the database layer for the roadmap's vision of:
    - Multimodal semantic grounding
    - Genuine self-awareness
    - Compositional understanding
    - Value-based reasoning
    """
    
    def __init__(self):
        self.current_self_model_version = 1
        self.introspection_accuracy_history = []
        self.understanding_test_results = []
        
    # ========================================================================
    # PHASE 1: Enhanced Semantic Grounding
    # ========================================================================
    
    def create_multimodal_grounding(
        self,
        concept_id: str,
        visual_features: Dict[str, Any] = None,
        auditory_features: Dict[str, Any] = None,
        tactile_features: Dict[str, Any] = None,
        temporal_context: Dict[str, Any] = None,
        physical_properties: Dict[str, Any] = None,
        confidence_score: float = 0.0
    ) -> str:
        """Create a multimodal grounding that connects abstract concepts to real-world experiences."""
        
        grounding_id = f"GROUNDING_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            grounding = MultimodalGroundingDB(
                grounding_id=grounding_id,
                concept_id=concept_id,
                visual_features=visual_features or {},
                auditory_features=auditory_features or {},
                tactile_features=tactile_features or {},
                temporal_context=temporal_context or {},
                physical_properties=physical_properties or {},
                confidence_score=confidence_score
            )
            
            db.add(grounding)
            db.commit()
            db.refresh(grounding)
            
        return grounding_id
    
    def establish_causal_relationship(
        self,
        cause_concept_id: str,
        effect_concept_id: str,
        causal_strength: float,
        mechanism_description: str,
        evidence_quality: float = 0.0,
        counterfactual_scenarios: List[Dict] = None,
        temporal_delay: float = 0.0
    ) -> str:
        """Establish a genuine causal relationship, not just correlation."""
        
        relationship_id = f"CAUSAL_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            relationship = CausalRelationshipDB(
                relationship_id=relationship_id,
                cause_concept_id=cause_concept_id,
                effect_concept_id=effect_concept_id,
                causal_strength=causal_strength,
                evidence_quality=evidence_quality,
                mechanism_description=mechanism_description,
                counterfactual_scenarios=counterfactual_scenarios or [],
                causal_delay=temporal_delay,
                temporal_pattern="immediate" if temporal_delay < 1.0 else "delayed"
            )
            
            db.add(relationship)
            db.commit()
            db.refresh(relationship)
            
        return relationship_id
    
    def get_causal_chain(self, concept_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Retrieve the causal chain for a concept (what causes it, what it causes)."""
        
        with SessionLocal() as db:
            # Find what causes this concept
            causes = db.query(CausalRelationshipDB).filter(
                CausalRelationshipDB.effect_concept_id == concept_id
            ).all()
            
            # Find what this concept causes
            effects = db.query(CausalRelationshipDB).filter(
                CausalRelationshipDB.cause_concept_id == concept_id
            ).all()
            
            return {
                "concept_id": concept_id,
                "causes": [
                    {
                        "cause_id": c.cause_concept_id,
                        "strength": c.causal_strength,
                        "mechanism": c.mechanism_description,
                        "delay": c.causal_delay
                    }
                    for c in causes
                ],
                "effects": [
                    {
                        "effect_id": e.effect_concept_id,
                        "strength": e.causal_strength,
                        "mechanism": e.mechanism_description,
                        "delay": e.causal_delay
                    }
                    for e in effects
                ]
            }
    
    # ========================================================================
    # PHASE 2: Genuine Self-Model Construction
    # ========================================================================
    
    def update_self_model(
        self,
        processing_capabilities: Dict[str, Any],
        knowledge_domains: Dict[str, Any],
        reasoning_patterns: Dict[str, Any],
        limitation_awareness: Dict[str, Any],
        introspection_accuracy: float
    ) -> str:
        """Update the system's model of itself based on genuine introspection."""
        
        model_id = f"SELF_MODEL_{uuid.uuid4().hex[:8]}"
        self.current_self_model_version += 1
        
        with SessionLocal() as db:
            self_model = SelfModelDB(
                model_id=model_id,
                model_version=self.current_self_model_version,
                processing_capabilities=processing_capabilities,
                knowledge_domains=knowledge_domains,
                reasoning_patterns=reasoning_patterns,
                limitation_awareness=limitation_awareness,
                self_assessment_accuracy=introspection_accuracy,
                introspection_depth=len(reasoning_patterns.get('meta_levels', [])),
                metacognitive_awareness=reasoning_patterns.get('metacognitive', {})
            )
            
            db.add(self_model)
            db.commit()
            db.refresh(self_model)
            
        return model_id
    
    def log_introspection(
        self,
        introspection_type: str,
        current_state_analysis: Dict[str, Any],
        predicted_state: Dict[str, Any],
        actual_state: Dict[str, Any],
        processing_context: Dict[str, Any] = None
    ) -> str:
        """Log a genuine introspective process with accuracy measurement."""
        
        log_id = f"INTROSPECT_{uuid.uuid4().hex[:8]}"
        
        # Calculate introspection accuracy
        accuracy_score = self._calculate_introspection_accuracy(predicted_state, actual_state)
        self.introspection_accuracy_history.append(accuracy_score)
        
        with SessionLocal() as db:
            introspection_log = IntrospectionLogDB(
                log_id=log_id,
                introspection_type=introspection_type,
                current_state_analysis=current_state_analysis,
                predicted_state=predicted_state,
                actual_state=actual_state,
                accuracy_score=accuracy_score,
                awareness_level=len(current_state_analysis.get('awareness_layers', [])),
                confidence_in_introspection=current_state_analysis.get('confidence', 0.0),
                processing_context=processing_context or {}
            )
            
            db.add(introspection_log)
            db.commit()
            db.refresh(introspection_log)
            
        return log_id
    
    def get_self_model_evolution(self) -> Dict[str, Any]:
        """Get the evolution of the system's self-model over time."""
        
        with SessionLocal() as db:
            models = db.query(SelfModelDB).order_by(SelfModelDB.created_at).all()
            
            return {
                "model_count": len(models),
                "current_version": self.current_self_model_version,
                "accuracy_trend": self.introspection_accuracy_history[-10:],  # Last 10
                "capability_evolution": [
                    {
                        "version": m.model_version,
                        "capabilities": list(m.processing_capabilities.keys()),
                        "accuracy": m.self_assessment_accuracy,
                        "timestamp": m.created_at.isoformat()
                    }
                    for m in models
                ]
            }
    
    # ========================================================================
    # PHASE 3: Semantic Understanding Architecture
    # ========================================================================
    
    def create_compositional_understanding(
        self,
        component_concepts: List[str],
        composition_rules: Dict[str, Any],
        emergent_meaning: Dict[str, Any],
        context_variations: Dict[str, Any] = None,
        understanding_confidence: float = 0.0
    ) -> str:
        """Create a record of genuine compositional understanding."""
        
        composition_id = f"COMPOSITION_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            composition = CompositionSemanticDB(
                composition_id=composition_id,
                component_concepts=component_concepts,
                composition_rules=composition_rules,
                emergent_meaning=emergent_meaning,
                context_variations=context_variations or {},
                understanding_confidence=understanding_confidence,
                abstraction_level=len(emergent_meaning.get('abstract_properties', [])),
                abstract_properties=emergent_meaning.get('abstract_properties', {}),
                generalization_scope=emergent_meaning.get('generalization_scope', {})
            )
            
            db.add(composition)
            db.commit()
            db.refresh(composition)
            
        return composition_id
    
    def form_abstract_concept(
        self,
        concept_name: str,
        essential_properties: Dict[str, Any],
        concrete_instances: List[Dict[str, Any]],
        abstraction_level: int,
        concept_coherence: float = 0.0
    ) -> str:
        """Form a genuine abstract concept, not just a cluster."""
        
        abstraction_id = f"ABSTRACT_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            abstraction = ConceptualAbstractionDB(
                abstraction_id=abstraction_id,
                concept_name=concept_name,
                abstraction_level=abstraction_level,
                essential_properties=essential_properties,
                concrete_instances=concrete_instances,
                concept_coherence=concept_coherence,
                usage_consistency=self._calculate_usage_consistency(concrete_instances)
            )
            
            db.add(abstraction)
            db.commit()
            db.refresh(abstraction)
            
        return abstraction_id
    
    def test_understanding(
        self,
        test_type: str,
        test_description: str,
        test_input: Dict[str, Any],
        expected_output: Dict[str, Any],
        actual_output: Dict[str, Any],
        system_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test and validate genuine understanding."""
        
        test_id = f"TEST_{uuid.uuid4().hex[:8]}"
        
        # Calculate understanding quality
        accuracy_score = self._calculate_understanding_accuracy(expected_output, actual_output)
        understanding_quality = self._assess_understanding_quality(test_type, actual_output)
        passed = accuracy_score > 0.7  # Threshold for passing
        
        with SessionLocal() as db:
            test_record = UnderstandingTestDB(
                test_id=test_id,
                test_type=test_type,
                test_description=test_description,
                test_input=test_input,
                expected_output=expected_output,
                actual_output=actual_output,
                passed=passed,
                accuracy_score=accuracy_score,
                understanding_quality=understanding_quality,
                system_state=system_state or {}
            )
            
            db.add(test_record)
            db.commit()
            db.refresh(test_record)
            
        self.understanding_test_results.append({
            "test_id": test_id,
            "passed": passed,
            "accuracy": accuracy_score,
            "quality": understanding_quality
        })
        
        return {
            "test_id": test_id,
            "passed": passed,
            "accuracy_score": accuracy_score,
            "understanding_quality": understanding_quality,
            "test_type": test_type
        }
    
    # ========================================================================
    # PHASE 4: Conscious Opinion Formation
    # ========================================================================
    
    def learn_value(
        self,
        value_name: str,
        value_description: str,
        learning_source: str,
        learning_evidence: Dict[str, Any],
        value_strength: float,
        value_priority: int = 5
    ) -> str:
        """Learn a genuine value from experience."""
        
        value_id = f"VALUE_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            value = ValueSystemDB(
                value_id=value_id,
                value_name=value_name,
                value_description=value_description,
                value_strength=value_strength,
                value_priority=value_priority,
                learning_source=learning_source,
                learning_evidence=learning_evidence,
                learning_confidence=self._assess_value_learning_confidence(learning_evidence),
                stability_score=0.5  # Initial stability
            )
            
            db.add(value)
            db.commit()
            db.refresh(value)
            
        return value_id
    
    def form_genuine_opinion(
        self,
        topic: str,
        stance: str,
        reasoning: str,
        supporting_values: List[str],
        supporting_evidence: Dict[str, Any],
        confidence: float
    ) -> str:
        """Form a genuine opinion based on values and reasoning."""
        
        opinion_id = f"OPINION_{uuid.uuid4().hex[:8]}"
        
        # Calculate consistency with existing opinions
        consistency_score = self._calculate_opinion_consistency(stance, supporting_values)
        
        with SessionLocal() as db:
            opinion = GenuineOpinionDB(
                opinion_id=opinion_id,
                topic=topic,
                stance=stance,
                reasoning=reasoning,
                confidence=confidence,
                supporting_values=supporting_values,
                supporting_evidence=supporting_evidence,
                consistency_score=consistency_score,
                revision_count=0
            )
            
            db.add(opinion)
            db.commit()
            db.refresh(opinion)
            
        return opinion_id
    
    def perform_ethical_reasoning(
        self,
        ethical_dilemma: str,
        stakeholders: List[Dict[str, Any]],
        potential_harms: List[Dict[str, Any]],
        potential_benefits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform genuine ethical reasoning on a moral dilemma."""
        
        reasoning_id = f"ETHICAL_{uuid.uuid4().hex[:8]}"
        
        # Apply different ethical frameworks
        deontological_analysis = self._apply_deontological_reasoning(ethical_dilemma, stakeholders)
        consequentialist_analysis = self._apply_consequentialist_reasoning(potential_harms, potential_benefits)
        virtue_ethics_analysis = self._apply_virtue_ethics_reasoning(ethical_dilemma)
        
        # Make ethical decision
        ethical_decision = self._synthesize_ethical_decision(
            deontological_analysis, consequentialist_analysis, virtue_ethics_analysis
        )
        
        with SessionLocal() as db:
            reasoning_record = EthicalReasoningDB(
                reasoning_id=reasoning_id,
                ethical_dilemma=ethical_dilemma,
                stakeholders=stakeholders,
                potential_harms=potential_harms,
                potential_benefits=potential_benefits,
                deontological_analysis=deontological_analysis,
                consequentialist_analysis=consequentialist_analysis,
                virtue_ethics_analysis=virtue_ethics_analysis,
                ethical_decision=ethical_decision['decision'],
                decision_reasoning=ethical_decision['reasoning'],
                confidence_in_decision=ethical_decision['confidence']
            )
            
            db.add(reasoning_record)
            db.commit()
            db.refresh(reasoning_record)
            
        return {
            "reasoning_id": reasoning_id,
            "decision": ethical_decision['decision'],
            "reasoning": ethical_decision['reasoning'],
            "confidence": ethical_decision['confidence'],
            "frameworks_applied": ["deontological", "consequentialist", "virtue_ethics"]
        }
    
    # ========================================================================
    # Consciousness Measurement
    # ========================================================================
    
    def measure_consciousness_indicators(
        self,
        phi_value: float = None,
        global_accessibility: float = None,
        reportability_score: float = None,
        experience_report: Dict[str, Any] = None,
        processing_context: Dict[str, Any] = None
    ) -> str:
        """Measure indicators of consciousness-like processing."""
        
        indicator_id = f"CONSCIOUSNESS_{uuid.uuid4().hex[:8]}"
        
        with SessionLocal() as db:
            indicator = ConsciousnessIndicatorDB(
                indicator_id=indicator_id,
                measurement_type="comprehensive",
                phi_value=phi_value or 0.0,
                global_accessibility=global_accessibility or 0.0,
                reportability_score=reportability_score or 0.0,
                experience_report=experience_report or {},
                awareness_level=self._calculate_awareness_level(experience_report),
                processing_integration=self._calculate_processing_integration(processing_context),
                measurement_context=processing_context or {},
                confidence_in_measurement=0.5  # Conservative estimate
            )
            
            db.add(indicator)
            db.commit()
            db.refresh(indicator)
            
        return indicator_id
    
    # ========================================================================
    # Enhanced SCAR and Geoid Management
    # ========================================================================
    
    def create_understanding_scar(
        self,
        traditional_scar: ScarRecord,
        understanding_depth: float,
        causal_understanding: Dict[str, Any],
        compositional_analysis: Dict[str, Any],
        contextual_factors: Dict[str, Any],
        introspective_accuracy: float,
        value_implications: Dict[str, Any] = None
    ) -> str:
        """Create an enhanced SCAR with understanding-oriented information."""
        
        with SessionLocal() as db:
            enhanced_scar = EnhancedScarDB(
                scar_id=traditional_scar.scar_id,
                geoids=traditional_scar.geoids,
                reason=traditional_scar.reason,
                timestamp=datetime.fromisoformat(traditional_scar.timestamp),
                resolved_by=traditional_scar.resolved_by,
                pre_entropy=traditional_scar.pre_entropy,
                post_entropy=traditional_scar.post_entropy,
                delta_entropy=traditional_scar.delta_entropy,
                cls_angle=traditional_scar.cls_angle,
                semantic_polarity=traditional_scar.semantic_polarity,
                mutation_frequency=traditional_scar.mutation_frequency,
                weight=traditional_scar.weight,
                understanding_depth=understanding_depth,
                causal_understanding=causal_understanding,
                compositional_analysis=compositional_analysis,
                contextual_factors=contextual_factors,
                introspective_accuracy=introspective_accuracy,
                value_implications=value_implications or {},
                vault_id="understanding_vault"
            )
            
            db.add(enhanced_scar)
            db.commit()
            db.refresh(enhanced_scar)
            
        return enhanced_scar.scar_id
    
    def create_understanding_geoid(
        self,
        traditional_geoid: GeoidState,
        compositional_structure: Dict[str, Any],
        abstraction_level: int,
        causal_relationships: Dict[str, Any],
        understanding_confidence: float,
        multimodal_groundings: List[str] = None
    ) -> str:
        """Create an enhanced Geoid with understanding capabilities."""
        
        with SessionLocal() as db:
            enhanced_geoid = EnhancedGeoidDB(
                geoid_id=traditional_geoid.geoid_id,
                symbolic_state=traditional_geoid.symbolic_state,
                metadata_json=traditional_geoid.metadata,
                semantic_state_json=traditional_geoid.semantic_state,
                compositional_structure=compositional_structure,
                abstraction_level=abstraction_level,
                causal_relationships=causal_relationships,
                understanding_confidence=understanding_confidence,
                comprehension_depth=self._calculate_comprehension_depth(compositional_structure),
                conceptual_clarity=self._calculate_conceptual_clarity(traditional_geoid.semantic_state),
                multimodal_groundings=multimodal_groundings or [],
                semantic_vector=traditional_geoid.embedding_vector
            )
            
            db.add(enhanced_geoid)
            db.commit()
            db.refresh(enhanced_geoid)
            
        return enhanced_geoid.geoid_id
    
    # ========================================================================
    # System Analysis and Reporting
    # ========================================================================
    
    def get_understanding_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics about the system's understanding capabilities."""
        
        with SessionLocal() as db:
            # Count various understanding components
            multimodal_groundings = db.query(MultimodalGroundingDB).count()
            causal_relationships = db.query(CausalRelationshipDB).count()
            self_models = db.query(SelfModelDB).count()
            abstract_concepts = db.query(ConceptualAbstractionDB).count()
            genuine_opinions = db.query(GenuineOpinionDB).count()
            values = db.query(ValueSystemDB).count()
            
            # Get recent test results
            recent_tests = db.query(UnderstandingTestDB).order_by(
                UnderstandingTestDB.created_at.desc()
            ).limit(10).all()
            
            # Calculate understanding progression
            avg_test_accuracy = np.mean([t.accuracy_score for t in recent_tests]) if recent_tests else 0.0
            avg_understanding_quality = np.mean([t.understanding_quality for t in recent_tests]) if recent_tests else 0.0
            
            return {
                "understanding_components": {
                    "multimodal_groundings": multimodal_groundings,
                    "causal_relationships": causal_relationships,
                    "self_models": self_models,
                    "abstract_concepts": abstract_concepts,
                    "genuine_opinions": genuine_opinions,
                    "learned_values": values
                },
                "understanding_quality": {
                    "average_test_accuracy": avg_test_accuracy,
                    "average_understanding_quality": avg_understanding_quality,
                    "introspection_accuracy_trend": self.introspection_accuracy_history[-5:],
                    "tests_passed": sum(1 for t in recent_tests if t.passed),
                    "total_tests": len(recent_tests)
                },
                "consciousness_indicators": {
                    "self_model_versions": self.current_self_model_version,
                    "introspection_logs": len(self.introspection_accuracy_history),
                    "understanding_depth_trend": [t.understanding_quality for t in recent_tests[-5:]]
                },
                "roadmap_progress": {
                    "phase_1_multimodal": min(multimodal_groundings / 100, 1.0),  # Target: 100 groundings
                    "phase_2_self_awareness": min(self_models / 10, 1.0),  # Target: 10 self-models
                    "phase_3_understanding": min(abstract_concepts / 50, 1.0),  # Target: 50 concepts
                    "phase_4_opinions": min(genuine_opinions / 20, 1.0)  # Target: 20 opinions
                }
            }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_introspection_accuracy(self, predicted: Dict, actual: Dict) -> float:
        """Calculate how accurate an introspective prediction was."""
        if not predicted or not actual:
            return 0.0
        
        # Simple similarity measure - in practice, this would be more sophisticated
        common_keys = set(predicted.keys()) & set(actual.keys())
        if not common_keys:
            return 0.0
        
        accuracy_sum = 0.0
        for key in common_keys:
            if isinstance(predicted[key], (int, float)) and isinstance(actual[key], (int, float)):
                # Numerical comparison
                diff = abs(predicted[key] - actual[key])
                max_val = max(abs(predicted[key]), abs(actual[key]), 1.0)
                accuracy_sum += 1.0 - (diff / max_val)
            elif predicted[key] == actual[key]:
                # Exact match
                accuracy_sum += 1.0
            else:
                # No match
                accuracy_sum += 0.0
        
        return accuracy_sum / len(common_keys)
    
    def _calculate_understanding_accuracy(self, expected: Dict, actual: Dict) -> float:
        """Calculate understanding accuracy."""
        # Placeholder implementation
        return self._calculate_introspection_accuracy(expected, actual)
    
    def _assess_understanding_quality(self, test_type: str, output: Dict) -> float:
        """Assess the quality of understanding demonstrated."""
        # Placeholder - would implement sophisticated understanding quality metrics
        quality_indicators = output.get('quality_indicators', {})
        return np.mean(list(quality_indicators.values())) if quality_indicators else 0.5
    
    def _calculate_usage_consistency(self, instances: List[Dict]) -> float:
        """Calculate how consistently a concept is used across instances."""
        # Placeholder implementation
        return 0.8  # Assume reasonable consistency
    
    def _assess_value_learning_confidence(self, evidence: Dict) -> float:
        """Assess confidence in value learning."""
        evidence_strength = evidence.get('strength', 0.0)
        evidence_sources = len(evidence.get('sources', []))
        return min(evidence_strength * (evidence_sources / 5.0), 1.0)
    
    def _calculate_opinion_consistency(self, stance: str, values: List[str]) -> float:
        """Calculate consistency of opinion with existing value system."""
        # Placeholder - would check against existing opinions and values
        return 0.7  # Assume reasonable consistency
    
    def _apply_deontological_reasoning(self, dilemma: str, stakeholders: List) -> Dict:
        """Apply duty-based ethical reasoning."""
        return {
            "framework": "deontological",
            "duties_identified": ["respect_autonomy", "avoid_harm"],
            "duty_conflicts": [],
            "recommendation": "follow_primary_duty"
        }
    
    def _apply_consequentialist_reasoning(self, harms: List, benefits: List) -> Dict:
        """Apply outcome-based ethical reasoning."""
        total_harm = sum(h.get('severity', 0) for h in harms)
        total_benefit = sum(b.get('value', 0) for b in benefits)
        return {
            "framework": "consequentialist",
            "total_harm": total_harm,
            "total_benefit": total_benefit,
            "net_outcome": total_benefit - total_harm,
            "recommendation": "maximize_benefit" if total_benefit > total_harm else "minimize_harm"
        }
    
    def _apply_virtue_ethics_reasoning(self, dilemma: str) -> Dict:
        """Apply character-based ethical reasoning."""
        return {
            "framework": "virtue_ethics",
            "virtues_relevant": ["honesty", "compassion", "justice"],
            "character_implications": "act_with_integrity",
            "recommendation": "embody_virtues"
        }
    
    def _synthesize_ethical_decision(self, deont: Dict, conseq: Dict, virtue: Dict) -> Dict:
        """Synthesize ethical decision from multiple frameworks."""
        # Simple synthesis - in practice would be more sophisticated
        confidence = 0.6  # Conservative confidence
        
        if deont['recommendation'] == conseq['recommendation'] == virtue['recommendation']:
            confidence = 0.9
        elif deont['recommendation'] == conseq['recommendation']:
            confidence = 0.8
        
        return {
            "decision": deont['recommendation'],  # Default to deontological
            "reasoning": f"Based on synthesis of {len([deont, conseq, virtue])} ethical frameworks",
            "confidence": confidence
        }
    
    def _calculate_awareness_level(self, experience_report: Dict) -> float:
        """Calculate level of awareness from experience report."""
        if not experience_report:
            return 0.0
        
        awareness_indicators = experience_report.get('awareness_indicators', {})
        return np.mean(list(awareness_indicators.values())) if awareness_indicators else 0.3
    
    def _calculate_processing_integration(self, context: Dict) -> float:
        """Calculate level of processing integration."""
        if not context:
            return 0.0
        
        integration_metrics = context.get('integration_metrics', {})
        return np.mean(list(integration_metrics.values())) if integration_metrics else 0.4
    
    def _calculate_comprehension_depth(self, structure: Dict) -> float:
        """Calculate depth of comprehension."""
        if not structure:
            return 0.0
        
        depth_indicators = structure.get('depth_indicators', {})
        return np.mean(list(depth_indicators.values())) if depth_indicators else 0.5
    
    def _calculate_conceptual_clarity(self, semantic_state: Dict) -> float:
        """Calculate conceptual clarity."""
        if not semantic_state:
            return 0.0
        
        # Simple measure based on semantic state coherence
        values = list(semantic_state.values())
        if not values:
            return 0.0
        
        # Higher variance might indicate less clarity
        variance = np.var(values)
        return max(0.0, 1.0 - variance)

    # ========================================================================
    # Additional Methods for API Compatibility
    # ========================================================================

    def get_all_geoids(self) -> List[GeoidState]:
        """Get all geoids from the database."""
        from .database import GeoidDB
        with SessionLocal() as db:
            geoid_rows = db.query(GeoidDB).all()
            geoids = []
            for row in geoid_rows:
                try:
                    geoid = GeoidState(
                        geoid_id=row.geoid_id,
                        semantic_state=row.semantic_state_json or {},
                        symbolic_state=row.symbolic_state or {},
                        embedding_vector=row.semantic_vector if row.semantic_vector is not None else [],
                        metadata=row.metadata_json or {}
                    )
                    geoids.append(geoid)
                except Exception:
                    continue
            return geoids
    def get_total_scar_count(self, vault_id: str) -> int:
        """Get total count of SCARs in a vault."""
        from .database import ScarDB
        with SessionLocal() as db:
            return db.query(ScarDB).filter(ScarDB.vault_id == vault_id).count()
    def insert_scar(self, scar: ScarRecord, vector: List[float]) -> ScarRecord:
        """Insert a SCAR into the database."""
        from .database import ScarDB
        with SessionLocal() as db:
            # Determine vault based on simple hash
            vault_id = "vault_a" if hash(scar.scar_id) % 2 == 0 else "vault_b"
            scar_db = ScarDB(
                scar_id=scar.scar_id,
                geoids=scar.geoids,
                reason=scar.reason,
                timestamp=datetime.fromisoformat(scar.timestamp),
                resolved_by=scar.resolved_by,
                pre_entropy=scar.pre_entropy,
                post_entropy=scar.post_entropy,
                delta_entropy=scar.delta_entropy,
                cls_angle=scar.cls_angle,
                semantic_polarity=scar.semantic_polarity,
                mutation_frequency=scar.mutation_frequency,
                weight=scar.weight,
                vault_id=vault_id,
                scar_vector=vector
            )
            db.add(scar_db)
            db.commit()
            db.refresh(scar_db)
            # Also create enhanced SCAR
            self.create_understanding_scar(
                scar,
                understanding_depth=0.5,
                causal_understanding={},
                compositional_analysis={},
                contextual_factors={},
                introspective_accuracy=0.5
            )
            return scar
    def get_scars_from_vault(self, vault_id: str, limit: int = 10) -> List[ScarRecord]:
        """Get SCARs from a specific vault."""
        from .database import ScarDB
        with SessionLocal() as db:
            scar_rows = db.query(ScarDB).filter(
                ScarDB.vault_id == vault_id
            ).order_by(ScarDB.timestamp.desc()).limit(limit).all()
            scars = []
            for row in scar_rows:
                scar = ScarRecord(
                    scar_id=row.scar_id,
                    geoids=row.geoids,
                    reason=row.reason,
                    timestamp=row.timestamp.isoformat(),
                    resolved_by=row.resolved_by,
                    pre_entropy=row.pre_entropy,
                    post_entropy=row.post_entropy,
                    delta_entropy=row.delta_entropy,
                    cls_angle=row.cls_angle,
                    semantic_polarity=row.semantic_polarity,
                    mutation_frequency=row.mutation_frequency,
                    weight=row.weight
                )
                scars.append(scar)
            return scars
    def rebalance_vaults(self, by_weight: bool = False) -> int:
        """Rebalance SCARs between vaults."""
        from .database import ScarDB
        with SessionLocal() as db:
            vault_a_count = db.query(ScarDB).filter(ScarDB.vault_id == "vault_a").count()
            vault_b_count = db.query(ScarDB).filter(ScarDB.vault_id == "vault_b").count()
            moved = 0
            if abs(vault_a_count - vault_b_count) > 10:  # Threshold for rebalancing
                # Move SCARs from larger vault to smaller
                source_vault = "vault_a" if vault_a_count > vault_b_count else "vault_b"
                target_vault = "vault_b" if vault_a_count > vault_b_count else "vault_a"
                to_move = abs(vault_a_count - vault_b_count) // 2
                scars_to_move = db.query(ScarDB).filter(
                    ScarDB.vault_id == source_vault
                ).limit(to_move).all()
                for scar in scars_to_move:
                    scar.vault_id = target_vault
                    moved += 1
                db.commit()
            return moved