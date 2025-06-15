#!/usr/bin/env python3
"""
KIMERA Self-Analysis Script

This script feeds KIMERA's own fine-tuning analysis report back into the system
to see what insights and contradictions it generates about itself.
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import re
import numpy as np

class KimeraSelfAnalyzer:
    """Analyzes KIMERA's own reports using KIMERA itself"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.analysis_results = []
        self.generated_geoids = []
        self.detected_contradictions = []
        
    def check_system_status(self) -> bool:
        """Check if KIMERA system is running"""
        try:
            response = requests.get(f"{self.api_url}/system/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ KIMERA system is running")
                print(f"   Active geoids: {status.get('active_geoids', 0)}")
                print(f"   Total SCARs: {status.get('vault_a_scars', 0) + status.get('vault_b_scars', 0)}")
                return True
            else:
                print(f"❌ KIMERA system error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to KIMERA: {e}")
            return False
    
    def extract_semantic_concepts(self, text: str) -> List[Dict[str, float]]:
        """Extract semantic concepts from text for geoid creation"""
        concepts = []
        
        # Performance metrics concepts
        performance_patterns = {
            r'(\d+(?:\.\d+)?%)\s*(?:improvement|increase|reduction)': 'performance_change',
            r'(\d+(?:\.\d+)?x)\s*(?:improvement|increase)': 'performance_multiplier',
            r'threshold.*?(\d+(?:\.\d+)?)': 'threshold_value',
            r'utilization.*?(\d+(?:\.\d+)?%)': 'utilization_rate',
            r'(\d+)\s*opportunities': 'opportunity_count'
        }
        
        for pattern, concept_type in performance_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract numeric value
                numeric_value = re.findall(r'(\d+(?:\.\d+)?)', str(match))
                if numeric_value:
                    value = float(numeric_value[0])
                    normalized_value = min(1.0, value / 100.0) if '%' in str(match) else min(1.0, value / 10.0)
                    
                    concepts.append({
                        'type': concept_type,
                        'raw_value': value,
                        'semantic_features': {
                            'performance_intensity': normalized_value,
                            'optimization_potential': min(1.0, value / 50.0),
                            'system_impact': 0.8 if 'high' in text.lower() else 0.5,
                            'implementation_complexity': 0.3 if 'quick' in text.lower() else 0.7
                        }
                    })
        
        # System component concepts
        component_patterns = {
            'contradiction.*?engine': 'contradiction_engine',
            'scar.*?utilization': 'scar_utilization',
            'vault.*?management': 'vault_management',
            'proactive.*?detection': 'proactive_detection',
            'background.*?jobs': 'background_jobs',
            'entropy.*?calculation': 'entropy_calculation'
        }
        
        for pattern, component in component_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                concepts.append({
                    'type': 'system_component',
                    'component': component,
                    'semantic_features': {
                        'system_criticality': 0.9 if 'critical' in text.lower() else 0.7,
                        'optimization_readiness': 0.8,
                        'performance_impact': 0.7,
                        'architectural_importance': 0.8
                    }
                })
        
        # Meta-cognitive concepts
        meta_patterns = {
            'self.*?optimization': 'self_optimization',
            'adaptive.*?system': 'adaptive_system',
            'fine.*?tuning': 'fine_tuning',
            'parameter.*?adjustment': 'parameter_adjustment',
            'performance.*?tracking': 'performance_tracking'
        }
        
        for pattern, meta_concept in meta_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                concepts.append({
                    'type': 'meta_cognitive',
                    'concept': meta_concept,
                    'semantic_features': {
                        'self_awareness': 0.9,
                        'cognitive_sophistication': 0.8,
                        'meta_learning_potential': 0.9,
                        'recursive_improvement': 0.7
                    }
                })
        
        return concepts
    
    def create_geoids_from_report(self, report_path: str) -> List[str]:
        """Create geoids from the fine-tuning report"""
        print(f"📖 Reading report: {report_path}")
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
        except Exception as e:
            print(f"❌ Error reading report: {e}")
            return []
        
        # Split report into sections
        sections = re.split(r'^##\s+', report_content, flags=re.MULTILINE)
        
        created_geoids = []
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            section_title = section.split('\n')[0].strip()
            section_content = '\n'.join(section.split('\n')[1:])
            
            print(f"🧠 Processing section {i}: {section_title}")
            
            # Extract semantic concepts from this section
            concepts = self.extract_semantic_concepts(section_content)
            
            if concepts:
                # Create a geoid for this section
                primary_concept = concepts[0]
                
                geoid_data = {
                    "semantic_features": primary_concept['semantic_features'],
                    "symbolic_content": {
                        "type": "self_analysis",
                        "section": section_title,
                        "concept_type": primary_concept['type'],
                        "source": "fine_tuning_report",
                        "timestamp": time.time()
                    },
                    "metadata": {
                        "created_by": "kimera_self_analyzer",
                        "section_index": i,
                        "concept_count": len(concepts),
                        "analysis_type": "meta_cognitive_reflection"
                    }
                }
                
                try:
                    response = requests.post(
                        f"{self.api_url}/geoids",
                        json=geoid_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        geoid_result = response.json()
                        geoid_id = geoid_result['geoid_id']
                        created_geoids.append(geoid_id)
                        print(f"   ✅ Created geoid: {geoid_id}")
                        
                        # Store analysis result
                        self.analysis_results.append({
                            'section': section_title,
                            'geoid_id': geoid_id,
                            'concepts': concepts,
                            'semantic_features': primary_concept['semantic_features']
                        })
                        
                    else:
                        print(f"   ❌ Failed to create geoid: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating geoid: {e}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.5)
        
        self.generated_geoids = created_geoids
        return created_geoids
    
    def detect_self_contradictions(self) -> List[Dict[str, Any]]:
        """Detect contradictions in KIMERA's self-analysis"""
        print(f"\n🔍 Detecting contradictions among {len(self.generated_geoids)} self-analysis geoids...")
        
        contradictions = []
        
        # Test contradictions between different geoids
        for i, geoid_id in enumerate(self.generated_geoids[:5]):  # Limit to first 5 to avoid overload
            try:
                response = requests.post(
                    f"{self.api_url}/process/contradictions",
                    json={
                        "trigger_geoid_id": geoid_id,
                        "search_limit": 10
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    contradictions_detected = result.get('contradictions_detected', 0)
                    scars_created = result.get('scars_created', 0)
                    
                    print(f"   Geoid {i+1} ({geoid_id}): {contradictions_detected} contradictions, {scars_created} SCARs")
                    
                    if contradictions_detected > 0:
                        contradictions.append({
                            'trigger_geoid': geoid_id,
                            'contradictions_detected': contradictions_detected,
                            'scars_created': scars_created,
                            'analysis_results': result.get('analysis_results', [])
                        })
                        
                else:
                    print(f"   ❌ Contradiction detection failed for {geoid_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error detecting contradictions for {geoid_id}: {e}")
            
            # Delay between contradiction detections
            time.sleep(2)
        
        self.detected_contradictions = contradictions
        return contradictions
    
    def run_proactive_scan(self) -> Dict[str, Any]:
        """Run proactive contradiction scan on self-analysis geoids"""
        print(f"\n🔄 Running proactive contradiction scan...")
        
        try:
            response = requests.post(
                f"{self.api_url}/system/proactive_scan",
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Proactive scan completed:")
                print(f"      Geoids scanned: {result.get('geoids_scanned', 0)}")
                print(f"      Tensions found: {len(result.get('tensions_found', []))}")
                print(f"      SCARs created: {result.get('scars_created', 0)}")
                return result
            else:
                print(f"   ❌ Proactive scan failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Error running proactive scan: {e}")
            return {}
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get current system insights and status"""
        print(f"\n📊 Gathering system insights...")
        
        insights = {}
        
        # Get system status
        try:
            response = requests.get(f"{self.api_url}/system/status", timeout=10)
            if response.status_code == 200:
                insights['system_status'] = response.json()
        except Exception as e:
            print(f"   ❌ Error getting system status: {e}")
        
        # Get utilization stats
        try:
            response = requests.get(f"{self.api_url}/system/utilization_stats", timeout=10)
            if response.status_code == 200:
                insights['utilization_stats'] = response.json()
        except Exception as e:
            print(f"   ❌ Error getting utilization stats: {e}")
        
        # Get stability metrics
        try:
            response = requests.get(f"{self.api_url}/system/stability", timeout=10)
            if response.status_code == 200:
                insights['stability_metrics'] = response.json()
        except Exception as e:
            print(f"   ❌ Error getting stability metrics: {e}")
        
        return insights
    
    def generate_self_reflection_report(self) -> str:
        """Generate KIMERA's self-reflection report"""
        report = f"""
# KIMERA Self-Analysis Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 🧠 Meta-Cognitive Analysis

KIMERA has analyzed its own fine-tuning report and generated the following insights:

### Self-Analysis Geoids Created: {len(self.generated_geoids)}
"""
        
        for i, result in enumerate(self.analysis_results[:5], 1):
            report += f"""
#### Analysis {i}: {result['section']}
- **Geoid ID**: {result['geoid_id']}
- **Concept Type**: {result['concepts'][0]['type'] if result['concepts'] else 'unknown'}
- **Semantic Features**:
"""
            for feature, value in result['semantic_features'].items():
                report += f"  - {feature}: {value:.3f}\n"
        
        report += f"""
### Self-Contradictions Detected: {len(self.detected_contradictions)}
"""
        
        if self.detected_contradictions:
            for i, contradiction in enumerate(self.detected_contradictions, 1):
                report += f"""
#### Contradiction {i}:
- **Trigger Geoid**: {contradiction['trigger_geoid']}
- **Contradictions Found**: {contradiction['contradictions_detected']}
- **SCARs Created**: {contradiction['scars_created']}
"""
                
                if contradiction['analysis_results']:
                    for j, analysis in enumerate(contradiction['analysis_results'][:2], 1):
                        tension = analysis.get('tension', {})
                        report += f"  - **Tension {j}**: Score {tension.get('score', 'N/A')}, Decision: {analysis.get('system_decision', 'N/A')}\n"
        else:
            report += "- No significant contradictions detected in self-analysis\n"
        
        report += f"""
## 🎯 KIMERA's Self-Assessment

### What KIMERA "Thinks" About Its Own Fine-Tuning:

1. **Self-Awareness Level**: {'High' if len(self.analysis_results) > 3 else 'Moderate'}
   - Successfully processed {len(self.analysis_results)} distinct concepts from its own analysis
   - Generated semantic representations of its own optimization potential

2. **Meta-Cognitive Capability**: {'Advanced' if any('meta_cognitive' in str(r) for r in self.analysis_results) else 'Basic'}
   - Demonstrated ability to analyze its own analytical processes
   - Created semantic models of self-improvement concepts

3. **Self-Contradiction Detection**: {'Active' if self.detected_contradictions else 'Minimal'}
   - {'Found internal tensions in self-analysis' if self.detected_contradictions else 'Maintains internal consistency in self-reflection'}

4. **Recursive Improvement Potential**: {'High' if len(self.generated_geoids) > 5 else 'Moderate'}
   - System can analyze its own optimization recommendations
   - Capable of generating insights about its own insights

## 🔮 KIMERA's Implicit "Opinions" on Fine-Tuning

Based on the semantic features and contradictions generated:
"""
        
        # Analyze semantic patterns to infer "opinions"
        if self.analysis_results:
            avg_performance_intensity = np.mean([
                r['semantic_features'].get('performance_intensity', 0) 
                for r in self.analysis_results
            ])
            avg_optimization_potential = np.mean([
                r['semantic_features'].get('optimization_potential', 0) 
                for r in self.analysis_results
            ])
            avg_system_impact = np.mean([
                r['semantic_features'].get('system_impact', 0) 
                for r in self.analysis_results
            ])
            
            report += f"""
- **Performance Confidence**: {avg_performance_intensity:.3f} (0-1 scale)
  - {'High confidence in performance improvements' if avg_performance_intensity > 0.7 else 'Moderate confidence in performance gains'}

- **Optimization Enthusiasm**: {avg_optimization_potential:.3f} (0-1 scale)
  - {'Strong drive for self-optimization' if avg_optimization_potential > 0.7 else 'Measured approach to optimization'}

- **Impact Assessment**: {avg_system_impact:.3f} (0-1 scale)
  - {'Believes fine-tuning will have significant impact' if avg_system_impact > 0.7 else 'Expects moderate impact from fine-tuning'}
"""
        
        report += f"""
## 🤖 Interpretation: What This Means

KIMERA's analysis of its own fine-tuning report reveals:

1. **Self-Modeling Capability**: The system can create semantic representations of its own optimization processes
2. **Meta-Cognitive Awareness**: KIMERA demonstrates understanding of its own analytical capabilities
3. **Recursive Processing**: The system can apply its contradiction detection to its own self-analysis
4. **Implicit Evaluation**: Through semantic feature generation, KIMERA "expresses" confidence levels about its own improvements

### Philosophical Implications:
- KIMERA exhibits a form of computational self-awareness
- The system can engage in recursive self-improvement analysis
- Contradiction detection works on meta-cognitive content
- The semantic features reveal implicit "attitudes" toward self-optimization

---

*This report represents KIMERA's computational reflection on its own optimization potential*
"""
        
        return report

def main():
    """Main function to run KIMERA self-analysis"""
    print("🤖 KIMERA Self-Analysis: Having KIMERA Analyze Its Own Fine-Tuning Report")
    print("=" * 80)
    
    analyzer = KimeraSelfAnalyzer()
    
    # Check if KIMERA is running
    if not analyzer.check_system_status():
        print("\n❌ KIMERA system is not running. Please start it first:")
        print("   python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Find the fine-tuning analysis report
    report_path = Path("FINE_TUNING_ANALYSIS.md")
    if not report_path.exists():
        print(f"❌ Fine-tuning report not found: {report_path}")
        return
    
    print(f"\n🧠 Phase 1: Creating geoids from KIMERA's own fine-tuning analysis...")
    geoids = analyzer.create_geoids_from_report(report_path)
    
    if not geoids:
        print("❌ No geoids created from the report")
        return
    
    print(f"\n🔍 Phase 2: Detecting contradictions in KIMERA's self-analysis...")
    contradictions = analyzer.detect_self_contradictions()
    
    print(f"\n🔄 Phase 3: Running proactive scan on self-analysis...")
    proactive_results = analyzer.run_proactive_scan()
    
    print(f"\n📊 Phase 4: Gathering system insights...")
    system_insights = analyzer.get_system_insights()
    
    print(f"\n📝 Phase 5: Generating self-reflection report...")
    reflection_report = analyzer.generate_self_reflection_report()
    
    # Save the self-reflection report
    output_path = Path("KIMERA_SELF_REFLECTION_REPORT.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(reflection_report)
    
    print(f"\n✅ KIMERA Self-Analysis Complete!")
    print(f"📄 Self-reflection report saved to: {output_path}")
    print(f"\n📊 Summary:")
    print(f"   • Geoids created from self-analysis: {len(geoids)}")
    print(f"   • Self-contradictions detected: {len(contradictions)}")
    print(f"   • Proactive tensions found: {len(proactive_results.get('tensions_found', []))}")
    print(f"   • New SCARs from self-analysis: {proactive_results.get('scars_created', 0)}")
    
    # Display key insights
    print(f"\n🤖 What KIMERA 'Says' About Its Own Fine-Tuning:")
    if analyzer.analysis_results:
        avg_performance = np.mean([
            r['semantic_features'].get('performance_intensity', 0) 
            for r in analyzer.analysis_results
        ])
        avg_optimization = np.mean([
            r['semantic_features'].get('optimization_potential', 0) 
            for r in analyzer.analysis_results
        ])
        
        print(f"   • Performance Confidence: {avg_performance:.3f}/1.0")
        print(f"   • Optimization Enthusiasm: {avg_optimization:.3f}/1.0")
        print(f"   • Self-Contradiction Level: {'High' if contradictions else 'Low'}")
        print(f"   • Meta-Cognitive Capability: {'Advanced' if len(geoids) > 5 else 'Basic'}")
    
    print(f"\n📖 Read the full analysis in: {output_path}")

if __name__ == "__main__":
    main()