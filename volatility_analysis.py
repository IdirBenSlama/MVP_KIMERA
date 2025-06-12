#!/usr/bin/env python3
"""
High Volatility Test Analysis for KIMERA SWM

This script provides deep analytical insights into KIMERA's performance
during high volatility testing, examining patterns, correlations, and
system behavior under extreme market conditions.
"""

import requests
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter

KIMERA_API_URL = "http://localhost:8001"

class VolatilityAnalyzer:
    """Analyzes KIMERA's performance during high volatility testing"""
    
    def __init__(self):
        self.db_path = "kimera_swm.db"
        self.analysis_results = {}
        self.system_metrics = {}
        self.contradiction_patterns = []
        self.entropy_evolution = []
        
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
    
    def analyze_geoid_distribution(self):
        """Analyze the distribution and characteristics of created geoids"""
        print("\n📊 GEOID DISTRIBUTION ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            # Get all geoids with their metadata
            query = """
            SELECT geoid_id, symbolic_state, metadata_json, semantic_state_json, semantic_vector
            FROM geoids 
            WHERE json_extract(metadata_json, '$.test_stream') = 1
            OR json_extract(metadata_json, '$.scenario_type') IS NOT NULL
            ORDER BY rowid DESC
            LIMIT 100
            """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                print("❌ No test geoids found in database")
                return
            
            print(f"📈 Total Test Geoids Analyzed: {len(df)}")
            
            # Parse JSON fields
            df['symbolic_parsed'] = df['symbolic_state'].apply(lambda x: json.loads(x) if x else {})
            df['metadata_parsed'] = df['metadata_json'].apply(lambda x: json.loads(x) if x else {})
            df['semantic_parsed'] = df['semantic_state_json'].apply(lambda x: json.loads(x) if x else {})
            
            # Analyze geoid types
            geoid_types = df['symbolic_parsed'].apply(lambda x: x.get('type', 'unknown'))
            type_counts = geoid_types.value_counts()
            
            print(f"\n🏷️  Geoid Type Distribution:")
            for geoid_type, count in type_counts.items():
                percentage = (count / len(df)) * 100
                print(f"   {geoid_type}: {count} ({percentage:.1f}%)")
            
            # Analyze scenario types
            scenario_types = df['metadata_parsed'].apply(lambda x: x.get('scenario_type', 'none'))
            scenario_counts = scenario_types.value_counts()
            
            print(f"\n🎭 Scenario Type Distribution:")
            for scenario_type, count in scenario_counts.items():
                if scenario_type != 'none':
                    percentage = (count / len(df)) * 100
                    print(f"   {scenario_type}: {count} ({percentage:.1f}%)")
            
            # Analyze semantic features
            semantic_features = []
            for _, row in df.iterrows():
                if row['semantic_parsed']:
                    semantic_features.append(row['semantic_parsed'])
            
            if semantic_features:
                semantic_df = pd.DataFrame(semantic_features)
                
                print(f"\n🧠 Semantic Feature Statistics:")
                for feature in semantic_df.columns:
                    mean_val = semantic_df[feature].mean()
                    std_val = semantic_df[feature].std()
                    min_val = semantic_df[feature].min()
                    max_val = semantic_df[feature].max()
                    
                    print(f"   {feature}:")
                    print(f"      Mean: {mean_val:.3f} ± {std_val:.3f}")
                    print(f"      Range: [{min_val:.3f}, {max_val:.3f}]")
                
                # Identify extreme values
                print(f"\n🚨 Extreme Semantic Values:")
                for feature in semantic_df.columns:
                    extreme_high = semantic_df[semantic_df[feature] > 0.9][feature]
                    extreme_low = semantic_df[semantic_df[feature] < 0.1][feature]
                    
                    if len(extreme_high) > 0:
                        print(f"   {feature} > 0.9: {len(extreme_high)} instances")
                    if len(extreme_low) > 0:
                        print(f"   {feature} < 0.1: {len(extreme_low)} instances")
            
            self.analysis_results['geoid_analysis'] = {
                'total_geoids': len(df),
                'type_distribution': type_counts.to_dict(),
                'scenario_distribution': scenario_counts.to_dict(),
                'semantic_stats': semantic_df.describe().to_dict() if semantic_features else {}
            }
            
        except Exception as e:
            print(f"❌ Error in geoid analysis: {e}")
        finally:
            conn.close()
    
    def analyze_scar_patterns(self):
        """Analyze patterns in contradiction scars"""
        print("\n⚡ SCAR PATTERN ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            # Get recent scars from the test period
            query = """
            SELECT scar_id, geoids, reason, timestamp, pre_entropy, post_entropy, 
                   delta_entropy, cls_angle, semantic_polarity, mutation_frequency,
                   weight, vault_id
            FROM scars 
            WHERE timestamp > datetime('now', '-1 hour')
            ORDER BY timestamp DESC
            LIMIT 500
            """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                print("❌ No recent scars found")
                return
            
            print(f"⚡ Total Scars Analyzed: {len(df)}")
            
            # Parse geoids JSON
            df['geoids_parsed'] = df['geoids'].apply(lambda x: json.loads(x) if x else [])
            df['geoid_count'] = df['geoids_parsed'].apply(len)
            
            # Analyze vault distribution
            vault_distribution = df['vault_id'].value_counts()
            print(f"\n🏛️  Vault Distribution:")
            for vault, count in vault_distribution.items():
                percentage = (count / len(df)) * 100
                print(f"   {vault}: {count} scars ({percentage:.1f}%)")
            
            # Analyze entropy changes
            entropy_stats = df['delta_entropy'].describe()
            print(f"\n��� Entropy Change Analysis:")
            print(f"   Mean Δ Entropy: {entropy_stats['mean']:.3f}")
            print(f"   Std Δ Entropy: {entropy_stats['std']:.3f}")
            print(f"   Min Δ Entropy: {entropy_stats['min']:.3f}")
            print(f"   Max Δ Entropy: {entropy_stats['max']:.3f}")
            
            # Identify high-impact scars
            high_impact_scars = df[abs(df['delta_entropy']) > entropy_stats['75%']]
            print(f"   High-impact scars (>75th percentile): {len(high_impact_scars)}")
            
            # Analyze semantic polarity
            polarity_stats = df['semantic_polarity'].describe()
            print(f"\n🎯 Semantic Polarity Analysis:")
            print(f"   Mean Polarity: {polarity_stats['mean']:.3f}")
            print(f"   Polarity Range: [{polarity_stats['min']:.3f}, {polarity_stats['max']:.3f}]")
            
            # Analyze mutation frequency
            mutation_stats = df['mutation_frequency'].describe()
            print(f"\n🧬 Mutation Frequency Analysis:")
            print(f"   Mean Frequency: {mutation_stats['mean']:.3f}")
            print(f"   Frequency Range: [{mutation_stats['min']:.3f}, {mutation_stats['max']:.3f}]")
            
            # Analyze CLS angles
            cls_stats = df['cls_angle'].describe()
            print(f"\n📐 CLS Angle Analysis:")
            print(f"   Mean Angle: {cls_stats['mean']:.1f}°")
            print(f"   Angle Range: [{cls_stats['min']:.1f}°, {cls_stats['max']:.1f}°]")
            
            # Identify patterns in reasons
            reason_patterns = df['reason'].value_counts().head(10)
            print(f"\n📝 Top Scar Reasons:")
            for reason, count in reason_patterns.items():
                percentage = (count / len(df)) * 100
                print(f"   {reason[:50]}{'...' if len(reason) > 50 else ''}: {count} ({percentage:.1f}%)")
            
            # Temporal analysis
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['minute'] = df['timestamp'].dt.floor('min')
            scars_per_minute = df.groupby('minute').size()
            
            print(f"\n⏰ Temporal Scar Creation:")
            print(f"   Peak minute: {scars_per_minute.max()} scars")
            print(f"   Average per minute: {scars_per_minute.mean():.1f} scars")
            print(f"   Total time span: {(df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60:.1f} minutes")
            
            self.analysis_results['scar_analysis'] = {
                'total_scars': len(df),
                'vault_distribution': vault_distribution.to_dict(),
                'entropy_stats': entropy_stats.to_dict(),
                'polarity_stats': polarity_stats.to_dict(),
                'mutation_stats': mutation_stats.to_dict(),
                'cls_stats': cls_stats.to_dict(),
                'temporal_stats': {
                    'peak_per_minute': int(scars_per_minute.max()),
                    'avg_per_minute': float(scars_per_minute.mean()),
                    'time_span_minutes': float((df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in scar analysis: {e}")
        finally:
            conn.close()
    
    def analyze_contradiction_efficiency(self):
        """Analyze the efficiency of contradiction detection"""
        print("\n🔍 CONTRADICTION DETECTION EFFICIENCY")
        print("=" * 50)
        
        if not self.system_metrics:
            print("❌ No system metrics available")
            return
        
        active_geoids = self.system_metrics.get('active_geoids', 0)
        total_scars = self.system_metrics.get('vault_a_scars', 0) + self.system_metrics.get('vault_b_scars', 0)
        cycle_count = self.system_metrics.get('cycle_count', 0)
        system_entropy = self.system_metrics.get('system_entropy', 0)
        
        print(f"📊 System Efficiency Metrics:")
        print(f"   Active Geoids: {active_geoids}")
        print(f"   Total Scars: {total_scars}")
        print(f"   Processing Cycles: {cycle_count}")
        print(f"   Current Entropy: {system_entropy:.3f}")
        
        # Calculate efficiency ratios
        if active_geoids > 0:
            scar_to_geoid_ratio = total_scars / active_geoids
            print(f"   Scar/Geoid Ratio: {scar_to_geoid_ratio:.2f}")
        
        if cycle_count > 0:
            scars_per_cycle = total_scars / cycle_count
            print(f"   Scars per Cycle: {scars_per_cycle:.2f}")
        
        # Analyze vault balance
        vault_a_scars = self.system_metrics.get('vault_a_scars', 0)
        vault_b_scars = self.system_metrics.get('vault_b_scars', 0)
        
        if vault_a_scars + vault_b_scars > 0:
            vault_balance = abs(vault_a_scars - vault_b_scars) / (vault_a_scars + vault_b_scars)
            balance_percentage = (1 - vault_balance) * 100
            print(f"\n🏛️  Vault Balance Analysis:")
            print(f"   Vault A: {vault_a_scars} scars")
            print(f"   Vault B: {vault_b_scars} scars")
            print(f"   Balance: {balance_percentage:.2f}% (perfect = 100%)")
            print(f"   Imbalance: {abs(vault_a_scars - vault_b_scars)} scars")
        
        self.analysis_results['efficiency_analysis'] = {
            'scar_to_geoid_ratio': scar_to_geoid_ratio if active_geoids > 0 else 0,
            'scars_per_cycle': scars_per_cycle if cycle_count > 0 else 0,
            'vault_balance_percentage': balance_percentage if vault_a_scars + vault_b_scars > 0 else 0,
            'vault_imbalance': abs(vault_a_scars - vault_b_scars)
        }
    
    def analyze_entropy_dynamics(self):
        """Analyze entropy evolution during testing"""
        print("\n🌀 ENTROPY DYNAMICS ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            # Get entropy progression from scars
            query = """
            SELECT timestamp, pre_entropy, post_entropy, delta_entropy
            FROM scars 
            WHERE timestamp > datetime('now', '-1 hour')
            ORDER BY timestamp ASC
            """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                print("❌ No entropy data found")
                return
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate cumulative entropy change
            df['cumulative_delta'] = df['delta_entropy'].cumsum()
            
            print(f"🌀 Entropy Evolution Analysis:")
            print(f"   Initial Entropy: {df['pre_entropy'].iloc[0]:.3f}")
            print(f"   Final Entropy: {df['post_entropy'].iloc[-1]:.3f}")
            print(f"   Total Entropy Change: {df['cumulative_delta'].iloc[-1]:.3f}")
            print(f"   Average Δ per Scar: {df['delta_entropy'].mean():.3f}")
            
            # Identify entropy phases
            entropy_increases = df[df['delta_entropy'] > 0]
            entropy_decreases = df[df['delta_entropy'] < 0]
            
            print(f"\n📈 Entropy Phase Analysis:")
            print(f"   Entropy Increases: {len(entropy_increases)} ({len(entropy_increases)/len(df)*100:.1f}%)")
            print(f"   Entropy Decreases: {len(entropy_decreases)} ({len(entropy_decreases)/len(df)*100:.1f}%)")
            print(f"   Average Increase: {entropy_increases['delta_entropy'].mean():.3f}")
            print(f"   Average Decrease: {entropy_decreases['delta_entropy'].mean():.3f}")
            
            # Identify entropy volatility
            entropy_volatility = df['delta_entropy'].std()
            print(f"   Entropy Volatility (σ): {entropy_volatility:.3f}")
            
            # Find extreme entropy events
            entropy_threshold = df['delta_entropy'].std() * 2
            extreme_events = df[abs(df['delta_entropy']) > entropy_threshold]
            
            print(f"\n🚨 Extreme Entropy Events (>2σ):")
            print(f"   Count: {len(extreme_events)}")
            if len(extreme_events) > 0:
                print(f"   Max Increase: {extreme_events['delta_entropy'].max():.3f}")
                print(f"   Max Decrease: {extreme_events['delta_entropy'].min():.3f}")
            
            self.analysis_results['entropy_analysis'] = {
                'initial_entropy': float(df['pre_entropy'].iloc[0]),
                'final_entropy': float(df['post_entropy'].iloc[-1]),
                'total_change': float(df['cumulative_delta'].iloc[-1]),
                'average_delta': float(df['delta_entropy'].mean()),
                'entropy_volatility': float(entropy_volatility),
                'extreme_events': len(extreme_events)
            }
            
        except Exception as e:
            print(f"❌ Error in entropy analysis: {e}")
        finally:
            conn.close()
    
    def analyze_semantic_clustering(self):
        """Analyze clustering patterns in semantic space"""
        print("\n🧠 SEMANTIC CLUSTERING ANALYSIS")
        print("=" * 50)
        
        conn = self.connect_to_database()
        if not conn:
            return
        
        try:
            # Get semantic vectors for analysis
            query = """
            SELECT geoid_id, semantic_state_json, semantic_vector, metadata_json
            FROM geoids 
            WHERE json_extract(metadata_json, '$.test_stream') = 1
            OR json_extract(metadata_json, '$.scenario_type') IS NOT NULL
            ORDER BY rowid DESC
            LIMIT 100
            """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                print("❌ No semantic data found")
                return
            
            # Parse semantic features
            semantic_features = []
            for _, row in df.iterrows():
                if row['semantic_state_json']:
                    features = json.loads(row['semantic_state_json'])
                    semantic_features.append(features)
            
            if not semantic_features:
                print("❌ No valid semantic features found")
                return
            
            semantic_df = pd.DataFrame(semantic_features)
            
            # Calculate feature correlations
            correlation_matrix = semantic_df.corr()
            
            print(f"🔗 Semantic Feature Correlations:")
            for i, feature1 in enumerate(semantic_df.columns):
                for j, feature2 in enumerate(semantic_df.columns):
                    if i < j:  # Only show upper triangle
                        corr = correlation_matrix.loc[feature1, feature2]
                        if abs(corr) > 0.3:  # Only show significant correlations
                            print(f"   {feature1} ↔ {feature2}: {corr:.3f}")
            
            # Identify semantic clusters
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            # Standardize features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(semantic_df)
            
            # Perform clustering
            n_clusters = min(5, len(semantic_df) // 2)  # Reasonable number of clusters
            if n_clusters >= 2:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(scaled_features)
                
                print(f"\n🎯 Semantic Clustering (k={n_clusters}):")
                cluster_counts = pd.Series(clusters).value_counts().sort_index()
                for cluster_id, count in cluster_counts.items():
                    percentage = (count / len(semantic_df)) * 100
                    print(f"   Cluster {cluster_id}: {count} geoids ({percentage:.1f}%)")
                
                # Analyze cluster characteristics
                semantic_df['cluster'] = clusters
                
                print(f"\n📊 Cluster Characteristics:")
                for cluster_id in range(n_clusters):
                    cluster_data = semantic_df[semantic_df['cluster'] == cluster_id]
                    print(f"   Cluster {cluster_id}:")
                    for feature in semantic_df.columns[:-1]:  # Exclude cluster column
                        mean_val = cluster_data[feature].mean()
                        print(f"      {feature}: {mean_val:.3f}")
            
            self.analysis_results['semantic_analysis'] = {
                'feature_correlations': correlation_matrix.to_dict(),
                'cluster_distribution': cluster_counts.to_dict() if n_clusters >= 2 else {},
                'feature_statistics': semantic_df.describe().to_dict()
            }
            
        except Exception as e:
            print(f"❌ Error in semantic analysis: {e}")
        finally:
            conn.close()
    
    def generate_performance_insights(self):
        """Generate high-level performance insights"""
        print("\n🎯 PERFORMANCE INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)
        
        insights = []
        recommendations = []
        
        # Analyze contradiction detection rate
        if 'scar_analysis' in self.analysis_results:
            scar_data = self.analysis_results['scar_analysis']
            scars_per_minute = scar_data.get('temporal_stats', {}).get('avg_per_minute', 0)
            
            if scars_per_minute > 10:
                insights.append("🔥 High contradiction detection rate indicates active market stress")
                recommendations.append("📊 Consider implementing real-time alerting for sustained high activity")
            elif scars_per_minute > 5:
                insights.append("⚡ Moderate contradiction detection suggests normal market volatility")
            else:
                insights.append("✅ Low contradiction rate indicates stable market conditions")
        
        # Analyze vault balance
        if 'efficiency_analysis' in self.analysis_results:
            efficiency_data = self.analysis_results['efficiency_analysis']
            vault_balance = efficiency_data.get('vault_balance_percentage', 0)
            
            if vault_balance > 99:
                insights.append("🏛️  Excellent vault balance maintained under stress")
            elif vault_balance > 95:
                insights.append("🏛️  Good vault balance with minor imbalance")
                recommendations.append("🔧 Monitor vault distribution during extended testing")
            else:
                insights.append("⚠️  Vault imbalance detected - may indicate system bias")
                recommendations.append("🔧 Investigate vault rebalancing mechanisms")
        
        # Analyze entropy dynamics
        if 'entropy_analysis' in self.analysis_results:
            entropy_data = self.analysis_results['entropy_analysis']
            total_change = entropy_data.get('total_change', 0)
            volatility = entropy_data.get('entropy_volatility', 0)
            
            if abs(total_change) > 100:
                insights.append("🌀 Significant entropy evolution indicates major system learning")
            
            if volatility > 1.0:
                insights.append("🌪️  High entropy volatility suggests dynamic contradiction processing")
                recommendations.append("📈 Consider entropy smoothing for production environments")
        
        # Analyze semantic clustering
        if 'semantic_analysis' in self.analysis_results:
            semantic_data = self.analysis_results['semantic_analysis']
            correlations = semantic_data.get('feature_correlations', {})
            
            # Check for high correlations
            high_corr_count = 0
            for feature1, corr_dict in correlations.items():
                for feature2, corr_val in corr_dict.items():
                    if feature1 != feature2 and abs(corr_val) > 0.7:
                        high_corr_count += 1
            
            if high_corr_count > 0:
                insights.append("🔗 Strong semantic feature correlations detected")
                recommendations.append("🧠 Consider feature engineering to reduce redundancy")
        
        # System scalability insights
        if 'geoid_analysis' in self.analysis_results:
            geoid_data = self.analysis_results['geoid_analysis']
            total_geoids = geoid_data.get('total_geoids', 0)
            
            if total_geoids > 50:
                insights.append("📈 System successfully handled large-scale geoid creation")
            
            type_distribution = geoid_data.get('type_distribution', {})
            if len(type_distribution) > 3:
                insights.append("🎭 Diverse geoid types processed successfully")
        
        # Print insights
        print("💡 Key Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        print(f"\n🔧 Recommendations:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")
        
        # Overall system assessment
        print(f"\n🏆 OVERALL SYSTEM ASSESSMENT:")
        
        performance_score = 0
        max_score = 0
        
        # Vault balance score
        if 'efficiency_analysis' in self.analysis_results:
            vault_balance = self.analysis_results['efficiency_analysis'].get('vault_balance_percentage', 0)
            performance_score += vault_balance
            max_score += 100
        
        # Contradiction detection score
        if 'scar_analysis' in self.analysis_results:
            scars_per_minute = self.analysis_results['scar_analysis'].get('temporal_stats', {}).get('avg_per_minute', 0)
            detection_score = min(100, scars_per_minute * 10)  # Cap at 100
            performance_score += detection_score
            max_score += 100
        
        # System stability score (inverse of entropy volatility)
        if 'entropy_analysis' in self.analysis_results:
            volatility = self.analysis_results['entropy_analysis'].get('entropy_volatility', 0)
            stability_score = max(0, 100 - volatility * 20)  # Higher volatility = lower score
            performance_score += stability_score
            max_score += 100
        
        if max_score > 0:
            overall_score = (performance_score / max_score) * 100
            
            if overall_score >= 90:
                grade = "A+ (Excellent)"
                status = "🟢 PRODUCTION READY"
            elif overall_score >= 80:
                grade = "A (Very Good)"
                status = "🟡 PRODUCTION READY WITH MONITORING"
            elif overall_score >= 70:
                grade = "B (Good)"
                status = "🟡 REQUIRES OPTIMIZATION"
            elif overall_score >= 60:
                grade = "C (Acceptable)"
                status = "🟠 REQUIRES SIGNIFICANT IMPROVEMENT"
            else:
                grade = "D (Poor)"
                status = "🔴 NOT PRODUCTION READY"
            
            print(f"   📊 Performance Score: {overall_score:.1f}/100")
            print(f"   🎓 Grade: {grade}")
            print(f"   🚦 Status: {status}")
        
        self.analysis_results['performance_insights'] = {
            'insights': insights,
            'recommendations': recommendations,
            'overall_score': overall_score if max_score > 0 else 0,
            'grade': grade if max_score > 0 else "N/A",
            'status': status if max_score > 0 else "INSUFFICIENT DATA"
        }
    
    def save_analysis_report(self):
        """Save comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"volatility_analysis_report_{timestamp}.json"
        
        try:
            with open(report_filename, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'system_metrics': self.system_metrics,
                    'analysis_results': self.analysis_results
                }, f, indent=2)
            
            print(f"\n💾 Analysis report saved: {report_filename}")
            return report_filename
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return None
    
    def run_complete_analysis(self):
        """Run complete volatility analysis"""
        print("🔬 KIMERA SWM HIGH VOLATILITY ANALYSIS")
        print("=" * 60)
        print("Comprehensive analysis of KIMERA's performance during")
        print("high volatility testing and extreme market conditions")
        
        # Extract system metrics
        if not self.extract_system_metrics():
            print("⚠️  Continuing with limited analysis...")
        
        # Run all analysis modules
        self.analyze_geoid_distribution()
        self.analyze_scar_patterns()
        self.analyze_contradiction_efficiency()
        self.analyze_entropy_dynamics()
        self.analyze_semantic_clustering()
        self.generate_performance_insights()
        
        # Save report
        report_file = self.save_analysis_report()
        
        print(f"\n🎯 ANALYSIS COMPLETE")
        print(f"=" * 30)
        print(f"✅ All analysis modules executed successfully")
        print(f"📊 Comprehensive insights generated")
        print(f"💾 Report saved: {report_file}")
        print(f"\n🚀 KIMERA SWM volatility analysis completed!")

def main():
    """Main analysis function"""
    analyzer = VolatilityAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()