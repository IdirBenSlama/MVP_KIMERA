# Cognitive Field Dynamics: Metrics & Monitoring Architecture

This document provides a detailed architectural overview of the Cognitive Field Dynamics (CFD) Metrics and Monitoring system. It covers the system's architecture, data workflows, component interactions, and the underlying design principles that enable real-time performance tracking and analysis.

## 1. System Architecture

The metrics system is designed as a non-invasive, loosely-coupled component that hooks into the core CFD engine. This ensures that the core physics and semantic processing logic remains independent of the monitoring implementation, while still providing deep, real-time insights.

### High-Level Architectural Diagram

The following diagram illustrates the primary components and their interactions:

```mermaid
graph TD
    subgraph "Cognitive Field Dynamics Engine"
        A[CFD Core Logic] -- "triggers" --> B(Metrics Hooks);
        C[Semantic Fields] -- "state" --> B;
        D[Semantic Waves] -- "state" --> B;
    end

    subgraph "Metrics Collection System"
        B -- "raw data" --> E[CognitiveFieldMetricsCollector];
        E -- "stores" --> F[Field Metrics];
        E -- "stores" --> G[Wave Metrics];
        E -- "stores" --> H[System & Performance Metrics];
    end

    subgraph "FastAPI Application"
        I[API Endpoints] -- "requests" --> E;
        E -- "processed metrics" --> I;
    end

    subgraph "Data Persistence & Analysis"
        I -- "on-demand" --> J[Export to JSON];
        K[Offline Analysis] -- "reads" --> J;
        L[Dashboards] -- "queries" --> I;
    end

    style A fill:#cde4ff,stroke:#6c8ebf,stroke-width:2px
    style E fill:#cde4ff,stroke:#6c8ebf,stroke-width:2px
    style I fill:#cde4ff,stroke:#6c8ebf,stroke-width:2px
    style J fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style L fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style K fill:#d5e8d4,stroke:#82b366,stroke-width:2px
```

**Component Descriptions:**

-   **CFD Engine**: The core system responsible for simulating semantic field and wave dynamics. It contains hooks at critical processing points (e.g., field creation, wave interaction) to emit data.
-   **Metrics Collector**: A singleton service that receives raw event data from the engine. It processes this data, updating its internal state which includes detailed metrics for every field and wave, as well as aggregated performance statistics.
-   **API Endpoints**: A set of FastAPI routes that expose the collected metrics. These endpoints provide access to both raw and summarized data, catering to different use cases like dashboards, alerting, and manual inspection.
-   **Persistence & Analysis**: While the system primarily operates in-memory for performance, it provides an API endpoint to export the complete metrics snapshot to a JSON file for offline analysis, historical archiving, or populating other data stores.

## 2. Data Workflows & Pipelines

### Metrics Collection Workflow

The collection process is event-driven, triggered by actions within the CFD engine. This ensures that metrics are captured in real-time as the system state evolves.

```mermaid
sequenceDiagram
    participant Engine as Cognitive Field Dynamics Engine
    participant Collector as CognitiveFieldMetricsCollector
    participant API as Metrics API Endpoints

    Engine->>+Collector: add_geoid() / create_wave()
    Collector->>Collector: track_field_creation()<br/>track_wave_creation()
    Collector-->>-Engine: Return

    loop Field Evolution Step
        Engine->>Engine: evolve_fields(dt)
        Engine-->>Collector: _process_wave_interactions()
        Collector->>Collector: track_wave_field_interaction()<br/>update_field_strength()<br/>update_wave_state()
        Engine-->>Collector: track_evolution_time()
    end

    API->>+Collector: GET /metrics/performance
    Collector->>Collector: get_performance_summary()
    Collector-->>-API: Return Performance JSON

    API->>+Collector: POST /metrics/export
    Collector->>Collector: export_metrics()
    Note right of Collector: Writes all tracked<br/>metrics to a JSON file.
    Collector-->>-API: Return Success Status
```

