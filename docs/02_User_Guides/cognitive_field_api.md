# Cognitive Field Dynamics API Reference

## Overview

The Cognitive Field Dynamics API provides endpoints for interacting with the semantic field system. All endpoints are prefixed with `/cognitive-fields/`.

## Base URL
```
http://localhost:8000/cognitive-fields/
```

## Endpoints

### 1. Add Geoid to Field

**POST** `/geoid/add`

Adds a new geoid to the semantic field, creating a field source in semantic space.

#### Request Body
```json
{
    "geoid_id": "string",
    "embedding": [float, float, ...]
}
```

#### Response
```json
{
    "geoid_id": "example_geoid",
    "status": "added",
    "resonance_frequency": 12.34,
    "phase": -1.57
}
```

#### Example
```bash
curl -X POST "http://localhost:8000/cognitive-fields/geoid/add" \
     -H "Content-Type: application/json" \
     -d '{
         "geoid_id": "concept_apple",
         "embedding": [0.1, 0.2, 0.3, ...]
     }'
```

### 2. Add Geoids from Database

**POST** `/geoid/add_from_db?limit={int}`

Loads geoids from the database and adds them to the semantic field.

#### Parameters
- `limit` (query): Maximum number of geoids to load (default: 100)

#### Response
```json
{
    "status": "Added 85 geoids from DB to semantic field."
}
```

#### Example
```bash
curl -X POST "http://localhost:8000/cognitive-fields/geoid/add_from_db?limit=50"
```

### 3. Find Semantic Neighbors

**POST** `/neighbors/find`

Finds semantic neighbors through dynamic field interactions (replaces traditional kNN).

#### Request Body
```json
{
    "geoid_id": "string",
    "energy_threshold": 0.1
}
```

#### Response
```json
{
    "geoid_id": "concept_apple",
    "neighbors": [
        {
            "geoid_id": "concept_fruit",
            "interaction_strength": 0.85,
            "classification": "strong_resonance"
        },
        {
            "geoid_id": "concept_red",
            "interaction_strength": 0.62,
            "classification": "moderate_coupling"
        }
    ],
    "neighbor_count": 2
}
```

#### Classification Types
- `strong_resonance` (>0.8)
- `moderate_coupling` (0.5-0.8)
- `weak_interaction` (0.2-0.5)
- `minimal_presence` (<0.2)

#### Example
```bash
curl -X POST "http://localhost:8000/cognitive-fields/neighbors/find" \
     -H "Content-Type: application/json" \
     -d '{
         "geoid_id": "concept_apple",
         "energy_threshold": 0.1
     }'
```

### 4. Get Influence Field

**GET** `/influence/{geoid_id}`

Finds the influence field of a geoid (continuous alternative to RkNN).

#### Parameters
- `geoid_id` (path): The ID of the geoid to analyze

#### Response
```json
{
    "geoid_id": "concept_apple",
    "influence_map": {
        "concept_fruit": 0.45,
        "concept_tree": 0.32,
        "concept_red": 0.28
    },
    "total_influence": 1.05,
    "average_influence": 0.35
}
```

#### Example
```bash
curl "http://localhost:8000/cognitive-fields/influence/concept_apple"
```

### 5. Detect Semantic Anomalies

**GET** `/anomalies/detect`

Detects semantic anomalies through field analysis.

#### Response
```json
{
    "anomalies": [
        {
            "geoid_id": "anomalous_concept",
            "type": "high_field_strength",
            "value": 2.5,
            "threshold": 2.0
        }
    ],
    "total_fields": 150,
    "field_health": 0.993
}
```

#### Anomaly Types
- `high_field_strength`: Field strength exceeds normal range
- `high_resonance_frequency`: Frequency outside expected bounds

#### Example
```bash
curl "http://localhost:8000/cognitive-fields/anomalies/detect"
```

### 6. Find Resonance Clusters

**GET** `/clusters/resonance`

Finds semantic clusters through resonance patterns.

#### Response
```json
{
    "clusters": [
        {
            "cluster_id": 0,
            "geoid_ids": ["concept_apple", "concept_orange", "concept_fruit"],
            "size": 3,
            "resonance_signature": {
                "avg_frequency": 12.5,
                "frequency_variance": 0.8,
                "phase_coherence": 0.92
            }
        }
    ],
    "total_clusters": 5,
    "clustering_method": "resonance_pattern"
}
```

