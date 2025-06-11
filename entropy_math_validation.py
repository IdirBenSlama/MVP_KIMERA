#!/usr/bin/env python3
"""
KIMERA SWM Entropy Metrics Mathematical Validation
==================================================

This script validates all mathematical calculations from the entropy stress test
to ensure accuracy and identify any computational errors.
"""

import json
import math
from datetime import datetime

def load_entropy_data():
    """Load the entropy stress test data"""
    try:
        with open("entropy_stress_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ entropy_stress_results.json not found")
        return None

def validate_basic_metrics(data):
    """Validate basic metrics calculations"""
    print("🔢 VALIDATING BASIC METRICS")
    print("=" * 50)
    
    entropy_history = data["entropy_history"]
    cascade_results = data["results"]["Entropy Cascade Test"]
    
    # Extract data arrays
    timestamps = [h["timestamp"] for h in entropy_history]
    entropies = [h["entropy"] for h in entropy_history]
    geoid_counts = [h["active_geoids"] for h in entropy_history]
    vault_a_scars = [h["vault_a_scars"] for h in entropy_history]
    vault_b_scars = [h["vault_b_scars"] for h in entropy_history]
    
    # Normalize timestamps
    start_time = timestamps[0]
    normalized_times = [(t - start_time) for t in timestamps]
    
    print(f"📊 Data Points Validation:")
    print(f"   Entropy samples: {len(entropies)} ✓")
    print(f"   Time samples: {len(normalized_times)} ✓")
    print(f"   Data consistency: {'✓' if len(entropies) == len(normalized_times) == len(geoid_counts) else '❌'}")
    
    # Validate entropy range calculation
    calculated_min = min(entropies)
    calculated_max = max(entropies)
    calculated_range = calculated_max - calculated_min
    
    print(f"\n🌡️  Entropy Range Validation:")
    print(f"   Minimum entropy: {calculated_min:.6f}")
    print(f"   Maximum entropy: {calculated_max:.6f}")
    print(f"   Calculated range: {calculated_range:.6f}")
    print(f"   Reported range: 123.6443")
    print(f"   Range accuracy: {'✓' if abs(calculated_range - 123.6443) < 0.001 else '❌'}")
    
    # Validate test duration
    calculated_duration = normalized_times[-1]
    reported_duration = cascade_results["total_time"]
    
    print(f"\n⏱️  Duration Validation:")
    print(f"   Calculated duration: {calculated_duration:.2f}s")
    print(f"   Reported duration: {reported_duration:.2f}s")
    print(f"   Duration accuracy: {'✓' if abs(calculated_duration - reported_duration) < 1.0 else '❌'}")
    
    return {
        "entropy_range": calculated_range,
        "duration": calculated_duration,
        "min_entropy": calculated_min,
        "max_entropy": calculated_max,
        "data_points": len(entropies)
    }

