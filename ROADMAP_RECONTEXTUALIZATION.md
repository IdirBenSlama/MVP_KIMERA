# Kimera SWM – Re-Contextualization & Insight Engine Road-map

> Version 0.3  |  June 2025  
> Author : Kimera Core Engineering Team
> **Status**: Phases 0, 1, 2, and parts of 3 are **COMPLETE** as of [Current Date]. This update reflects the successful implementation of the core insight generation and management pipeline.

This road-map converts the theoretical gap-analysis into an actionable, engineering-ready plan that completes the missing **Step 3 – Insight Generation & Re-Contextualization** cycle inside Kimera SWM while hardening adjacent subsystems. This version incorporates advanced meta-cognitive and collaborative capabilities. Tasks are grouped by **Phase**, ordered by **priority**, and include explicit deliverables, owner roles, time-boxing, and acceptance tests.

---
## 📈 Road-map at a Glance
| Phase | Duration | Goal |
|-------|----------|------|
| **0** | 1 week | Repository & CI refresh, branch cut, meta-schema freeze |
| **1** | 2 weeks | Core Insight Event data-model (with lifecycle support) + EchoForm extensions |
| **2** | 2 weeks | Validation, governance, **insight lifecycle management** & storage hooks |
| **3** | 2 weeks | Activation-synthesis, feedback, Chaos layer & **meta-insight detection** |
| **4** | 2 weeks | KCCL integration, **user-guided API**, dashboards & traceability |
| **5** | Ongoing | **Self-tuning governance**, optimisation, documentation, edge-cases |

Total initial sprint: **9 weeks**.

---
## ⏱️ Phase 0 – Foundational Setup *(Week 1)*
### 0.1 Create Dedicated Road-map Branch
* **Action :** `git checkout -b feature/recontextualization-engine`
* **Done When :** Branch exists, pushed to origin.

### 0.2 Freeze Core Schemas
* Lock `Geoid`, `Scar`, `EchoForm` JSON-schema versions → tag `schema-v1.0`.
* Update `backend/core/constants.py` with `SCHEMA_VERSION = "1.0"`.

### 0.3 CI / Test Matrix Refresh
* Add Python 3.12 & 3.13 jobs; lint, mypy, pytest on new branch.
* Acceptance: CI green on untouched code.

---
## 🧩 Phase 1 – Insight Data-Structures *(Weeks 2-3) - COMPLETE*
### 1.1 InsightScar Class - COMPLETE
* File: `backend/core/insight.py`
* Fields: `insight_type`, `source_resonance_id`, `entropy_reduction`, `confidence`, `application_domains`, `echoform_repr`.
* **Enhancement:** Add lifecycle fields: `status` ('provisional' | 'active' | 'strengthened' | 'deprecated'), `utility_score` (float), `last_reinforced_cycle` (int).
* Automatic entropy delta calculation.

### 1.2 EchoForm Grammar Extensions - COMPLETE
* Add `INSIGHT_EVENT`, `ANALOGY`, `HYPOTHESIS`, `FRAMEWORK` tokens.
* Round-trip tests: parse ↔ render.

### 1.3 MemoryStore Indexing - COMPLETE
* Extend `ExtendedMemoryStore.indices` with `insight_type`, `application_domains`, `source_resonance`.
* Migration script to add indices to existing SQLite DB.

**Acceptance tests**
```bash
pytest tests/insight/test_insight_scar.py
pytest tests/echoform/test_insight_grammar.py
```

---
## 🔒 Phase 2 – Validation, Contradiction & Storage *(Weeks 4-5) - COMPLETE*
### 2.1 Entropy Validator - COMPLETE
* File: `backend/engines/insight_entropy.py`
* Threshold constants in `config/optimized_settings.json`.
* Unit tests with synthetic insights (hi/lo entropy).

### 2.2 Insight Contradiction Engine - COMPLETE
* Extend `backend/engines/contradiction_engine.py`:
  * `check_insight_conflict(insight: InsightScar)`
  * Decision: keep/supersede/flag.

### 2.3 Ethical Reflex Layer (ERL) Hook - COMPLETE
* **Action:** In `check_insight_conflict`, add a call to a new `erl.validate(insight)` method.
* **Goal:** Ensure generated insights do not violate core ethical or safety axioms defined in the Law Registry.
* **Deliverable:** A mock ERL module in `backend/governance/erl.py` that checks for keywords or high-risk patterns.

### 2.4 Insight Lifecycle Manager - COMPLETE
* **New Module:** `backend/engines/insight_lifecycle.py`
* **Goal:** Manage the evolution of insights based on their usage and feedback.
* **Implementation:**
  * `update_utility_score(insight_id, feedback_event)`: Modifies `utility_score` based on user feedback or system reinforcement.
  * `manage_insight_lifecycle()`: A periodic task that promotes insights to 'strengthened' status if their score is high, or 'deprecated' if it falls below a threshold, making them candidates for pruning.

### 2.5 Storage & Pruning Integration - COMPLETE
* `ExtendedMemoryStore.add_insight_event()` and `update_insight_status()`.
* Update `EntropyManager.should_prune()` to prioritize pruning 'deprecated' insights.

