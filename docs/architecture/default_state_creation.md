# Default State Creation Specification
**StreamForge Aggregation Engine**

## 1. Objective
This specification defines the **Default State Creation** component, which establishes the absolute baseline `TruckState` when a truck first reports an event within a new processing window. By formalizing this initialization, the engine guarantees that all subsequent mathematical aggregations begin from a strictly deterministic, perfectly zeroed origin.

## 2. Architecture & Responsibilities
The Default State Creator acts as a pure factory function within the Aggregation Engine.
- **Responsibilities:** Constructing a new `TruckState` domain object, mapping immutable identity fields from the triggering event, zeroing out all mutable metrics, assigning the creation timestamp, and yielding a validation-ready domain object.
- **Out of Scope:** Making CRUD calls to RocksDB, performing the actual `sum` or `average` aggregation logic, applying business rules, or serialization.

```text
Stream Processor → Aggregation Engine → Default State Creator → Initialized TruckState
```

## 3. Initialization Workflow
When a stream event arrives, the Aggregation Engine checks if state exists. If not, the Default State Creator is invoked:
1. **Determine Window:** The stream processor extracts `truck_id` and calculates `window_start`/`window_end` from the event timestamp.
2. **Construction:** A new `TruckState` object is instantiated.
3. **Default Assignment:** Deterministic baseline values are strictly applied.
4. **Validation:** The object is validated against domain invariants.
5. **Yield to Engine:** The initial state is returned to the Aggregation Engine so that the very first event can be logically processed exactly like any subsequent event (Read-Modify-Write).

## 4. Default Field Values
A newly initialized `TruckState` is completely empty of metrics, establishing a mathematically sound base for the upcoming first update.

| Field | Default Initialization Value |
|---|---|
| `truck_id` | Mapped from Event |
| `window_start` | Mapped from Event / Window Logic |
| `window_end` | Mapped from Event / Window Logic |
| `sum_temperature` | `0.0` |
| `count` | `0` |
| `average_temperature` | `0.0` |
| `last_updated` | Current UTC Timestamp (`DateTime`) |

## 5. Validation Rules & Lifecycle
Before being handed to the Aggregation Engine, the initialized object must pass the standard domain constraints:
- `truck_id` is present.
- `window_start < window_end`.
- `count == 0`, `sum_temperature == 0`, `average_temperature == 0`.
- `last_updated` is successfully bound.

**Lifecycle Integration:**
```text
Event Arrives → State Not Found → Create Default State → Validate → Pass to Aggregation Engine → Apply Event → Persist via CRUD Engine
```

## 6. Component Interactions
- **Aggregation Engine:** Calls the Default State Creator when `exists_state` or `get_state` yields no results.
- **CRUD Engine / RocksDB:** Has no interaction with this component. The creator operates purely in memory.

## 7. Future Extensibility & Design Constraints
- **Extensibility:** When new fields are introduced (e.g., `minimum_temperature`, `sensor_status`, `schema_version`), they will receive logical defaults (e.g., `Float.MAX_VALUE`, `UNKNOWN`, `1.0`) in this layer. The zero-state nature of the factory ensures backward-compatible behavior.
- **Constraints:** The component must remain purely deterministic, side-effect free, and completely uncoupled from storage I/O mechanisms.