def validate_contradiction_metrics(data):
    """Validate contradiction and scar metrics"""
    print("\n💥 VALIDATING CONTRADICTION METRICS")
    print("=" * 50)
    
    cascade_results = data["results"]["Entropy Cascade Test"]
    entropy_history = data["entropy_history"]
    
    # Extract reported values
    target_pairs = cascade_results["target_pairs"]
    created_pairs = cascade_results["created_pairs"]
    total_contradictions = cascade_results["total_contradictions"]
    total_scars = cascade_results["total_scars"]
    
    # Validate contradictions per pair
    calculated_contradictions_per_pair = total_contradictions / created_pairs if created_pairs > 0 else 0
    reported_contradictions_per_pair = 51.0
    
    print(f"🎯 Contradiction Analysis:")
    print(f"   Target pairs: {target_pairs}")
    print(f"   Created pairs: {created_pairs}")
    print(f"   Total contradictions: {total_contradictions}")
    print(f"   Calculated contradictions/pair: {calculated_contradictions_per_pair:.1f}")
    print(f"   Reported contradictions/pair: {reported_contradictions_per_pair:.1f}")
    print(f"   Contradictions/pair accuracy: {'✓' if abs(calculated_contradictions_per_pair - reported_contradictions_per_pair) < 0.1 else '❌'}")
    
    # Validate scars per pair
    calculated_scars_per_pair = total_scars / created_pairs if created_pairs > 0 else 0
    reported_scars_per_pair = 51.0
    
    print(f"\n🔗 Scar Analysis:")
    print(f"   Total scars: {total_scars}")
    print(f"   Calculated scars/pair: {calculated_scars_per_pair:.1f}")
    print(f"   Reported scars/pair: {reported_scars_per_pair:.1f}")
    print(f"   Scars/pair accuracy: {'✓' if abs(calculated_scars_per_pair - reported_scars_per_pair) < 0.1 else '❌'}")
    
    # Validate scar-contradiction ratio
    scar_contradiction_ratio = total_scars / total_contradictions if total_contradictions > 0 else 0
    
    print(f"\n⚖️  Scar-Contradiction Ratio:")
    print(f"   Calculated ratio: {scar_contradiction_ratio:.6f}")
    print(f"   Expected ratio: ~1.0 (1 scar per contradiction)")
    print(f"   Ratio accuracy: {'✓' if abs(scar_contradiction_ratio - 1.0) < 0.01 else '❌'}")
    
    # Validate final scar counts from entropy history
    final_vault_a = entropy_history[-1]["vault_a_scars"]
    final_vault_b = entropy_history[-1]["vault_b_scars"]
    calculated_total_scars = final_vault_a + final_vault_b
    
    print(f"\n🏛️  Vault Scar Validation:")
    print(f"   Final Vault A scars: {final_vault_a}")
    print(f"   Final Vault B scars: {final_vault_b}")
    print(f"   Calculated total: {calculated_total_scars}")
    print(f"   Reported total: {total_scars}")
    print(f"   Vault total accuracy: {'✓' if abs(calculated_total_scars - total_scars) < 5 else '❌'}")
    
    # Vault balance validation
    vault_imbalance = abs(final_vault_a - final_vault_b)
    print(f"   Vault imbalance: {vault_imbalance}")
    print(f"   Balance quality: {'EXCELLENT' if vault_imbalance <= 1 else 'GOOD' if vault_imbalance <= 5 else 'POOR'}")
    
    return {
        "contradictions_per_pair": calculated_contradictions_per_pair,
        "scars_per_pair": calculated_scars_per_pair,
        "scar_contradiction_ratio": scar_contradiction_ratio,
        "vault_imbalance": vault_imbalance,
        "total_scars_calculated": calculated_total_scars
    }

def validate_rate_calculations(data):
    """Validate all rate calculations"""
    print("\n⚡ VALIDATING RATE CALCULATIONS")
    print("=" * 50)
    
    cascade_results = data["results"]["Entropy Cascade Test"]
    entropy_history = data["entropy_history"]
    
    # Time calculations
    timestamps = [h["timestamp"] for h in entropy_history]
    normalized_times = [(t - timestamps[0]) for t in timestamps]
    total_duration = normalized_times[-1]
    
    # Scar generation rate
    final_scars = entropy_history[-1]["vault_a_scars"] + entropy_history[-1]["vault_b_scars"]
    initial_scars = entropy_history[0]["vault_a_scars"] + entropy_history[0]["vault_b_scars"]
    net_scars_generated = final_scars - initial_scars
    
    calculated_scar_rate = net_scars_generated / total_duration
    reported_scar_rate = 4.91
    
    print(f"🔗 Scar Generation Rate:")
    print(f"   Initial scars: {initial_scars}")
    print(f"   Final scars: {final_scars}")
    print(f"   Net scars generated: {net_scars_generated}")
    print(f"   Test duration: {total_duration:.2f}s")
    print(f"   Calculated rate: {calculated_scar_rate:.2f} scars/second")
    print(f"   Reported rate: {reported_scar_rate:.2f} scars/second")
    print(f"   Rate accuracy: {'✓' if abs(calculated_scar_rate - reported_scar_rate) < 0.1 else '❌'}")
    
    # Geoid creation rate
    final_geoids = entropy_history[-1]["active_geoids"]
    initial_geoids = entropy_history[0]["active_geoids"]
    net_geoids_created = final_geoids - initial_geoids
    
    calculated_geoid_rate = net_geoids_created / total_duration
    reported_geoid_rate = 0.19
    
    print(f"\n🧠 Geoid Creation Rate:")
    print(f"   Initial geoids: {initial_geoids}")
    print(f"   Final geoids: {final_geoids}")
    print(f"   Net geoids created: {net_geoids_created}")
    print(f"   Calculated rate: {calculated_geoid_rate:.3f} geoids/second")
    print(f"   Reported rate: {reported_geoid_rate:.3f} geoids/second")
    print(f"   Rate accuracy: {'✓' if abs(calculated_geoid_rate - reported_geoid_rate) < 0.01 else '❌'}")
    
    # Contradiction pair processing rate
    created_pairs = cascade_results["created_pairs"]
    test_duration = cascade_results["total_time"]
    
    calculated_pair_rate = created_pairs / test_duration
    reported_pair_rate = 0.097
    
    print(f"\n💥 Contradiction Pair Rate:")
    print(f"   Created pairs: {created_pairs}")
    print(f"   Test duration: {test_duration:.2f}s")
    print(f"   Calculated rate: {calculated_pair_rate:.3f} pairs/second")
    print(f"   Reported rate: {reported_pair_rate:.3f} pairs/second")
    print(f"   Rate accuracy: {'✓' if abs(calculated_pair_rate - reported_pair_rate) < 0.001 else '❌'}")
    
    # Average time per pair
    calculated_time_per_pair = test_duration / created_pairs
    reported_time_per_pair = 10.35
    
    print(f"\n⏱️  Time per Pair:")
    print(f"   Calculated time/pair: {calculated_time_per_pair:.2f} seconds")
    print(f"   Reported time/pair: {reported_time_per_pair:.2f} seconds")
    print(f"   Time/pair accuracy: {'✓' if abs(calculated_time_per_pair - reported_time_per_pair) < 0.1 else '❌'}")
    
    return {
        "scar_rate": calculated_scar_rate,
        "geoid_rate": calculated_geoid_rate,
        "pair_rate": calculated_pair_rate,
        "time_per_pair": calculated_time_per_pair
    }

