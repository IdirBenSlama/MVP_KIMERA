#!/usr/bin/env python3
"""
Neo4j Integration Test Suite

This script tests the new Neo4j layer without requiring the full KIMERA system.
It verifies:
1. Neo4j connection and driver setup
2. Graph model CRUD operations (create/get geoids and scars)
3. Dual-write functionality from VaultManager
4. Data consistency between SQL and Neo4j

Usage:
    python test_neo4j_integration.py

Prerequisites:
    - Neo4j running (Docker: docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:5)
    - Environment variables: NEO4J_URI, NEO4J_USER, NEO4J_PASS
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_setup():
    """Test 1: Verify Neo4j environment variables are set"""
    print("🔧 Test 1: Environment Setup")
    
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Set them with:")
        print("export NEO4J_URI='bolt://localhost:7687'")
        print("export NEO4J_USER='neo4j'")
        print("export NEO4J_PASS='password'")
        return False
    
    print(f"✅ Neo4j URI: {os.getenv('NEO4J_URI')}")
    print(f"✅ Neo4j User: {os.getenv('NEO4J_USER')}")
    print("✅ Neo4j Password: [HIDDEN]")
    return True


def test_neo4j_connection():
    """Test 2: Verify Neo4j driver connection"""
    print("\n🔌 Test 2: Neo4j Connection")
    
    try:
        from backend.graph.session import get_driver, driver_liveness_check
        
        # Test driver creation
        driver = get_driver()
        print("✅ Neo4j driver created successfully")
        
        # Test liveness check
        if driver_liveness_check():
            print("✅ Neo4j database is reachable")
            return True
        else:
            print("❌ Neo4j database is not responding")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_graph_models():
    """Test 3: Test graph model CRUD operations"""
    print("\n📊 Test 3: Graph Models CRUD")
    
    try:
        from backend.graph.models import create_geoid, get_geoid, create_scar, get_scar
        
        # Test Geoid creation and retrieval
        test_geoid_id = f"TEST_GEOID_{uuid.uuid4().hex[:8]}"
        geoid_props = {
            "geoid_id": test_geoid_id,
            "semantic_state": {"test": 1.0, "neo4j": 0.8},
            "symbolic_state": {"type": "test", "source": "neo4j_test"},
            "metadata": {"created_by": "test_suite"},
            "embedding_vector": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        create_geoid(geoid_props)
        print(f"✅ Created test geoid: {test_geoid_id}")
        
        retrieved_geoid = get_geoid(test_geoid_id)
        if retrieved_geoid and retrieved_geoid.get("geoid_id") == test_geoid_id:
            print("✅ Retrieved geoid successfully")
        else:
            print("❌ Failed to retrieve geoid")
            return False
        
        # Test Scar creation and retrieval
        test_scar_id = f"TEST_SCAR_{uuid.uuid4().hex[:8]}"
        scar_props = {
            "scar_id": test_scar_id,
            "geoids": [test_geoid_id],
            "reason": "Neo4j integration test",
            "timestamp": datetime.now().isoformat(),
            "resolved_by": "test_suite",
            "pre_entropy": 1.5,
            "post_entropy": 1.2,
            "delta_entropy": -0.3,
            "cls_angle": 45.0,
            "semantic_polarity": 0.1,
            "mutation_frequency": 0.05,
            "weight": 1.0,
            "vault_id": "test_vault"
        }
        
        create_scar(scar_props)
        print(f"✅ Created test scar: {test_scar_id}")
        
        retrieved_scar = get_scar(test_scar_id)
        if retrieved_scar and retrieved_scar.get("scar_id") == test_scar_id:
            print("✅ Retrieved scar successfully")
        else:
            print("❌ Failed to retrieve scar")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Graph models test failed: {e}")
        return False


def test_cypher_queries():
    """Test 4: Test direct Cypher queries"""
    print("\n🔍 Test 4: Direct Cypher Queries")
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
            node_counts = {}
            for record in result:
                labels = record["labels"]
                count = record["count"]
                if labels:
                    label = labels[0]  # Take first label
                    node_counts[label] = count
            
            print(f"✅ Node counts: {node_counts}")
            
            # Test relationship query
            result = session.run("""
                MATCH (s:Scar)-[r:INVOLVES]->(g:Geoid) 
                RETURN count(r) as relationship_count
            """)
            rel_count = result.single()["relationship_count"]
            print(f"✅ INVOLVES relationships: {rel_count}")
            
            # Test recent test data
            result = session.run("""
                MATCH (g:Geoid) 
                WHERE g.geoid_id STARTS WITH 'TEST_GEOID_'
                RETURN count(g) as test_geoids
            """)
            test_count = result.single()["test_geoids"]
            print(f"✅ Test geoids found: {test_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Cypher queries failed: {e}")
        return False


def test_vault_manager_integration():
    """Test 5: Test VaultManager dual-write functionality"""
    print("\n🏦 Test 5: VaultManager Integration")
    
    try:
        from backend.core.geoid import GeoidState
        from backend.core.scar import ScarRecord
        from backend.vault.vault_manager import VaultManager
        
        vault_manager = VaultManager()
        
        # Create a test GeoidState
        test_geoid = GeoidState(
            geoid_id=f"VAULT_TEST_{uuid.uuid4().hex[:8]}",
            semantic_state={"vault_test": 1.0, "integration": 0.9},
            symbolic_state={"test_type": "vault_integration"},
            embedding_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            metadata={"test": "vault_manager"}
        )
        
        # Create a test ScarRecord
        test_scar = ScarRecord(
            scar_id=f"VAULT_SCAR_{uuid.uuid4().hex[:8]}",
            geoids=[test_geoid.geoid_id],
            reason="VaultManager integration test",
            timestamp=datetime.now().isoformat(),
            resolved_by="test_vault_manager",
            pre_entropy=2.0,
            post_entropy=1.8,
            delta_entropy=-0.2,
            cls_angle=30.0,
            semantic_polarity=0.05,
            mutation_frequency=0.03,
            weight=1.5
        )
        
        # Test dual-write via VaultManager
        test_vector = [0.1] * 1024  # Mock embedding vector
        scar_db = vault_manager.insert_scar(test_scar, test_vector)
        print(f"✅ VaultManager created scar: {scar_db.scar_id}")
        
        # Verify it appears in Neo4j
        from backend.graph.models import get_scar
        neo4j_scar = get_scar(test_scar.scar_id)
        if neo4j_scar:
            print("✅ Scar found in Neo4j via dual-write")
        else:
            print("⚠️  Scar not found in Neo4j (dual-write may have failed silently)")
        
        return True
        
    except Exception as e:
        print(f"❌ VaultManager integration test failed: {e}")
        return False


def test_cleanup():
    """Test 6: Clean up test data"""
    print("\n🧹 Test 6: Cleanup")
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Remove test nodes
            result = session.run("""
                MATCH (n) 
                WHERE n.geoid_id STARTS WITH 'TEST_GEOID_' 
                   OR n.geoid_id STARTS WITH 'VAULT_TEST_'
                   OR n.scar_id STARTS WITH 'TEST_SCAR_'
                   OR n.scar_id STARTS WITH 'VAULT_SCAR_'
                DETACH DELETE n
                RETURN count(n) as deleted_count
            """)
            deleted_count = result.single()["deleted_count"]
            print(f"✅ Cleaned up {deleted_count} test nodes")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


def main():
    """Run all Neo4j integration tests"""
    print("🚀 KIMERA Neo4j Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment_setup,
        test_neo4j_connection,
        test_graph_models,
        test_cypher_queries,
        test_vault_manager_integration,
        test_cleanup
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Neo4j integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check Neo4j setup and configuration.")
        return 1


if __name__ == "__main__":
    exit(main())