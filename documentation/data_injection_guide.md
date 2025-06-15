# KIMERA SWM Data Injection Guide

This guide provides multiple methods for manually injecting data into the KIMERA SWM system, including direct database manipulation, API endpoints, and programmatic approaches.

## 🗄️ Database Structure

The KIMERA SWM system uses SQLite by default (`kimera_swm.db`) with three main tables:

### Tables Overview
- **geoids**: Semantic entities with vector embeddings
- **scars**: Contradiction resolution records
- **insights**: Generated insights and hypotheses

### Database Schema

```sql
-- Geoids Table
CREATE TABLE geoids (
    geoid_id VARCHAR PRIMARY KEY,
    symbolic_state JSON,
    metadata_json JSON,
    semantic_state_json JSON,
    semantic_vector JSON  -- Vector embeddings as JSON array
);

-- Scars Table  
CREATE TABLE scars (
    scar_id VARCHAR PRIMARY KEY,
    geoids JSON,              -- Array of geoid IDs involved
    reason VARCHAR,           -- Description of contradiction
    timestamp DATETIME,
    resolved_by VARCHAR,
    pre_entropy FLOAT,
    post_entropy FLOAT,
    delta_entropy FLOAT,
    cls_angle FLOAT,
    semantic_polarity FLOAT,
    mutation_frequency FLOAT,
    weight FLOAT DEFAULT 1.0,
    last_accessed DATETIME,
    scar_vector JSON,         -- Vector embedding as JSON array
    vault_id VARCHAR          -- 'vault_a' or 'vault_b'
);

-- Insights Table
CREATE TABLE insights (
    insight_id VARCHAR PRIMARY KEY,
    insight_type VARCHAR,     -- 'ANALOGY', 'HYPOTHESIS', 'FRAMEWORK', 'SOLUTION'
    source_resonance_id VARCHAR,
    echoform_repr JSON,
    application_domains JSON,
    confidence FLOAT,
    entropy_reduction FLOAT,
    utility_score FLOAT DEFAULT 0.0,
    status VARCHAR DEFAULT 'provisional',
    created_at DATETIME,
    last_reinforced_cycle VARCHAR
);
```

## 🔌 Method 1: API Endpoints (Recommended)

### Starting the API Server
```bash
python run_kimera.py
# Server runs on http://localhost:8001
```

### 1. Create Geoids via API

```bash
# Create a semantic geoid
curl -X POST http://localhost:8001/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_features": {
      "concept": 0.8,
      "intensity": 0.6,
      "polarity": 0.3,
      "complexity": 0.7
    },
    "symbolic_content": {
      "type": "concept",
      "category": "abstract",
      "description": "A test concept for injection"
    },
    "metadata": {
      "source": "manual_injection",
      "created_by": "user",
      "tags": ["test", "manual"]
    },
    "echoform_text": "concept[intensity:high, polarity:positive]"
  }'
```

### 2. Create Geoids from Images

```bash
# Upload an image to create a visual geoid
curl -X POST http://localhost:8001/geoids/from_image \
  -F "file=@/path/to/your/image.jpg"
```

### 3. Process Contradictions

```bash
# Trigger contradiction processing for a geoid
curl -X POST http://localhost:8001/process/contradictions \
  -H "Content-Type: application/json" \
  -d '{
    "trigger_geoid_id": "GEOID_12345678",
    "search_limit": 10,
    "force_collapse": false
  }'
```

### 4. Search and Query Data

```bash
# Search for similar geoids
curl "http://localhost:8001/geoids/search?query=abstract%20concept&limit=5"

# Search for similar scars
curl "http://localhost:8001/scars/search?query=contradiction%20between%20concepts&limit=3"

# Get system status
curl http://localhost:8001/system/status

# Get vault contents
curl http://localhost:8001/vaults/vault_a?limit=10
```

## 🐍 Method 2: Python Scripts

### Direct Database Injection Script