def validate_entropy_statistics(data):
    """Validate entropy statistical calculations"""
    print("\n📊 VALIDATING ENTROPY STATISTICS")
    print("=" * 50)
    
    entropy_history = data["entropy_history"]
    entropies = [h["entropy"] for h in entropy_history]
    
    # Entropy changes between phases
    entropy_changes = [entropies[i+1] - entropies[i] for i in range(len(entropies)-1)]
    
    # Average entropy change
    calculated_avg_change = sum(entropy_changes) / len(entropy_changes)
    reported_avg_change = -8.2038
    
    print(f"📈 Entropy Change Analysis:")
    print(f"   Number of entropy changes: {len(entropy_changes)}")
    print(f"   Calculated avg change: {calculated_avg_change:.4f}")
    print(f"   Reported avg change: {reported_avg_change:.4f}")
    print(f"   Avg change accuracy: {'✓' if abs(calculated_avg_change - reported_avg_change) < 0.001 else '❌'}")
    
    # Maximum and minimum entropy jumps
    calculated_max_jump = max(entropy_changes)
    calculated_min_jump = min(entropy_changes)
    reported_max_jump = 61.7595
    reported_min_jump = -123.6443
    
    print(f"\n🔄 Entropy Jump Analysis:")
    print(f"   Calculated max jump: {calculated_max_jump:.4f}")
    print(f"   Reported max jump: {reported_max_jump:.4f}")
    print(f"   Max jump accuracy: {'✓' if abs(calculated_max_jump - reported_max_jump) < 0.001 else '❌'}")
    
    print(f"   Calculated min jump: {calculated_min_jump:.4f}")
    print(f"   Reported min jump: {reported_min_jump:.4f}")
    print(f"   Min jump accuracy: {'✓' if abs(calculated_min_jump - reported_min_jump) < 0.001 else '❌'}")
    
    # Direction changes (volatility)
    direction_changes = 0
    for i in range(1, len(entropy_changes)):
        if (entropy_changes[i] > 0) != (entropy_changes[i-1] > 0):
            direction_changes += 1
    
    reported_direction_changes = 4
    
    print(f"\n🌊 Entropy Volatility:")
    print(f"   Calculated direction changes: {direction_changes}")
    print(f"   Reported direction changes: {reported_direction_changes}")
    print(f"   Direction changes accuracy: {'✓' if direction_changes == reported_direction_changes else '❌'}")
    
    # Negative entropy phases
    negative_phases = sum(1 for e in entropies if e < 0)
    total_phases = len(entropies)
    reported_negative_phases = 3
    
    print(f"\n❄️  Negative Entropy Analysis:")
    print(f"   Calculated negative phases: {negative_phases}/{total_phases}")
    print(f"   Reported negative phases: {reported_negative_phases}/7")
    print(f"   Negative phases accuracy: {'✓' if negative_phases == reported_negative_phases else '❌'}")
    
    # Entropy variance calculation
    mean_entropy = sum(entropies) / len(entropies)
    calculated_variance = sum((e - mean_entropy)**2 for e in entropies) / len(entropies)
    reported_variance = 1693.324967
    
    print(f"\n📊 Entropy Variance:")
    print(f"   Mean entropy: {mean_entropy:.6f}")
    print(f"   Calculated variance: {calculated_variance:.6f}")
    print(f"   Reported variance: {reported_variance:.6f}")
    print(f"   Variance accuracy: {'✓' if abs(calculated_variance - reported_variance) < 0.001 else '❌'}")
    
    return {
        "avg_change": calculated_avg_change,
        "max_jump": calculated_max_jump,
        "min_jump": calculated_min_jump,
        "direction_changes": direction_changes,
        "negative_phases": negative_phases,
        "variance": calculated_variance
    }

