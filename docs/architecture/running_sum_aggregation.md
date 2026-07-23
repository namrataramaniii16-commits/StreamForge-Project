# Running Sum Aggregation Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification defines the architecture and mathematical constraints for the **Running Sum Aggregation** component. This component incrementally updates the cumulative temperature total (`sum_temperature`) for a `TruckState` in true constant time ($O(1)$). It acts as the core foundational metric for deriving all future statistical values without ever scanning historical event data.

## 2. Architecture & Responsibilities
The Running Sum Aggregator is a pure, functional mutation step within the broader Aggregation Engine pipeline.
- **Responsibilities:** Validating the incoming numeric temperature, executing the addition formula against the current `TruckState` sum, and preserving floating-point stability.
- **Out of Scope:** Making CRUD calls to RocksDB, updating event counts, recalculating averages, or window streaming logic.

```text
Current TruckState + Incoming Event Temperature → Running Sum Aggregation → Updated TruckState
```

## 3. Aggregation Formula & Workflow
Instead of storing unbounded historical arrays, the engine strictly maintains a running aggregate:
- **Formula:** `New Running Sum = Previous Running Sum + Incoming Temperature`
- **Workflow:**
  1. Receive the current `TruckState` (either freshly initialized at `0.0` or retrieved from RocksDB).
  2. Extract and validate the incoming event's temperature payload.
  3. Perform the in-place addition on `sum_temperature`.
  4. Return the updated `TruckState` to the pipeline.

## 4. Validation Rules & Error Handling
Before execution, the payload must pass strict pre-conditions to prevent poisoning the aggregate:
- **Validation:** The incoming temperature must exist, be purely numeric (no NaNs or Infinity values), and the `TruckState` must be a valid, instantiated domain object.
- **Error Handling:** If the temperature payload is corrupt or non-numeric, the component instantly raises an `AggregationError`. The `TruckState` remains unmodified, ensuring invalid events do not permanently corrupt the window's total.

## 5. Numerical Accuracy
To support enterprise-grade analytics, the aggregator guarantees:
- **Precision:** Uses stable floating-point operations. It must not aggressively round intermediate states, preserving the raw accumulated value exactly as processed.
- **Determinism:** Identical input streams must always yield identical running sums regardless of processing latency, recovery cycles, or cluster placement.

## 6. Performance & Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time execution. It never scans, loops, or queries past events.
- **Memory Cost:** Guaranteed $O(1)$ constant space. It allocates no history arrays.
- **Constraint:** The component modifies exactly one field: `sum_temperature`. It must not alter identifiers, timestamps, or unrelated metrics.

## 7. Component Interactions
- **Inputs:** A `TruckState` (from `get_state` or `Default State Creator`) and a parsed Event stream metric.
- **Consumers:** The updated `TruckState` is immediately forwarded to the **Event Count Aggregation** component, and eventually the **Average Calculation** component.

## 8. Future Extensibility
While currently scoped strictly to simple addition, the running sum architecture establishes the foundation for calculating future statistical derivatives (e.g., Variance, Standard Deviation, Exponential Moving Averages), which all rely on preserving mathematically sound running cumulative base states rather than raw event storage.