#### Example
```bash
curl "http://localhost:8000/cognitive-fields/clusters/resonance"
```

### 7. Get Semantic Field Map

**GET** `/field-map`

Gets a comprehensive map of the entire semantic field space.

#### Response
```json
{
    "fields": {
        "concept_apple": {
            "resonance_frequency": 12.34,
            "phase": -1.57,
            "field_strength": 1.0
        }
    },
    "interactions": [
        {
            "source": "concept_apple",
            "target": "concept_fruit",
            "strength": 0.85
        }
    ],
    "topology": {
        "critical_points": 0,
        "vortices": 0
    }
}
```

#### Example
```bash
curl "http://localhost:8000/cognitive-fields/field-map"
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "detail": "Geoid 'non_existent' not found in semantic field"
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Internal processing error"
}
```

## Field Evolution

The semantic field continuously evolves through wave propagation. Field strengths, relationships, and clusters change over time as waves interact with fields.

### Key Concepts

1. **Wave Propagation**: Semantic waves expand at finite speed through the field
2. **Resonance**: Fields amplify when waves match their resonance frequency
3. **Temporal Dynamics**: Relationships evolve over time, not instantly
4. **Emergence**: Complex patterns arise from simple wave interactions

## Usage Patterns

### 1. Semantic Search
```python
# Add concepts to field
add_geoid("query_concept", query_embedding)

# Find semantic neighbors
neighbors = find_neighbors("query_concept", threshold=0.2)
```

### 2. Concept Analysis
```python
# Get influence field
influence = get_influence_field("target_concept")

# Detect anomalies
anomalies = detect_anomalies()
```

### 3. Knowledge Discovery
```python
# Find natural clusters
clusters = find_resonance_clusters()

# Get field overview
field_map = get_field_map()
```

## Performance Considerations

- **Field Size**: Performance scales with number of active fields
- **Wave Density**: More waves increase computation time
- **Threshold Tuning**: Adjust energy thresholds for performance vs. accuracy
- **Batch Operations**: Use database loading for bulk field creation

## Integration Examples

### Python Client
```python
import requests

class CognitiveFieldClient:
    def __init__(self, base_url="http://localhost:8000/cognitive-fields"):
        self.base_url = base_url
    
    def add_geoid(self, geoid_id, embedding):
        response = requests.post(
            f"{self.base_url}/geoid/add",
            json={"geoid_id": geoid_id, "embedding": embedding}
        )
        return response.json()
    
    def find_neighbors(self, geoid_id, threshold=0.1):
        response = requests.post(
            f"{self.base_url}/neighbors/find",
            json={"geoid_id": geoid_id, "energy_threshold": threshold}
        )
        return response.json()
```

### JavaScript Client
```javascript
class CognitiveFieldClient {
    constructor(baseUrl = "http://localhost:8000/cognitive-fields") {
        this.baseUrl = baseUrl;
    }
    
    async addGeoid(geoidId, embedding) {
        const response = await fetch(`${this.baseUrl}/geoid/add`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({geoid_id: geoidId, embedding: embedding})
        });
        return response.json();
    }
    
    async findNeighbors(geoidId, threshold = 0.1) {
        const response = await fetch(`${this.baseUrl}/neighbors/find`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({geoid_id: geoidId, energy_threshold: threshold})
        });
        return response.json();
    }
}
```

## Configuration

Field behavior can be tuned through the configuration file `backend/core/cognitive_field_config.py`:

```python
# Wave propagation speed
PROPAGATION_SPEED = 1.0

# Wave collision detection tolerance  
WAVE_THICKNESS = 0.1

# Field interaction thresholds
INTERACTION_STRENGTH_THRESHOLD = 0.1
RESONANCE_EFFECT_STRENGTH = 0.1
```

## Monitoring and Debugging

### Field Statistics
- Monitor field count and wave density
- Track resonance frequency distributions
- Observe clustering patterns over time

### Performance Metrics
- API response times
- Field evolution step duration
- Memory usage patterns

### Debug Endpoints
- Field map provides system overview
- Anomaly detection identifies issues
- Cluster analysis shows emergent patterns 