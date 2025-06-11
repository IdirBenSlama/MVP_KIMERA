# KIMERA SWM Quick Testing Guide

## 🎯 Best Ways to Test KIMERA SWM

### 1. 🚀 **Automated Demo Script (Recommended)**
```bash
python test_kimera_demo.py
```
This runs a comprehensive test that:
- Creates contradictory semantic geoids
- Processes contradictions to generate scars
- Tests the cognitive cycle
- Demonstrates semantic search

### 2. 🌐 **Interactive API Documentation**
Visit: http://localhost:8002/docs

This provides a web interface where you can:
- Try all endpoints interactively
- See request/response schemas
- Test with custom data

### 3. 📱 **Manual API Testing with curl**

#### Check System Status
```bash
curl http://localhost:8002/system/status
```

#### Create a Semantic Geoid
```bash
curl -X POST http://localhost:8002/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_features": {
      "temperature": 0.9,
      "liquid": 0.8,
      "beverage": 0.9
    },
    "symbolic_content": {"type": "hot_coffee"},
    "metadata": {"test": true}
  }'
```

#### Search for Similar Concepts
```bash
curl "http://localhost:8002/geoids/search?query=hot%20beverage&limit=3"
```

### 4. 🧪 **Testing Scenarios**

#### Scenario A: Contradictory Concepts
1. Create "Hot Coffee" geoid (high temperature)
2. Create "Ice Cream" geoid (low temperature)
3. Process contradictions between them
4. Observe scar generation

#### Scenario B: Semantic Clustering
1. Create multiple food-related geoids
2. Use semantic search to find similar concepts
3. Test the clustering behavior

#### Scenario C: Cognitive Cycles
1. Create several geoids
2. Trigger cognitive cycles
3. Monitor entropy changes and system evolution

### 5. 📊 **Key Metrics to Monitor**

- **Active Geoids**: Number of concepts in working memory
- **Scars Created**: Resolved contradictions
- **System Entropy**: Overall system complexity
- **Stability Metrics**: System coherence measures

### 6. 🔍 **Expected Behaviors**

#### ✅ **Success Indicators:**
- Geoids created successfully with unique IDs
- Contradictions detected between opposing concepts
- Scars generated when contradictions are resolved
- Semantic search returns relevant results
- System entropy changes with new concepts

#### ⚠️ **What to Look For:**
- Contradiction detection between semantically opposite concepts
- Scar creation when tensions are resolved
- Semantic clustering of similar concepts
- Stable system metrics over time

### 7. 🎮 **Interactive Testing Steps**

1. **Start Simple**: Create 2-3 basic geoids
2. **Add Contradictions**: Create opposing concepts
3. **Process Tensions**: Trigger contradiction processing
4. **Observe Evolution**: Watch system metrics change
5. **Test Search**: Query for semantic similarities
6. **Run Cycles**: Execute cognitive cycles

### 8. 🐛 **Troubleshooting**

If tests fail:
- Check server is running: `curl http://localhost:8002/system/status`
- Verify port 8002 is accessible
- Check console for error messages
- Review API documentation at `/docs`

### 9. 🎯 **Advanced Testing**

For deeper testing:
- Upload images via `/geoids/from_image`
- Test EchoForm parsing with linguistic structures
- Experiment with vault rebalancing
- Monitor stability metrics over time
