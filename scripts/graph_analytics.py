#!/usr/bin/env python3
"""
Graph Analytics for Kimera SWM using Neo4j
Implements pattern discovery and semantic analysis
"""

import os
import sys
from neo4j import GraphDatabase
from typing import List, Dict, Tuple, Any
import json
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class KimeraGraphAnalytics:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def close(self):
        self.driver.close()
    
    def analyze_contradiction_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in semantic contradictions"""
        with self.driver.session() as session:
            # Find contradiction clusters
            clusters = session.run("""
                MATCH (n1)-[r:CONTRADICTS]-(n2)
                WITH n1, collect(n2) as contradictions
                WHERE size(contradictions) > 1
                RETURN n1.id as node_id, 
                       n1.name as concept,
                       size(contradictions) as contradiction_count,
                       [n IN contradictions | n.name] as contradicting_concepts
                ORDER BY contradiction_count DESC
                LIMIT 10
            """).data()
            
            # Find contradiction chains
            chains = session.run("""
                MATCH path = (n1)-[:CONTRADICTS*2..4]-(n2)
                WHERE n1 <> n2
                WITH path, length(path) as chain_length
                RETURN [n IN nodes(path) | n.name] as chain,
                       chain_length
                ORDER BY chain_length DESC
                LIMIT 10
            """).data()
            
            # Resolution success patterns
            resolutions = session.run("""
                MATCH (s:SCAR)-[:RESOLVED_BY]->(r:Resolution)
                WITH r.strategy as strategy, count(s) as usage_count
                RETURN strategy, usage_count
                ORDER BY usage_count DESC
            """).data()
            
            return {
                "contradiction_clusters": clusters,
                "contradiction_chains": chains,
                "resolution_patterns": resolutions
            }
    
    def discover_semantic_communities(self) -> List[Dict[str, Any]]:
        """Discover semantic communities using Louvain algorithm"""
        with self.driver.session() as session:
            # Create graph projection for community detection
            session.run("""
                CALL gds.graph.project.cypher(
                    'semantic-graph',
                    'MATCH (n) WHERE n:Concept OR n:Geoid RETURN id(n) AS id',
                    'MATCH (n1)-[r:RELATES_TO|SIMILAR_TO]-(n2) 
                     RETURN id(n1) AS source, id(n2) AS target, 
                     coalesce(r.weight, 1.0) AS weight'
                )
            """)
            
            # Run Louvain community detection
            communities = session.run("""
                CALL gds.louvain.stream('semantic-graph')
                YIELD nodeId, communityId
                WITH communityId, collect(gds.util.asNode(nodeId).name) as members
                WHERE size(members) > 2
                RETURN communityId, members, size(members) as size
                ORDER BY size DESC
                LIMIT 20
            """).data()
            
            # Clean up projection
            session.run("CALL gds.graph.drop('semantic-graph')")
            
            return communities
    
    def analyze_causal_networks(self) -> Dict[str, Any]:
        """Analyze causal relationship networks"""
        with self.driver.session() as session:
            # Find causal hubs (high in/out degree)
            hubs = session.run("""
                MATCH (n)
                WITH n, 
                     size((n)-[:CAUSES]->()) as out_degree,
                     size((n)<-[:CAUSES]-()) as in_degree
                WHERE out_degree + in_degree > 3
                RETURN n.name as concept,
                       out_degree as causes_count,
                       in_degree as caused_by_count,
                       out_degree + in_degree as total_degree
                ORDER BY total_degree DESC
                LIMIT 15
            """).data()
            
            # Find causal chains
            chains = session.run("""
                MATCH path = (start)-[:CAUSES*2..5]->(end)
                WHERE NOT (start)<-[:CAUSES]-() AND NOT (end)-[:CAUSES]->()
                WITH path, length(path) as chain_length
                RETURN [n IN nodes(path) | n.name] as causal_chain,
                       chain_length
                ORDER BY chain_length DESC
                LIMIT 10
            """).data()
            
            # Detect causal cycles
            cycles = session.run("""
                MATCH path = (n)-[:CAUSES*2..6]->(n)
                WITH path, length(path) as cycle_length
                RETURN [node IN nodes(path) | node.name][0..-1] as cycle,
                       cycle_length
                ORDER BY cycle_length ASC
                LIMIT 10
            """).data()
            
            return {
                "causal_hubs": hubs,
                "causal_chains": chains,
                "causal_cycles": cycles
            }
    
    def compute_semantic_centrality(self) -> List[Dict[str, Any]]:
        """Compute various centrality measures for semantic importance"""
        with self.driver.session() as session:
            # Create projection
            session.run("""
                CALL gds.graph.project(
                    'centrality-graph',
                    ['Concept', 'Geoid'],
                    {
                        RELATES_TO: {orientation: 'UNDIRECTED'},
                        SIMILAR_TO: {orientation: 'UNDIRECTED'},
                        CAUSES: {orientation: 'NATURAL'}
                    }
                )
            """)
            
            # PageRank for overall importance
            pagerank = session.run("""
                CALL gds.pageRank.stream('centrality-graph')
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) as node, score
                RETURN node.name as concept, score as pagerank
                ORDER BY score DESC
                LIMIT 20
            """).data()
            
            # Betweenness centrality for bridge concepts
            betweenness = session.run("""
                CALL gds.betweenness.stream('centrality-graph')
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) as node, score
                WHERE score > 0
                RETURN node.name as concept, score as betweenness
                ORDER BY score DESC
                LIMIT 20
            """).data()
            
            # Clean up
            session.run("CALL gds.graph.drop('centrality-graph')")
            
            return {
                "pagerank": pagerank,
                "betweenness": betweenness
            }
    
    def find_semantic_bridges(self) -> List[Dict[str, Any]]:
        """Find concepts that bridge different semantic domains"""
        with self.driver.session() as session:
            bridges = session.run("""
                MATCH (n1:Concept)-[:RELATES_TO]-(bridge)-[:RELATES_TO]-(n2:Concept)
                WHERE n1 <> n2 AND NOT (n1)-[:RELATES_TO]-(n2)
                WITH bridge, count(DISTINCT [n1, n2]) as bridge_count
                WHERE bridge_count > 3
                RETURN bridge.name as bridge_concept,
                       bridge_count as connections_bridged
                ORDER BY bridge_count DESC
                LIMIT 15
            """).data()
            
            return bridges
    
    def analyze_scar_resolution_paths(self) -> Dict[str, Any]:
        """Analyze SCAR resolution pathways and patterns"""
        with self.driver.session() as session:
            # Most effective resolution strategies
            strategies = session.run("""
                MATCH (s:SCAR)-[r:RESOLVED_BY]->(res:Resolution)
                WHERE s.post_entropy < s.pre_entropy
                WITH res.strategy as strategy,
                     avg(s.pre_entropy - s.post_entropy) as avg_entropy_reduction,
                     count(s) as usage_count
                RETURN strategy, avg_entropy_reduction, usage_count
                ORDER BY avg_entropy_reduction DESC
            """).data()
            
            # SCAR clustering by similarity
            similar_scars = session.run("""
                MATCH (s1:SCAR)-[sim:SIMILAR_TO]-(s2:SCAR)
                WHERE sim.similarity > 0.8
                WITH s1, collect(s2) as similar_group
                WHERE size(similar_group) > 2
                RETURN s1.id as scar_id,
                       s1.reason as reason,
                       size(similar_group) as cluster_size,
                       [s IN similar_group | s.reason][0..3] as similar_reasons
                ORDER BY cluster_size DESC
                LIMIT 10
            """).data()
            
            return {
                "effective_strategies": strategies,
                "scar_clusters": similar_scars
            }
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report"""
        print("\n📊 Kimera Graph Analytics Report")
        print("=" * 50)
        
        # Contradiction patterns
        print("\n🔍 Analyzing Contradiction Patterns...")
        contradictions = self.analyze_contradiction_patterns()
        print(f"   Found {len(contradictions['contradiction_clusters'])} contradiction clusters")
        print(f"   Found {len(contradictions['contradiction_chains'])} contradiction chains")
        
        # Semantic communities
        print("\n🌐 Discovering Semantic Communities...")
        communities = self.discover_semantic_communities()
        print(f"   Discovered {len(communities)} semantic communities")
        
        # Causal networks
        print("\n🔗 Analyzing Causal Networks...")
        causal = self.analyze_causal_networks()
        print(f"   Found {len(causal['causal_hubs'])} causal hubs")
        print(f"   Found {len(causal['causal_cycles'])} causal cycles")
        
        # Centrality analysis
        print("\n📈 Computing Semantic Centrality...")
        centrality = self.compute_semantic_centrality()
        
        # Semantic bridges
        print("\n🌉 Finding Semantic Bridges...")
        bridges = self.find_semantic_bridges()
        print(f"   Found {len(bridges)} bridge concepts")
        
        # SCAR analysis
        print("\n🔧 Analyzing SCAR Resolution Paths...")
        scar_analysis = self.analyze_scar_resolution_paths()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "contradictions": contradictions,
            "communities": communities,
            "causal_analysis": causal,
            "centrality": centrality,
            "bridges": bridges,
            "scar_patterns": scar_analysis
        }

