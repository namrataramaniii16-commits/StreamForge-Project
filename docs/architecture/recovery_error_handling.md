# Recovery Error Handling & Fault Tolerance Specification
**StreamForge RocksDB State Engine**

## 1. Objective
This specification defines the **Recovery Error Handling & Fault Tolerance** framework. It establishes strict, deterministic policies for identifying, categorizing, and mitigating failures encountered during application startup. This framework ensures that StreamForge never boots into a corrupted, partial, or silently failing state, preserving mathematical integrity across crashes.

## 2. Fault-Tolerance Architecture & Responsibilities
The Error Handler intercepts any exception thrown during the State Recovery Workflow.
- **Responsibilities:** Categorizing the failure, applying the configured recovery policy (Retry vs Reject vs Abort), recording rich diagnostic logs, and generating the final Startup Summary report.
- **Out of Scope:** Automated self-healing of corrupted domain objects, resetting Kafka offsets, or executing downstream stream aggregations.

```text
Recovery Workflow Exception → Error Handler → Policy Engine → Log & Report → Boot Decision
```

## 3. Failure Categories & Severity Levels
Failures are rigorously categorized to trigger the correct deterministic policy:

| Category | Example | Severity | Policy Action |
|---|---|---|---|
| **Storage Failures** | RocksDB I/O Error, Permission Denied | `CRITICAL` | Retry (if timeout), else Abort Startup |
| **Deserialization** | Truncated JSON bytes, non-UTF8 payload | `ERROR` | Reject State & Continue |
| **Validation** | `count < 0`, schema incompatible | `ERROR` | Reject State & Continue |
| **Runtime Failures** | OOM (Out of Memory), Thread starvation | `CRITICAL` | Abort Startup |

## 4. Retry Strategy
- **Eligible (Transient):** Hardware timeouts or transient OS file locks allow a finite number of retries with exponential backoff.
- **Ineligible (Persistent):** Corrupted bytes, schema mismatches, and domain validation failures are **never** retried. The state is instantly rejected to avoid infinite boot loops and wasted CPU cycles.

## 5. Partial Recovery & Startup Decision Logic
StreamForge supports partial recovery to maximize uptime, governed by a strict Startup Decision Matrix:
- **100% Valid:** `SUCCESS` → Start Application.
- **Partial Valid / Some Rejected:** `WARNING` → Start Application. The valid states enter the active registry. The corrupted states are logged and permanently dropped (meaning those specific trucks will start fresh at count `0` for the current window).
- **Storage/Runtime Fatalities:** `FATAL` → Abort Startup. If RocksDB itself is unreachable, the application must crash rather than boot with a false "empty" database assumption.

## 6. Logging Strategy & Recovery Reporting
Transparency is critical. Every rejected state produces a structured diagnostic log containing:
- `Timestamp`, `truck_id` (if successfully parsed), `window_start` (if successfully parsed)
- `Failure Category` and `Severity`
- `Exception Details` and `Recovery Policy Applied`

**Final Recovery Summary:**
Before unblocking the stream processor, the engine emits a final telemetry report:
```text
=== RECOVERY SUMMARY ===
Status: SUCCESS_WITH_WARNINGS
Total Keys Processed: 10,000
Valid States Registered: 9,998
Rejected (Corrupt/Invalid): 2
Storage Retries Executed: 0
Fatal Errors: 0
========================
```

## 7. Performance & Constraints
- **Constraints:** The framework must never infinitely loop. It must never silently swallow an exception (all drops must be aggressively logged). It must never attempt to repair or guess the missing data in a corrupted state.
- **Execution Cost:** Failure paths must execute quickly and explicitly release memory associated with corrupted payloads to prevent garbage collection pressure during massive boot-time database scans.

## 8. Future Extensibility
- **Quarantine Storage (Dead Letter Queue):** Moving corrupted byte arrays into a separate RocksDB column family for offline forensic analysis rather than just discarding them.
- **Adaptive Boot Policies:** Allowing dynamic configuration via environment variables (e.g., "Abort startup if > 5% of states are corrupted").
- **Metrics Integration:** Hooking the summary report directly into Prometheus/Datadog counters for alerting on infrastructure degradation.
