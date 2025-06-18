"""
Understanding Progress Monitor
Real-time dashboard for tracking KIMERA's journey toward genuine understanding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vault.understanding_vault_manager import UnderstandingVaultManager
from backend.semantic_grounding import EmbodiedSemanticEngine
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
import numpy as np
from collections import deque
import sqlite3


class UnderstandingMonitor:
    """Monitor and visualize understanding progress"""
    
    def __init__(self):
        self.understanding_vault = UnderstandingVaultManager()
        self.semantic_engine = EmbodiedSemanticEngine()
        
        # History tracking
        self.history_window = 100
        self.grounding_history = deque(maxlen=self.history_window)
        self.confidence_history = deque(maxlen=self.history_window)
        self.test_accuracy_history = deque(maxlen=self.history_window)
        self.timestamps = deque(maxlen=self.history_window)
        
    def get_current_stats(self):
        """Get current understanding statistics"""
        metrics = self.understanding_vault.get_understanding_metrics()
        
        # Get database stats
        conn = sqlite3.connect('kimera_swm.db')
        cursor = conn.cursor()
        
        # Count groundings by confidence level
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high_conf,
                COUNT(CASE WHEN confidence_score >= 0.6 AND confidence_score < 0.8 THEN 1 END) as med_conf,
                COUNT(CASE WHEN confidence_score < 0.6 THEN 1 END) as low_conf,
                AVG(confidence_score) as avg_conf
            FROM multimodal_groundings
        """)
        conf_stats = cursor.fetchone()
        
        # Get recent causal relationships
        cursor.execute("""
            SELECT COUNT(*) FROM causal_relationships 
            WHERE created_at > datetime('now', '-1 hour')
        """)
        recent_causal = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'metrics': metrics,
            'confidence_distribution': {
                'high': conf_stats[0] or 0,
                'medium': conf_stats[1] or 0,
                'low': conf_stats[2] or 0,
                'average': conf_stats[3] or 0
            },
            'recent_causal': recent_causal,
            'timestamp': datetime.now()
        }
    
    def create_dashboard(self):
        """Create the monitoring dashboard"""
        # Set up the figure
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('KIMERA Understanding Progress Monitor', fontsize=16, fontweight='bold')
        
        # Create subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Roadmap Progress (top left)
        ax_roadmap = fig.add_subplot(gs[0, 0])
        
        # 2. Confidence Distribution (top middle)
        ax_confidence = fig.add_subplot(gs[0, 1])
        
        # 3. Understanding Components (top right)
        ax_components = fig.add_subplot(gs[0, 2])
        
        # 4. Grounding Rate Over Time (middle left)
        ax_grounding_rate = fig.add_subplot(gs[1, 0])
        
        # 5. Test Accuracy Trend (middle middle)
        ax_test_accuracy = fig.add_subplot(gs[1, 1])
        
        # 6. Causal Network Growth (middle right)
        ax_causal = fig.add_subplot(gs[1, 2])
        
        # 7. Recent Activity Log (bottom)
        ax_activity = fig.add_subplot(gs[2, :])
        
        def update_dashboard(frame):
            """Update all dashboard components"""
            # Clear all axes
            for ax in [ax_roadmap, ax_confidence, ax_components, 
                      ax_grounding_rate, ax_test_accuracy, ax_causal, ax_activity]:
                ax.clear()
            
            # Get current stats
            stats = self.get_current_stats()
            metrics = stats['metrics']
            
            # Update history
            self.timestamps.append(datetime.now())
            self.grounding_history.append(
                metrics['understanding_components']['multimodal_groundings']
            )
            self.confidence_history.append(
                stats['confidence_distribution']['average'] or 0
            )
            self.test_accuracy_history.append(
                metrics['understanding_quality']['average_test_accuracy']
            )
            
            # 1. Roadmap Progress
            phases = list(metrics['roadmap_progress'].keys())
            progress = list(metrics['roadmap_progress'].values())
            colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
            
            bars = ax_roadmap.barh(phases, progress, color=colors)
            ax_roadmap.set_xlim(0, 1)
            ax_roadmap.set_xlabel('Progress')
            ax_roadmap.set_title('Roadmap Progress')
            
            # Add percentage labels
            for i, (bar, prog) in enumerate(zip(bars, progress)):
                ax_roadmap.text(prog + 0.02, i, f'{prog:.1%}', 
                              va='center', fontsize=9)
            
            # 2. Confidence Distribution
            conf_dist = stats['confidence_distribution']
            labels = ['High\n(≥0.8)', 'Medium\n(0.6-0.8)', 'Low\n(<0.6)']
            sizes = [conf_dist['high'], conf_dist['medium'], conf_dist['low']]
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            
            if sum(sizes) > 0:
                wedges, texts, autotexts = ax_confidence.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.0f%%',
                    startangle=90
                )
                ax_confidence.set_title(f'Grounding Confidence\n(Avg: {conf_dist["average"]:.2f})')
            else:
                ax_confidence.text(0.5, 0.5, 'No data', ha='center', va='center')
                ax_confidence.set_title('Grounding Confidence')
            
            # 3. Understanding Components
            components = metrics['understanding_components']
            comp_names = ['Groundings', 'Causal', 'Self-Models', 
                         'Concepts', 'Opinions', 'Values']
            comp_values = [
                components['multimodal_groundings'],
                components['causal_relationships'],
                components['self_models'],
                components['abstract_concepts'],
                components['genuine_opinions'],
                components['learned_values']
            ]
            
            bars = ax_components.bar(comp_names, comp_values, 
                                    color=['#3498db', '#e74c3c', '#f39c12', 
                                          '#9b59b6', '#2ecc71', '#1abc9c'])
            ax_components.set_title('Understanding Components')
            ax_components.set_ylabel('Count')
            ax_components.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar, val in zip(bars, comp_values):
                height = bar.get_height()
                ax_components.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                 f'{int(val)}', ha='center', va='bottom')
            
            # 4. Grounding Rate Over Time
            if len(self.grounding_history) > 1:
                x = list(range(len(self.grounding_history)))
                ax_grounding_rate.plot(x, list(self.grounding_history), 
                                     'b-', linewidth=2)
                ax_grounding_rate.fill_between(x, list(self.grounding_history), 
                                             alpha=0.3)
                ax_grounding_rate.set_title('Groundings Over Time')
                ax_grounding_rate.set_xlabel('Time')
                ax_grounding_rate.set_ylabel('Total Groundings')
                ax_grounding_rate.grid(True, alpha=0.3)
            
            # 5. Test Accuracy Trend
            if len(self.test_accuracy_history) > 1:
                x = list(range(len(self.test_accuracy_history)))
                ax_test_accuracy.plot(x, list(self.test_accuracy_history), 
                                    'g-', linewidth=2, marker='o')
                ax_test_accuracy.axhline(y=0.7, color='r', linestyle='--', 
                                       label='Target: 70%')
                ax_test_accuracy.set_title('Understanding Test Accuracy')
                ax_test_accuracy.set_xlabel('Time')
                ax_test_accuracy.set_ylabel('Accuracy')
                ax_test_accuracy.set_ylim(0, 1)
                ax_test_accuracy.grid(True, alpha=0.3)
                ax_test_accuracy.legend()
            
            # 6. Causal Network Growth
            causal_data = [
                components['causal_relationships'],
                stats['recent_causal']
            ]
            labels = ['Total\nRelationships', 'Recent\n(1 hour)']
            colors = ['#3498db', '#2ecc71']
            
            bars = ax_causal.bar(labels, causal_data, color=colors)
            ax_causal.set_title('Causal Understanding')
            ax_causal.set_ylabel('Count')
            
            for bar, val in zip(bars, causal_data):
                height = bar.get_height()
                ax_causal.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                             f'{int(val)}', ha='center', va='bottom')
            
            # 7. Recent Activity Log
            activity_text = f"System Status: ACTIVE\n"
            activity_text += f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            activity_text += f"Total Groundings: {components['multimodal_groundings']}\n"
            activity_text += f"Average Confidence: {conf_dist['average']:.3f}\n"
            activity_text += f"Recent Causal Discoveries: {stats['recent_causal']}\n"
            
            # Add understanding quality
            quality = metrics['understanding_quality']
            activity_text += f"\nUnderstanding Quality:\n"
            activity_text += f"  - Test Accuracy: {quality['average_test_accuracy']:.1%}\n"
            activity_text += f"  - Tests Passed: {quality['tests_passed']}/{quality['total_tests']}\n"
            
            ax_activity.text(0.05, 0.95, activity_text, transform=ax_activity.transAxes,
                           fontsize=10, verticalalignment='top', fontfamily='monospace',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax_activity.axis('off')
            
            plt.tight_layout()
        
        # Create animation
        ani = animation.FuncAnimation(fig, update_dashboard, interval=2000, 
                                    cache_frame_data=False)
        
        plt.show()
        
        return ani
    
    def generate_report(self):
        """Generate a text-based progress report"""
        stats = self.get_current_stats()
        metrics = stats['metrics']
        
        report = "\n" + "="*60 + "\n"
        report += "KIMERA UNDERSTANDING PROGRESS REPORT\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "="*60 + "\n\n"
        
        # Roadmap Progress
        report += "📊 ROADMAP PROGRESS:\n"
        for phase, progress in metrics['roadmap_progress'].items():
            bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
            report += f"  {phase}: [{bar}] {progress:.1%}\n"
        
        # Understanding Components
        report += "\n📈 UNDERSTANDING COMPONENTS:\n"
        for comp, count in metrics['understanding_components'].items():
            report += f"  - {comp}: {count}\n"
        
        # Confidence Distribution
        conf = stats['confidence_distribution']
        report += f"\n🎯 CONFIDENCE DISTRIBUTION:\n"
        report += f"  - High (≥0.8): {conf['high']} groundings\n"
        report += f"  - Medium (0.6-0.8): {conf['medium']} groundings\n"
        report += f"  - Low (<0.6): {conf['low']} groundings\n"
        report += f"  - Average: {conf['average']:.3f}\n"
        
        # Understanding Quality
        quality = metrics['understanding_quality']
        report += f"\n✅ UNDERSTANDING QUALITY:\n"
        report += f"  - Average Test Accuracy: {quality['average_test_accuracy']:.1%}\n"
        report += f"  - Tests Passed: {quality['tests_passed']}/{quality['total_tests']}\n"
        
        # Recent Activity
        report += f"\n🔄 RECENT ACTIVITY:\n"
        report += f"  - Causal relationships (last hour): {stats['recent_causal']}\n"
        
        # Recommendations
        report += "\n💡 RECOMMENDATIONS:\n"
        
        if metrics['roadmap_progress']['phase_1_multimodal'] < 0.5:
            report += "  - Focus on grounding more concepts to reach 50% Phase 1 completion\n"
        
        if conf['average'] < 0.7:
            report += "  - Improve grounding quality - average confidence below 0.7\n"
        
        if quality['average_test_accuracy'] < 0.7:
            report += "  - Enhance understanding mechanisms - test accuracy below target\n"
        
        if metrics['understanding_components']['causal_relationships'] < 20:
            report += "  - Discover more causal relationships for better reasoning\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report


def main():
    """Run the understanding monitor"""
    monitor = UnderstandingMonitor()
    
    print("\n🖥️ KIMERA Understanding Progress Monitor")
    print("="*60)
    
    # Generate text report
    report = monitor.generate_report()
    print(report)
    
    # Ask if user wants to see live dashboard
    response = input("\nLaunch live monitoring dashboard? (y/n): ")
    
    if response.lower() == 'y':
        print("\n📊 Launching dashboard...")
        print("(Close window to exit)")
        
        try:
            ani = monitor.create_dashboard()
        except KeyboardInterrupt:
            print("\n\nDashboard closed.")
    
    print("\n✅ Monitoring session complete.")


if __name__ == "__main__":
    main()