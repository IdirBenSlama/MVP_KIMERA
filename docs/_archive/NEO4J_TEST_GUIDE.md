# Neo4j Integration Test Guide

This guide helps you test the new Neo4j integration in KIMERA SWM.

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
test_neo4j.bat
```

**Linux/Mac:**
```bash
chmod +x test_neo4j.sh
./test_neo4j.sh
```

### Option 2: Manual Setup

1. **Start Neo4j with Docker:**
   ```bash
   docker run -d --name kimera-neo4j-test \
     -p 7687:7687 -p 7474:7474 \
     -e NEO4J_AUTH=neo4j/testpassword \
     neo4j:5
   ```

2. **Set Environment Variables:**
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASS="testpassword"
   ```

3. **Run Tests:**
   ```bash
   python test_neo4j_integration.py
   ```

## What Gets Tested

The test suite verifies:

### 1. Environment Setup ✅
- Neo4j environment variables are configured
- Required packages are available

### 2. Neo4j Connection ✅
- Driver can connect to Neo4j database
- Liveness check passes

### 3. Graph Models CRUD ✅
- `create_geoid()` and `get_geoid()` work
- `create_scar()` and `get_scar()` work
- Relationships are created correctly

### 4. Cypher Queries ✅
- Direct Cypher execution works
- Node and relationship counts are accurate
- Test data is properly stored

### 5. VaultManager Integration ✅
- Dual-write functionality works
- SQL data is mirrored to Neo4j
- No disruption to existing functionality

### 6. Cleanup ✅
- Test data is removed after testing

## Expected Output

```
🚀 KIMERA Neo4j Integration Test Suite
==================================================
🔧 Test 1: Environment Setup
✅ Neo4j URI: bolt://localhost:7687
✅ Neo4j User: neo4j
✅ Neo4j Password: [HIDDEN]

🔌 Test 2: Neo4j Connection
✅ Neo4j driver created successfully
✅ Neo4j database is reachable

📊 Test 3: Graph Models CRUD
✅ Created test geoid: TEST_GEOID_12345678
✅ Retrieved geoid successfully
✅ Created test scar: TEST_SCAR_87654321
✅ Retrieved scar successfully

🔍 Test 4: Direct Cypher Queries
✅ Node counts: {'Geoid': 1, 'Scar': 1}
✅ INVOLVES relationships: 1
✅ Test geoids found: 1

🏦 Test 5: VaultManager Integration
✅ VaultManager created scar: VAULT_SCAR_ABCDEF12
✅ Scar found in Neo4j via dual-write

🧹 Test 6: Cleanup
✅ Cleaned up 4 test nodes

==================================================
📊 Test Results: 6 passed, 0 failed
🎉 All tests passed! Neo4j integration is working correctly.
```

## Troubleshooting

### Neo4j Not Starting
```
❌ Neo4j database is not responding
```
**Solution:** Wait longer for Neo4j to start, or check Docker logs:
```bash
docker logs kimera-neo4j-test
```

### Connection Refused
```
❌ Connection error: Failed to establish connection
```
**Solutions:**
- Ensure Neo4j container is running: `docker ps`
- Check port 7687 is not blocked
- Verify environment variables are set

### Import Errors
```
❌ Import error: No module named 'backend.graph'
```
**Solution:** Run from the project root directory where `backend/` exists.

### Permission Denied (Linux/Mac)
```bash
chmod +x test_neo4j.sh
```

## Exploring the Data

After running tests, open Neo4j Browser at http://localhost:7474

**Login:**
- Username: `neo4j`
- Password: `testpassword`

**Useful Queries:**
```cypher
// See all nodes
MATCH (n) RETURN n LIMIT 25;

// See all Geoids
MATCH (g:Geoid) RETURN g LIMIT 10;

// See Scar-Geoid relationships
MATCH (s:Scar)-[:INVOLVES]->(g:Geoid) 
RETURN s, g LIMIT 5;

// Count nodes by type
MATCH (n) 
RETURN labels(n) as type, count(n) as count;

// See node properties
MATCH (g:Geoid) 
RETURN g.geoid_id, keys(g) LIMIT 5;
```

## Integration Status

✅ **Completed:**
- Neo4j driver and session management
- Basic CRUD operations for Geoids and Scars
- Dual-write from VaultManager
- Health check integration
- Comprehensive test suite

🚧 **Next Steps:**
- Migrate read operations to Neo4j
- Add support for enhanced understanding tables
- Implement graph-specific queries (causal chains, etc.)
- Performance optimization

## Files Created

- `backend/graph/__init__.py` - Package initialization
- `backend/graph/session.py` - Neo4j driver factory
- `backend/graph/models.py` - CRUD helper functions
- `test_neo4j_integration.py` - Comprehensive test suite
- `setup_neo4j_test.py` - Automated setup helper
- `test_neo4j.bat` - Windows test script
- `test_neo4j.sh` - Unix/Linux test script
- `NEO4J_TEST_GUIDE.md` - This guide

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Database username |
| `NEO4J_PASS` | `neo4j` | Database password |
| `NEO4J_ENCRYPTED` | `1` | Enable/disable encryption |
| `NEO4J_POOL_SIZE` | `20` | Connection pool size |

## Docker Commands

```bash
# Start Neo4j
docker run -d --name kimera-neo4j-test -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/testpassword neo4j:5

# Stop Neo4j
docker stop kimera-neo4j-test

# Remove container
docker rm kimera-neo4j-test

# View logs
docker logs kimera-neo4j-test

# Access Neo4j shell
docker exec -it kimera-neo4j-test cypher-shell -u neo4j -p testpassword
```