**Workflow Steps:**

1.  **Initialization**: When a `SemanticField` or `SemanticWave` is created in the engine, a corresponding tracking method (`track_field_creation`, `track_wave_creation`) is called on the `CognitiveFieldMetricsCollector`.
2.  **Evolution Loop**: During each `evolve_fields` cycle, the engine reports key events:
    -   Wave-field interactions and resonance events.
    -   Changes in field strength or wave amplitude.
    -   The total time taken for the evolution step.
3.  **Data Aggregation**: The collector updates its internal data structures—dictionaries and deques—that hold the current state and historical performance data.
4.  **API Access**: External clients can query the metrics data via the API, which reads directly from the collector's in-memory store.
5.  **Export**: A client can trigger an export, which serializes the collector's entire state into a structured JSON file.

### API Request Pipeline

This diagram shows the lifecycle of an API request for metrics data.

```mermaid
graph TD
    subgraph "Client"
        A[User / Dashboard / cURL]
    end

    subgraph "API Gateway & Web Server"
        A -- "HTTP GET /metrics/performance" --> B[FastAPI Router];
    end

    subgraph "Application Logic"
        B -- "routes to" --> C["/performance Endpoint"];
        C -- "collects snapshot" --> D["Metrics Collector"];
        D -- "gets state" --> E["CFD Engine"];
        C -- "gets summary" --> D;
    end

    subgraph "Response Generation"
        D -- "returns summary" --> C;
        C -- "builds" --> H[JSON Response Model];
        H -- "HTTP 200 OK" --> A;
    end

    style A fill:#f9f9f9,stroke:#333,stroke-width:2px
    style B fill:#cde4ff,stroke:#6c8ebf
    style C fill:#d5e8d4,stroke:#82b366
    style H fill:#fff2cc,stroke:#d6b656
    style E stroke-dasharray: 5 5
```

## 3. Semantic Field Topology

In the context of Cognitive Field Dynamics, **topology** refers to the emergent relational structure of the semantic space. It's not just about the spatial position of fields but about their dynamic relationships based on resonance, influence, and interaction strength.

The `FieldTopology` class in the engine is designed to track these higher-order structures. While its implementation is currently a placeholder for future enhancement, its architectural purpose is to enable analysis of:

-   **Semantic Adjacency**: Which fields are "close" based on interaction potential, not just Euclidean distance. This is captured in the `find_semantic_neighbors` function.
-   **Critical Points**: Fields that act as major hubs of influence, identified by high field strength and numerous strong interactions. Anomalies in field strength can be an indicator of such points.
-   **Vortices & Sinks**: Areas where semantic energy is either rapidly circulating or being absorbed. This can be analyzed by tracking the total energy received by fields.
-   **Resonance Clusters**: Groups of fields that are strongly coupled due to similar resonance frequencies. This is a primary method for emergent structure detection and is implemented in the `find_semantic_clusters_by_resonance` function.

The metrics system provides the raw data necessary to analyze this topology. For example, by analyzing the `wave_interactions` and `total_energy_received` from the `FieldMetrics`, one can map out the flow of semantic energy and identify key topological features.

## 4. Design Principles

-   **Performance**: The metrics collection is designed to be extremely lightweight to minimize its impact on the core engine's performance. It uses efficient data structures and avoids blocking operations.
-   **Decoupling**: The collector is decoupled from the engine. The engine emits data without knowledge of how it's being used, allowing for different monitoring strategies to be swapped in without changing the core logic.
-   **Real-time Access**: Data is available for query in real-time, enabling live dashboards and immediate feedback on system state.
-   **Comprehensiveness**: The system aims to capture all key aspects of the CFD simulation, from high-level performance aggregates down to the state of individual fields and waves.
-   **Extensibility**: The architecture makes it straightforward to add new metrics or tracking capabilities as the CFD engine evolves. 