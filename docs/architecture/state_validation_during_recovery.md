# State Validation During Recovery Specification
**StreamForge RocksDB State Engine**

## 1. Objective
This specification defines the **State Validation During Recovery** component. Serving as the primary defense mechanism against corrupted persistence, this layer rigorously inspects every reconstructed `TruckState` retrieved from RocksDB. It guarantees that only structurally sound, mathematically consistent, and schema-compatible state objects are permitted into the active streaming memory pool.

## 2. Architecture & Responsibilities
The Validation Engine is a stateless inspector invoked by the Recovery Workflow immediately after deserialization.
- **Responsibilities:** Enforcing the presence of all required fields, verifying numeric boundaries, asserting mathematical consistency, checking schema compatibility, and yielding a strict boolean Pass/Fail result.
- **Out of Scope:** Repairing corrupted data, extracting bytes from RocksDB, calculating aggregations, or managing the Active Registry.

```text
Deserialized TruckState → Validation Engine → Validation Result (Pass / Fail)
```

## 3. Validation Workflow & Categories
Every recovered object runs a gauntlet of five distinct validation tiers:

### Tier 1: Structural Validation
Validates the physical presence of all mandatory fields:
- `truck_id`, `window_start`, `window_end`
- `sum_temperature`, `count`, `average_temperature`
- `last_updated`

### Tier 2: Data Type Validation
Validates the primitive typing of the payload:
- `count` is a valid Integer.
- `sum_temperature` and `average_temperature` are valid Floats (explicitly rejecting `NaN` and `Infinity`).
- Timestamps conform to standard, parsable formatting.

### Tier 3: Aggregation (Mathematical) Validation
Validates that the domain invariants have not drifted due to prior software bugs, disk corruption, or manual database tampering:
- `count >= 0`
- `sum_temperature >= 0`
- **Internal Consistency Check:** If `count > 0`, `average_temperature` must mathematically align with `sum_temperature / count` (within an acceptable floating-point tolerance). If `count == 0`, `average_temperature` must be exactly `0.0`.

### Tier 4: Metadata Validation
Validates logical time boundaries:
- `window_start < window_end`
- `truck_id` is a non-empty string.
- `last_updated` represents a plausible historical or current timestamp.

### Tier 5: Schema Compatibility Validation
Checks for forward/backward compatibility identifiers (if embedded in the payload). If the loaded record reflects a severely deprecated or strictly future schema version that cannot be safely mapped by the current engine, the state is rejected.

## 4. Validation Lifecycle & Error Handling
- **Pass:** The `TruckState` is marked VALID and control is returned to the Recovery Workflow to finalize Active Registration.
- **Fail:** If a single tier fails, the object is immediately marked INVALID. 
- **Error Handling:** 
  - The corrupted state is permanently rejected from the active runtime.
  - The Validation Engine logs the exact reason for failure (e.g., `Aggregation Validation Failed: count is negative`).
  - The engine **must not** attempt to automatically "heal", guess, or repair the state.
  - By default, the recovery workflow will quarantine the invalid state, log the error, and continue validating the remaining keys to salvage as much of the database as possible (unless a strict fail-fast startup policy is configured).

## 5. Performance Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time logic per `TruckState`.
- **Memory Cost:** Zero allocations. The engine inspects the object by reference.
- **Efficiency (Short-Circuiting):** The pipeline instantly halts at the first failing tier to avoid wasting CPU cycles on deeply corrupted payloads.

## 6. Component Interactions
- **Deserializer (Upstream):** Provides the unverified, raw `TruckState` objects.
- **Recovery Workflow (Caller):** Acts directly on the `Pass/Fail` result to either route the object to memory or quarantine it.
- **Active Registry (Downstream):** Protected entirely by this layer. It only ever receives objects that have successfully cleared the Validation Engine.

## 7. Future Extensibility
The modular, tiered design easily supports plugging in advanced validation rules in the future:
- **Cryptographic Signatures:** Validating a checksum or digital signature to ensure the RocksDB payload wasn't maliciously manipulated outside the application.
- **Cross-State Validation:** Ensuring a newly loaded window doesn't logically conflict with a previously loaded window for the same truck.
- **Business Rule Plugins:** Enabling users to inject custom domain logic (e.g., "temperature cannot mathematically exceed 1000 degrees") strictly into the recovery boot cycle.
