# KIMERA SWM API Reference

## Complete API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8001`  
**Content-Type:** `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Geoid Management](#geoid-management)
3. [Contradiction Processing](#contradiction-processing)
4. [System Operations](#system-operations)
5. [Vault Management](#vault-management)
6. [Monitoring & Health](#monitoring--health)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

### API Key Authentication

```http
Authorization: Bearer <api_key>
```

### Request Headers

```http
Content-Type: application/json
X-Kimera-Profile: <profile_name>  # Optional: Request profile
X-Request-ID: <unique_id>         # Optional: Request tracking
```

---

## Geoid Management

### Create Geoid

Creates a new semantic geoid with specified features and content.

**Endpoint:** `POST /geoids`

**Request Body:**
```json
{
  "semantic_features": {
    "feature_name": 0.8,
    "another_feature": -0.3,
    "intensity": 0.95
  },
  "symbolic_content": {
    "type": "concept",
    "category": "abstract",
    "description": "Example concept"
  },
  "metadata": {
    "source": "api",
    "timestamp": "2025-06-10T12:00:00Z",
    "tags": ["test", "example"]
  },
  "echoform_text": "(concept (properties (intensity high)))"  # Optional
}
```

**Response:**
```json
{
  "geoid_id": "GEOID_a1b2c3d4",
  "geoid": {
    "geoid_id": "GEOID_a1b2c3d4",
    "semantic_state": {
      "feature_name": 0.8,
      "another_feature": -0.3,
      "intensity": 0.95
    },
    "symbolic_state": {
      "type": "concept",
      "category": "abstract",
      "description": "Example concept",
      "echoform": [["concept", [["properties", [["intensity", "high"]]]]]]
    },
    "metadata": {
      "source": "api",
      "timestamp": "2025-06-10T12:00:00Z",
      "tags": ["test", "example"],
      "created_at": "2025-06-10T12:00:01.234Z",
      "entropy": 0.0
    }
  },
  "entropy": 0.0,
  "processing_time": 0.045
}
```

**Status Codes:**
- `200 OK` - Geoid created successfully
- `400 Bad Request` - Invalid request format
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error

### Retrieve Geoid

Retrieves details of a specific geoid.

**Endpoint:** `GET /geoids/{geoid_id}`

**Path Parameters:**
- `geoid_id` (string, required) - Unique geoid identifier

**Response:**
```json
{
  "geoid_id": "GEOID_a1b2c3d4",
  "semantic_state": {
    "feature_name": 0.8,
    "another_feature": -0.3
  },
  "symbolic_state": {
    "type": "concept",
    "category": "abstract"
  },
  "metadata": {
    "created_at": "2025-06-10T12:00:01.234Z",
    "entropy": 0.0,
    "access_count": 5
  }
}
```

### Search Geoids

Performs semantic search across geoids.

**Endpoint:** `GET /geoids/search`

**Query Parameters:**
- `query` (string, required) - Search query
- `limit` (integer, optional, default: 10) - Maximum results
- `threshold` (float, optional, default: 0.7) - Similarity threshold
- `include_metadata` (boolean, optional, default: false) - Include metadata

**Example Request:**
```http
GET /geoids/search?query=abstract%20concept&limit=5&threshold=0.8
```

**Response:**
```json
{
  "query": "abstract concept",
  "results": [
    {
      "geoid_id": "GEOID_a1b2c3d4",
      "similarity_score": 0.95,
      "semantic_state": {
        "feature_name": 0.8,
        "another_feature": -0.3
      },
      "symbolic_state": {
        "type": "concept",
        "category": "abstract"
      }
    }
  ],
  "total_results": 1,
  "processing_time": 0.023
}
```

### Update Geoid

Updates an existing geoid's features or metadata.

**Endpoint:** `PUT /geoids/{geoid_id}`

**Request Body:**
```json
{
  "semantic_features": {
    "updated_feature": 0.9
  },
  "metadata": {
    "updated_field": "new_value"
  }
}
```

### Delete Geoid

Removes a geoid from the system.

**Endpoint:** `DELETE /geoids/{geoid_id}`

**Response:**
```json
{
  "message": "Geoid deleted successfully",
  "geoid_id": "GEOID_a1b2c3d4",
  "deleted_at": "2025-06-10T12:05:00.123Z"
}
```

---

## Contradiction Processing

### Process Contradictions

Detects and processes contradictions for a given geoid.

**Endpoint:** `POST /process/contradictions`

**Request Body:**
```json
{
  "trigger_geoid_id": "GEOID_a1b2c3d4",
  "search_limit": 10,
  "force_collapse": false,
  "intensity_threshold": 0.5,
  "processing_mode": "standard"  # Options: standard, intensive, lightweight
}
```

**Response:**
```json
{
  "trigger_geoid_id": "GEOID_a1b2c3d4",
  "contradictions_detected": 3,
  "scars_created": 3,
  "processing_time": 1.234,
  "entropy_change": 0.15,
  "contradictions": [
    {
      "contradiction_id": "CONT_x1y2z3",
      "geoid_a": "GEOID_a1b2c3d4",
      "geoid_b": "GEOID_b2c3d4e5",
      "intensity": 0.85,
      "type": "semantic_opposition",
      "resolution": "scar_generated",
      "scar_id": "SCAR_s1t2u3v4"
    }
  ],
  "system_state": {
    "entropy": 2.45,
    "active_geoids": 150,
    "total_scars": 89
  }
}
```

### Get Contradiction Details

Retrieves details of a specific contradiction.

**Endpoint:** `GET /contradictions/{contradiction_id}`

**Response:**
```json
{
  "contradiction_id": "CONT_x1y2z3",
  "geoids": ["GEOID_a1b2c3d4", "GEOID_b2c3d4e5"],
  "intensity": 0.85,
  "type": "semantic_opposition",
  "detected_at": "2025-06-10T12:01:00.123Z",
  "resolved_at": "2025-06-10T12:01:01.456Z",
  "resolution_method": "scar_generation",
  "scar_id": "SCAR_s1t2u3v4",
  "entropy_impact": 0.15
}
```

---

## System Operations

### Execute Cognitive Cycle

Triggers a cognitive cycle for system maintenance and processing.

**Endpoint:** `POST /system/cycle`

**Request Body (Optional):**
```json
{
  "cycle_type": "standard",  # Options: standard, intensive, maintenance
  "force_execution": false,
  "target_entropy": null
}
```

**Response:**
```json
{
  "cycle_id": "CYCLE_c1d2e3f4",
  "cycle_type": "standard",
  "execution_time": 0.156,
  "operations_performed": {
    "contradictions_processed": 5,
    "scars_generated": 5,
    "entropy_adjustments": 2,
    "vault_rebalancing": true
  },
  "system_state_before": {
    "entropy": 15.2,
    "active_geoids": 145,
    "vault_a_scars": 42,
    "vault_b_scars": 41
  },
  "system_state_after": {
    "entropy": 12.8,
    "active_geoids": 145,
    "vault_a_scars": 44,
    "vault_b_scars": 44
  },
  "performance_metrics": {
    "cycle_efficiency": 0.95,
    "entropy_reduction": 2.4,
    "processing_rate": 32.1
  }
}
```

### System Status

Retrieves comprehensive system status and metrics.

**Endpoint:** `GET /system/status`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-10T12:00:00.123Z",
  "uptime": 86400,
  "version": "1.0.0",
  "system_metrics": {
    "active_geoids": 150,
    "total_scars": 89,
    "system_entropy": 12.8,
    "vault_a_scars": 44,
    "vault_b_scars": 45,
    "cycle_count": 25,
    "last_cycle": "2025-06-10T11:59:45.678Z"
  },
  "performance_metrics": {
    "avg_response_time": 0.045,
    "requests_per_second": 12.5,
    "error_rate": 0.001,
    "cpu_usage": 35.2,
    "memory_usage": 68.5,
    "disk_usage": 15.3
  },
  "health_checks": {
    "database": "healthy",
    "vault_system": "healthy",
    "contradiction_engine": "healthy",
    "thermodynamic_processor": "healthy"
  }
}
```

