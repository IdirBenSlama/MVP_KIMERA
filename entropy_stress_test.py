#!/usr/bin/env python3
"""
KIMERA SWM Entropy Stress Test Suite
====================================

This test pushes the entropy and thermodynamic systems to their limits:
1. Massive semantic contradiction generation
2. Entropy cascade testing
3. Thermodynamic pressure overload
4. Semantic polarity extremes
5. Entropy oscillation patterns
6. System stability under entropy chaos

The goal is to test the system's entropy handling at scale and find entropy-related breaking points.
"""

import os
import sys
import time
import threading
import concurrent.futures
import random
import requests
import json
import math
from datetime import datetime
from typing import List, Dict, Any

# Set environment for entropy testing
os.environ["LIGHTWEIGHT_EMBEDDING"] = "1"
os.environ["ENABLE_JOBS"] = "0"

class EntropyStressTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = {}
        self.entropy_history = []
        self.contradiction_count = 0
        self.scar_count = 0
        
    def get_system_entropy(self):
        """Get current system entropy"""
        try:
            response = requests.get(f"{self.base_url}/system/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                entropy = data.get('system_entropy', 0.0)
                self.entropy_history.append({
                    'timestamp': time.time(),
                    'entropy': entropy,
                    'active_geoids': data.get('active_geoids', 0),
                    'vault_a_scars': data.get('vault_a_scars', 0),
                    'vault_b_scars': data.get('vault_b_scars', 0)
                })
                return entropy
            return None
        except Exception as e:
            print(f"   ❌ Error getting entropy: {e}")
            return None

    def create_contradictory_geoid_pair(self, concept: str, intensity: float = 1.0):
        """Create a pair of highly contradictory geoids"""
        # Positive concept
        positive_features = {
            f"{concept}_positive": intensity,
            f"{concept}_strength": intensity,
            "polarity": intensity,
            "certainty": intensity,
            "semantic_weight": intensity
        }
        
        # Negative concept (direct contradiction)
        negative_features = {
            f"{concept}_positive": -intensity,
            f"{concept}_strength": intensity,
            "polarity": -intensity,
            "certainty": intensity,
            "semantic_weight": intensity
        }
        
        # Add noise features to increase complexity
        for i in range(random.randint(5, 15)):
            feature_name = f"noise_{i}"
            noise_value = random.uniform(-0.5, 0.5)
            positive_features[feature_name] = noise_value
            negative_features[feature_name] = -noise_value  # Opposite noise
        
        geoid_pair = []
        
        # Create positive geoid
        try:
            response = requests.post(f"{self.base_url}/geoids", json={
                "semantic_features": positive_features,
                "symbolic_content": {
                    "concept": concept,
                    "polarity": "positive",
                    "intensity": intensity,
                    "type": "entropy_stress_test"
                },
                "metadata": {
                    "test_type": "entropy_stress",
                    "concept": concept,
                    "polarity": "positive"
                }
            }, timeout=15)
            
            if response.status_code == 200:
                geoid_pair.append(response.json()["geoid_id"])
        except Exception as e:
            print(f"   ❌ Error creating positive geoid: {e}")
        
        # Create negative geoid
        try:
            response = requests.post(f"{self.base_url}/geoids", json={
                "semantic_features": negative_features,
                "symbolic_content": {
                    "concept": concept,
                    "polarity": "negative",
                    "intensity": intensity,
                    "type": "entropy_stress_test"
                },
                "metadata": {
                    "test_type": "entropy_stress",
                    "concept": concept,
                    "polarity": "negative"
                }
            }, timeout=15)
            
            if response.status_code == 200:
                geoid_pair.append(response.json()["geoid_id"])
        except Exception as e:
            print(f"   ❌ Error creating negative geoid: {e}")
        
        return geoid_pair

    def entropy_cascade_test(self, num_contradiction_pairs: int = 50, intensity_range: tuple = (0.5, 1.0)):
        """Create cascading contradictions to test entropy handling"""
        print(f"\n🌪️  ENTROPY CASCADE TEST: Creating {num_contradiction_pairs} contradiction pairs")
        
        start_time = time.time()
        initial_entropy = self.get_system_entropy()
        created_pairs = 0
        failed_pairs = 0
        
        concepts = [
            "temperature", "morality", "size", "speed", "intelligence", 
            "beauty", "truth", "justice", "freedom", "order",
            "chaos", "light", "darkness", "life", "death",
            "love", "hate", "peace", "war", "creation",
            "destruction", "knowledge", "ignorance", "hope", "despair"
        ]
        
        print(f"   Initial entropy: {initial_entropy}")
        
        for i in range(num_contradiction_pairs):
            try:
                concept = random.choice(concepts)
                intensity = random.uniform(*intensity_range)
                
                pair = self.create_contradictory_geoid_pair(concept, intensity)
                
                if len(pair) == 2:
                    created_pairs += 1
                    
                    # Trigger contradiction processing
                    try:
                        response = requests.post(f"{self.base_url}/process/contradictions", json={
                            "trigger_geoid_id": pair[0],
                            "search_limit": 10
                        }, timeout=20)
                        
                        if response.status_code == 200:
                            result = response.json()
                            self.contradiction_count += result.get("contradictions_detected", 0)
                            self.scar_count += result.get("scars_created", 0)
                    except Exception as e:
                        print(f"   ⚠️  Contradiction processing failed for pair {i}: {e}")
                else:
                    failed_pairs += 1
                
                # Monitor entropy every 10 pairs
                if i % 10 == 0:
                    current_entropy = self.get_system_entropy()
                    print(f"   Pair {i:2d}: Entropy = {current_entropy:.4f}, "
                          f"Contradictions = {self.contradiction_count}, Scars = {self.scar_count}")
                
                # Small delay to prevent overwhelming
                time.sleep(0.1)
                
            except Exception as e:
                failed_pairs += 1
                print(f"   ❌ Failed to create pair {i}: {e}")
        
        final_entropy = self.get_system_entropy()
        total_time = time.time() - start_time
        
        result = {
            "target_pairs": num_contradiction_pairs,
            "created_pairs": created_pairs,
            "failed_pairs": failed_pairs,
            "initial_entropy": initial_entropy,
            "final_entropy": final_entropy,
            "entropy_delta": final_entropy - initial_entropy if initial_entropy and final_entropy else None,
            "total_contradictions": self.contradiction_count,
            "total_scars": self.scar_count,
            "total_time": round(total_time, 2),
            "pairs_per_second": round(created_pairs / total_time, 2)
        }
        
        self.results["Entropy Cascade Test"] = result
        print(f"   ✅ Cascade completed: {created_pairs} pairs, entropy Δ = {result['entropy_delta']:.4f}")
        return result

    def thermodynamic_pressure_test(self, pressure_cycles: int = 20, geoids_per_cycle: int = 25):
        """Test system under extreme thermodynamic pressure"""
        print(f"\n🔥 THERMODYNAMIC PRESSURE TEST: {pressure_cycles} cycles, {geoids_per_cycle} geoids each")
        
        start_time = time.time()
        initial_entropy = self.get_system_entropy()
        cycle_results = []
        
        for cycle in range(pressure_cycles):
            cycle_start = time.time()
            cycle_entropy_start = self.get_system_entropy()
            
            # Create high-pressure semantic environment
            def create_pressure_geoid():
                # Generate extreme semantic features
                features = {}
                
                # Create high-magnitude, conflicting features
                for i in range(random.randint(20, 40)):
                    feature_name = f"pressure_feature_{i}"
                    # Extreme values to create thermodynamic pressure
                    features[feature_name] = random.choice([-1.0, -0.9, 0.9, 1.0])
                
                # Add thermodynamic indicators
                features.update({
                    "thermodynamic_pressure": random.uniform(0.8, 1.0),
                    "semantic_tension": random.uniform(0.7, 1.0),
                    "entropy_catalyst": random.uniform(-1.0, 1.0),
                    "system_stress": random.uniform(0.5, 1.0)
                })
                
                try:
                    response = requests.post(f"{self.base_url}/geoids", json={
                        "semantic_features": features,
                        "symbolic_content": {
                            "type": "thermodynamic_pressure",
                            "cycle": cycle,
                            "pressure_level": "extreme"
                        },
                        "metadata": {
                            "test_type": "thermodynamic_pressure",
                            "cycle": cycle
                        }
                    }, timeout=15)
                    
                    return response.status_code == 200
                except:
                    return False
            
            # Create geoids concurrently for maximum pressure
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(create_pressure_geoid) for _ in range(geoids_per_cycle)]
                successful = sum(1 for f in concurrent.futures.as_completed(futures, timeout=60) if f.result())
            
            # Trigger cognitive cycle to process pressure
            try:
                cycle_response = requests.post(f"{self.base_url}/system/cycle", timeout=30)
                cycle_success = cycle_response.status_code == 200
            except:
                cycle_success = False
            
            cycle_entropy_end = self.get_system_entropy()
            cycle_time = time.time() - cycle_start
            
            cycle_result = {
                "cycle": cycle,
                "successful_geoids": successful,
                "cycle_success": cycle_success,
                "entropy_start": cycle_entropy_start,
                "entropy_end": cycle_entropy_end,
                "entropy_delta": cycle_entropy_end - cycle_entropy_start if cycle_entropy_start and cycle_entropy_end else None,
                "cycle_time": round(cycle_time, 2)
            }
            
            cycle_results.append(cycle_result)
            
            print(f"   Cycle {cycle:2d}: {successful:2d}/{geoids_per_cycle} geoids, "
                  f"entropy Δ = {cycle_result['entropy_delta']:.4f}, "
                  f"time = {cycle_time:.2f}s")
            
            # Brief pause between cycles
            time.sleep(0.5)
        
        final_entropy = self.get_system_entropy()
        total_time = time.time() - start_time
        
        result = {
            "pressure_cycles": pressure_cycles,
            "geoids_per_cycle": geoids_per_cycle,
            "initial_entropy": initial_entropy,
            "final_entropy": final_entropy,
            "total_entropy_delta": final_entropy - initial_entropy if initial_entropy and final_entropy else None,
            "total_time": round(total_time, 2),
            "cycle_results": cycle_results,
            "avg_cycle_time": round(sum(c["cycle_time"] for c in cycle_results) / len(cycle_results), 2)
        }
        
        self.results["Thermodynamic Pressure Test"] = result
        print(f"   ✅ Pressure test completed: total entropy Δ = {result['total_entropy_delta']:.4f}")
        return result

    def entropy_oscillation_test(self, oscillations: int = 15, amplitude: float = 0.8):
        """Test system with rapid entropy oscillations"""
        print(f"\n🌊 ENTROPY OSCILLATION TEST: {oscillations} oscillations, amplitude {amplitude}")
        
        start_time = time.time()
        initial_entropy = self.get_system_entropy()
        oscillation_results = []
        
        for osc in range(oscillations):
            # Create oscillating semantic patterns
            phase = (osc / oscillations) * 2 * math.pi
            
            # High entropy phase (chaos)
            chaos_features = {
                f"chaos_{i}": amplitude * random.uniform(-1, 1) * math.sin(phase + i)
                for i in range(20)
            }
            chaos_features.update({
                "entropy_driver": amplitude * math.sin(phase),
                "chaos_level": amplitude,
                "oscillation_phase": phase
            })
            
            # Low entropy phase (order)
            order_features = {
                f"order_{i}": amplitude * (0.1 if i % 2 == 0 else -0.1) * math.cos(phase + i)
                for i in range(20)
            }
            order_features.update({
                "entropy_driver": -amplitude * math.cos(phase),
                "order_level": amplitude,
                "oscillation_phase": phase + math.pi
            })
            
            osc_start = time.time()
            entropy_before = self.get_system_entropy()
            
            # Create chaos geoid
            try:
                chaos_response = requests.post(f"{self.base_url}/geoids", json={
                    "semantic_features": chaos_features,
                    "symbolic_content": {"type": "chaos", "oscillation": osc},
                    "metadata": {"test_type": "entropy_oscillation", "phase": "chaos"}
                }, timeout=15)
                chaos_success = chaos_response.status_code == 200
            except:
                chaos_success = False
            
            # Create order geoid
            try:
                order_response = requests.post(f"{self.base_url}/geoids", json={
                    "semantic_features": order_features,
                    "symbolic_content": {"type": "order", "oscillation": osc},
                    "metadata": {"test_type": "entropy_oscillation", "phase": "order"}
                }, timeout=15)
                order_success = order_response.status_code == 200
            except:
                order_success = False
            
            # Process contradictions
            if chaos_success and order_success:
                try:
                    requests.post(f"{self.base_url}/process/contradictions", json={
                        "trigger_geoid_id": chaos_response.json()["geoid_id"],
                        "search_limit": 5
                    }, timeout=20)
                except:
                    pass
            
            entropy_after = self.get_system_entropy()
            osc_time = time.time() - osc_start
            
            oscillation_result = {
                "oscillation": osc,
                "phase": phase,
                "chaos_success": chaos_success,
                "order_success": order_success,
                "entropy_before": entropy_before,
                "entropy_after": entropy_after,
                "entropy_delta": entropy_after - entropy_before if entropy_before and entropy_after else None,
                "time": round(osc_time, 2)
            }
            
            oscillation_results.append(oscillation_result)
            
            print(f"   Oscillation {osc:2d}: phase = {phase:.2f}, "
                  f"entropy Δ = {oscillation_result['entropy_delta']:.4f}")
            
            time.sleep(0.2)
        
        final_entropy = self.get_system_entropy()
        total_time = time.time() - start_time
        
        # Calculate oscillation metrics
        entropy_deltas = [r["entropy_delta"] for r in oscillation_results if r["entropy_delta"] is not None]
        entropy_variance = sum((d - sum(entropy_deltas)/len(entropy_deltas))**2 for d in entropy_deltas) / len(entropy_deltas) if entropy_deltas else 0
        
        result = {
            "oscillations": oscillations,
            "amplitude": amplitude,
            "initial_entropy": initial_entropy,
            "final_entropy": final_entropy,
            "total_entropy_delta": final_entropy - initial_entropy if initial_entropy and final_entropy else None,
            "entropy_variance": round(entropy_variance, 6),
            "total_time": round(total_time, 2),
            "oscillation_results": oscillation_results
        }
        
        self.results["Entropy Oscillation Test"] = result
        print(f"   ✅ Oscillation test completed: variance = {entropy_variance:.6f}")
        return result

    def entropy_saturation_test(self, saturation_target: int = 200):
        """Test system behavior at entropy saturation point"""
        print(f"\n💥 ENTROPY SATURATION TEST: Creating {saturation_target} high-entropy geoids")
        
        start_time = time.time()
        initial_entropy = self.get_system_entropy()
        created_count = 0
        failed_count = 0
        entropy_samples = []
        
        for i in range(saturation_target):
            try:
                # Create maximum entropy geoid
                max_entropy_features = {
                    f"random_feature_{j}": random.uniform(-1, 1)
                    for j in range(random.randint(30, 50))
                }
                
                # Add entropy maximizers
                max_entropy_features.update({
                    "entropy_maximizer": 1.0,
                    "chaos_factor": random.uniform(0.8, 1.0),
                    "uncertainty": random.uniform(0.9, 1.0),
                    "contradiction_seed": random.uniform(-1, 1),
                    "semantic_noise": random.uniform(-0.5, 0.5)
                })
                
                response = requests.post(f"{self.base_url}/geoids", json={
                    "semantic_features": max_entropy_features,
                    "symbolic_content": {
                        "type": "entropy_saturation",
                        "index": i,
                        "entropy_level": "maximum"
                    },
                    "metadata": {
                        "test_type": "entropy_saturation",
                        "target_entropy": "maximum"
                    }
                }, timeout=15)
                
                if response.status_code == 200:
                    created_count += 1
                else:
                    failed_count += 1
                
                # Sample entropy every 20 geoids
                if i % 20 == 0:
                    current_entropy = self.get_system_entropy()
                    entropy_samples.append(current_entropy)
                    print(f"   Created {i:3d}/{saturation_target}: entropy = {current_entropy:.4f}")
                
                # Trigger cognitive cycle occasionally to process entropy
                if i % 50 == 0 and i > 0:
                    try:
                        requests.post(f"{self.base_url}/system/cycle", timeout=30)
                    except:
                        pass
                
                time.sleep(0.05)  # Small delay
                
            except Exception as e:
                failed_count += 1
                if failed_count % 10 == 0:
                    print(f"   ⚠️  {failed_count} failures so far")
        
        final_entropy = self.get_system_entropy()
        total_time = time.time() - start_time
        
        result = {
            "saturation_target": saturation_target,
            "created_geoids": created_count,
            "failed_geoids": failed_count,
            "initial_entropy": initial_entropy,
            "final_entropy": final_entropy,
            "entropy_delta": final_entropy - initial_entropy if initial_entropy and final_entropy else None,
            "entropy_samples": entropy_samples,
            "max_entropy_observed": max(entropy_samples) if entropy_samples else None,
            "total_time": round(total_time, 2),
            "creation_rate": round(created_count / total_time, 2)
        }
        
        self.results["Entropy Saturation Test"] = result
        print(f"   ✅ Saturation test completed: {created_count} geoids, "
              f"max entropy = {result['max_entropy_observed']:.4f}")
        return result

    def run_comprehensive_entropy_stress_test(self):
        """Run the complete entropy stress test suite"""
        print("🌪️  KIMERA SWM COMPREHENSIVE ENTROPY STRESS TEST")
        print("=" * 60)
        print("Testing entropy and thermodynamic systems at scale...")
        print("=" * 60)
        
        test_start = time.time()
        initial_system_state = self.get_system_entropy()
        
        print(f"🔧 Initial System Entropy: {initial_system_state}")
        
        # Run entropy stress tests in order of increasing intensity
        try:
            self.entropy_cascade_test(num_contradiction_pairs=30, intensity_range=(0.6, 1.0))
            self.thermodynamic_pressure_test(pressure_cycles=15, geoids_per_cycle=20)
            self.entropy_oscillation_test(oscillations=12, amplitude=0.9)
            self.entropy_saturation_test(saturation_target=150)
            
        except Exception as e:
            print(f"💥 CRITICAL ENTROPY TEST FAILURE: {e}")
        
        total_test_time = time.time() - test_start
        final_system_state = self.get_system_entropy()
        
        # Generate comprehensive entropy report
        print("\n" + "=" * 60)
        print("🌪️  ENTROPY STRESS TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            print(f"\n🔥 {test_name}:")
            for key, value in result.items():
                if key not in ["cycle_results", "oscillation_results", "entropy_samples"]:
                    print(f"   {key}: {value}")
        
        # Entropy analysis
        print(f"\n📊 ENTROPY ANALYSIS:")
        print(f"   Initial System Entropy: {initial_system_state}")
        print(f"   Final System Entropy: {final_system_state}")
        if initial_system_state and final_system_state:
            total_entropy_change = final_system_state - initial_system_state
            print(f"   Total Entropy Change: {total_entropy_change:.6f}")
        
        print(f"   Total Contradictions Generated: {self.contradiction_count}")
        print(f"   Total Scars Created: {self.scar_count}")
        print(f"   Entropy Samples Collected: {len(self.entropy_history)}")
        
        # Entropy stability analysis
        if len(self.entropy_history) > 1:
            entropies = [h['entropy'] for h in self.entropy_history]
            entropy_range = max(entropies) - min(entropies)
            entropy_variance = sum((e - sum(entropies)/len(entropies))**2 for e in entropies) / len(entropies)
            
            print(f"   Entropy Range: {entropy_range:.6f}")
            print(f"   Entropy Variance: {entropy_variance:.6f}")
            print(f"   Entropy Stability: {'HIGH' if entropy_variance < 0.01 else 'MEDIUM' if entropy_variance < 0.1 else 'LOW'}")
        
        print(f"\n⏱️  Total Test Duration: {round(total_test_time, 2)} seconds")
        
        # Final system health check
        try:
            final_status = requests.get(f"{self.base_url}/system/status", timeout=10)
            if final_status.status_code == 200:
                status_data = final_status.json()
                print(f"\n🏁 FINAL SYSTEM STATUS:")
                print(f"   Active Geoids: {status_data.get('active_geoids', 'N/A')}")
                print(f"   System Entropy: {status_data.get('system_entropy', 'N/A')}")
                print(f"   Vault A Scars: {status_data.get('vault_a_scars', 'N/A')}")
                print(f"   Vault B Scars: {status_data.get('vault_b_scars', 'N/A')}")
                print(f"   Cycle Count: {status_data.get('cycle_count', 'N/A')}")
                system_survived = True
            else:
                print(f"\n💀 SYSTEM COMPROMISED: Status check returned {final_status.status_code}")
                system_survived = False
        except Exception as e:
            print(f"\n💀 SYSTEM UNRESPONSIVE: {e}")
            system_survived = False
        
        # Overall entropy stress assessment
        if system_survived:
            if final_system_state and initial_system_state:
                entropy_change = abs(final_system_state - initial_system_state)
                if entropy_change < 0.1:
                    print("\n🎉 ENTROPY STRESS TEST VERDICT: EXCELLENT ENTROPY STABILITY!")
                    print("   System maintained entropy equilibrium under extreme stress")
                elif entropy_change < 0.5:
                    print("\n✅ ENTROPY STRESS TEST VERDICT: GOOD ENTROPY HANDLING")
                    print("   System showed controlled entropy response")
                else:
                    print("\n⚠️  ENTROPY STRESS TEST VERDICT: ENTROPY SENSITIVITY DETECTED")
                    print("   System showed significant entropy fluctuations")
            else:
                print("\n✅ ENTROPY STRESS TEST VERDICT: SYSTEM SURVIVED")
                print("   System remained responsive despite entropy stress")
        else:
            print("\n💥 ENTROPY STRESS TEST VERDICT: ENTROPY OVERLOAD")
            print("   System reached entropy-related breaking point")
        
        return self.results, self.entropy_history

if __name__ == "__main__":
    print("Initializing KIMERA Entropy Stress Tester...")
    print("⚠️  WARNING: This will create extreme entropy conditions!")
    
    tester = EntropyStressTester()
    
    try:
        results, entropy_history = tester.run_comprehensive_entropy_stress_test()
        
        # Save comprehensive results
        with open("entropy_stress_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "entropy_history": entropy_history,
                "total_contradictions": tester.contradiction_count,
                "total_scars": tester.scar_count
            }, f, indent=2)
        
        print(f"\n💾 Entropy stress test results saved to entropy_stress_results.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Entropy stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical entropy test failure: {e}")
        import traceback
        traceback.print_exc()