```python
# create_manual_data.py
import sqlite3
import json
import uuid
from datetime import datetime
import numpy as np

def inject_sample_geoids():
    """Inject sample geoids directly into database"""
    conn = sqlite3.connect('kimera_swm.db')
    cursor = conn.cursor()
    
    sample_geoids = [
        {
            'geoid_id': f'GEOID_{uuid.uuid4().hex[:8]}',
            'symbolic_state': json.dumps({
                'type': 'concept',
                'name': 'artificial_intelligence',
                'category': 'technology'
            }),
            'metadata_json': json.dumps({
                'source': 'manual_injection',
                'domain': 'computer_science',
                'complexity': 'high'
            }),
            'semantic_state_json': json.dumps({
                'intelligence': 0.9,
                'artificial': 0.8,
                'learning': 0.7,
                'automation': 0.6
            }),
            'semantic_vector': json.dumps(np.random.rand(384).tolist())  # 384-dim vector
        },
        {
            'geoid_id': f'GEOID_{uuid.uuid4().hex[:8]}',
            'symbolic_state': json.dumps({
                'type': 'concept',
                'name': 'human_creativity',
                'category': 'cognition'
            }),
            'metadata_json': json.dumps({
                'source': 'manual_injection',
                'domain': 'psychology',
                'complexity': 'high'
            }),
            'semantic_state_json': json.dumps({
                'creativity': 0.9,
                'human': 0.8,
                'intuition': 0.7,
                'originality': 0.8
            }),
            'semantic_vector': json.dumps(np.random.rand(384).tolist())
        }
    ]
    
    for geoid in sample_geoids:
        cursor.execute('''
            INSERT INTO geoids (geoid_id, symbolic_state, metadata_json, 
                              semantic_state_json, semantic_vector)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            geoid['geoid_id'],
            geoid['symbolic_state'],
            geoid['metadata_json'],
            geoid['semantic_state_json'],
            geoid['semantic_vector']
        ))
        print(f"Inserted geoid: {geoid['geoid_id']}")
    
    conn.commit()
    conn.close()

def inject_sample_scars():
    """Inject sample scars directly into database"""
    conn = sqlite3.connect('kimera_swm.db')
    cursor = conn.cursor()
    
    # Get some geoid IDs first
    cursor.execute('SELECT geoid_id FROM geoids LIMIT 2')
    geoid_ids = [row[0] for row in cursor.fetchall()]
    
    if len(geoid_ids) < 2:
        print("Need at least 2 geoids to create scars")
        return
    
    sample_scar = {
        'scar_id': f'SCAR_{uuid.uuid4().hex[:8]}',
        'geoids': json.dumps(geoid_ids[:2]),
        'reason': 'Manual contradiction injection between AI and human creativity',
        'timestamp': datetime.utcnow(),
        'resolved_by': 'ManualInjection',
        'pre_entropy': 2.5,
        'post_entropy': 2.8,
        'delta_entropy': 0.3,
        'cls_angle': 45.0,
        'semantic_polarity': 0.2,
        'mutation_frequency': 0.1,
        'weight': 1.0,
        'last_accessed': datetime.utcnow(),
        'scar_vector': json.dumps(np.random.rand(384).tolist()),
        'vault_id': 'vault_a'
    }
    
    cursor.execute('''
        INSERT INTO scars (scar_id, geoids, reason, timestamp, resolved_by,
                          pre_entropy, post_entropy, delta_entropy, cls_angle,
                          semantic_polarity, mutation_frequency, weight,
                          last_accessed, scar_vector, vault_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sample_scar['scar_id'],
        sample_scar['geoids'],
        sample_scar['reason'],
        sample_scar['timestamp'],
        sample_scar['resolved_by'],
        sample_scar['pre_entropy'],
        sample_scar['post_entropy'],
        sample_scar['delta_entropy'],
        sample_scar['cls_angle'],
        sample_scar['semantic_polarity'],
        sample_scar['mutation_frequency'],
        sample_scar['weight'],
        sample_scar['last_accessed'],
        sample_scar['scar_vector'],
        sample_scar['vault_id']
    ))
    
    print(f"Inserted scar: {sample_scar['scar_id']}")
    conn.commit()
    conn.close()

def inject_sample_insights():
    """Inject sample insights directly into database"""
    conn = sqlite3.connect('kimera_swm.db')
    cursor = conn.cursor()
    
    sample_insight = {
        'insight_id': f'INSIGHT_{uuid.uuid4().hex[:8]}',
        'insight_type': 'HYPOTHESIS',
        'source_resonance_id': 'manual_injection',
        'echoform_repr': json.dumps({
            'hypothesis': 'AI and human creativity are complementary',
            'structure': 'complementarity[ai, human_creativity]'
        }),
        'application_domains': json.dumps(['technology', 'psychology', 'philosophy']),
        'confidence': 0.75,
        'entropy_reduction': 0.3,
        'utility_score': 0.8,
        'status': 'active',
        'created_at': datetime.utcnow(),
        'last_reinforced_cycle': '0'
    }
    
    cursor.execute('''
        INSERT INTO insights (insight_id, insight_type, source_resonance_id,
                            echoform_repr, application_domains, confidence,
                            entropy_reduction, utility_score, status,
                            created_at, last_reinforced_cycle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sample_insight['insight_id'],
        sample_insight['insight_type'],
        sample_insight['source_resonance_id'],
        sample_insight['echoform_repr'],
        sample_insight['application_domains'],
        sample_insight['confidence'],
        sample_insight['entropy_reduction'],
        sample_insight['utility_score'],
        sample_insight['status'],
        sample_insight['created_at'],
        sample_insight['last_reinforced_cycle']
    ))
    
    print(f"Inserted insight: {sample_insight['insight_id']}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Injecting sample data...")
    inject_sample_geoids()
    inject_sample_scars()
    inject_sample_insights()
    print("Data injection complete!")
```