### System Stability Analysis

Provides detailed stability analysis and recommendations.

**Endpoint:** `GET /system/stability`

**Response:**
```json
{
  "stability_score": 0.95,
  "stability_level": "excellent",
  "analysis": {
    "entropy_stability": {
      "score": 0.98,
      "variance": 1.23,
      "trend": "stable",
      "recommendation": "no_action_required"
    },
    "vault_balance": {
      "score": 0.99,
      "imbalance": 1,
      "quality": "excellent",
      "recommendation": "maintain_current_state"
    },
    "processing_efficiency": {
      "score": 0.92,
      "throughput": 12.5,
      "latency": 0.045,
      "recommendation": "monitor_performance"
    }
  },
  "recommendations": [
    {
      "priority": "low",
      "category": "optimization",
      "description": "Consider increasing cache size for improved performance",
      "estimated_impact": "5% performance improvement"
    }
  ],
  "next_analysis": "2025-06-10T13:00:00.000Z"
}
```

---

## Vault Management

### Get Vault Contents

Retrieves contents of a specific vault.

**Endpoint:** `GET /vaults/{vault_id}`

**Path Parameters:**
- `vault_id` (string, required) - Vault identifier (vault_a or vault_b)

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Maximum scars to return
- `offset` (integer, optional, default: 0) - Pagination offset
- `sort_by` (string, optional, default: timestamp) - Sort field
- `order` (string, optional, default: desc) - Sort order (asc/desc)

