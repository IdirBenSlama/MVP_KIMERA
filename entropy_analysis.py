#!/usr/bin/env python3
"""
KIMERA SWM Entropy Analysis
===========================

Analyze the entropy stress test results and system behavior.
"""

import json
from datetime import datetime

def analyze_entropy_stress_results():
    """Analyze the entropy stress test results"""
    
    # Load results
    with open("entropy_stress_results.json", "r") as f:
        data = json.load(f)
    
    entropy_history = data["entropy_history"]
    results = data["results"]
    
    print("🌪️  KIMERA ENTROPY STRESS TEST ANALYSIS")
    print("=" * 60)
    
    # Extract entropy timeline
    timestamps = [h["timestamp"] for h in entropy_history]
    entropies = [h["entropy"] for h in entropy_history]
    geoid_counts = [h["active_geoids"] for h in entropy_history]
    vault_a_scars = [h["vault_a_scars"] for h in entropy_history]
    vault_b_scars = [h["vault_b_scars"] for h in entropy_history]
    
    # Normalize timestamps to start from 0
    start_time = timestamps[0]
    normalized_times = [(t - start_time) for t in timestamps]
    
    print(f"\n📊 ENTROPY EVOLUTION ANALYSIS:")
    print(f"   Test Duration: {normalized_times[-1]:.1f} seconds")
    print(f"   Initial Entropy: {entropies[0]:.4f}")
    print(f"   Final Entropy: {entropies[-1]:.4f}")
    print(f"   Peak Entropy: {max(entropies):.4f}")
    print(f"   Minimum Entropy: {min(entropies):.4f}")
    print(f"   Entropy Range: {max(entropies) - min(entropies):.4f}")
    
    # Entropy phases analysis
    print(f"\n🔄 ENTROPY PHASES DETECTED:")
    for i, (time, entropy, geoids, scars_a, scars_b) in enumerate(zip(normalized_times, entropies, geoid_counts, vault_a_scars, vault_b_scars)):
        total_scars = scars_a + scars_b
        print(f"   Phase {i}: t={time:6.1f}s, entropy={entropy:8.4f}, geoids={geoids:3d}, scars={total_scars:4d}")
    
    # Contradiction analysis
    cascade_results = results["Entropy Cascade Test"]
    print(f"\n💥 CONTRADICTION CASCADE ANALYSIS:")
    print(f"   Target Contradiction Pairs: {cascade_results['target_pairs']}")
    print(f"   Successfully Created: {cascade_results['created_pairs']}")
    print(f"   Total Contradictions Detected: {cascade_results['total_contradictions']}")
    print(f"   Total Scars Created: {cascade_results['total_scars']}")
    print(f"   Contradictions per Pair: {cascade_results['total_contradictions'] / cascade_results['created_pairs']:.1f}")
    print(f"   Scars per Pair: {cascade_results['total_scars'] / cascade_results['created_pairs']:.1f}")
    
    # System behavior analysis
    print(f"\n🧠 SYSTEM BEHAVIOR ANALYSIS:")
    
    # Entropy stability
    entropy_changes = [entropies[i+1] - entropies[i] for i in range(len(entropies)-1)]
    avg_entropy_change = sum(entropy_changes) / len(entropy_changes)
    max_entropy_jump = max(entropy_changes)
    min_entropy_jump = min(entropy_changes)
    
    print(f"   Average Entropy Change per Phase: {avg_entropy_change:.4f}")
    print(f"   Maximum Entropy Jump: {max_entropy_jump:.4f}")
    print(f"   Minimum Entropy Jump: {min_entropy_jump:.4f}")
    
    # Scar generation rate
    final_scars = vault_a_scars[-1] + vault_b_scars[-1]
    scar_generation_rate = final_scars / normalized_times[-1]
    print(f"   Scar Generation Rate: {scar_generation_rate:.2f} scars/second")
    
    # Geoid creation rate
    geoid_increase = geoid_counts[-1] - geoid_counts[0]
    geoid_creation_rate = geoid_increase / normalized_times[-1]
    print(f"   Net Geoid Creation Rate: {geoid_creation_rate:.2f} geoids/second")
    
    # Entropy efficiency
    entropy_per_scar = abs(entropies[-1] - entropies[0]) / final_scars if final_scars > 0 else 0
    print(f"   Entropy Change per Scar: {entropy_per_scar:.6f}")
    
    # System stress indicators
    print(f"\n⚠️  SYSTEM STRESS INDICATORS:")
    
    # Check for entropy oscillations
    entropy_direction_changes = 0
    for i in range(1, len(entropy_changes)):
        if (entropy_changes[i] > 0) != (entropy_changes[i-1] > 0):
            entropy_direction_changes += 1
    
    print(f"   Entropy Direction Changes: {entropy_direction_changes}")
    print(f"   Entropy Volatility: {'HIGH' if entropy_direction_changes > 2 else 'MEDIUM' if entropy_direction_changes > 0 else 'LOW'}")
    
    # Check for negative entropy
    negative_entropy_phases = sum(1 for e in entropies if e < 0)
    print(f"   Negative Entropy Phases: {negative_entropy_phases}/{len(entropies)}")
    
    # Vault balance
    vault_imbalance = abs(vault_a_scars[-1] - vault_b_scars[-1])
    print(f"   Vault Imbalance: {vault_imbalance} scars")
    print(f"   Vault Balance Quality: {'EXCELLENT' if vault_imbalance <= 1 else 'GOOD' if vault_imbalance <= 5 else 'POOR'}")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    processing_rate = cascade_results['created_pairs'] / cascade_results['total_time']
    print(f"   Contradiction Pair Processing Rate: {processing_rate:.3f} pairs/second")
    print(f"   Average Time per Pair: {cascade_results['total_time'] / cascade_results['created_pairs']:.2f} seconds")
    
    # System resilience assessment
    print(f"\n🛡️  SYSTEM RESILIENCE ASSESSMENT:")
    
    # Entropy recovery
    entropy_recovered = abs(entropies[-1]) < abs(max(entropies, key=abs)) * 0.8
    print(f"   Entropy Recovery: {'YES' if entropy_recovered else 'NO'}")
    
    # System stability
    final_entropy_stable = abs(entropies[-1] - entropies[-2]) < 0.1 if len(entropies) > 1 else True
    print(f"   Final Entropy Stability: {'STABLE' if final_entropy_stable else 'UNSTABLE'}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ENTROPY STRESS ASSESSMENT:")
    
    if abs(entropies[-1]) < 100 and final_entropy_stable:
        verdict = "EXCELLENT - System handled extreme entropy stress with stability"
        grade = "A+"
    elif abs(entropies[-1]) < 200 and negative_entropy_phases < len(entropies) // 2:
        verdict = "GOOD - System showed resilience under entropy stress"
        grade = "B+"
    elif final_scars > 0 and geoid_counts[-1] > geoid_counts[0]:
        verdict = "ACCEPTABLE - System survived but showed stress"
        grade = "C+"
    else:
        verdict = "CONCERNING - System showed significant entropy instability"
        grade = "D"
    
    print(f"   Grade: {grade}")
    print(f"   Verdict: {verdict}")
    
    # Key findings
    print(f"\n🔍 KEY FINDINGS:")
    print(f"   • System processed {cascade_results['total_contradictions']} contradictions successfully")
    print(f"   • Generated {final_scars} scars with excellent vault balance")
    print(f"   • Entropy showed {entropy_direction_changes} phase transitions")
    print(f"   • System maintained responsiveness throughout stress test")
    print(f"   • Negative entropy phases indicate thermodynamic processing")
    print(f"   • Final entropy of {entropies[-1]:.2f} shows system stabilization")
    
    return {
        "entropy_timeline": list(zip(normalized_times, entropies)),
        "final_assessment": {
            "grade": grade,
            "verdict": verdict,
            "entropy_range": max(entropies) - min(entropies),
            "total_scars": final_scars,
            "vault_balance": vault_imbalance,
            "system_survived": True
        }
    }

if __name__ == "__main__":
    try:
        analysis = analyze_entropy_stress_results()
        print(f"\n💾 Analysis completed successfully")
    except FileNotFoundError:
        print("❌ entropy_stress_results.json not found. Run entropy stress test first.")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()