### Using the System's Internal APIs

```python
# system_injection.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.geoid import GeoidState
from backend.core.scar import ScarRecord
from backend.core.insight import InsightScar
from backend.vault.database import SessionLocal, GeoidDB, ScarDB, InsightDB
from backend.core.embedding_utils import encode_text
import uuid
from datetime import datetime
import json

def inject_via_system_apis():
    """Use the system's internal APIs for data injection"""
    
    # Create geoids using system classes
    geoid1 = GeoidState(
        geoid_id=f"GEOID_{uuid.uuid4().hex[:8]}",
        semantic_state={
            "technology": 0.9,
            "innovation": 0.8,
            "complexity": 0.7
        },
        symbolic_state={
            "type": "concept",
            "name": "blockchain_technology",
            "category": "distributed_systems"
        },
        metadata={
            "source": "system_injection",
            "domain": "computer_science"
        }
    )
    
    # Generate embedding
    semantic_text = " ".join([f"{k}:{v:.2f}" for k, v in geoid1.semantic_state.items()])
    vector1 = encode_text(semantic_text)
    
    # Save to database
    with SessionLocal() as db:
        geoid_db = GeoidDB(
            geoid_id=geoid1.geoid_id,
            symbolic_state=geoid1.symbolic_state,
            metadata_json=geoid1.metadata,
            semantic_state_json=geoid1.semantic_state,
            semantic_vector=vector1.tolist()
        )
        db.add(geoid_db)
        db.commit()
        print(f"Created geoid via system API: {geoid1.geoid_id}")
    
    # Create insights using system classes
    insight = InsightScar(
        insight_id=f"INSIGHT_{uuid.uuid4().hex[:8]}",
        insight_type="FRAMEWORK",
        source_resonance_id="system_injection",
        echoform_repr={
            "framework": "distributed_trust_model",
            "components": ["consensus", "cryptography", "decentralization"]
        },
        confidence=0.85,
        entropy_reduction=0.4,
        application_domains=["finance", "supply_chain", "identity"]
    )
    
    # Save insight to database
    with SessionLocal() as db:
        insight_db = InsightDB(
            insight_id=insight.insight_id,
            insight_type=insight.insight_type,
            source_resonance_id=insight.source_resonance_id,
            echoform_repr=insight.echoform_repr,
            application_domains=insight.application_domains,
            confidence=insight.confidence,
            entropy_reduction=insight.entropy_reduction,
            utility_score=insight.utility_score,
            status=insight.status,
            created_at=datetime.fromisoformat(insight.created_at),
            last_reinforced_cycle=str(insight.last_reinforced_cycle)
        )
        db.add(insight_db)
        db.commit()
        print(f"Created insight via system API: {insight.insight_id}")

if __name__ == "__main__":
    inject_via_system_apis()
```