**Response:**
```json
{
  "vault_id": "vault_a",
  "total_scars": 44,
  "scars": [
    {
      "scar_id": "SCAR_s1t2u3v4",
      "geoids": ["GEOID_a1b2c3d4", "GEOID_b2c3d4e5"],
      "reason": "semantic_opposition",
      "timestamp": "2025-06-10T12:01:01.456Z",
      "resolved_by": "contradiction_engine",
      "entropy_metrics": {
        "pre_entropy": 15.2,
        "post_entropy": 12.8,
        "delta_entropy": -2.4
      },
      "weight": 1.0,
      "last_accessed": "2025-06-10T12:05:00.123Z"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 44,
    "has_more": true
  }
}
```

### Rebalance Vaults

Triggers vault rebalancing operation.

**Endpoint:** `POST /vaults/rebalance`

**Request Body (Optional):**
```json
{
  "strategy": "equal_distribution",  # Options: equal_distribution, weight_based
  "force_rebalance": false,
  "target_balance_threshold": 0.05
}
```

**Response:**
```json
{
  "rebalance_id": "REBAL_r1s2t3u4",
  "strategy": "equal_distribution",
  "execution_time": 0.234,
  "before_state": {
    "vault_a_scars": 50,
    "vault_b_scars": 40,
    "imbalance": 10
  },
  "after_state": {
    "vault_a_scars": 45,
    "vault_b_scars": 45,
    "imbalance": 0
  },
  "operations": {
    "scars_moved": 5,
    "direction": "vault_a_to_vault_b",
    "success_rate": 1.0
  }
}
```

### Vault Statistics

Provides detailed vault statistics and analytics.

**Endpoint:** `GET /vaults/{vault_id}/stats`

**Response:**
```json
{
  "vault_id": "vault_a",
  "statistics": {
    "total_scars": 45,
    "average_weight": 1.0,
    "total_weight": 45.0,
    "oldest_scar": "2025-06-10T10:00:00.000Z",
    "newest_scar": "2025-06-10T12:01:01.456Z",
    "access_frequency": 2.5,
    "storage_efficiency": 0.95
  },
  "distribution": {
    "by_type": {
      "semantic_opposition": 25,
      "contextual_conflict": 15,
      "intensity_mismatch": 5
    },
    "by_weight": {
      "light": 10,
      "medium": 25,
      "heavy": 10
    }
  },
  "performance": {
    "avg_retrieval_time": 0.002,
    "cache_hit_rate": 0.85,
    "compression_ratio": 0.75
  }
}
```

---

## Monitoring & Health

### Health Check

