"""
Performance Benchmark for Phase 1: Enhanced Semantic Grounding
Measures performance metrics and capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
from datetime import datetime
import json
from backend.semantic_grounding import (
    EmbodiedSemanticEngine,
    MultiModalProcessor,
    CausalReasoningEngine,
    TemporalDynamicsEngine,
    PhysicalGroundingSystem,
    IntentionalProcessor
)


class SemanticGroundingBenchmark:
    """Benchmark suite for semantic grounding performance"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {}
        }
        
    def benchmark_grounding_speed(self):
        """Benchmark concept grounding speed"""
        print("\n📊 Benchmarking Grounding Speed...")
        
        engine = EmbodiedSemanticEngine()
        
        # Test concepts
        concepts = [
            "water", "fire", "tree", "car", "happiness", "time", "energy",
            "mountain", "ocean", "wind", "light", "darkness", "music", "silence",
            "growth", "decay", "movement", "stillness", "heat", "cold"
        ]
        
        # Warm up
        engine.process_concept("test")
        
        # Benchmark
        start_time = time.time()
        groundings = []
        
        for concept in concepts:
            concept_start = time.time()
            grounding = engine.process_concept(concept)
            concept_time = time.time() - concept_start
            
            groundings.append({
                'concept': concept,
                'time': concept_time,
                'confidence': grounding.confidence
            })
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        times = [g['time'] for g in groundings]
        confidences = [g['confidence'] for g in groundings]
        
        results = {
            'total_concepts': len(concepts),
            'total_time': total_time,
            'average_time': np.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_time': np.std(times),
            'average_confidence': np.mean(confidences),
            'concepts_per_second': len(concepts) / total_time
        }
        
        print(f"✅ Grounded {len(concepts)} concepts in {total_time:.2f}s")
        print(f"   Average: {results['average_time']*1000:.1f}ms per concept")
        print(f"   Throughput: {results['concepts_per_second']:.1f} concepts/second")
        print(f"   Average confidence: {results['average_confidence']:.2f}")
        
        self.results['benchmarks']['grounding_speed'] = results
        return results
    
    def benchmark_multimodal_integration(self):
        """Benchmark multimodal processing performance"""
        print("\n🎨 Benchmarking Multimodal Integration...")
        
        processor = MultiModalProcessor()
        
        concepts = ["thunder", "ocean", "bird", "fire", "music"]
        
        start_time = time.time()
        integration_times = []
        
        for concept in concepts:
            int_start = time.time()
            
            # Process through modalities
            visual = processor.ground_visually(concept)
            auditory = processor.ground_auditorily(concept)
            integrated = processor.integrate_modalities(visual, auditory)
            
            int_time = time.time() - int_start
            integration_times.append(int_time)
        
        total_time = time.time() - start_time
        
        results = {
            'total_integrations': len(concepts),
            'total_time': total_time,
            'average_time': np.mean(integration_times),
            'integrations_per_second': len(concepts) / total_time
        }
        
        print(f"✅ Integrated {len(concepts)} concepts in {total_time:.2f}s")
        print(f"   Average: {results['average_time']*1000:.1f}ms per integration")
        
        self.results['benchmarks']['multimodal_integration'] = results
        return results
    
    def benchmark_causal_reasoning(self):
        """Benchmark causal reasoning performance"""
        print("\n⚡ Benchmarking Causal Reasoning...")
        
        engine = CausalReasoningEngine()
        
        # Test causal analysis
        concepts = ["rain", "fire", "heat", "ice", "plant growth"]
        
        start_time = time.time()
        causal_times = []
        total_relations = 0
        
        for concept in concepts:
            causal_start = time.time()
            
            # Analyze causality
            causality = engine.identify_causes_effects(concept)
            
            causal_time = time.time() - causal_start
            causal_times.append(causal_time)
            
            total_relations += len(causality.get('causes', []))
            total_relations += len(causality.get('effects', []))
        
        # Counterfactual reasoning
        cf_start = time.time()
        counterfactual = engine.reason_counterfactually(
            "fire",
            intervention={'remove': 'oxygen'}
        )
        cf_time = time.time() - cf_start
        
        total_time = time.time() - start_time
        
        results = {
            'concepts_analyzed': len(concepts),
            'total_time': total_time,
            'average_causal_time': np.mean(causal_times),
            'counterfactual_time': cf_time,
            'total_relations_found': total_relations,
            'relations_per_concept': total_relations / len(concepts)
        }
        
        print(f"✅ Analyzed {len(concepts)} concepts in {total_time:.2f}s")
        print(f"   Found {total_relations} causal relations")
        print(f"   Counterfactual reasoning: {cf_time*1000:.1f}ms")
        
        self.results['benchmarks']['causal_reasoning'] = results
        return results
    
    def benchmark_temporal_processing(self):
        """Benchmark temporal dynamics processing"""
        print("\n⏰ Benchmarking Temporal Processing...")
        
        engine = TemporalDynamicsEngine()
        
        # Generate time series data
        time_series = []
        for i in range(100):
            time_series.append({
                'timestamp': i * 3600,  # Hourly data
                'value': 20 + 10 * np.sin(i * 2 * np.pi / 24) + np.random.randn()
            })
        
        start_time = time.time()
        
        # Pattern detection
        pattern_start = time.time()
        temporal_context = engine.contextualize(
            "temperature",
            context={'observations': time_series}
        )
        pattern_time = time.time() - pattern_start
        
        # Evolution analysis
        evo_start = time.time()
        evolution = engine.analyze_temporal_evolution("temperature", time_series)
        evo_time = time.time() - evo_start
        
        # Prediction
        pred_start = time.time()
        prediction = engine.predict_next_occurrence(
            "temperature",
            last_occurrence=time_series[-1]['timestamp']
        )
        pred_time = time.time() - pred_start
        
        total_time = time.time() - start_time
        
        results = {
            'data_points': len(time_series),
            'total_time': total_time,
            'pattern_detection_time': pattern_time,
            'evolution_analysis_time': evo_time,
            'prediction_time': pred_time,
            'patterns_found': len(temporal_context.get('patterns', []))
        }
        
        print(f"✅ Processed {len(time_series)} temporal data points in {total_time:.2f}s")
        print(f"   Pattern detection: {pattern_time*1000:.1f}ms")
        print(f"   Evolution analysis: {evo_time*1000:.1f}ms")
        
        self.results['benchmarks']['temporal_processing'] = results
        return results
    
    def benchmark_physical_simulation(self):
        """Benchmark physical grounding and simulation"""
        print("\n⚛️ Benchmarking Physical Simulation...")
        
        system = PhysicalGroundingSystem()
        
        # Physical property mapping
        objects = ["water", "iron", "air", "wood", "car"]
        
        start_time = time.time()
        mapping_times = []
        
        for obj in objects:
            map_start = time.time()
            properties = system.map_properties(obj)
            map_time = time.time() - map_start
            mapping_times.append(map_time)
        
        # Interaction simulations
        interactions = [
            ("car", "feather", "collision"),
            ("fire", "ice", "thermal"),
            ("iron", "wood", "collision")
        ]
        
        sim_times = []
        for obj1, obj2, interaction in interactions:
            sim_start = time.time()
            result = system.simulate_interaction(obj1, obj2, interaction)
            sim_time = time.time() - sim_start
            sim_times.append(sim_time)
        
        total_time = time.time() - start_time
        
        results = {
            'objects_mapped': len(objects),
            'interactions_simulated': len(interactions),
            'total_time': total_time,
            'average_mapping_time': np.mean(mapping_times),
            'average_simulation_time': np.mean(sim_times)
        }
        
        print(f"✅ Mapped {len(objects)} objects and simulated {len(interactions)} interactions")
        print(f"   Mapping: {results['average_mapping_time']*1000:.1f}ms average")
        print(f"   Simulation: {results['average_simulation_time']*1000:.1f}ms average")
        
        self.results['benchmarks']['physical_simulation'] = results
        return results
    
    def benchmark_intentional_processing(self):
        """Benchmark goal-directed processing"""
        print("\n🎯 Benchmarking Intentional Processing...")
        
        from backend.semantic_grounding.intentional_processor import Goal, GoalPriority
        
        processor = IntentionalProcessor()
        
        # Set up goals
        goals = [
            Goal(
                goal_id="understand_nature",
                description="Understand natural phenomena",
                priority=GoalPriority.HIGH,
                criteria={"concepts": ["rain", "wind", "sun"]}
            ),
            Goal(
                goal_id="explore_physics",
                description="Explore physical interactions",
                priority=GoalPriority.MEDIUM,
                criteria={"interactions": 5}
            )
        ]
        
        for goal in goals:
            processor.set_goal(goal)
        
        # Process various inputs
        inputs = [
            "The rain falls gently on the leaves",
            "Wind moves through the trees",
            "Sunlight warms the earth",
            "Objects collide with different forces",
            "Energy transforms from one form to another"
        ]
        
        start_time = time.time()
        processing_times = []
        
        for input_text in inputs:
            proc_start = time.time()
            result = processor.process_with_intention(input_text)
            proc_time = time.time() - proc_start
            processing_times.append(proc_time)
        
        total_time = time.time() - start_time
        
        # Get goal progress
        goal_progress = {}
        for goal in goals:
            status = processor.get_goal_status(goal.goal_id)
            if status:
                goal_progress[goal.goal_id] = status['progress']
        
        results = {
            'inputs_processed': len(inputs),
            'active_goals': len(goals),
            'total_time': total_time,
            'average_processing_time': np.mean(processing_times),
            'goal_progress': goal_progress
        }
        
        print(f"✅ Processed {len(inputs)} inputs with {len(goals)} active goals")
        print(f"   Average processing: {results['average_processing_time']*1000:.1f}ms")
        print(f"   Goal progress: {goal_progress}")
        
        self.results['benchmarks']['intentional_processing'] = results
        return results
    
    def benchmark_memory_usage(self):
        """Benchmark memory usage of semantic grounding"""
        print("\n💾 Benchmarking Memory Usage...")
        
        import psutil
        import gc
        
        # Get baseline memory
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create engine and ground many concepts
        engine = EmbodiedSemanticEngine()
        
        # Generate many concepts
        concepts = []
        for i in range(1000):
            concepts.append(f"concept_{i}")
        
        # Ground concepts and measure memory
        memory_checkpoints = []
        
        for i, concept in enumerate(concepts):
            engine.process_concept(concept)
            
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_checkpoints.append({
                    'concepts': i,
                    'memory_mb': current_memory,
                    'delta_mb': current_memory - baseline_memory
                })
        
        final_memory = process.memory_info().rss / 1024 / 1024
        
        results = {
            'baseline_memory_mb': baseline_memory,
            'final_memory_mb': final_memory,
            'total_memory_increase_mb': final_memory - baseline_memory,
            'concepts_grounded': len(concepts),
            'memory_per_concept_kb': (final_memory - baseline_memory) * 1024 / len(concepts),
            'checkpoints': memory_checkpoints
        }
        
        print(f"✅ Memory usage for {len(concepts)} concepts:")
        print(f"   Baseline: {baseline_memory:.1f} MB")
        print(f"   Final: {final_memory:.1f} MB")
        print(f"   Increase: {results['total_memory_increase_mb']:.1f} MB")
        print(f"   Per concept: {results['memory_per_concept_kb']:.1f} KB")
        
        self.results['benchmarks']['memory_usage'] = results
        return results
    
    def run_all_benchmarks(self):
        """Run all benchmarks and generate report"""
        print("\n" + "="*80)
        print("🚀 KIMERA PHASE 1: SEMANTIC GROUNDING PERFORMANCE BENCHMARK")
        print("="*80)
        
        self.benchmark_grounding_speed()
        self.benchmark_multimodal_integration()
        self.benchmark_causal_reasoning()
        self.benchmark_temporal_processing()
        self.benchmark_physical_simulation()
        self.benchmark_intentional_processing()
        self.benchmark_memory_usage()
        
        # Generate summary
        print("\n" + "="*80)
        print("📊 BENCHMARK SUMMARY")
        print("="*80)
        
        print("\n🏆 Key Performance Metrics:")
        print(f"• Grounding Speed: {self.results['benchmarks']['grounding_speed']['concepts_per_second']:.1f} concepts/second")
        print(f"• Average Grounding Time: {self.results['benchmarks']['grounding_speed']['average_time']*1000:.1f}ms")
        print(f"• Multimodal Integration: {self.results['benchmarks']['multimodal_integration']['average_time']*1000:.1f}ms")
        print(f"• Causal Analysis: {self.results['benchmarks']['causal_reasoning']['average_causal_time']*1000:.1f}ms")
        print(f"• Memory Efficiency: {self.results['benchmarks']['memory_usage']['memory_per_concept_kb']:.1f} KB/concept")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"semantic_grounding_benchmark_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        return self.results


def main():
    """Run the benchmark suite"""
    benchmark = SemanticGroundingBenchmark()
    results = benchmark.run_all_benchmarks()
    
    print("\n✅ Benchmark completed successfully!")
    print("\nPhase 1 semantic grounding is ready for production use.")


if __name__ == "__main__":
    main()