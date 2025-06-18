# Kimera SWM Quick Start Guide

## 🚀 System is Running!

The Kimera SWM system is now fully operational. Here's how to interact with it:

## 📡 API Endpoints

### View Interactive Documentation
Open your browser to: http://localhost:8001/docs

### Basic Operations

#### 1. Create a Semantic Geoid
```bash
curl -X POST http://localhost:8001/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_features": {
      "intelligence": 0.8,
      "creativity": 0.9,
      "emotion": 0.6
    },
    "metadata": {"source": "manual", "type": "concept"}
  }'
```

#### 2. Create an Echoform Geoid
```bash
curl -X POST http://localhost:8001/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "echoform_text": "(define consciousness (emerges complexity awareness))",
    "metadata": {"source": "echoform"}
  }'
```

#### 3. Process Contradictions
```bash
curl -X POST http://localhost:8001/process/contradictions \
  -H "Content-Type: application/json" \
  -d '{
    "trigger_geoid_id": "GEOID_ab3e4925",
    "search_limit": 5
  }'
```

#### 4. Check System Status
```bash
curl http://localhost:8001/system/status | python -m json.tool
```

#### 5. View Monitoring Status
```bash
curl http://localhost:8001/monitoring/status | python -m json.tool
```

#### 6. Run a Cognitive Cycle
```bash
curl -X POST http://localhost:8001/system/cycle
```

#### 7. Get Understanding Metrics
```bash
curl http://localhost:8001/vault/understanding/metrics | python -m json.tool
```

## 🔍 Explore the Data

### Neo4j Graph Database
1. Open: http://localhost:7474
2. Login: neo4j / password
3. Run queries:
   ```cypher
   // See all nodes
   MATCH (n) RETURN n LIMIT 50
   
   // See SCARs and their relationships
   MATCH (s:Scar)-[r:INVOLVES]->(g:Geoid) 
   RETURN s, r, g LIMIT 50
   
   // Find geoids with most SCARs
   MATCH (g:Geoid)<-[:INVOLVES]-(s:Scar)
   RETURN g.geoid_id, COUNT(s) as scar_count
   ORDER BY scar_count DESC
   ```

### View Vault Contents
```bash
# View SCARs in Vault A
curl http://localhost:8001/vaults/vault_a?limit=10 | python -m json.tool

# View SCARs in Vault B
curl http://localhost:8001/vaults/vault_b?limit=10 | python -m json.tool
```

## 🧪 Experiments to Try

### 1. Create Conflicting Concepts
```bash
# Create "order" concept
curl -X POST http://localhost:8001/geoids \
  -d '{"semantic_features": {"structure": 0.9, "predictability": 0.8, "stability": 0.9}}'

# Create "chaos" concept  
curl -X POST http://localhost:8001/geoids \
  -d '{"semantic_features": {"randomness": 0.9, "unpredictability": 0.8, "change": 0.9}}'

# Process contradictions between them
# (use the returned geoid IDs)
```

### 2. Test Semantic Search
```bash
curl "http://localhost:8001/geoids/search?query=consciousness&limit=5"
```

### 3. Monitor Entropy Changes
```bash
# Get entropy trends
curl http://localhost:8001/monitoring/entropy/trends?window_size=50

# Detect anomalies
curl http://localhost:8001/monitoring/entropy/anomalies
```

### 4. Run Proactive Scan
```bash
curl -X POST http://localhost:8001/system/proactive_scan
```

## 📊 System Monitoring

### Real-time Metrics
- Active Geoids: Check `/system/status`
- SCAR Distribution: Check vault counts
- Entropy Levels: Monitor system entropy
- Processing Rate: Watch contradiction detection

### Performance Testing
```bash
# Run multiple cycles
for i in {1..5}; do
  curl -X POST http://localhost:8001/system/cycle
  sleep 2
done
```

## 🛠️ Troubleshooting

### If API is not responding:
1. Check if server is running: `ps aux | grep python`
2. Check logs in the terminal where server is running
3. Restart server: `python run_kimera.py`

### If Neo4j is not connecting:
1. Check Docker: `docker ps | grep neo4j`
2. Restart Neo4j: `docker restart kimera-neo4j`
3. Check logs: `docker logs kimera-neo4j`

### If getting errors:
1. Check system health: `curl http://localhost:8001/system/health`
2. Review specific endpoint docs at http://localhost:8001/docs
3. Check environment variables are loaded

## 🎯 What's Next?

1. **Explore the codebase** - Understanding the architecture
2. **Run more experiments** - Test different semantic combinations
3. **Monitor system behavior** - Watch how entropy evolves
4. **Implement new features** - Follow the development roadmap
5. **Contribute improvements** - Enhance existing functionality

The system is ready for exploration and development. Happy experimenting with Kimera SWM!

---
*For detailed development instructions, see `DEVELOPMENT_ROADMAP.md`*