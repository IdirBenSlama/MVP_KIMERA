#!/usr/bin/env python3
"""
Quick Demo: KIMERA Set Theory Test

This is a simplified demonstration of how KIMERA can process
the Axiom of Choice and related set theory concepts.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def quick_demo():
    """Run a quick demonstration of the set theory capabilities"""
    
    print("🧮 KIMERA Set Theory Quick Demo")
    print("=" * 40)
    print()
    
    try:
        from tests.set_theory.axiom_of_choice_test import AxiomOfChoiceTest
        
        print("🔬 Initializing Set Theory Test Suite...")
        test_suite = AxiomOfChoiceTest()
        
        print("📊 Running abbreviated test...")
        
        # Create a small family of sets
        print("\n1. Creating family of sets...")
        set_family = test_suite.create_infinite_family_of_sets()
        
        # Test Axiom of Choice
        print("\n2. Testing Axiom of Choice...")
        ac_results = test_suite.test_axiom_of_choice(set_family)
        print(f"   ✅ Choice functions: {ac_results['choice_functions_constructed']}")
        print(f"   ✅ Consistency: {ac_results['choice_consistency']:.3f}")
        
        # Test Zorn's Lemma
        print("\n3. Testing Zorn's Lemma...")
        zorn_results = test_suite.test_zorn_lemma()
        print(f"   ✅ Chains found: {zorn_results['chains_found']}")
        print(f"   ✅ Maximal elements: {len(zorn_results['maximal_elements'])}")
        
        # Test Cardinal Arithmetic
        print("\n4. Testing Cardinal Arithmetic...")
        cardinal_results = test_suite.test_cardinal_arithmetic()
        print(f"   ✅ Cantor's theorem: {cardinal_results['cantor_theorem_verified']}")
        print(f"   ✅ Arithmetic consistency: {cardinal_results['arithmetic_consistency']:.3f}")
        
        # Analyze semantic coherence
        print("\n5. Analyzing Semantic Coherence...")
        coherence_results = test_suite.analyze_semantic_coherence()
        print(f"   ✅ Overall coherence: {coherence_results['overall_coherence']:.3f}")
        print(f"   ✅ Geoids analyzed: {coherence_results['total_geoids_analyzed']}")
        
        if coherence_results.get('symbolic_archetype'):
            print(f"   🎭 Detected archetype: {coherence_results['symbolic_archetype']}")
        
        print("\n" + "=" * 40)
        print("🎯 Demo completed successfully!")
        print("   KIMERA can process abstract mathematical concepts")
        print("   within its semantic working memory framework.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False

def show_concept_explanation():
    """Show explanation of the concepts being tested"""
    
    print("\n📚 MATHEMATICAL CONCEPTS EXPLAINED")
    print("=" * 50)
    
    concepts = {
        "Axiom of Choice": """
        The Axiom of Choice states that for any collection of non-empty sets,
        there exists a choice function that selects exactly one element from
        each set. This seemingly simple statement has profound implications
        for mathematics and leads to counterintuitive results.
        """,
        
        "Zorn's Lemma": """
        Zorn's Lemma states that every partially ordered set in which every
        chain has an upper bound contains at least one maximal element.
        It's equivalent to the Axiom of Choice and is often used in algebra
        to prove existence of maximal ideals, bases for vector spaces, etc.
        """,
        
        "Well-Ordering Principle": """
        The Well-Ordering Principle states that every set can be well-ordered,
        meaning there exists a total ordering where every non-empty subset
        has a least element. This is also equivalent to the Axiom of Choice.
        """,
        
        "Banach-Tarski Paradox": """
        The Banach-Tarski Paradox shows that a solid ball can be decomposed
        into finitely many pieces and reassembled into two balls of the same
        size as the original. This paradox relies on the Axiom of Choice and
        demonstrates the existence of non-measurable sets.
        """,
        
        "Cardinal Arithmetic": """
        Cardinal arithmetic deals with the arithmetic of infinite sets.
        Cantor's theorem shows that the power set of any set has strictly
        greater cardinality than the set itself, leading to different
        'sizes' of infinity.
        """
    }
    
    for concept, explanation in concepts.items():
        print(f"\n🔹 {concept}")
        print(explanation.strip())
    
    print("\n" + "=" * 50)
    print("These concepts form the foundation of modern set theory and")
    print("demonstrate how KIMERA can handle abstract mathematical reasoning.")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run quick demo")
    print("2. Show concept explanations")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['2', '3']:
        show_concept_explanation()
    
    if choice in ['1', '3']:
        print("\n" + "=" * 50)
        success = quick_demo()
        
        if success:
            print("\n💡 To run the full test suite, execute:")
            print("   python run_set_theory_test.py")
    
    print("\n🎓 Thank you for exploring KIMERA's mathematical capabilities!")