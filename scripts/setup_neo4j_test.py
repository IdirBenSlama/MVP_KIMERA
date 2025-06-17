#!/usr/bin/env python3
"""
Neo4j Test Setup Helper

This script helps set up Neo4j for testing the integration.
It provides Docker commands and environment setup.
"""

import os
import subprocess
import time

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False

def start_neo4j_container():
    """Start Neo4j container for testing"""
    container_name = "kimera-neo4j-test"
    
    # Check if container already exists
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        if container_name in result.stdout:
            print(f"📦 Container {container_name} already exists")
            # Start if stopped
            subprocess.run(['docker', 'start', container_name], capture_output=True)
            print(f"🚀 Started existing container {container_name}")
        else:
            # Create new container
            cmd = [
                'docker', 'run', '-d',
                '--name', container_name,
                '-p', '7687:7687',
                '-p', '7474:7474',
                '-e', 'NEO4J_AUTH=neo4j/testpassword',
                '-e', 'NEO4J_PLUGINS=["apoc"]',
                'neo4j:5'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Created and started Neo4j container: {container_name}")
            else:
                print(f"❌ Failed to start container: {result.stderr}")
                return False
        
        # Wait for Neo4j to be ready
        print("⏳ Waiting for Neo4j to be ready...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ Error managing Docker container: {e}")
        return False

def set_environment_variables():
    """Set environment variables for Neo4j connection"""
    env_vars = {
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASS': 'testpassword'
    }
    
    print("\n🔧 Setting environment variables:")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    # Also create a .env file for persistence
    with open('.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Environment variables set and saved to .env file")

def test_connection():
    """Test Neo4j connection"""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from backend.graph.session import driver_liveness_check
        
        if driver_liveness_check():
            print("✅ Neo4j connection test successful")
            return True
        else:
            print("❌ Neo4j connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

def show_neo4j_info():
    """Show Neo4j access information"""
    print("\n���� Neo4j Access Information:")
    print("   Web Interface: http://localhost:7474")
    print("   Bolt URI: bolt://localhost:7687")
    print("   Username: neo4j")
    print("   Password: testpassword")
    print("\n🔍 Useful Cypher queries to run in Neo4j Browser:")
    print("   MATCH (n) RETURN n LIMIT 25;")
    print("   MATCH (g:Geoid) RETURN g LIMIT 10;")
    print("   MATCH (s:Scar)-[:INVOLVES]->(g:Geoid) RETURN s, g LIMIT 5;")

def main():
    print("🚀 KIMERA Neo4j Test Setup")
    print("=" * 40)
    
    # Check Docker
    if not check_docker():
        print("\n❌ Docker is required for this setup. Please install Docker first.")
        return 1
    
    # Start Neo4j container
    if not start_neo4j_container():
        print("\n❌ Failed to start Neo4j container")
        return 1
    
    # Set environment variables
    set_environment_variables()
    
    # Test connection
    print("\n🔌 Testing Neo4j connection...")
    if test_connection():
        print("\n🎉 Neo4j setup complete!")
        show_neo4j_info()
        
        print("\n▶️  Next steps:")
        print("   1. Run: python test_neo4j_integration.py")
        print("   2. Or start KIMERA with Neo4j integration enabled")
        
        return 0
    else:
        print("\n⚠️  Setup completed but connection test failed.")
        print("   Neo4j might still be starting up. Wait a moment and try:")
        print("   python test_neo4j_integration.py")
        return 1

if __name__ == "__main__":
    exit(main())