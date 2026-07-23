# Recovery Engine Architecture Specification
**StreamForge RocksDB State Engine**

## 1. Objective
This specification defines the **Recovery Engine Architecture**. The Recovery Engine is the fault-tolerance coordinator for StreamForge, responsible for safely reviving persisted `TruckState` objects from RocksDB into active memory immediately after an application crash, restart, or deployment. It guarantees that the stream processor resumes from the exact mathematical state last committed to disk, preventing data loss or aggregation skew.

## 2. Architecture & Responsibilities
The Recovery Engine acts as the startup gatekeeper. The Aggregation Engine is strictly forbidden from processing new stream events until the Recovery Engine signals completion.
- **Responsibilities:** Scanning RocksDB for active keys upon startup, extracting bytes, invoking the Deserializer, validating the reconstructed domain objects, and populating the active aggregation pool.
- **Out of Scope:** Pulling/rewinding Kafka offsets, creating new events, assigning streaming windows, evaluating aggregations, or cleaning up expired state.

```text
Startup → Recovery Engine → RocksDB Fetch → Deserialization & Validation → Aggregation Ready
```

## 3. Recovery Workflow & Lifecycle
1. **Application Startup:** The Python process initializes. The event consumer is paused.
2. **Initialize Recovery:** The engine binds to the RocksDB instance via the `DatabaseManager`.
3. **Scan Storage:** The engine scans persistent `{truck_id}:{window_start}` keys.
4. **Reconstruct & Validate:** The `Deserializer` converts JSON bytes into `TruckState` objects. Domain validation executes instantly.
5. **State Registration:** Valid objects are registered as the active state for their respective windows.
6. **Resume Processing:** The Recovery Engine exits successfully and unblocks the event stream.

## 4. Validation & Recovery Guarantees
The Recovery Engine operates on a strict **No Partial State** guarantee:
- A recovered state must pass every domain constraint (`sum >= 0`, `count >= 0`, timestamps valid, fields populated).
- **Corrupted State Handling:** If a state fails validation or deserialization (e.g. truncated bytes caused by a hard disk power failure), the engine must log a CRITICAL alert and quarantine the key. Corrupt state must **never** be handed to the Aggregation Engine.
- **Determinism:** The mathematical values restored exactly match the state as it existed at the moment of the crash.

## 5. Error Handling & Failure Scenarios
- **Storage Read Failures:** If RocksDB throws hardware or permissions exceptions during the scan, the application must abort startup rather than starting with a false "empty" state.
- **Schema Mismatches:** If older JSON payloads lack required new fields, the Deserializer's schema coercion rules apply. If coercion fails, the specific state is rejected.
- **Empty Database:** A completely clean start is handled gracefully; the engine simply logs zero states recovered.

## 6. Performance Constraints
- **Startup Latency:** The recovery process blocks the live event stream. It must scan and deserialize efficiently, avoiding memory thrashing.
- **Memory Pressure:** Instead of buffering millions of states into a single massive array, recovery should yield states iteratively or selectively load only active unexpired windows (utilizing RocksDB range scans).

## 7. Component Interactions
- **DatabaseManager / CRUD Engine:** Supplies the persistent bytes.
- **Deserializer:** Handles the critical byte-to-object translation.
- **Aggregation Engine:** Remains idle until the Recovery Engine declares state is fully restored and active.
- **Cleanup Engine (Phase 5):** Operates closely with recovery. States that expired *while* the application was offline may be immediately handed to the Cleanup Manager post-recovery.

## 8. Future Extensibility
Establishing this architectural gateway lays the foundation for:
- **Parallel Recovery:** Utilizing multiple threads to deserialize different truck shards concurrently to minimize startup delay.
- **Checkpoint Recovery:** Using RocksDB native snapshots to rewind state to a specific historical point-in-time.
- **Schema Migrations:** Running bulk migration scripts during the recovery phase before live aggregation resumes.