## 🛠️ Method 3: Direct SQL Commands

### Using SQLite Command Line

```bash
# Open the database
sqlite3 kimera_swm.db

# Insert a geoid directly
INSERT INTO geoids (geoid_id, symbolic_state, metadata_json, semantic_state_json, semantic_vector)
VALUES (
    'GEOID_manual001',
    '{"type": "concept", "name": "quantum_computing"}',
    '{"source": "manual_sql", "domain": "physics"}',
    '{"quantum": 0.9, "computing": 0.8, "superposition": 0.7}',
    '[0.1, 0.2, 0.3, 0.4]'  -- Simplified vector for example
);

# Insert a scar directly
INSERT INTO scars (scar_id, geoids, reason, timestamp, resolved_by, pre_entropy, post_entropy, delta_entropy, cls_angle, semantic_polarity, mutation_frequency, weight, last_accessed, scar_vector, vault_id)
VALUES (
    'SCAR_manual001',
    '["GEOID_manual001", "GEOID_12345678"]',
    'Manual contradiction injection',
    datetime('now'),
    'ManualSQL',
    2.0, 2.5, 0.5, 30.0, 0.1, 0.05, 1.0,
    datetime('now'),
    '[0.5, 0.6, 0.7, 0.8]',
    'vault_a'
);

# Query data
SELECT * FROM geoids WHERE geoid_id LIKE 'GEOID_manual%';
SELECT * FROM scars WHERE vault_id = 'vault_a';
```

## 📊 Method 4: Bulk Data Import

### CSV to Database Import Script

```python
# bulk_import.py
import pandas as pd
import sqlite3
import json
import uuid
import numpy as np
from datetime import datetime

def import_geoids_from_csv(csv_file):
    """Import geoids from CSV file"""
    df = pd.read_csv(csv_file)
    conn = sqlite3.connect('kimera_swm.db')
    
    for _, row in df.iterrows():
        geoid_id = f"GEOID_{uuid.uuid4().hex[:8]}"
        
        # Parse semantic features from CSV columns
        semantic_state = {}
        for col in df.columns:
            if col.startswith('semantic_'):
                feature_name = col.replace('semantic_', '')
                semantic_state[feature_name] = float(row[col])
        
        # Create symbolic state
        symbolic_state = {
            'type': row.get('type', 'concept'),
            'name': row.get('name', ''),
            'category': row.get('category', '')
        }
        
        # Create metadata
        metadata = {
            'source': 'csv_import',
            'original_row': int(row.name)
        }
        
        # Generate random vector (in production, use proper embeddings)
        vector = np.random.rand(384).tolist()
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO geoids (geoid_id, symbolic_state, metadata_json, 
                              semantic_state_json, semantic_vector)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            geoid_id,
            json.dumps(symbolic_state),
            json.dumps(metadata),
            json.dumps(semantic_state),
            json.dumps(vector)
        ))
        
        print(f"Imported: {geoid_id} - {row.get('name', 'unnamed')}")
    
    conn.commit()
    conn.close()

# Example CSV format:
# name,type,category,semantic_intelligence,semantic_creativity,semantic_complexity
# artificial_intelligence,concept,technology,0.9,0.6,0.8
# human_intuition,concept,cognition,0.7,0.9,0.6
```