def main():
    """Run graph analytics and save report"""
    analytics = KimeraGraphAnalytics()
    
    try:
        # Generate comprehensive report
        report = analytics.generate_insights_report()
        
        # Save report
        report_path = "graph_analytics_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved to {report_path}")
        
        # Print key insights
        print("\n🎯 Key Insights:")
        
        # Top contradiction clusters
        if report['contradictions']['contradiction_clusters']:
            print("\n   Top Contradiction Clusters:")
            for cluster in report['contradictions']['contradiction_clusters'][:3]:
                print(f"   - {cluster['concept']}: {cluster['contradiction_count']} contradictions")
        
        # Largest communities
        if report['communities']:
            print("\n   Largest Semantic Communities:")
            for comm in report['communities'][:3]:
                print(f"   - Community {comm['communityId']}: {comm['size']} members")
                print(f"     Members: {', '.join(comm['members'][:5])}...")
        
        # Top causal hubs
        if report['causal_analysis']['causal_hubs']:
            print("\n   Top Causal Hubs:")
            for hub in report['causal_analysis']['causal_hubs'][:3]:
                print(f"   - {hub['concept']}: causes {hub['causes_count']}, caused by {hub['caused_by_count']}")
        
        # Most central concepts
        if report['centrality']['pagerank']:
            print("\n   Most Central Concepts (PageRank):")
            for concept in report['centrality']['pagerank'][:5]:
                print(f"   - {concept['concept']}: {concept['pagerank']:.4f}")
        
    finally:
        analytics.close()

if __name__ == "__main__":
    main()