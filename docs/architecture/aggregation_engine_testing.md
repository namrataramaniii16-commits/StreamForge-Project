# Aggregation Engine Testing Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification outlines the comprehensive testing strategy for the **Aggregation Engine**. It guarantees that the core mathematical components developed in Phase 3 (Default State, Sum, Count, Average, Metadata, and Orchestration API) are deterministically correct, mathematically sound, fault-tolerant, and performant before being integrated with the recovery or database layers.

## 2. Testing Architecture & Scope
The testing framework isolates mathematical logic from database I/O boundaries.
- **Scope:** `Default State Creation`, `Running Sum Aggregation`, `Event Count Aggregation`, `Average Temperature Calculation`, `Window Metadata Management`, and `Aggregation Update API`.
- **Layers:** Unit Tests (pure functions), Mathematical Validation (data correctness), Integration Tests (pipeline sequence), and Stress/Performance Tests.

## 3. Unit Testing Strategy (Per Component)
Each component is tested as an isolated, stateless mutation function.
- **Default State Creation:** Asserts that an incoming event yields a `TruckState` with exact zeroed defaults (`count=0`, `sum=0`, `average=0`) and matching identifiers.
- **Running Sum Aggregation:** Asserts deterministic floating-point addition. Passing `35.0` to a state with `175.0` must strictly return `210.0`. Asserts rejection of `NaN` or `Infinity`.
- **Event Count Aggregation:** Asserts strictly monotonic `+1` incrementation.
- **Average Temperature Calculation:** Asserts standard mean calculation. Critically asserts the **Zero-Count** rule: if `count == 0`, `average` must explicitly equal `0.0` without throwing a `ZeroDivisionError`.
- **Window Metadata Management:** Asserts that the identity boundaries (`window_start`/`window_end`) are never mutated, while `last_updated` is successfully refreshed to a newer timestamp.

## 4. Orchestration & Integration Testing
The **Aggregation Update API** is tested to guarantee strict pipeline execution order.
- **End-to-End Workflow:** Passing an event through the orchestrator must demonstrably trigger all internal components sequentially.
- **Pipeline Abort / Fail-Fast:** If an event payload is malformed (e.g., missing temperature), the orchestrator must raise an exception immediately. It must never return a partially aggregated state. The initial `TruckState` must remain intact.

## 5. Mathematical Validation & State Consistency
Data correctness is verified using known statistical datasets.
- **Fixture Tests:** Given an input stream of `[30, 35, 40, 45]`, the engine must output exactly `Sum=150`, `Count=4`, `Average=37.5`.
- **Internal Consistency:** Post-aggregation validation asserts `average == sum / count` mathematically holds true for every generated `TruckState` (safeguarded by the `count > 0` check).

## 6. Edge Case & Failure Testing
The engine is subjected to boundary conditions:
- Extremely large temperatures, zero temperatures, or mathematically negative temperatures.
- Max-value event counts to ensure integer/float boundaries don't overflow unexpectedly in the runtime environment.
- Simulated exceptions injected within the pipeline to guarantee the orchestrator safely unwinds without state corruption.

## 7. Performance & Stress Testing
Because the aggregation engine executes synchronously per-event, latency is critical.
- **Latency Benchmarks:** The orchestrator must execute the complete pipeline in $O(1)$ constant time regardless of how large the event `count` grows.
- **Stress Runs:** Executing millions of events against a single in-memory `TruckState` to ensure no memory leaks exist and that garbage collection isn't overly burdened by temporary object creation.

## 8. Regression Strategy
Any future statistical plugins (e.g., Variance, Min/Max) added to the orchestration pipeline mandate a full re-run of this test matrix to ensure the foundational sum, count, and average calculations remain mathematically uncompromised.
