"""
Automated Learning Script
Helps KIMERA expand its understanding by systematically grounding concepts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.semantic_grounding import EmbodiedSemanticEngine
from backend.vault.understanding_vault_manager import UnderstandingVaultManager
from backend.semantic_grounding.intentional_processor import Goal, GoalPriority
import json
import time
from datetime import datetime


class AutomatedLearner:
    """Automated learning system for KIMERA"""
    
    def __init__(self):
        self.semantic_engine = EmbodiedSemanticEngine()
        self.understanding_vault = UnderstandingVaultManager()
        self.learned_concepts = set()
        self.learning_queue = []
        
    def load_concept_library(self):
        """Load a library of concepts to learn"""
        # Organized by domain
        concept_library = {
            "nature": [
                "ocean", "mountain", "river", "forest", "desert",
                "volcano", "glacier", "canyon", "island", "lake",
                "rain", "snow", "wind", "storm", "sunshine",
                "earthquake", "tsunami", "hurricane", "tornado", "flood"
            ],
            "technology": [
                "computer", "internet", "software", "algorithm", "database",
                "network", "server", "cloud", "encryption", "firewall",
                "robot", "automation", "sensor", "processor", "memory"
            ],
            "biology": [
                "cell", "organism", "ecosystem", "evolution", "genetics",
                "photosynthesis", "metabolism", "reproduction", "adaptation", "mutation",
                "bacteria", "virus", "fungus", "protein", "enzyme"
            ],
            "physics": [
                "gravity", "magnetism", "electricity", "radiation", "quantum",
                "relativity", "momentum", "friction", "pressure", "temperature",
                "wave", "particle", "field", "force", "energy"
            ],
            "society": [
                "culture", "language", "education", "government", "economy",
                "family", "community", "tradition", "innovation", "communication",
                "cooperation", "competition", "leadership", "democracy", "justice"
            ],
            "emotions": [
                "joy", "sadness", "anger", "fear", "surprise",
                "love", "hate", "hope", "despair", "pride",
                "shame", "guilt", "empathy", "compassion", "gratitude"
            ],
            "abstract": [
                "truth", "beauty", "freedom", "wisdom", "courage",
                "honor", "loyalty", "creativity", "imagination", "purpose",
                "meaning", "existence", "consciousness", "reality", "possibility"
            ]
        }
        
        # Flatten into learning queue with domain context
        for domain, concepts in concept_library.items():
            for concept in concepts:
                self.learning_queue.append({
                    'concept': concept,
                    'domain': domain,
                    'priority': self._calculate_priority(concept, domain)
                })
        
        # Sort by priority
        self.learning_queue.sort(key=lambda x: x['priority'], reverse=True)
        
        return len(self.learning_queue)
    
    def _calculate_priority(self, concept, domain):
        """Calculate learning priority for a concept"""
        # Prioritize fundamental concepts
        fundamental = ["energy", "time", "space", "matter", "information", 
                      "life", "consciousness", "change", "cause", "effect"]
        
        if concept in fundamental:
            return 10
        
        # Domain priorities
        domain_priority = {
            "physics": 8,
            "nature": 7,
            "biology": 7,
            "abstract": 6,
            "technology": 5,
            "society": 5,
            "emotions": 4
        }
        
        return domain_priority.get(domain, 5)
    
    def learn_concept(self, concept_info):
        """Learn a single concept with appropriate context"""
        concept = concept_info['concept']
        domain = concept_info['domain']
        
        print(f"\n📚 Learning: {concept} (domain: {domain})")
        
        # Create domain-specific context
        context = self._create_domain_context(concept, domain)
        
        # Ground the concept
        grounding = self.semantic_engine.process_concept(concept, context)
        
        # Store in understanding vault
        if grounding.confidence > 0.5:  # Only store confident groundings
            self.understanding_vault.create_multimodal_grounding(
                concept_id=concept,
                visual_features=grounding.visual,
                auditory_features=grounding.auditory,
                temporal_context=grounding.temporal,
                physical_properties=grounding.physical,
                confidence_score=grounding.confidence
            )
            
            print(f"  ✅ Grounded with confidence: {grounding.confidence:.2f}")
            
            # Discover relationships
            self._discover_relationships(concept, domain, grounding)
            
            self.learned_concepts.add(concept)
            return True
        else:
            print(f"  ⚠️ Low confidence: {grounding.confidence:.2f}")
            return False
    
    def _create_domain_context(self, concept, domain):
        """Create appropriate context based on domain"""
        context = {'domain': domain}
        
        if domain == "nature":
            context.update({
                'physical_properties': {'state': 'natural'},
                'temporal_aspect': 'geological timescale'
            })
        elif domain == "technology":
            context.update({
                'physical_properties': {'state': 'artificial'},
                'temporal_aspect': 'recent invention'
            })
        elif domain == "biology":
            context.update({
                'physical_properties': {'state': 'organic'},
                'temporal_aspect': 'evolutionary timescale'
            })
        elif domain == "physics":
            context.update({
                'physical_properties': {'state': 'fundamental'},
                'temporal_aspect': 'universal constant'
            })
        elif domain == "emotions":
            context.update({
                'physical_properties': {'state': 'mental'},
                'temporal_aspect': 'transient'
            })
        elif domain == "abstract":
            context.update({
                'physical_properties': {'state': 'conceptual'},
                'temporal_aspect': 'timeless'
            })
        
        return context
    
    def _discover_relationships(self, concept, domain, grounding):
        """Discover and establish relationships with other concepts"""
        # Domain-specific relationships
        relationships = {
            "nature": {
                "rain": [("causes", "wet_ground"), ("part_of", "water_cycle")],
                "ocean": [("contains", "water"), ("habitat_for", "fish")],
                "mountain": [("made_of", "rock"), ("affects", "weather")]
            },
            "physics": {
                "energy": [("conserved_in", "closed_system"), ("transforms_to", "different_forms")],
                "gravity": [("causes", "attraction"), ("affects", "motion")],
                "temperature": [("measures", "heat"), ("affects", "state_of_matter")]
            },
            "biology": {
                "cell": [("basic_unit_of", "life"), ("contains", "dna")],
                "photosynthesis": [("requires", "sunlight"), ("produces", "oxygen")],
                "evolution": [("drives", "adaptation"), ("requires", "variation")]
            }
        }
        
        # Check for known relationships
        domain_rels = relationships.get(domain, {})
        concept_rels = domain_rels.get(concept, [])
        
        for rel_type, target in concept_rels:
            if rel_type == "causes":
                self.understanding_vault.establish_causal_relationship(
                    cause_concept_id=concept,
                    effect_concept_id=target,
                    causal_strength=0.8,
                    mechanism_description=f"{concept} {rel_type} {target}",
                    evidence_quality=0.7
                )
                print(f"  🔗 Established: {concept} → {target}")
            
        # Discover cross-domain patterns
        if grounding.confidence > 0.7:
            related = self.semantic_engine.get_related_concepts(concept, threshold=0.6)
            for related_concept, similarity in related[:3]:  # Top 3
                print(f"  🔍 Related to: {related_concept} (similarity: {similarity:.2f})")
    
    def run_learning_session(self, concepts_to_learn=10):
        """Run an automated learning session"""
        print("\n" + "="*60)
        print("🤖 AUTOMATED LEARNING SESSION")
        print(f"Target: Learn {concepts_to_learn} new concepts")
        print("="*60)
        
        # Load concept library if not loaded
        if not self.learning_queue:
            total = self.load_concept_library()
            print(f"\n📚 Loaded {total} concepts to learn")
        
        # Get current stats
        initial_stats = self.understanding_vault.get_understanding_metrics()
        initial_groundings = initial_stats['understanding_components']['multimodal_groundings']
        initial_causal = initial_stats['understanding_components']['causal_relationships']
        
        # Learn concepts
        learned = 0
        attempted = 0
        
        while learned < concepts_to_learn and self.learning_queue:
            concept_info = self.learning_queue.pop(0)
            
            # Skip if already learned
            if concept_info['concept'] in self.learned_concepts:
                continue
            
            attempted += 1
            if self.learn_concept(concept_info):
                learned += 1
            
            # Brief pause to avoid overwhelming the system
            time.sleep(0.1)
        
        # Get final stats
        final_stats = self.understanding_vault.get_understanding_metrics()
        final_groundings = final_stats['understanding_components']['multimodal_groundings']
        final_causal = final_stats['understanding_components']['causal_relationships']
        
        # Summary
        print("\n" + "="*60)
        print("📊 LEARNING SESSION SUMMARY")
        print("="*60)
        print(f"  Concepts attempted: {attempted}")
        print(f"  Concepts learned: {learned}")
        print(f"  Success rate: {learned/attempted*100:.1f}%")
        print(f"  New groundings: {final_groundings - initial_groundings}")
        print(f"  New causal relations: {final_causal - initial_causal}")
        print(f"  Remaining in queue: {len(self.learning_queue)}")
        
        # Update roadmap progress
        print("\n📈 ROADMAP PROGRESS:")
        for phase, progress in final_stats['roadmap_progress'].items():
            print(f"  {phase}: {progress:.1%}")
        
        return learned
    
    def suggest_next_learning_goals(self):
        """Suggest what to learn next based on current understanding"""
        stats = self.understanding_vault.get_understanding_metrics()
        suggestions = []
        
        # Check what's lacking
        components = stats['understanding_components']
        
        if components['multimodal_groundings'] < 100:
            suggestions.append({
                'goal': 'Expand vocabulary',
                'target': 100 - components['multimodal_groundings'],
                'reason': 'Build foundational semantic understanding'
            })
        
        if components['causal_relationships'] < 50:
            suggestions.append({
                'goal': 'Discover causal patterns',
                'target': 50 - components['causal_relationships'],
                'reason': 'Enable predictive reasoning'
            })
        
        if components['abstract_concepts'] < 20:
            suggestions.append({
                'goal': 'Form abstract concepts',
                'target': 20 - components['abstract_concepts'],
                'reason': 'Generalize understanding across domains'
            })
        
        print("\n💡 LEARNING RECOMMENDATIONS:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion['goal']}")
            print(f"   Target: {suggestion['target']} more")
            print(f"   Reason: {suggestion['reason']}")
        
        return suggestions


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Learning for KIMERA')
    parser.add_argument('--concepts', type=int, default=10, 
                       help='Number of concepts to learn (default: 10)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous learning sessions')
    
    args = parser.parse_args()
    
    learner = AutomatedLearner()
    
    if args.continuous:
        print("🔄 Starting continuous learning mode...")
        print("Press Ctrl+C to stop\n")
        
        session = 1
        try:
            while True:
                print(f"\n🎓 Learning Session #{session}")
                learner.run_learning_session(args.concepts)
                
                # Suggest next goals
                learner.suggest_next_learning_goals()
                
                # Pause between sessions
                print("\n⏸️ Pausing for 30 seconds before next session...")
                time.sleep(30)
                session += 1
                
        except KeyboardInterrupt:
            print("\n\n✋ Learning stopped by user")
    else:
        # Single session
        learner.run_learning_session(args.concepts)
        learner.suggest_next_learning_goals()
    
    print("\n✅ Learning complete!")


if __name__ == "__main__":
    main()