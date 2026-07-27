# Recovery State Registration Specification
**StreamForge RocksDB Recovery Engine**

## 1. Objective
This specification defines the **Recovery State Registration** component. Operating as the final gate in the recovery pipeline, this component safely admits fully validated `TruckState` objects into the active in-memory runtime registry. It guarantees that the Aggregation Engine only ever processes events against unique, untampered, and fully consistent window states.

## 2. Architecture & Responsibilities
The Registration component bridges the critical gap between disk recovery and active stream processing.
- **Responsibilities:** Managing the Active Runtime Registry, enforcing unique runtime identities (`truck_id:window_start:window_end`), inserting validated objects into memory, and verifying successful admission.
- **Out of Scope:** Deserialization, mathematical validation, reading RocksDB, calculating aggregations, or evicting expired states.

```text
Validated TruckState → Registration Manager → Active Runtime Registry → Aggregation Engine
```

## 3. Active Runtime Registry Design
The Registry is an isolated in-memory data structure (e.g., a hash map or concurrent dictionary) heavily optimized for $O(1)$ lookups.
- **Identity Key:** The strict unique identifier is `{truck_id}:{window_start}:{window_end}`.
- **Purpose:** The Aggregation Update API queries this registry to load existing state when a new event arrives.

## 4. Execution Workflow & Lifecycle
1. **Receive:** The component accepts a `TruckState` that has strictly passed all 5 tiers of the Validation Engine.
2. **Uniqueness Check:** The Registry is queried using the `TruckState` identity.
3. **Insert:** If no entry exists, the state reference is stored in the Registry.
4. **Verify:** A post-insertion check confirms the memory pointer correctly matches the recovered object.
5. **Ready:** The state is now officially active and eligible for mutation by the Aggregation Engine once the recovery phase completely unblocks Kafka.

## 5. Duplicate Registration & Uniqueness Rules
A fundamental rule of the engine is that duplicate runtime states must never exist for the same window.
- **Duplicate Handling:** If the Uniqueness Check reveals that an object with the same identity already occupies the Registry, the new registration is immediately **rejected**.
- **Conflict Resolution:** The Registration Manager does not attempt to mathematically merge the two objects. It logs a `WARNING` detailing the collision and safely discards the incoming duplicate. The originally registered runtime object remains the single source of truth.

## 6. Error Handling
- **Memory/Runtime Failures:** If the host runtime throws an allocation exception (e.g., Out Of Memory) during insertion, the Registration Manager throws a fatal error, triggering the overarching `Abort Startup` fault-tolerance policy.
- **Partial Registration:** Registration is strictly atomic. An object is either fully admitted into the Registry or entirely rejected.

## 7. Performance Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time logic. Checking and inserting into the registry dictionary must execute in near-instantaneous time without scanning existing objects.
- **Startup Latency:** The registration process avoids heavy global locks where possible, ensuring that bootstrapping millions of recovered keys into memory takes milliseconds to seconds, rather than minutes.

## 8. Future Extensibility
While currently designed as a monolithic in-memory structure, the Registration layer accommodates future scale:
- **Distributed Runtime Registry:** Using Redis or a clustered cache to share active state across multiple distributed StreamForge application instances.
- **Hot State Migration:** Permitting a failing node to actively push state into this healthy node's Registry during automated rebalancing.
- **Dynamic Partitioning:** Sharding the in-memory registry by `truck_id` to eliminate lock contention on high-throughput, highly concurrent systems.
