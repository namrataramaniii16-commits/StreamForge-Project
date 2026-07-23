# Window Metadata Management Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification defines the architecture and constraints of the **Window Metadata Management** component. It is strictly responsible for managing, validating, and updating the temporal and structural identity (`truck_id`, `window_start`, `window_end`, `last_updated`) of every `TruckState`, ensuring that streaming windows remain perfectly aligned, immutable, and correctly tracked throughout their lifecycle.

## 2. Architecture & Responsibilities
The Window Metadata Management component oversees the non-mathematical, identity-focused properties of the state object.
- **Responsibilities:** Protecting window boundaries from illegal mutations, tracking the latest successful event update timestamp, and asserting metadata consistency.
- **Out of Scope:** Making CRUD calls to RocksDB, evaluating mathematical aggregations (`sum`, `count`, `average`), assigning windows (routing logic), or executing cleanup processes.

```text
Aggregation Pipeline Success → Metadata Manager (Update last_updated) → Validated TruckState
```

## 3. Managed Metadata & Rules
The component explicitly manages four fields:

| Field | Nature | Rule |
|---|---|---|
| `truck_id` | **Immutable** | Identity marker. Cannot change once initialized. |
| `window_start` | **Immutable** | Identity marker. Cannot change once initialized. |
| `window_end` | **Immutable** | Identity marker. Cannot change once initialized. |
| `last_updated` | **Mutable** | Must strictly update to the exact processing timestamp after every successful aggregation cycle. |

## 4. Metadata Workflow & Timestamp Management
The lifecycle of metadata spans from the initialization of the state to its eventual expiration.
1. **Creation:** At window origin, the Default State Creator assigns the immutable boundaries and sets an initial `last_updated` time.
2. **Pre-Update Validation:** Before applying aggregation metrics, the component verifies the target `TruckState` actually belongs to the current streaming window.
3. **Post-Update Modification:** Following successful `sum`, `count`, and `average` mutations, the Metadata Manager intercepts the `TruckState`.
4. **Timestamp Assignment:** Generates the current UTC timestamp and assigns it to `last_updated`, explicitly recording exactly when the state was last physically altered.

## 5. Window Validation & Consistency Rules
If any of the following constraints fail, an `AggregationError` is thrown, and the `TruckState` is rejected from the pipeline:
- `window_start` must exist and strictly precede `window_end`.
- `truck_id` must be fully populated and non-empty.
- `last_updated` must be a valid, non-null timestamp.
- **Identity Invariant:** Once a `TruckState` object is bound to a specific window, its boundaries cannot shift.

## 6. Performance & Constraints
- **Execution Cost:** Guaranteed $O(1)$ constant time execution. Verifications are simple comparisons and the timestamp generation is a single system call.
- **Constraints:** The component strictly operates on the `TruckState` domain object memory reference. It performs zero allocations and zero storage API I/O operations.

## 7. Component Interactions
- **Default State Creator:** Seeds the initial metadata constraints.
- **Mathematical Aggregators:** Rely on the metadata manager to guarantee they are mutating a state belonging to a valid time window.
- **CRUD Engine:** Persists the final state metadata to RocksDB (where the metadata forms the key basis `{truck_id}:{window_start}`).
- **Cleanup Manager (Future Phase):** Actively queries `window_end` and `last_updated` to determine if a state has expired and should be permanently removed via `delete_state()`.

## 8. Future Extensibility
Metadata naturally acts as the foundation for broader stream features:
- **Watermarking:** Associating stream progression markers directly onto the `TruckState`.
- **Schema Versions:** Identifying payload compatibility for forward/backward schema migration without disrupting the raw numeric aggregations.
- **Processing Time vs Event Time Tracking:** Evolving `last_updated` to distinguish between when an event *occurred* on the physical truck versus when the engine *processed* it.
