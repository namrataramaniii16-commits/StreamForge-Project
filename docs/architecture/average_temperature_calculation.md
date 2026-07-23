# Average Temperature Calculation Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification defines the architecture and mathematical logic for the **Average Temperature Calculation** component. It computes and maintains the `average_temperature` field in the `TruckState` domain object. This is a derived metric, calculated in strictly constant time ($O(1)$) using the latest `sum_temperature` and `count` aggregations, ensuring analytics and down-stream consumers always have access to real-time, human-readable operating conditions.

## 2. Architecture & Responsibilities
This component functions as the final mathematical step in the event processing pipeline before the `TruckState` is passed to the storage layer.
- **Responsibilities:** Validating the presence and numerical safety of the inputs, handling the zero-count edge case, computing the scalar division, and mutating the `TruckState.average_temperature`.
- **Out of Scope:** Summing temperatures, counting events, executing RocksDB storage operations, or managing streaming window lifecycles.

```text
Updated TruckState (Sum + Count) → Average Temperature Calculation → Finalized TruckState
```

## 3. Calculation Formula & Workflow
The average is strictly a derivative metric. It never scans historical events.
- **Formula:** `average_temperature = sum_temperature / count` (where `count > 0`)
- **Workflow:**
  1. Receive the updated `TruckState` from the Event Count Aggregation component.
  2. Extract `sum_temperature` and `count`.
  3. Validate numerical safety (specifically division-by-zero pre-checks).
  4. Perform the floating-point division.
  5. Assign the result to `TruckState.average_temperature`.
  6. Return the finalized state.

## 4. Zero-Count Handling & Validation Rules
Division by zero causes catastrophic runtime failures and must be strictly avoided.
- **Zero-Count Rule:** If `count == 0`, then `average_temperature` must be strictly set to `0.0`. No division is performed.
- **Validation Constraints:** Before division, the component verifies:
  - `sum_temperature >= 0`
  - `count >= 0`
  - Both values are physically present and resolve to valid numerical primitives (not NaN, Infinity, or null).
If validation fails, an `AggregationError` is thrown and the state is left unmodified.

## 5. Numerical Accuracy & Determinism
Because the average is calculated dynamically from two deterministic running metrics, it inherits their determinism:
- **Consistency:** Given identical `sum` and `count`, the average calculation will always produce the exact same floating-point result.
- **Precision:** The division is performed using standard high-precision floating-point arithmetic. No artificial rounding or truncation occurs at this layer, ensuring maximum fidelity for subsequent data consumers.

## 6. Performance & Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time logic. A single arithmetic division executes in nanoseconds.
- **Memory Cost:** Guaranteed $O(1)$ constant space.
- **Constraints:** The component exclusively mutates `average_temperature`. It treats `sum_temperature` and `count` as strictly read-only parameters and avoids all database API interactions.

## 7. Component Interactions
- **Upstream Dependencies:** Relies completely on the **Running Sum** and **Event Count** aggregators to execute prior to invocation.
- **Downstream Consumers:** Once the average is derived, the aggregation pipeline is complete. The Aggregation Engine passes the `TruckState` to `update_state` (or `put_state` for initial creation) for serialization and RocksDB persistence.

## 8. Future Extensibility
Establishing a robust average calculation lays the groundwork for more advanced statistical models:
- **Exponential Moving Average (EMA):** Providing greater weight to recent temperatures.
- **Variance & Standard Deviation:** Requiring calculations that build upon the baseline mean.
- **Threshold Alarms:** Triggering business-logic events if the average crosses established safety/refrigeration bounds.