**Acceptance :** An insight flagged by the ERL is quarantined. An insight receiving positive feedback has its `utility_score` increased and its status eventually becomes 'strengthened'.

---
## 🌐 Phase 3 – Activation Synthesis & Symbolic Chaos *(Weeks 6-7) - PARTIALLY COMPLETE*
### 3.1 Activation-Based Synthesis Engine - COMPLETE
* New module `backend/engines/activation_synthesis.py`.
* Implements:
  * `trigger_activation_cascade(resonance_event)`
  * `follow_activation_paths()`
  * `synthesize_patterns()` → returns `GeoidMosaic`.
  * **Enhancement:** The synthesis process must also compute a `synthesis_cost` metric.

### 3.2 Symbolic Chaos Processor - COMPLETE
* Module `backend/engines/symbolic_processor.py`.
* Implements archetypal lookup table in `resources/archetypes.json`.

### 3.3 Insight Output Generator - COMPLETE
* `backend/engines/output_generator.py`  
  Generates EchoForm `INSIGHT_EVENT` objects from mosaics.
* **Enhancement:** The generator will compute a final `InsightQualityScore` based on both `entropy_reduction` and `synthesis_cost`.

### 3.4 Insight Feedback Engine
* **New Module:** `backend/engines/insight_feedback.py`
* **Goal:** Create a mechanism for the system to learn from the utility of its own insights.
* **Implementation:**
  * `track_insight_engagement(insight_id, user_action)`: Logs user interactions (e.g., 'explored', 'dismissed', 'elaborated').
  * `adjust_synthesis_parameters(feedback_data)`: A simple heuristic model that tunes the Activation Synthesis Engine based on which types of insights are most engaged with.

### 3.5 Meta-Insight Engine (Recursive Abstraction)
* **New Module:** `backend/engines/meta_insight.py`
* **Goal:** To generate insights *about* the system's own insight generation process.
* **Implementation:**
  * `scan_recent_insights(insight_scars: list)`: A batch process that runs after several KCCL cycles.
  * `detect_recurring_patterns()`: Uses pattern matching (e.g., identifies repeated use of the same analogy type or symbolic archetype across different domains).
  * **Output:** Generates a higher-order `InsightScar` of type `META_FRAMEWORK` (e.g., "The 'feedback loop' analogy appears to be a highly effective cross-domain tool.").

### 3.6 Activation-Decay Tuning *(Thermodynamic Alignment)*
* **ActivationManager** service (`backend/engines/activation_manager.py`).
  * Exponential decay constant `λ_decay` (configurable), inverse-square entropy damping.
  * Boost factor for high-entropy geoids (`H_s > 3.5`), 70 % faster damping for low-entropy nodes.
* Unit benchmark: activation half-life configurable; compare before/after entropy spread.

### 3.7 Coherence Score & Temperature Control
* **CoherenceService** (`backend/engines/coherence.py`).
  * Computes global `coherence` ∈ [0-1] using contradiction count, support links, thematic alignment.
  * Exposes `temperature` signal to Symbolic Chaos Processor; low coherence ⇒ exploration mode.

### 3.8 Unit & Integration Tests
* Simulate cross-domain resonance; assert at least one analogy insight produced; entropy reduced.

---
## 🔄 Phase 4 – KCCL & API Integration *(Weeks 8-9)*
### 4.1 Extend Core Cognitive Loop
* File: `backend/engines/kccl.py`
* Insert step **after** Vaulting: `self.recontextualizer.process_resonance_for_insights(...)`.
* **Enhancement:** Add a meta-cycle hook that triggers the `Meta-Insight Engine` every N cycles.

### 4.2 REST Endpoints
* `POST /recontextualize/{resonance_id}` → returns insight list.
* `GET  /insights/{insight_id}`
* `GET  /insights?type=analogy&domain=bio`
* `POST /insights/{insight_id}/feedback` - Allows the user/UI to submit engagement data.
* **New:** `POST /insights/generate` - Allows user to proactively guide insight generation with contextual hints (e.g., `{ "source_geoid": "GEOID_A", "target_domain": "engineering", "focus": "structural_patterns" }`).
* Swagger update in `docs/api/README.md`.

### 4.3 Dashboard Widgets
* Update `dashboard/app.js` to plot:
  * Insight generation rate
  * Entropy reduction per insight
  * **New:** Insight Lifecycle dashboard (provisional vs. active vs. strengthened vs. deprecated counts).
  * Insight engagement metrics (explored vs. dismissed).

### 4.4 Insight Lineage Tracer
* **New Module:** `backend/tools/lineage_tracer.py`.
* **Goal:** Provide a developer tool to visualize the full history of an insight.
* **Function:** `trace(insight_id)` → generates a DOT graph or JSON file detailing the source Geoids, the resonance event, the activation paths, the symbolic chaos interpretation, and the final `InsightScar`.

### 4.5 Performance Benchmarks
* Target: < 100 ms added latency per KCCL cycle.

---
## ♻️ Phase 5 – Hardening & Optimisation *(Post-launch, ongoing)*
1. **Self-Tuning Governance Monitor**
   * **New Module:** `