def validate_derived_metrics(data, basic_metrics, contradiction_metrics, rate_metrics):
    """Validate derived and complex metrics"""
    print("\n🧮 VALIDATING DERIVED METRICS")
    print("=" * 50)
    
    entropy_history = data["entropy_history"]
    cascade_results = data["results"]["Entropy Cascade Test"]
    
    # Entropy per scar calculation
    initial_entropy = entropy_history[0]["entropy"]
    final_entropy = entropy_history[-1]["entropy"]
    entropy_change = abs(final_entropy - initial_entropy)
    
    final_scars = contradiction_metrics["total_scars_calculated"]
    calculated_entropy_per_scar = entropy_change / final_scars if final_scars > 0 else 0
    reported_entropy_per_scar = 0.032109
    
    print(f"🔗 Entropy per Scar:")
    print(f"   Initial entropy: {initial_entropy:.6f}")
    print(f"   Final entropy: {final_entropy:.6f}")
    print(f"   Entropy change: {entropy_change:.6f}")
    print(f"   Total scars: {final_scars}")
    print(f"   Calculated entropy/scar: {calculated_entropy_per_scar:.6f}")
    print(f"   Reported entropy/scar: {reported_entropy_per_scar:.6f}")
    print(f"   Entropy/scar accuracy: {'✓' if abs(calculated_entropy_per_scar - reported_entropy_per_scar) < 0.000001 else '❌'}")
    
    # Success rate validation (should be 100% for created pairs)
    target_pairs = cascade_results["target_pairs"]
    created_pairs = cascade_results["created_pairs"]
    failed_pairs = cascade_results["failed_pairs"]
    
    calculated_success_rate = (created_pairs / target_pairs) * 100
    calculated_failure_rate = (failed_pairs / target_pairs) * 100
    
    print(f"\n✅ Success Rate Analysis:")
    print(f"   Target pairs: {target_pairs}")
    print(f"   Created pairs: {created_pairs}")
    print(f"   Failed pairs: {failed_pairs}")
    print(f"   Calculated success rate: {calculated_success_rate:.1f}%")
    print(f"   Calculated failure rate: {calculated_failure_rate:.1f}%")
    print(f"   Total validation: {'✓' if created_pairs + failed_pairs == target_pairs else '❌'}")
    
    return {
        "entropy_per_scar": calculated_entropy_per_scar,
        "success_rate": calculated_success_rate,
        "failure_rate": calculated_failure_rate
    }

