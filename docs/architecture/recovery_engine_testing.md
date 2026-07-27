# Recovery Engine Testing Specification
**StreamForge RocksDB Recovery Engine**

## 1. Objective
This specification defines the comprehensive testing strategy for the **Recovery Engine**. It ensures that the recovery pipeline (discovery, deserialization, validation, registration, and dependency integration) executes flawlessly and deterministically. This rigorous testing shields the StreamForge runtime from corrupted data, ensures predictable startup sequences, and guarantees mathematical continuity across application restarts.

## 2. Testing Architecture & Scope
The testing framework divides the Recovery Engine into isolated, verifiable components before testing the full integration sequence against simulated infrastructure.
- **Scope:** `State Recovery Workflow`, `State Validation`, `Error Handling & Policies`, `State Registration`, and `Startup Integration`.
- **Layers:** Unit Tests (isolated logic), Integration Tests (workflow sequences), Fault-Injection Tests (simulated disk/memory errors), and Stress/Performance Tests.

## 3. Unit Testing Strategy
- **State Validation Tests:** Supply the engine with manually corrupted JSON payloads (e.g., negative `count`, missing `truck_id`, mismatched `average_temperature`) and assert that the Validator strictly rejects them. Supply perfectly formed JSON and assert seamless passage.
- **State Registration Tests:** Verify the active registry's uniqueness constraints. Assert that injecting a `TruckState` successfully persists it in memory. Attempt to inject a second `TruckState` with the exact same `{truck_id}:{window_start}:{window_end}` identity and assert that the Registration Manager explicitly rejects the duplicate without mutating the original.
- **Error Handling Tests:** Inject simulated `StorageExceptions` and `ValidationExceptions` directly into the handler. Assert that storage hardware timeouts correctly trigger the exponential backoff `Retry` policy, while domain validation failures instantly trigger the `Reject State` policy without retries.

## 4. Startup Integration & Workflow Testing
- **Execution Sequence:** Assert that the dependency initializer strictly boots in order: `Configuration → RocksDB → CRUD → Recovery → Registry → Aggregation → Kafka Consumer`.
- **Blocking Guarantees:** Assert that the Kafka Consumer initialization thread remains fully blocked, dormant, and un-instantiated until the Recovery Engine explicitly returns its final Status Summary.
- **Exactly-Once Execution:** Assert that invoking the recovery workflow twice consecutively returns instantly on the second call, utilizing an immutable "already recovered" flag rather than repeatedly scanning the disk.

## 5. Partial Recovery & Fault Tolerance Testing
- **Mixed Workload Simulation:** Seed a test RocksDB instance with 100 known states: 95 perfectly valid, and 5 intentionally corrupted (e.g., truncated JSON strings or non-UTF8 bytes).
- **Assertion:** Run the Recovery Integration pipeline. Assert that the system successfully boots with a `SUCCESS_WITH_WARNINGS` status, the active registry contains exactly 95 active states, the 5 corrupt states are completely ignored by the registry, and 5 detailed error logs are generated.

## 6. Performance & Stress Testing
- **Latency Benchmarks:** Seed a test database with 1,000,000 randomized valid state keys. Assert that the Recovery Workflow (scan, deserialize, validate, register) completes within strict, bounded latency limits (e.g., under 10 seconds), preventing unbearable deployment delays.
- **Memory Profiling (OOM Prevention):** During the 1-million key test, assert that memory consumption remains stable and scales strictly with the active registry size. Ensure that no orphaned byte arrays or temporary JSON strings leak into the garbage collector during the massive deserialization loop.

## 7. Regression & End-to-End Testing
- **End-to-End Pipeline:** Run a full simulation: Start application → Process 100 live events → Assert Aggregation → Force Crash → Restart application → Assert Recovery matching exact previous Aggregation → Process 100 more events.
- **Schema Evolution:** Any future modifications to the underlying `TruckState` schema mandate a full regression run of this test matrix using both legacy payloads and updated payloads to guarantee backward compatibility during recovery.
