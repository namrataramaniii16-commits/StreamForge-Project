# RocksDB Key Format Specification

## 1. Objective and Design Principles

This specification defines a standardized, collision-free key format for storing and retrieving `TruckState` objects in the RocksDB State Storage module. Since RocksDB is a key-value store with no tables or schemas, a robust key design is paramount. 

The key format is designed to be:
- **Unique:** Every state combination maps to exactly one key.
- **Human-readable:** Easily interpretable for debugging and operations.
- **Deterministic & Stable:** Identical inputs always yield the identical key.
- **Predictable:** Follows a consistent structural pattern.
- **Easy to Parse:** Simple string splitting can extract components.
- **Future Extensible:** Supports new data types and entities without conflicts.

## 2. Key Format Specification

The standardized key format for the RocksDB storage follows this structure:

```text
truck:{truck_id}:window:{window_start}
```

**Example Keys:**
```text
truck:TRUCK-101:window:2026-07-23T10:00:00Z
truck:TRUCK-102:window:2026-07-23T10:05:00Z
truck:TRUCK-103:window:2026-07-23T11:15:00Z
```

## 3. Key Components Breakdown

Every key consists of the following components separated by colons (`:`):

1. **Namespace Prefix (`truck`)**: 
   - Defines the domain entity being stored.
   - Provides an isolated namespace to avoid collisions with other potential future entities (like drivers or sensors).
2. **Truck Identifier (`{truck_id}`)**:
   - The unique business identifier of the truck (e.g., `TRUCK-101`).
3. **Window Prefix (`window`)**:
   - Acts as a structural separator indicating that the following value represents a time window.
4. **Window Identifier (`{window_start}`)**:
   - The ISO 8601 timestamp representing the *start* of the aggregation window.
   - **Why Window Start?** The start time of a window is deterministic and fixed from the moment the window opens, ensuring a stable, immutable identifier for the aggregation timeframe.

## 4. Uniqueness Rules

Each combination of `Truck ID` and `Window Start` MUST correspond to exactly one record in RocksDB.

For example, `TRUCK-101` and the `10:00` window must yield a single entry. If an event for the same truck and window arrives later, it must result in the exact same key, facilitating an update (read-modify-write) rather than creating a duplicate record.

## 5. Key Generation and Parsing Workflow

To ensure consistency, higher-level components must use dedicated utility functions rather than building or parsing keys manually. 

### Generation Workflow
```text
TruckState Object
       │
       ▼
Extract `truck_id` and `window_start`
       │
       ▼
Concatenate using `truck:{truck_id}:window:{window_start}`
       │
       ▼
Store in RocksDB
```

### Parsing Workflow
```text
RocksDB Key
       │
       ▼
Split string by `:` delimiter
       │
       ▼
Extract index [1] (Truck ID) and index [3] (Window Start)
       │
       ▼
Return Parsed Components
```

*(Note: The implementation should expose utilities like `generate_key()`, `parse_key()`, and `validate_key()`.)*

## 6. Validation Requirements

A valid RocksDB key for truck state must satisfy all of the following rules:
- Must begin exactly with the `truck:` prefix.
- Must contain a non-empty `{truck_id}`.
- Must contain the literal `:window:` separator.
- Must end with a non-empty, valid `{window_start}` timestamp.
- Must have exactly four structural segments when split by `:`.

**Examples of Invalid Keys:**
- `truck::` (Missing truck ID and window information)
- `truck:window` (Missing identifiers)
- `truck:TRUCK-101` (Missing window context)
- `window:TRUCK-101` (Incorrect namespace prefix)
- `truck:TRUCK-101:window` (Missing window timestamp)

## 7. Future Extensibility

By utilizing a namespace prefix (`truck:`), this storage layout is naturally extensible. If StreamForge expands to track different entities in the future, they can be stored in the same RocksDB instance without any risk of collision.

**Future Examples:**
```text
driver:DRIVER-22:shift:2026-07-23
sensor:SENSOR-18:calibration:2026-07-23T10:00
fleet:FLEET-A:metrics:daily
```
This structured approach ensures that the state storage layer can grow seamlessly alongside the business requirements.