Basic health check endpoint.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-10T12:00:00.123Z",
  "checks": {
    "database": "ok",
    "vault_system": "ok",
    "api": "ok"
  }
}
```

### Detailed Health Check

Comprehensive health assessment.

**Endpoint:** `GET /health/detailed`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-10T12:00:00.123Z",
  "uptime": 86400,
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time": 0.005,
      "connections": {
        "active": 5,
        "max": 100,
        "utilization": 0.05
      }
    },
    "vault_system": {
      "status": "healthy",
      "balance_quality": "excellent",
      "vault_a_health": "ok",
      "vault_b_health": "ok"
    },
    "contradiction_engine": {
      "status": "healthy",
      "processing_queue": 0,
      "avg_processing_time": 0.156
    },
    "thermodynamic_processor": {
      "status": "healthy",
      "entropy_level": "stable",
      "last_cycle": "2025-06-10T11:59:45.678Z"
    }
  },
  "resources": {
    "cpu_usage": 35.2,
    "memory_usage": 68.5,
    "disk_usage": 15.3,
    "network_io": {
      "bytes_in": 1048576,
      "bytes_out": 2097152
    }
  }
}
```

### Metrics Endpoint

Prometheus-compatible metrics.

**Endpoint:** `GET /metrics`

**Response:**
```
# HELP kimera_requests_total Total number of requests
# TYPE kimera_requests_total counter
kimera_requests_total{method="GET",endpoint="/geoids"} 1234

# HELP kimera_request_duration_seconds Request duration in seconds
# TYPE kimera_request_duration_seconds histogram
kimera_request_duration_seconds_bucket{le="0.1"} 1000
kimera_request_duration_seconds_bucket{le="0.5"} 1200
kimera_request_duration_seconds_bucket{le="1.0"} 1234

# HELP kimera_system_entropy Current system entropy
# TYPE kimera_system_entropy gauge
kimera_system_entropy 12.8

# HELP kimera_active_geoids Number of active geoids
# TYPE kimera_active_geoids gauge
kimera_active_geoids 150
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid semantic features format",
    "details": {
      "field": "semantic_features",
      "expected": "object",
      "received": "string"
    },
    "request_id": "req_a1b2c3d4e5f6",
    "timestamp": "2025-06-10T12:00:00.123Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Authentication required |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Common Error Scenarios

#### Invalid Geoid ID
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Geoid not found",
    "details": {
      "geoid_id": "GEOID_invalid123"
    }
  }
}
```

#### Validation Error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Semantic features must be numeric values between -1 and 1",
    "details": {
      "invalid_features": ["feature_name"],
      "invalid_values": [1.5]
    }
  }
}
```

#### Rate Limit Exceeded
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "60s",
      "retry_after": 30
    }
  }
}
```

---

## Rate Limiting

### Rate Limit Headers

All responses include rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
X-RateLimit-Window: 60
```

### Rate Limit Tiers

| Tier | Requests/Minute | Burst Limit |
|------|-----------------|-------------|
| **Free** | 60 | 10 |
| **Standard** | 300 | 50 |
| **Premium** | 1000 | 100 |
| **Enterprise** | Unlimited | 500 |

### Rate Limit Bypass

For high-priority operations, use the bypass header:

```http
X-Priority: high
```

---

## SDK Examples

### Python SDK

```python
from kimera_sdk import KimeraClient

client = KimeraClient(
    base_url="http://localhost:8001",
    api_key="your_api_key"
)

# Create geoid
geoid = client.geoids.create({
    "semantic_features": {"concept": 0.8},
    "symbolic_content": {"type": "test"}
})

# Process contradictions
result = client.contradictions.process(
    trigger_geoid_id=geoid.geoid_id,
    search_limit=10
)

# Get system status
status = client.system.status()
```

### JavaScript SDK

```javascript
import { KimeraClient } from '@kimera/sdk';

const client = new KimeraClient({
  baseUrl: 'http://localhost:8001',
  apiKey: 'your_api_key'
});

// Create geoid
const geoid = await client.geoids.create({
  semantic_features: { concept: 0.8 },
  symbolic_content: { type: 'test' }
});

// Process contradictions
const result = await client.contradictions.process({
  trigger_geoid_id: geoid.geoid_id,
  search_limit: 10
});
```

---

This API reference provides comprehensive documentation for all KIMERA SWM endpoints with detailed examples, error handling, and best practices for integration.