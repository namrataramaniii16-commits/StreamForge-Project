# TruckState Domain Model Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This document defines the **TruckState Domain Model**, the central entity representing the in-memory and persistent aggregation state of a single truck within a specific processing window. The model serves as the Single Source of Truth for all storage, serialization, and aggregation logic while remaining completely independent of RocksDB, Kafka, or business transport mechanisms.

## 2. Domain Architecture & Responsibilities
The `TruckState` model isolates domain properties from persistence logic. It is strictly responsible for:
- Maintaining truck identity and processing metadata.
- Holding running aggregation metrics.
- Enforcing structural and logical invariants.
- Acting as the standard data transfer object (DTO) for the CRUD Engine and Serializers.

It is **not responsible for** writing to RocksDB, performing JSON serialization, or calculating streaming window boundaries.

## 3. Core Fields & Relationships

| Field | Type | Description |
|---|---|---|
| `truck_id` | String | Unique, immutable identifier for the truck (e.g., `TRUCK-101`). Used heavily in RocksDB key generation. |
| `window_start` | DateTime | The starting boundary of the aggregation window. |
| `window_end` | DateTime | The ending boundary of the aggregation window. |
| `sum_temperature` | Float | The running sum of all temperature readings in the window. |
| `count` | Integer | The total number of events processed for this truck in this window. |
| `average_temperature`| Float | The computed average temperature. |
| `last_updated` | DateTime | The timestamp of the last successful state modification. |

## 4. Domain Invariants & Validation Rules
A `TruckState` instance is only valid if all of the following invariants hold true:
- **Identity Invariant:** `truck_id` must not be empty and is immutable.
- **Window Invariant:** `window_start` and `window_end` must exist, and `window_start < window_end`.
- **Metric Invariants:** 
  - `count >= 0`
  - `sum_temperature >= 0`
  - `average_temperature >= 0`
  - If `count == 0`, `average_temperature` must be exactly `0`.
  - If `count > 0`, `average_temperature` must equal `sum_temperature / count`.
- **Metadata Invariant:** `last_updated` must be a valid, present timestamp representing the latest update.

## 5. Object Lifecycle
```text
Create Empty TruckState → Receive Update (via Aggregation Engine) → Re-calculate Metrics → Update last_updated → Validate Invariants → Serialize → Persist (RocksDB)
```
Upon application restart, the lifecycle begins at recovery:
```text
Recover Bytes (RocksDB) → Deserialize → Validate Invariants → Return Validated TruckState
```

## 6. Component Interactions
The domain model interfaces with adjacent layers without depending on them:
- **Aggregation Engine:** Modifies `sum_temperature` and `count`, updating the model.
- **Serializer / Deserializer:** Translates the valid domain model into/out of JSON bytes.
- **CRUD Engine:** Uses the model as an input/output payload but never alters it internally.

## 7. Future Extensibility & Design Constraints
To support schema evolution, the model is designed such that future properties (e.g., `minimum_temperature`, `maximum_temperature`, `location`, `schema_version`) can be introduced as optional extensions without breaking existing invariants or backward compatibility.

**Constraint:** The model must be instantiable and testable in pure Python environments without requiring `python-rocksdb` or external network connections.
