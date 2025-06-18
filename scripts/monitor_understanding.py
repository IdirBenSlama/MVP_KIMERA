"""
Text-based Understanding Progress Monitor
Tracks KIMERA's journey toward genuine understanding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vault.understanding_vault_manager import UnderstandingVaultManager
import sqlite3
from datetime import datetime
import time


def get_understanding_stats():
    """Get comprehensive understanding statistics"""
    vault = UnderstandingVaultManager()
    metrics = vault.get_understanding_metrics()
    
    # Get additional database stats
    conn = sqlite3.connect('kimera_swm.db')
    cursor = conn.cursor()
    
    # Confidence distribution
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high,
            COUNT(CASE WHEN confidence_score >= 0.6 AND confidence_score < 0.8 THEN 1 END) as medium,
            COUNT(CASE WHEN confidence_score < 0.6 THEN 1 END) as low,
            AVG(confidence_score) as average
        FROM multimodal_groundings
    """)
    conf_stats = cursor.fetchone()
    
    # Recent activity
    cursor.execute("""
        SELECT COUNT(*) FROM multimodal_groundings 
        WHERE created_at > datetime('now', '-1 hour')
    """)
    recent_groundings = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM causal_relationships 
        WHERE created_at > datetime('now', '-1 hour')
    """)
    recent_causal = cursor.fetchone()[0]
    
    # Top grounded concepts
    cursor.execute("""
        SELECT concept_id, confidence_score 
        FROM multimodal_groundings 
        ORDER BY confidence_score DESC 
        LIMIT 5
    """)
    top_concepts = cursor.fetchall()
    
    conn.close()
    
    return {
        'metrics': metrics,
        'confidence': {
            'high': conf_stats[0] or 0,
            'medium': conf_stats[1] or 0,
            'low': conf_stats[2] or 0,
            'average': conf_stats[3] or 0
        },
        'recent': {
            'groundings': recent_groundings,
            'causal': recent_causal
        },
        'top_concepts': top_concepts
    }


def display_progress_bar(value, max_value=1.0, width=30, label=""):
    """Display a text progress bar"""
    filled = int(width * value / max_value)
    bar = "█" * filled + "░" * (width - filled)
    percentage = value / max_value * 100
    return f"{label:20} [{bar}] {percentage:5.1f}%"


def display_understanding_monitor():
    """Display the understanding monitor"""
    while True:
        # Clear screen (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        stats = get_understanding_stats()
        metrics = stats['metrics']
        
        # Header
        print("╔" + "═"*78 + "╗")
        print("║" + " "*25 + "KIMERA UNDERSTANDING MONITOR" + " "*25 + "║")
        print("║" + " "*78 + "║")
        print("║" + f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*48 + "║")
        print("╚" + "═"*78 + "╝")
        
        # Roadmap Progress
        print("\n📊 ROADMAP PROGRESS")
        print("─" * 80)
        for phase, progress in metrics['roadmap_progress'].items():
            phase_name = phase.replace('_', ' ').title()
            print(display_progress_bar(progress, label=phase_name))
        
        # Understanding Components
        print("\n📈 UNDERSTANDING COMPONENTS")
        print("─" * 80)
        components = metrics['understanding_components']
        print(f"  Multimodal Groundings: {components['multimodal_groundings']:>6}")
        print(f"  Causal Relationships:  {components['causal_relationships']:>6}")
        print(f"  Self Models:           {components['self_models']:>6}")
        print(f"  Abstract Concepts:     {components['abstract_concepts']:>6}")
        print(f"  Genuine Opinions:      {components['genuine_opinions']:>6}")
        print(f"  Learned Values:        {components['learned_values']:>6}")
        
        # Confidence Distribution
        print("\n🎯 GROUNDING CONFIDENCE")
        print("─" * 80)
        conf = stats['confidence']
        total = conf['high'] + conf['medium'] + conf['low']
        if total > 0:
            print(f"  High (≥0.8):    {conf['high']:>4} ({conf['high']/total*100:>5.1f}%)")
            print(f"  Medium (0.6-0.8): {conf['medium']:>4} ({conf['medium']/total*100:>5.1f}%)")
            print(f"  Low (<0.6):      {conf['low']:>4} ({conf['low']/total*100:>5.1f}%)")
            print(f"  Average Score:   {conf['average']:>4.3f}")
        
        # Understanding Quality
        print("\n✅ UNDERSTANDING QUALITY")
        print("─" * 80)
        quality = metrics['understanding_quality']
        print(f"  Test Accuracy:    {quality['average_test_accuracy']:>5.1%}")
        print(f"  Tests Passed:     {quality['tests_passed']}/{quality['total_tests']}")
        print(f"  Quality Score:    {quality['average_understanding_quality']:>5.1%}")
        
        # Recent Activity
        print("\n🔄 RECENT ACTIVITY (Last Hour)")
        print("─" * 80)
        print(f"  New Groundings:        {stats['recent']['groundings']:>4}")
        print(f"  Causal Discoveries:    {stats['recent']['causal']:>4}")
        
        # Top Concepts
        if stats['top_concepts']:
            print("\n🏆 TOP GROUNDED CONCEPTS")
            print("─" * 80)
            for i, (concept, confidence) in enumerate(stats['top_concepts'], 1):
                print(f"  {i}. {concept:<30} (confidence: {confidence:.3f})")
        
        # Status Summary
        print("\n📋 STATUS SUMMARY")
        print("─" * 80)
        
        # Calculate overall progress
        overall_progress = sum(metrics['roadmap_progress'].values()) / len(metrics['roadmap_progress'])
        
        if overall_progress < 0.25:
            status = "🟡 Early Stage - Building Foundation"
        elif overall_progress < 0.5:
            status = "🟢 Progressing - Developing Understanding"
        elif overall_progress < 0.75:
            status = "🔵 Advanced - Deepening Comprehension"
        else:
            status = "🟣 Mature - Approaching Genuine Understanding"
        
        print(f"  Status: {status}")
        print(f"  Overall Progress: {overall_progress:.1%}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("─" * 80)
        
        if components['multimodal_groundings'] < 100:
            print("  • Ground more concepts to build semantic foundation")
        
        if conf['average'] < 0.7:
            print("  • Focus on improving grounding quality (target: 0.7+)")
        
        if components['causal_relationships'] < 20:
            print("  • Discover more causal relationships for reasoning")
        
        if components['abstract_concepts'] < 10:
            print("  • Form abstract concepts to generalize understanding")
        
        if quality['average_test_accuracy'] < 0.7:
            print("  • Improve understanding mechanisms (target: 70% accuracy)")
        
        # Footer
        print("\n" + "─" * 80)
        print("Press Ctrl+C to exit | Updates every 5 seconds")
        
        # Wait before refresh
        time.sleep(5)


def generate_report():
    """Generate a one-time report"""
    stats = get_understanding_stats()
    metrics = stats['metrics']
    
    print("\n" + "="*80)
    print("KIMERA UNDERSTANDING PROGRESS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Overall Progress
    overall = sum(metrics['roadmap_progress'].values()) / len(metrics['roadmap_progress'])
    print(f"\n🎯 OVERALL PROGRESS: {overall:.1%}")
    
    # Detailed Progress
    print("\n📊 PHASE PROGRESS:")
    for phase, progress in metrics['roadmap_progress'].items():
        print(f"  {phase}: {progress:.1%}")
    
    # Key Metrics
    print(f"\n📈 KEY METRICS:")
    print(f"  Total Groundings: {metrics['understanding_components']['multimodal_groundings']}")
    print(f"  Causal Relations: {metrics['understanding_components']['causal_relationships']}")
    print(f"  Confidence Average: {stats['confidence']['average']:.3f}")
    print(f"  Test Accuracy: {metrics['understanding_quality']['average_test_accuracy']:.1%}")
    
    # Next Milestones
    print("\n🎯 NEXT MILESTONES:")
    
    groundings_needed = max(0, 100 - metrics['understanding_components']['multimodal_groundings'])
    if groundings_needed > 0:
        print(f"  • Ground {groundings_needed} more concepts to reach 100")
    
    causal_needed = max(0, 50 - metrics['understanding_components']['causal_relationships'])
    if causal_needed > 0:
        print(f"  • Discover {causal_needed} more causal relationships")
    
    if metrics['understanding_components']['abstract_concepts'] < 10:
        print(f"  • Form {10 - metrics['understanding_components']['abstract_concepts']} abstract concepts")
    
    print("\n" + "="*80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor KIMERA Understanding Progress')
    parser.add_argument('--live', action='store_true', help='Show live monitoring dashboard')
    parser.add_argument('--report', action='store_true', help='Generate one-time report')
    
    args = parser.parse_args()
    
    if args.live:
        print("Starting live monitoring... (Press Ctrl+C to exit)")
        try:
            display_understanding_monitor()
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    else:
        generate_report()


if __name__ == "__main__":
    main()