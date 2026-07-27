# Aggregation Update API Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification defines the architecture and orchestration rules for the **Aggregation Update API**. This API serves as the single deterministic entry point for processing incoming events. It orchestrates the Default State Creator, Running Sum Aggregator, Event Count Aggregator, Average Temperature Calculator, and Window Metadata Manager in a strict, guaranteed sequence, producing a validated `TruckState` ready for persistence.

## 2. Architecture & Responsibilities
The Aggregation Update API acts as a pure functional orchestrator.
- **Responsibilities:** Receiving incoming parsed events, executing the aggregation components in a mathematically required order, verifying the final object, and yielding an updated `TruckState`.
- **Out of Scope:** Making business decisions (like window sizing), reading directly from Kafka, or executing the RocksDB CRUD operations (the CRUD Engine handles actual persistence after this API returns).

```text
Event + Current State → Aggregation Update API (Orchestrator) → Finalized Updated State
```

## 3. Orchestration Workflow & Execution Order
Determinism is guaranteed by enforcing an unbreakable execution pipeline. Altering this sequence will inevitably corrupt derived metrics.

**Required Pipeline Sequence:**
1. **Load / Initialize:** Evaluate if `TruckState` exists. If not, invoke **Default State Creation** (`G3.1`).
2. **Sum Aggregation:** Invoke **Running Sum Aggregation** (`G3.2`) to incrementally update `sum_temperature`.
3. **Count Aggregation:** Invoke **Event Count Aggregation** (`G3.3`) to incrementally update `count`.
4. **Average Calculation:** Invoke **Average Temperature Calculation** (`G3.4`) to derive `average_temperature` from the newly updated sum and count.
5. **Metadata Update:** Invoke **Window Metadata Management** (`G3.5`) to stamp `last_updated`.
6. **State Validation:** Perform a final structural validation on the `TruckState`.
7. **Return:** Yield the finalized `TruckState` back to the caller for persistence.

## 4. API Inputs and Outputs
- **Input Payload:** An incoming parsed Event (containing at minimum `truck_id`, `temperature`, and `timestamp`), along with the current `TruckState` (or window information to trigger initialization).
- **Output Payload:** A fully mutated, logically valid `TruckState` domain object.

## 5. Validation Strategy & Error Handling
Before returning the `TruckState` to the consumer, the orchestrator asserts the following domain invariants:
- `truck_id`, `window_start`, `window_end`, and `last_updated` exist.
- `sum_temperature >= 0` and `count >= 0`.
- **Error Handling:** If any component in the pipeline throws an `AggregationError` (e.g., due to corrupt event payloads or zero-count logic flaws), the pipeline instantly aborts.
- **Fail-Fast:** The orchestrator suppresses no exceptions. Aborting ensures that corrupted partial aggregations are never passed to the CRUD Engine, maintaining perfect database consistency.

## 6. Performance & Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time execution. The pipeline is an entirely in-memory chain of lightweight scalar operations.
- **Stateless Orchestration:** The API itself holds no state between event calls; it relies entirely on the provided `TruckState` and Event.
- **Constraints:** The orchestrator must never skip a pipeline step for a valid event, must never reorder the mathematical sequence, and must strictly avoid any RocksDB network/disk API calls.

## 7. Component Interactions
- **Consumers:** The top-level Stream Processor invokes this API for every incoming event.
- **Internal Sub-components:** It orchestrates all G3.1–G3.5 components developed in Phase 3.
- **Downstream Processors:** The returned `TruckState` is handed off to the CRUD engine (`update_state` or `put_state`).

## 8. Future Extensibility
The strict pipeline pattern allows for modular injection of future features:
- **Statistical Plugins:** (e.g., Min/Max, Variance, Anomaly Detection) can be cleanly inserted before the Metadata Update step without rewriting the foundational sum/count logic.
- **Quality Gates:** Pre-aggregation filters can be inserted at Step 0 to silently discard mathematically impossible events (e.g., temperatures below absolute zero) before they taint the running sum.
