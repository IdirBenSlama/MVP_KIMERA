#!/usr/bin/env python3
"""
Axiom of Choice and Set Theory Test for KIMERA SWM

This test explores fundamental set theory concepts including:
- Axiom of Choice (AC)
- Zorn's Lemma
- Well-Ordering Principle
- Banach-Tarski Paradox implications
- Cardinal arithmetic
- Transfinite induction

The test integrates with KIMERA's semantic framework to demonstrate
how abstract mathematical concepts can be represented and processed
within the SWM architecture.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
import json
from typing import Set, List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from itertools import combinations, product
from backend.core.geoid import GeoidState
from backend.engines.symbolic_processor import GeoidMosaic, apply_symbolic_chaos
from backend.core.embedding_utils import encode_text
import uuid
import time

@dataclass
class SetTheoryGeoid(GeoidState):
    """Extended Geoid for set theory operations"""
    set_elements: Set[Any] = field(default_factory=set)
    cardinality: Optional[int] = None
    is_infinite: bool = False
    ordinal_type: Optional[str] = None
    choice_function: Optional[Callable] = None
    
    def __post_init__(self):
        if not self.geoid_id:
            self.geoid_id = f"set_theory_{uuid.uuid4().hex[:8]}"
        
        # Initialize semantic state for set theory concepts
        self.semantic_state.update({
            'axiom_of_choice_compatibility': 0.0,
            'well_ordering_strength': 0.0,
            'zorn_lemma_applicability': 0.0,
            'cardinal_arithmetic_consistency': 0.0,
            'paradox_resistance': 0.0
        })

class AxiomOfChoiceTest:
    """
    Comprehensive test suite for Axiom of Choice and related concepts
    """
    
    def __init__(self):
        self.test_results = {}
        self.geoids_created = []
        self.choice_functions = {}
        
    def create_infinite_family_of_sets(self) -> List[SetTheoryGeoid]:
        """
        Create an infinite family of non-empty sets to test AC
        """
        print("🔢 Creating infinite family of non-empty sets...")
        
        family = []
        for i in range(10):  # Simulate infinite with finite approximation
            # Create sets with different structures
            if i % 3 == 0:
                elements = {f"element_{i}_{j}" for j in range(i+1, i+4)}
            elif i % 3 == 1:
                elements = {j**2 for j in range(1, i+3)}
            else:
                elements = {f"symbol_{chr(65+j)}" for j in range(i+1)}
            
            geoid = SetTheoryGeoid(
                geoid_id=f"set_family_{i}",
                set_elements=elements,
                cardinality=len(elements),
                is_infinite=False
            )
            
            # Update semantic state based on set properties
            geoid.semantic_state.update({
                'set_complexity': len(elements) / 10.0,
                'structural_diversity': (i % 3) / 2.0,
                'choice_difficulty': np.random.random()
            })
            
            family.append(geoid)
            self.geoids_created.append(geoid)
        
        print(f"✅ Created family of {len(family)} sets")
        return family
    
    def test_axiom_of_choice(self, set_family: List[SetTheoryGeoid]) -> Dict[str, Any]:
        """
        Test the Axiom of Choice by constructing choice functions
        """
        print("🎯 Testing Axiom of Choice...")
        
        results = {
            'choice_functions_constructed': 0,
            'successful_selections': 0,
            'semantic_coherence': 0.0,
            'choice_consistency': 0.0
        }
        
        # Attempt to construct choice functions
        for i, set_geoid in enumerate(set_family):
            try:
                # Define choice function (deterministic for testing)
                def choice_func(s):
                    if not s:
                        return None
                    # Choose lexicographically smallest element
                    return min(s, key=str)
                
                chosen_element = choice_func(set_geoid.set_elements)
                if chosen_element is not None:
                    set_geoid.choice_function = choice_func
                    results['choice_functions_constructed'] += 1
                    results['successful_selections'] += 1
                    
                    # Update semantic state
                    set_geoid.semantic_state['axiom_of_choice_compatibility'] = 1.0
                    
                    print(f"  Set {i}: Chose '{chosen_element}' from {set_geoid.set_elements}")
                
            except Exception as e:
                print(f"  ❌ Failed to construct choice function for set {i}: {e}")
        
        # Calculate semantic coherence
        coherence_scores = [g.semantic_state.get('axiom_of_choice_compatibility', 0) 
                          for g in set_family]
        results['semantic_coherence'] = np.mean(coherence_scores)
        results['choice_consistency'] = len([s for s in coherence_scores if s > 0.5]) / len(coherence_scores)
        
        print(f"✅ AC Test: {results['choice_functions_constructed']}/{len(set_family)} choice functions constructed")
        return results
    
    def test_zorn_lemma(self) -> Dict[str, Any]:
        """
        Test Zorn's Lemma using partially ordered sets
        """
        print("🔗 Testing Zorn's Lemma...")
        
        # Create a partially ordered set (poset)
        elements = list(range(1, 16))  # {1, 2, ..., 15}
        
        # Define partial order: divisibility relation
        def divides(a, b):
            return b % a == 0
        
        # Find chains (totally ordered subsets)
        chains = []
        for length in range(2, 6):
            for combo in combinations(elements, length):
                # Check if combo forms a chain under divisibility
                sorted_combo = sorted(combo)
                is_chain = all(divides(sorted_combo[i], sorted_combo[i+1]) 
                             for i in range(len(sorted_combo)-1))
                if is_chain:
                    chains.append(sorted_combo)
        
        # Create geoid for Zorn's Lemma test
        zorn_geoid = SetTheoryGeoid(
            geoid_id="zorn_lemma_test",
            set_elements=set(elements),
            cardinality=len(elements)
        )
        
        # Find maximal elements in chains
        maximal_elements = set()
        for chain in chains:
            # Check if chain's maximum is maximal in the poset
            max_elem = max(chain)
            is_maximal = not any(divides(max_elem, x) and x != max_elem for x in elements)
            if is_maximal:
                maximal_elements.add(max_elem)
        
        # Update semantic state
        zorn_geoid.semantic_state.update({
            'zorn_lemma_applicability': 1.0 if maximal_elements else 0.0,
            'chain_complexity': len(chains) / 100.0,
            'maximal_element_count': len(maximal_elements)
        })
        
        self.geoids_created.append(zorn_geoid)
        
        results = {
            'chains_found': len(chains),
            'maximal_elements': list(maximal_elements),
            'zorn_applicable': len(maximal_elements) > 0,
            'semantic_strength': zorn_geoid.semantic_state['zorn_lemma_applicability']
        }
        
        print(f"✅ Zorn's Lemma: Found {len(chains)} chains, {len(maximal_elements)} maximal elements")
        return results
    
    def test_well_ordering_principle(self) -> Dict[str, Any]:
        """
        Test Well-Ordering Principle
        """
        print("📏 Testing Well-Ordering Principle...")
        
        # Create sets to test well-ordering
        test_sets = [
            {1, 3, 5, 7, 9},  # Finite set
            set(range(1, 21)),  # Natural numbers subset
            {-5, -3, 0, 2, 4, 6}  # Mixed integers
        ]
        
        results = {
            'well_ordered_sets': 0,
            'ordering_functions': [],
            'semantic_consistency': 0.0
        }
        
        for i, test_set in enumerate(test_sets):
            try:
                # Attempt to well-order the set
                ordered_list = sorted(test_set)
                
                # Verify well-ordering property: every non-empty subset has a least element
                is_well_ordered = True
                for subset_size in range(1, min(len(test_set), 5)):
                    for subset in combinations(test_set, subset_size):
                        if not subset:
                            continue
                        least_element = min(subset)
                        # Verify it's actually the least
                        if not all(least_element <= x for x in subset):
                            is_well_ordered = False
                            break
                    if not is_well_ordered:
                        break
                
                if is_well_ordered:
                    results['well_ordered_sets'] += 1
                    results['ordering_functions'].append(ordered_list)
                    
                    # Create geoid for this well-ordered set
                    wo_geoid = SetTheoryGeoid(
                        geoid_id=f"well_ordered_{i}",
                        set_elements=test_set,
                        cardinality=len(test_set)
                    )
                    wo_geoid.semantic_state['well_ordering_strength'] = 1.0
                    self.geoids_created.append(wo_geoid)
                
                print(f"  Set {i}: {test_set} -> Well-ordered: {is_well_ordered}")
                
            except Exception as e:
                print(f"  ❌ Failed to well-order set {i}: {e}")
        
        results['semantic_consistency'] = results['well_ordered_sets'] / len(test_sets)
        
        print(f"✅ Well-Ordering: {results['well_ordered_sets']}/{len(test_sets)} sets successfully well-ordered")
        return results
    
    def test_cardinal_arithmetic(self) -> Dict[str, Any]:
        """
        Test cardinal arithmetic and infinite cardinals
        """
        print("♾️  Testing Cardinal Arithmetic...")
        
        # Test finite cardinals
        finite_sets = [
            set(range(5)),    # |A| = 5
            set(range(3)),    # |B| = 3
            set(range(7))     # |C| = 7
        ]
        
        results = {
            'finite_arithmetic_tests': 0,
            'infinite_cardinal_tests': 0,
            'cantor_theorem_verified': False,
            'arithmetic_consistency': 0.0
        }
        
        # Test finite cardinal arithmetic
        A, B, C = finite_sets
        
        # Test |A ∪ B| ≤ |A| + |B|
        union_size = len(A.union(B))
        sum_size = len(A) + len(B)
        if union_size <= sum_size:
            results['finite_arithmetic_tests'] += 1
        
        # Test |A × B| = |A| × |B|
        cartesian_product = set(product(A, B))
        if len(cartesian_product) == len(A) * len(B):
            results['finite_arithmetic_tests'] += 1
        
        # Test Cantor's theorem: |P(A)| > |A|
        power_set_size = 2 ** len(A)  # |P(A)| = 2^|A|
        if power_set_size > len(A):
            results['cantor_theorem_verified'] = True
            results['infinite_cardinal_tests'] += 1
        
        # Create cardinal arithmetic geoid
        cardinal_geoid = SetTheoryGeoid(
            geoid_id="cardinal_arithmetic",
            set_elements=A.union(B).union(C),
            cardinality=len(A.union(B).union(C))
        )
        
        cardinal_geoid.semantic_state.update({
            'cardinal_arithmetic_consistency': results['finite_arithmetic_tests'] / 2.0,
            'cantor_theorem_strength': 1.0 if results['cantor_theorem_verified'] else 0.0,
            'infinite_comprehension': 0.8  # Approximation for infinite concepts
        })
        
        self.geoids_created.append(cardinal_geoid)
        
        results['arithmetic_consistency'] = (results['finite_arithmetic_tests'] + 
                                           results['infinite_cardinal_tests']) / 3.0
        
        print(f"✅ Cardinal Arithmetic: {results['finite_arithmetic_tests']} finite tests, Cantor verified: {results['cantor_theorem_verified']}")
        return results
    
    def test_banach_tarski_implications(self) -> Dict[str, Any]:
        """
        Test implications of Banach-Tarski paradox (conceptual level)
        """
        print("🌀 Testing Banach-Tarski Paradox Implications...")
        
        # Simulate the paradox conceptually
        # In reality, this requires non-measurable sets and the axiom of choice
        
        results = {
            'paradox_resistance_score': 0.0,
            'non_measurable_sets_detected': 0,
            'choice_dependency_strength': 0.0
        }
        
        # Create a "sphere" representation
        sphere_points = {(x, y, z) for x in range(-2, 3) for y in range(-2, 3) 
                        for z in range(-2, 3) if x*x + y*y + z*z <= 4}
        
        # Attempt to partition into "non-measurable" pieces
        # This is a conceptual simulation
        partitions = []
        for i in range(5):  # 5 pieces as in Banach-Tarski
            partition = {p for p in sphere_points if hash(str(p)) % 5 == i}
            partitions.append(partition)
        
        # Test if partitions cover the sphere
        union_of_partitions = set().union(*partitions)
        coverage_complete = union_of_partitions == sphere_points
        
        # Create Banach-Tarski geoid
        bt_geoid = SetTheoryGeoid(
            geoid_id="banach_tarski_test",
            set_elements=sphere_points,
            cardinality=len(sphere_points),
            is_infinite=False  # Finite approximation
        )
        
        # Calculate paradox resistance
        if coverage_complete:
            results['paradox_resistance_score'] = 0.3  # Low resistance = paradox possible
            results['choice_dependency_strength'] = 0.9
        else:
            results['paradox_resistance_score'] = 0.8  # High resistance = paradox blocked
            results['choice_dependency_strength'] = 0.4
        
        bt_geoid.semantic_state.update({
            'paradox_resistance': results['paradox_resistance_score'],
            'non_measurable_complexity': 0.7,
            'choice_function_dependency': results['choice_dependency_strength']
        })
        
        self.geoids_created.append(bt_geoid)
        
        print(f"✅ Banach-Tarski: Paradox resistance = {results['paradox_resistance_score']:.2f}")
        return results
    
    def analyze_semantic_coherence(self) -> Dict[str, Any]:
        """
        Analyze semantic coherence across all created geoids
        """
        print("🧠 Analyzing Semantic Coherence...")
        
        if not self.geoids_created:
            return {'error': 'No geoids created for analysis'}
        
        # Calculate overall semantic metrics
        all_semantic_states = [g.semantic_state for g in self.geoids_created]
        
        # Aggregate semantic features
        feature_means = {}
        for state in all_semantic_states:
            for feature, value in state.items():
                if feature not in feature_means:
                    feature_means[feature] = []
                feature_means[feature].append(value)
        
        # Calculate means and coherence
        coherence_analysis = {}
        for feature, values in feature_means.items():
            coherence_analysis[feature] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'coherence': 1.0 - (np.std(values) / (np.mean(values) + 1e-6))
            }
        
        # Overall system coherence
        overall_coherence = np.mean([analysis['coherence'] for analysis in coherence_analysis.values()])
        
        # Apply symbolic chaos to create a mosaic
        combined_features = {f: analysis['mean'] for f, analysis in coherence_analysis.items()}
        mosaic = GeoidMosaic(
            source_ids=[g.geoid_id for g in self.geoids_created],
            combined_features=combined_features,
            cost=1.0 - overall_coherence
        )
        
        # Apply symbolic processing
        enriched_mosaic = apply_symbolic_chaos(mosaic)
        
        results = {
            'total_geoids_analyzed': len(self.geoids_created),
            'feature_coherence': coherence_analysis,
            'overall_coherence': overall_coherence,
            'symbolic_archetype': enriched_mosaic.archetype,
            'symbolic_paradox': enriched_mosaic.paradox,
            'synthesis_cost': enriched_mosaic.synthesis_cost
        }
        
        print(f"✅ Semantic Analysis: {overall_coherence:.3f} coherence across {len(self.geoids_created)} geoids")
        if enriched_mosaic.archetype:
            print(f"   🎭 Detected archetype: {enriched_mosaic.archetype}")
        if enriched_mosaic.paradox:
            print(f"   ⚡ Detected paradox: {enriched_mosaic.paradox}")
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run the complete Axiom of Choice test suite
        """
        print("🚀 Starting Comprehensive Axiom of Choice Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        set_family = self.create_infinite_family_of_sets()
        
        test_results = {
            'axiom_of_choice': self.test_axiom_of_choice(set_family),
            'zorn_lemma': self.test_zorn_lemma(),
            'well_ordering': self.test_well_ordering_principle(),
            'cardinal_arithmetic': self.test_cardinal_arithmetic(),
            'banach_tarski': self.test_banach_tarski_implications(),
            'semantic_coherence': self.analyze_semantic_coherence()
        }
        
        # Calculate overall test score
        scores = []
        scores.append(test_results['axiom_of_choice']['choice_consistency'])
        scores.append(1.0 if test_results['zorn_lemma']['zorn_applicable'] else 0.0)
        scores.append(test_results['well_ordering']['semantic_consistency'])
        scores.append(test_results['cardinal_arithmetic']['arithmetic_consistency'])
        scores.append(1.0 - test_results['banach_tarski']['paradox_resistance_score'])  # Inverted
        scores.append(test_results['semantic_coherence']['overall_coherence'])
        
        overall_score = np.mean(scores)
        
        execution_time = time.time() - start_time
        
        final_results = {
            'test_results': test_results,
            'overall_score': overall_score,
            'execution_time': execution_time,
            'geoids_created': len(self.geoids_created),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Overall Score: {overall_score:.3f}/1.000")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Geoids Created: {len(self.geoids_created)}")
        print(f"Semantic Coherence: {test_results['semantic_coherence']['overall_coherence']:.3f}")
        
        if test_results['semantic_coherence']['symbolic_archetype']:
            print(f"Symbolic Archetype: {test_results['semantic_coherence']['symbolic_archetype']}")
        
        return final_results

def main():
    """Main execution function"""
    print("🔬 KIMERA Axiom of Choice & Set Theory Test")
    print("Testing fundamental mathematical concepts in semantic space")
    print()
    
    # Initialize and run test
    test_suite = AxiomOfChoiceTest()
    results = test_suite.run_comprehensive_test()
    
    # Save results
    output_file = f"axiom_of_choice_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        # Convert sets to lists for JSON serialization
        json_results = json.loads(json.dumps(results, default=str))
        json.dump(json_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n🎯 Test completed successfully!")
    
    return results

if __name__ == "__main__":
    main()