def generate_validation_report(data, validations):
    """Generate comprehensive validation report"""
    print("\n" + "=" * 60)
    print("📋 MATHEMATICAL VALIDATION REPORT")
    print("=" * 60)
    
    # Count accurate vs inaccurate calculations
    all_checks = []
    
    # Basic metrics checks
    basic = validations["basic"]
    all_checks.extend([
        abs(basic["entropy_range"] - 123.6443) < 0.001,
        abs(basic["duration"] - 310.35) < 1.0
    ])
    
    # Contradiction metrics checks
    contradiction = validations["contradiction"]
    all_checks.extend([
        abs(contradiction["contradictions_per_pair"] - 51.0) < 0.1,
        abs(contradiction["scars_per_pair"] - 51.0) < 0.1,
        abs(contradiction["scar_contradiction_ratio"] - 1.0) < 0.01
    ])
    
    # Rate calculations checks
    rates = validations["rates"]
    all_checks.extend([
        abs(rates["scar_rate"] - 4.91) < 0.1,
        abs(rates["geoid_rate"] - 0.19) < 0.01,
        abs(rates["pair_rate"] - 0.097) < 0.001
    ])
    
    # Entropy statistics checks
    entropy_stats = validations["entropy_stats"]
    all_checks.extend([
        abs(entropy_stats["avg_change"] - (-8.2038)) < 0.001,
        abs(entropy_stats["max_jump"] - 61.7595) < 0.001,
        abs(entropy_stats["min_jump"] - (-123.6443)) < 0.001,
        entropy_stats["direction_changes"] == 4,
        entropy_stats["negative_phases"] == 3
    ])
    
    # Derived metrics checks
    derived = validations["derived"]
    all_checks.extend([
        abs(derived["entropy_per_scar"] - 0.032109) < 0.000001,
        derived["success_rate"] == 100.0
    ])
    
    accurate_count = sum(all_checks)
    total_count = len(all_checks)
    accuracy_percentage = (accurate_count / total_count) * 100
    
    print(f"📊 VALIDATION SUMMARY:")
    print(f"   Total metrics validated: {total_count}")
    print(f"   Accurate calculations: {accurate_count}")
    print(f"   Inaccurate calculations: {total_count - accurate_count}")
    print(f"   Overall accuracy: {accuracy_percentage:.1f}%")
    
    if accuracy_percentage == 100.0:
        verdict = "✅ ALL METRICS MATHEMATICALLY CORRECT"
        grade = "PERFECT"
    elif accuracy_percentage >= 95.0:
        verdict = "✅ METRICS HIGHLY ACCURATE"
        grade = "EXCELLENT"
    elif accuracy_percentage >= 90.0:
        verdict = "⚠️  METRICS MOSTLY ACCURATE"
        grade = "GOOD"
    else:
        verdict = "❌ SIGNIFICANT CALCULATION ERRORS"
        grade = "POOR"
    
    print(f"\n🎯 MATHEMATICAL VALIDATION VERDICT:")
    print(f"   Grade: {grade}")
    print(f"   Verdict: {verdict}")
    
    # Detailed error analysis
    if accuracy_percentage < 100.0:
        print(f"\n🔍 ERROR ANALYSIS:")
        error_categories = []
        
        if not all_checks[0:2]:  # Basic metrics
            error_categories.append("Basic calculations (range, duration)")
        if not all_checks[2:5]:  # Contradiction metrics
            error_categories.append("Contradiction/scar calculations")
        if not all_checks[5:8]:  # Rate calculations
            error_categories.append("Rate calculations")
        if not all_checks[8:13]:  # Entropy statistics
            error_categories.append("Entropy statistics")
        if not all_checks[13:15]:  # Derived metrics
            error_categories.append("Derived metrics")
        
        for category in error_categories:
            print(f"   - {category}")
    
    return {
        "total_metrics": total_count,
        "accurate_metrics": accurate_count,
        "accuracy_percentage": accuracy_percentage,
        "verdict": verdict,
        "grade": grade
    }

def main():
    """Main validation function"""
    print("🔢 KIMERA ENTROPY METRICS MATHEMATICAL VALIDATION")
    print("=" * 60)
    
    # Load data
    data = load_entropy_data()
    if not data:
        return
    
    # Run all validations
    validations = {}
    validations["basic"] = validate_basic_metrics(data)
    validations["contradiction"] = validate_contradiction_metrics(data)
    validations["rates"] = validate_rate_calculations(data)
    validations["entropy_stats"] = validate_entropy_statistics(data)
    validations["derived"] = validate_derived_metrics(data, validations["basic"], 
                                                     validations["contradiction"], 
                                                     validations["rates"])
    
    # Generate final report
    report = generate_validation_report(data, validations)
    
    # Save validation results
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "validations": validations,
        "report": report
    }
    
    with open("entropy_validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n💾 Validation results saved to entropy_validation_results.json")

if __name__ == "__main__":
    main()