## 🔍 Method 5: Database Inspection and Validation

### Inspection Script

```python
# inspect_data.py
import sqlite3
import json

def inspect_database():
    """Inspect current database contents"""
    conn = sqlite3.connect('kimera_swm.db')
    cursor = conn.cursor()
    
    # Count records
    cursor.execute('SELECT COUNT(*) FROM geoids')
    geoid_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM scars')
    scar_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM insights')
    insight_count = cursor.fetchone()[0]
    
    print(f"Database Contents:")
    print(f"  Geoids: {geoid_count}")
    print(f"  Scars: {scar_count}")
    print(f"  Insights: {insight_count}")
    
    # Show recent geoids
    cursor.execute('SELECT geoid_id, symbolic_state FROM geoids LIMIT 5')
    print(f"\nRecent Geoids:")
    for row in cursor.fetchall():
        symbolic = json.loads(row[1]) if row[1] else {}
        print(f"  {row[0]}: {symbolic.get('name', 'unnamed')}")
    
    # Show vault distribution
    cursor.execute('SELECT vault_id, COUNT(*) FROM scars GROUP BY vault_id')
    print(f"\nVault Distribution:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} scars")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
```

## 🚀 Quick Start Examples

### 1. Simple Concept Injection
```bash
# Start the API server
python run_kimera.py

# In another terminal, inject a concept
curl -X POST http://localhost:8001/geoids \
  -H "Content-Type: application/json" \
  -d '{
    "semantic_features": {"intelligence": 0.9, "artificial": 0.8},
    "symbolic_content": {"type": "concept", "name": "AI"},
    "metadata": {"source": "quick_test"}
  }'
```

### 2. Batch Concept Creation
```python
# batch_create.py
import requests
import json

concepts = [
    {"name": "machine_learning", "intelligence": 0.8, "learning": 0.9},
    {"name": "neural_networks", "intelligence": 0.7, "artificial": 0.8},
    {"name": "deep_learning", "intelligence": 0.9, "complexity": 0.8}
]

for concept in concepts:
    data = {
        "semantic_features": {k: v for k, v in concept.items() if k != "name"},
        "symbolic_content": {"type": "concept", "name": concept["name"]},
        "metadata": {"source": "batch_creation"}
    }
    
    response = requests.post("http://localhost:8001/geoids", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"Created: {result['geoid_id']}")
```

## ⚠️ Important Notes

1. **Vector Embeddings**: The system uses 384-dimensional vectors. For manual injection, you can use random vectors for testing, but production data should use proper embeddings.

2. **Vault Balance**: Scars are distributed between `vault_a` and `vault_b`. The system maintains balance automatically, but manual injection should consider this.

3. **Data Validation**: The system expects specific data formats. Always validate your data structure before injection.

4. **Backup**: Always backup your database before manual injection:
   ```bash
   cp kimera_swm.db kimera_swm.db.backup
   ```

5. **System State**: After manual injection, restart the API server to ensure all caches are refreshed.

## 🔧 Troubleshooting

### Common Issues

1. **Foreign Key Constraints**: Ensure referenced geoid_ids exist before creating scars
2. **JSON Format**: All JSON fields must be valid JSON strings
3. **Vector Dimensions**: Vectors must be exactly 384 dimensions
4. **Timestamp Format**: Use ISO format or datetime objects

### Validation Queries

```sql
-- Check for orphaned scars
SELECT s.scar_id, s.geoids 
FROM scars s 
WHERE NOT EXISTS (
    SELECT 1 FROM geoids g 
    WHERE json_extract(s.geoids, '$[0]') = g.geoid_id
);

-- Check vector dimensions
SELECT geoid_id, json_array_length(semantic_vector) as vector_dim 
FROM geoids 
WHERE json_array_length(semantic_vector) != 384;
```

This guide provides comprehensive methods for data injection into the KIMERA SWM system. Choose the method that best fits your use case and data volume.