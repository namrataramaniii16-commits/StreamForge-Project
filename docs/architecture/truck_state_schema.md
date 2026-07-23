# TruckState Schema Specification

## 1. Overview and Design Principles

The **TruckState** schema represents the persistent aggregation state of a single truck within a specific processing window. This data model serves as the fundamental data structure stored in the RocksDB State Storage module and is utilized by all higher-level components of the StreamForge processing pipeline.

This schema is designed around the following core principles:
- **Simplicity:** Focuses purely on aggregation metrics rather than raw event histories.
- **Determinism:** Ensures consistent data structures and predictable serialization for storage.
- **Extensibility:** Accommodates future additions without breaking backward compatibility.
- **Independence:** Remains entirely decoupled from RocksDB internals, Kafka, and stream processing framework specifics.

## 2. Schema Definition

The TruckState object consists of the following required fields:

| Field | Type | Description |
| :--- | :--- | :--- |
| `truck_id` | String | Unique identifier of the truck |
| `window_start` | DateTime | Start time of the aggregation window |
| `window_end` | DateTime | End time of the aggregation window |
| `sum_temperature` | Float | Running sum of all received temperature values |
| `count` | Integer | Number of events processed in the window |
| `average_temperature` | Float | Current calculated average temperature |
| `last_updated` | DateTime | Timestamp of the most recent update |

## 3. Data Relationships

The data within the TruckState object is logically grouped as follows:

```text
TruckState
├── Truck Information
│      └── truck_id
├── Window Information
│      ├── window_start
│      └── window_end
├── Aggregation Metrics
│      ├── sum_temperature
│      ├── count
│      └── average_temperature
└── Metadata
       └── last_updated
```

## 4. Field Responsibilities

- **`truck_id`**: Identifies the specific truck whose state is being stored (e.g., `"TRUCK-101"`).
- **`window_start`**: Represents the beginning timestamp of the current aggregation window in ISO 8601 format (e.g., `"2026-07-23T10:00:00Z"`).
- **`window_end`**: Represents the ending timestamp of the current aggregation window in ISO 8601 format (e.g., `"2026-07-23T10:05:00Z"`).
- **`sum_temperature`**: Stores the cumulative sum of all temperature values processed within the current window.
- **`count`**: Tracks the total number of temperature events successfully processed within the window.
- **`average_temperature`**: The currently calculated average temperature, derived continuously from `sum_temperature / count`.
- **`last_updated`**: Stores the timestamp of the most recent state modification, allowing systems to understand data freshness.

## 5. Example State Object

```json
{
    "truck_id": "TRUCK-101",
    "window_start": "2026-07-23T10:00:00Z",
    "window_end": "2026-07-23T10:05:00Z",
    "sum_temperature": 175.6,
    "count": 5,
    "average_temperature": 35.12,
    "last_updated": "2026-07-23T10:03:25Z"
}
```

## 6. Validation Rules

To ensure data integrity, any component reading or writing the `TruckState` must enforce the following validation rules:

1. `truck_id` must be a non-empty string.
2. `window_start` must logically precede `window_end` (`window_start < window_end`).
3. `count` must always be an integer greater than or equal to zero.
4. `sum_temperature` must be greater than or equal to zero (assuming valid temperature scale).
5. `average_temperature` must exactly equal `sum_temperature / count` whenever `count > 0`. If `count == 0`, `average_temperature` may be `0.0` or null.
6. `last_updated` must always contain the latest modification timestamp.

## 7. Lifecycle

The lifecycle of a `TruckState` instance flows predictably as events arrive:

```text
Create Empty State
        │
        ▼
Receive Event
        │
        ▼
Update Aggregation Fields (sum, count)
        │
        ▼
Recalculate Average
        │
        ▼
Persist Updated State to RocksDB
        │
        ▼
Recover On Restart (if applicable)
```

## 8. Future Extensibility

The schema is designed to allow the introduction of additional fields in future versions without breaking compatibility for older consumers. To support this, serialization formats like JSON should be parsed such that unknown fields are ignored or preserved harmlessly.

Possible future additions may include:
- `min_temperature` / `max_temperature`: To track extreme values within the window.
- `event_count_by_type`: If multiple event types are introduced.
- `anomaly_detected`: A boolean flag triggered by specific business rules.
- `checksum`: For enhanced data integrity verification.
- `schema_version`: To explicitly manage versioning as the model evolves.
