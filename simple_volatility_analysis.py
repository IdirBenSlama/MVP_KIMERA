#!/usr/bin/env python3
"""
Simplified High Volatility Analysis for KIMERA SWM

Direct analysis of KIMERA's performance during high volatility testing
without external dependencies.
"""

import requests
import json
import sqlite3
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter

KIMERA_API_URL = "http://localhost:8001"

class SimpleVolatilityAnalyzer:
    """Analyzes KIMERA's performance during high volatility testing"""
    
    def __init__(self):
        self.db_path = "kimera_swm.db"
        self.analysis_results = {}
        self.system_metrics = {}
        
    def connect_to_database(self):
        """Connect to KIMERA database for analysis"""
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def extract_system_metrics(self):
        """Extract current system metrics from KIMERA"""
        try:
            response = requests.get(f"{KIMERA_API_URL}/system/status", timeout=10)
            if response.status_code == 200:
                self.system_metrics = response.json()
                print("✅ System metrics extracted")
                return True
            else:
                print(f"❌ Failed to get system metrics: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error extracting system metrics: {e}")
            return False
    
    def analyze_database_contents(self):
        """Analyze the contents of the KIMERA database"""
        print("\n📊 DATABASE CONTENT ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM geoids")
            total_geoids = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scars")
            total_scars = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM insights")
            total_insights = cursor.fetchone()[0]
            
            print(f"📈 Database Overview:")
            print(f"   Total Geoids: {total_geoids:,}")
            print(f"   Total Scars: {total_scars:,}")
            print(f"   Total Insights: {total_insights:,}")
            
            # Analyze recent test data
            cursor.execute("""
                SELECT COUNT(*) FROM geoids 
                WHERE json_extract(metadata_json, '$.test_stream') = 1
                OR json_extract(metadata_json, '$.scenario_type') IS NOT NULL
            """)
            test_geoids = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM scars 
                WHERE timestamp > datetime('now', '-2 hours')
            """)
            recent_scars = cursor.fetchone()[0]
            
            print(f"\n🧪 Test Data Analysis:")
            print(f"   Test Geoids Created: {test_geoids}")
            print(f"   Recent Scars (2h): {recent_scars}")
            print(f"   Test Efficiency: {recent_scars/max(test_geoids, 1):.1f} scars per test geoid")
            
            self.analysis_results['database_overview'] = {
                'total_geoids': total_geoids,
                'total_scars': total_scars,
                'total_insights': total_insights,
                'test_geoids': test_geoids,
                'recent_scars': recent_scars
            }
            
        except Exception as e:
            print(f"❌ Error in database analysis: {e}")
        finally:
            conn.close()
    
    def analyze_scar_characteristics(self):
        """Analyze characteristics of contradiction scars"""
        print("\n⚡ SCAR CHARACTERISTICS ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Get recent scars for analysis
            cursor.execute("""
                SELECT scar_id, geoids, reason, pre_entropy, post_entropy, 
                       delta_entropy, cls_angle, semantic_polarity, mutation_frequency,
                       vault_id, timestamp
                FROM scars 
                WHERE timestamp > datetime('now', '-2 hours')
                ORDER BY timestamp DESC
                LIMIT 1000
            """)
            
            scars = cursor.fetchall()
            
            if not scars:
                print("❌ No recent scars found for analysis")
                return
            
            print(f"⚡ Analyzing {len(scars)} recent scars...")
            
            # Extract numerical data
            delta_entropies = []
            cls_angles = []
            semantic_polarities = []
            mutation_frequencies = []
            vault_distribution = defaultdict(int)
            
            for scar in scars:
                delta_entropies.append(scar[5])  # delta_entropy
                cls_angles.append(scar[6])       # cls_angle
                semantic_polarities.append(scar[7])  # semantic_polarity
                mutation_frequencies.append(scar[8])  # mutation_frequency
                vault_distribution[scar[9]] += 1     # vault_id
            
            # Calculate statistics
            print(f"\n🌀 Entropy Change Analysis:")
            print(f"   Mean Δ Entropy: {statistics.mean(delta_entropies):.3f}")
            print(f"   Median Δ Entropy: {statistics.median(delta_entropies):.3f}")
            print(f"   Min Δ Entropy: {min(delta_entropies):.3f}")
            print(f"   Max Δ Entropy: {max(delta_entropies):.3f}")
            print(f"   Std Dev: {statistics.stdev(delta_entropies):.3f}")
            
            # Entropy direction analysis
            positive_deltas = [d for d in delta_entropies if d > 0]
            negative_deltas = [d for d in delta_entropies if d < 0]
            zero_deltas = [d for d in delta_entropies if d == 0]
            
            print(f"\n📊 Entropy Direction:")
            print(f"   Entropy Increases: {len(positive_deltas)} ({len(positive_deltas)/len(scars)*100:.1f}%)")
            print(f"   Entropy Decreases: {len(negative_deltas)} ({len(negative_deltas)/len(scars)*100:.1f}%)")
            print(f"   No Change: {len(zero_deltas)} ({len(zero_deltas)/len(scars)*100:.1f}%)")
            
            print(f"\n📐 CLS Angle Analysis:")
            print(f"   Mean Angle: {statistics.mean(cls_angles):.1f}°")
            print(f"   Angle Range: [{min(cls_angles):.1f}°, {max(cls_angles):.1f}°]")
            
            print(f"\n🎯 Semantic Polarity Analysis:")
            print(f"   Mean Polarity: {statistics.mean(semantic_polarities):.3f}")
            print(f"   Polarity Range: [{min(semantic_polarities):.3f}, {max(semantic_polarities):.3f}]")
            
            print(f"\n🧬 Mutation Frequency Analysis:")
            print(f"   Mean Frequency: {statistics.mean(mutation_frequencies):.3f}")
            print(f"   Frequency Range: [{min(mutation_frequencies):.3f}, {max(mutation_frequencies):.3f}]")
            
            print(f"\n🏛️  Vault Distribution:")
            total_vault_scars = sum(vault_distribution.values())
            for vault, count in vault_distribution.items():
                percentage = (count / total_vault_scars) * 100
                print(f"   {vault}: {count} scars ({percentage:.1f}%)")
            
            # Calculate vault balance
            vault_a_count = vault_distribution.get('vault_a', 0)
            vault_b_count = vault_distribution.get('vault_b', 0)
            if vault_a_count + vault_b_count > 0:
                balance = abs(vault_a_count - vault_b_count) / (vault_a_count + vault_b_count)
                balance_percentage = (1 - balance) * 100
                print(f"   Vault Balance: {balance_percentage:.2f}%")
            
            self.analysis_results['scar_analysis'] = {
                'total_analyzed': len(scars),
                'entropy_stats': {
                    'mean': statistics.mean(delta_entropies),
                    'median': statistics.median(delta_entropies),
                    'min': min(delta_entropies),
                    'max': max(delta_entropies),
                    'std': statistics.stdev(delta_entropies)
                },
                'entropy_direction': {
                    'increases': len(positive_deltas),
                    'decreases': len(negative_deltas),
                    'no_change': len(zero_deltas)
                },
                'vault_distribution': dict(vault_distribution),
                'vault_balance': balance_percentage if vault_a_count + vault_b_count > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error in scar analysis: {e}")
        finally:
            conn.close()
    
    def analyze_geoid_patterns(self):
        """Analyze patterns in created geoids"""
        print("\n🧠 GEOID PATTERN ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Get test geoids
            cursor.execute("""
                SELECT geoid_id, symbolic_state, metadata_json, semantic_state_json
                FROM geoids 
                WHERE json_extract(metadata_json, '$.test_stream') = 1
                OR json_extract(metadata_json, '$.scenario_type') IS NOT NULL
                ORDER BY rowid DESC
                LIMIT 100
            """)
            
            geoids = cursor.fetchall()
            
            if not geoids:
                print("❌ No test geoids found")
                return
            
            print(f"🧠 Analyzing {len(geoids)} test geoids...")
            
            # Analyze geoid types
            geoid_types = defaultdict(int)
            scenario_types = defaultdict(int)
            semantic_features = []
            
            for geoid in geoids:
                # Parse symbolic state
                try:
                    symbolic = json.loads(geoid[1]) if geoid[1] else {}
                    geoid_type = symbolic.get('type', 'unknown')
                    geoid_types[geoid_type] += 1
                except:
                    geoid_types['parse_error'] += 1
                
                # Parse metadata
                try:
                    metadata = json.loads(geoid[2]) if geoid[2] else {}
                    scenario_type = metadata.get('scenario_type', 'none')
                    if scenario_type != 'none':
                        scenario_types[scenario_type] += 1
                except:
                    pass
                
                # Parse semantic features
                try:
                    semantic = json.loads(geoid[3]) if geoid[3] else {}
                    if semantic:
                        semantic_features.append(semantic)
                except:
                    pass
            
            print(f"\n🏷️  Geoid Type Distribution:")
            for geoid_type, count in geoid_types.items():
                percentage = (count / len(geoids)) * 100
                print(f"   {geoid_type}: {count} ({percentage:.1f}%)")
            
            print(f"\n🎭 Scenario Type Distribution:")
            for scenario_type, count in scenario_types.items():
                percentage = (count / len(geoids)) * 100
                print(f"   {scenario_type}: {count} ({percentage:.1f}%)")
            
            # Analyze semantic features
            if semantic_features:
                print(f"\n🧠 Semantic Feature Analysis:")
                
                # Get all unique features
                all_features = set()
                for features in semantic_features:
                    all_features.update(features.keys())
                
                for feature in sorted(all_features):
                    values = [f.get(feature, 0) for f in semantic_features if feature in f]
                    if values:
                        mean_val = statistics.mean(values)
                        min_val = min(values)
                        max_val = max(values)
                        
                        print(f"   {feature}:")
                        print(f"      Mean: {mean_val:.3f}")
                        print(f"      Range: [{min_val:.3f}, {max_val:.3f}]")
                        
                        # Count extreme values
                        extreme_high = len([v for v in values if v > 0.9])
                        extreme_low = len([v for v in values if v < 0.1])
                        
                        if extreme_high > 0:
                            print(f"      Extreme High (>0.9): {extreme_high}")
                        if extreme_low > 0:
                            print(f"      Extreme Low (<0.1): {extreme_low}")
            
            self.analysis_results['geoid_analysis'] = {
                'total_analyzed': len(geoids),
                'type_distribution': dict(geoid_types),
                'scenario_distribution': dict(scenario_types),
                'semantic_features_count': len(semantic_features)
            }
            
        except Exception as e:
            print(f"❌ Error in geoid analysis: {e}")
        finally:
            conn.close()
    
    def analyze_temporal_patterns(self):
        """Analyze temporal patterns in contradiction detection"""
        print("\n⏰ TEMPORAL PATTERN ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Get scar creation timestamps
            cursor.execute("""
                SELECT timestamp, delta_entropy
                FROM scars 
                WHERE timestamp > datetime('now', '-2 hours')
                ORDER BY timestamp ASC
            """)
            
            scars = cursor.fetchall()
            
            if not scars:
                print("❌ No temporal data found")
                return
            
            print(f"⏰ Analyzing {len(scars)} scars over time...")
            
            # Parse timestamps and group by minute
            from datetime import datetime
            
            minute_counts = defaultdict(int)
            minute_entropy_changes = defaultdict(list)
            
            for scar in scars:
                timestamp_str = scar[0]
                delta_entropy = scar[1]
                
                try:
                    # Parse timestamp and round to minute
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    minute_key = dt.strftime('%H:%M')
                    
                    minute_counts[minute_key] += 1
                    minute_entropy_changes[minute_key].append(delta_entropy)
                except:
                    continue
            
            if minute_counts:
                # Find peak activity
                peak_minute = max(minute_counts, key=minute_counts.get)
                peak_count = minute_counts[peak_minute]
                avg_per_minute = statistics.mean(minute_counts.values())
                
                print(f"\n📊 Temporal Activity:")
                print(f"   Peak Minute: {peak_minute} ({peak_count} scars)")
                print(f"   Average per Minute: {avg_per_minute:.1f} scars")
                print(f"   Total Time Span: {len(minute_counts)} minutes")
                
                # Activity distribution
                high_activity_minutes = len([c for c in minute_counts.values() if c > avg_per_minute])
                low_activity_minutes = len([c for c in minute_counts.values() if c <= avg_per_minute])
                
                print(f"   High Activity Minutes: {high_activity_minutes}")
                print(f"   Low Activity Minutes: {low_activity_minutes}")
                
                # Show top 5 most active minutes
                sorted_minutes = sorted(minute_counts.items(), key=lambda x: x[1], reverse=True)
                print(f"\n🔥 Top 5 Most Active Minutes:")
                for i, (minute, count) in enumerate(sorted_minutes[:5], 1):
                    avg_entropy_change = statistics.mean(minute_entropy_changes[minute])
                    print(f"   {i}. {minute}: {count} scars (Avg ΔEntropy: {avg_entropy_change:.3f})")
            
            self.analysis_results['temporal_analysis'] = {
                'total_minutes': len(minute_counts),
                'peak_minute_count': peak_count if minute_counts else 0,
                'average_per_minute': avg_per_minute if minute_counts else 0,
                'high_activity_minutes': high_activity_minutes if minute_counts else 0
            }
            
        except Exception as e:
            print(f"❌ Error in temporal analysis: {e}")
        finally:
            conn.close()
    
    def generate_performance_assessment(self):
        """Generate overall performance assessment"""
        print("\n🎯 PERFORMANCE ASSESSMENT")
        print("=" * 50)
        
        # Extract key metrics
        system_metrics = self.system_metrics
        analysis_results = self.analysis_results
        
        print(f"📊 Current System State:")
        if system_metrics:
            print(f"   Active Geoids: {system_metrics.get('active_geoids', 0):,}")
            print(f"   Vault A Scars: {system_metrics.get('vault_a_scars', 0):,}")
            print(f"   Vault B Scars: {system_metrics.get('vault_b_scars', 0):,}")
            print(f"   System Entropy: {system_metrics.get('system_entropy', 0):.3f}")
            print(f"   Processing Cycles: {system_metrics.get('cycle_count', 0):,}")
        
        # Performance scoring
        scores = {}
        
        # Vault Balance Score
        if 'scar_analysis' in analysis_results:
            vault_balance = analysis_results['scar_analysis'].get('vault_balance', 0)
            scores['vault_balance'] = vault_balance
            
            if vault_balance > 99:
                vault_status = "🟢 EXCELLENT"
            elif vault_balance > 95:
                vault_status = "🟡 GOOD"
            elif vault_balance > 90:
                vault_status = "🟠 ACCEPTABLE"
            else:
                vault_status = "🔴 POOR"
            
            print(f"\n🏛️  Vault Balance: {vault_balance:.2f}% - {vault_status}")
        
        # Contradiction Detection Efficiency
        if 'temporal_analysis' in analysis_results:
            avg_per_minute = analysis_results['temporal_analysis'].get('average_per_minute', 0)
            
            if avg_per_minute > 20:
                detection_status = "🟢 VERY HIGH"
                detection_score = 100
            elif avg_per_minute > 10:
                detection_status = "🟡 HIGH"
                detection_score = 80
            elif avg_per_minute > 5:
                detection_status = "🟠 MODERATE"
                detection_score = 60
            else:
                detection_status = "🔴 LOW"
                detection_score = 40
            
            scores['detection_efficiency'] = detection_score
            print(f"🔍 Detection Rate: {avg_per_minute:.1f}/min - {detection_status}")
        
        # System Stability (based on entropy variance)
        if 'scar_analysis' in analysis_results:
            entropy_std = analysis_results['scar_analysis'].get('entropy_stats', {}).get('std', 0)
            
            if entropy_std < 0.5:
                stability_status = "🟢 VERY STABLE"
                stability_score = 100
            elif entropy_std < 1.0:
                stability_status = "🟡 STABLE"
                stability_score = 80
            elif entropy_std < 2.0:
                stability_status = "🟠 MODERATE"
                stability_score = 60
            else:
                stability_status = "🔴 UNSTABLE"
                stability_score = 40
            
            scores['stability'] = stability_score
            print(f"🌀 System Stability: σ={entropy_std:.3f} - {stability_status}")
        
        # Data Processing Capability
        if 'database_overview' in analysis_results:
            test_geoids = analysis_results['database_overview'].get('test_geoids', 0)
            recent_scars = analysis_results['database_overview'].get('recent_scars', 0)
            
            if test_geoids > 0:
                processing_ratio = recent_scars / test_geoids
                
                if processing_ratio > 50:
                    processing_status = "🟢 EXCELLENT"
                    processing_score = 100
                elif processing_ratio > 20:
                    processing_status = "🟡 GOOD"
                    processing_score = 80
                elif processing_ratio > 10:
                    processing_status = "🟠 ACCEPTABLE"
                    processing_score = 60
                else:
                    processing_status = "🔴 POOR"
                    processing_score = 40
                
                scores['processing_capability'] = processing_score
                print(f"⚡ Processing Ratio: {processing_ratio:.1f} - {processing_status}")
        
        # Calculate overall score
        if scores:
            overall_score = statistics.mean(scores.values())
            
            print(f"\n🏆 OVERALL PERFORMANCE SCORE: {overall_score:.1f}/100")
            
            if overall_score >= 90:
                grade = "A+ (Outstanding)"
                recommendation = "🟢 PRODUCTION READY - Excellent performance"
            elif overall_score >= 80:
                grade = "A (Excellent)"
                recommendation = "🟢 PRODUCTION READY - Very good performance"
            elif overall_score >= 70:
                grade = "B (Good)"
                recommendation = "🟡 PRODUCTION READY - Monitor performance"
            elif overall_score >= 60:
                grade = "C (Acceptable)"
                recommendation = "🟠 REQUIRES OPTIMIZATION - Acceptable for testing"
            else:
                grade = "D (Poor)"
                recommendation = "🔴 REQUIRES MAJOR IMPROVEMENTS"
            
            print(f"🎓 Performance Grade: {grade}")
            print(f"💡 Recommendation: {recommendation}")
        
        # Key insights
        print(f"\n💡 KEY INSIGHTS:")
        
        insights = []
        
        if 'scar_analysis' in analysis_results:
            entropy_direction = analysis_results['scar_analysis'].get('entropy_direction', {})
            increases = entropy_direction.get('increases', 0)
            decreases = entropy_direction.get('decreases', 0)
            total = increases + decreases
            
            if total > 0:
                increase_pct = (increases / total) * 100
                if increase_pct > 60:
                    insights.append("🌀 System shows net entropy increase - active learning")
                elif increase_pct < 40:
                    insights.append("🌀 System shows net entropy decrease - stabilizing")
                else:
                    insights.append("🌀 System shows balanced entropy dynamics")
        
        if 'temporal_analysis' in analysis_results:
            high_activity = analysis_results['temporal_analysis'].get('high_activity_minutes', 0)
            total_minutes = analysis_results['temporal_analysis'].get('total_minutes', 1)
            
            if high_activity / total_minutes > 0.5:
                insights.append("⚡ High sustained contradiction detection activity")
            else:
                insights.append("⚡ Bursty contradiction detection pattern")
        
        if system_metrics:
            total_scars = system_metrics.get('vault_a_scars', 0) + system_metrics.get('vault_b_scars', 0)
            active_geoids = system_metrics.get('active_geoids', 1)
            
            if total_scars / active_geoids > 2:
                insights.append("🧠 High contradiction density - complex semantic space")
            else:
                insights.append("🧠 Moderate contradiction density - stable semantic space")
        
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        self.analysis_results['performance_assessment'] = {
            'scores': scores,
            'overall_score': overall_score if scores else 0,
            'grade': grade if scores else "N/A",
            'insights': insights
        }
    
    def save_analysis_report(self):
        """Save analysis report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"volatility_analysis_{timestamp}.json"
        
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self.system_metrics,
                'analysis_results': self.analysis_results
            }
            
            with open(report_filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Analysis report saved: {report_filename}")
            return report_filename
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return None
    
    def run_complete_analysis(self):
        """Run complete volatility analysis"""
        print("🔬 KIMERA SWM HIGH VOLATILITY ANALYSIS")
        print("=" * 60)
        print("Deep analysis of KIMERA's performance during high volatility")
        print("testing and extreme market condition simulation")
        
        # Extract system metrics
        if not self.extract_system_metrics():
            print("⚠️  Continuing with database-only analysis...")
        
        # Run analysis modules
        self.analyze_database_contents()
        self.analyze_scar_characteristics()
        self.analyze_geoid_patterns()
        self.analyze_temporal_patterns()
        self.generate_performance_assessment()
        
        # Save report
        report_file = self.save_analysis_report()
        
        print(f"\n🎯 ANALYSIS COMPLETE")
        print(f"=" * 30)
        print(f"✅ Comprehensive analysis completed successfully")
        print(f"📊 Performance insights generated")
        print(f"💾 Report saved: {report_file}")
        print(f"\n🚀 KIMERA SWM volatility analysis finished!")

def main():
    """Main analysis function"""
    analyzer = SimpleVolatilityAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()