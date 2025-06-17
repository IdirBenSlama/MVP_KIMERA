#!/bin/bash

echo "🚀 KIMERA Neo4j Integration Test"
echo "================================"

# Set environment variables for Neo4j
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASS="testpassword"

echo "🔧 Environment variables set:"
echo "   NEO4J_URI=$NEO4J_URI"
echo "   NEO4J_USER=$NEO4J_USER"
echo "   NEO4J_PASS=[HIDDEN]"

echo ""
echo "📦 Starting Neo4j Docker container..."
docker run -d --name kimera-neo4j-test -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/testpassword neo4j:5

if [ $? -ne 0 ]; then
    echo "⚠️  Container might already exist, trying to start existing one..."
    docker start kimera-neo4j-test
fi

echo ""
echo "⏳ Waiting for Neo4j to be ready..."
sleep 15

echo ""
echo "🧪 Running Neo4j integration tests..."
python test_neo4j_integration.py

echo ""
echo "📋 Neo4j Browser: http://localhost:7474"
echo "   Username: neo4j"
echo "   Password: testpassword"
echo ""
echo "🔍 Try these queries in Neo4j Browser:"
echo "   MATCH (n) RETURN n LIMIT 25;"
echo "   MATCH (g:Geoid) RETURN g LIMIT 10;"
echo "   MATCH (s:Scar)-[:INVOLVES]->(g:Geoid) RETURN s, g LIMIT 5;"