# TruckState Serializer Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the architecture, workflow, and deterministic rules for the **TruckState Serializer**. The serializer serves as the translation boundary between the rich, in-memory `TruckState` domain model and the raw binary key-value storage engine (RocksDB). It ensures every valid `TruckState` object is consistently, deterministically, and safely encoded into UTF-8 JSON bytes.

## 2. Architecture & Responsibilities
The Serializer strictly limits its scope to conversion:
- **Responsibilities:** Validating the input domain object, converting fields to JSON primitives, enforcing deterministic key sorting/ordering, encoding the JSON to UTF-8 bytes, and returning the byte array.
- **Out of Scope:** Reading/writing to RocksDB, aggregating values, performing window time math, or managing database lifecycles.

```text
Aggregation Engine → TruckState → Serializer → (UTF-8 Bytes) → CRUD Engine → RocksDB
```

## 3. Serialization Workflow
The operation proceeds linearly:
1. **Validation:** Checks if the input is a non-null `TruckState` and invariants hold true.
2. **Extraction:** Pulls the domain fields (`truck_id`, `window_start`, etc.) from the object.
3. **Construction:** Builds an intermediate JSON map/dictionary.
4. **Serialization (Deterministic):** Dumps the JSON with strict key sorting to ensure deterministic outputs.
5. **Encoding:** Converts the serialized JSON string into UTF-8 bytes.
6. **Output:** Yields the `byte[]` payload for storage.

## 4. Field Mapping & Output Format
All elements map directly to JSON primitives. Timestamps strictly use ISO-8601 formatting.

| TruckState Field | Output JSON Type | Example |
|---|---|---|
| `truck_id` | String | `"TRUCK-101"` |
| `window_start` | String (ISO-8601) | `"2026-07-24T10:00:00Z"` |
| `window_end` | String (ISO-8601) | `"2026-07-24T10:05:00Z"` |
| `sum_temperature` | Float | `135.4` |
| `count` | Integer | `5` |
| `average_temperature` | Float | `27.08` |
| `last_updated` | String (ISO-8601) | `"2026-07-24T10:04:58Z"` |

*Example UTF-8 Encoded JSON:*
```json
{
  "average_temperature": 27.08,
  "count": 5,
  "last_updated": "2026-07-24T10:04:58Z",
  "sum_temperature": 135.4,
  "truck_id": "TRUCK-101",
  "window_end": "2026-07-24T10:05:00Z",
  "window_start": "2026-07-24T10:00:00Z"
}
```

## 5. Deterministic Guarantee
To ensure stable checksums, reproducible testing, and predictable storage footprint:
- Keys must be sorted alphabetically.
- No dynamic whitespace formatting is allowed (compact serialization).
- Floating-point representations must follow strict precision formatting.
Therefore, `Serialize(A)` will always yield the exact same byte sequence for the exact same state properties.

## 6. Error Handling
The serializer is fail-fast:
- **Null Input / Missing Fields:** Raises a `SerializationError` immediately; no bytes are emitted.
- **Type or Encoding Errors:** Caught and re-thrown cleanly to alert the calling component (CRUD Engine).
Errors must never be swallowed to prevent silent data loss or database corruption.

## 7. Performance & Constraints
- **Compactness:** Eliminates JSON pretty-printing.
- **Allocations:** Minimizes object copies by encoding directly from the mapped dictionary.
- **Constraints:** The serializer is purely stateless. It cannot communicate with the database or mutate the `TruckState`.

## 8. Future Extensibility
The JSON medium allows forward-compatible schema evolution. If future fields (e.g., `schema_version`, `sensor_status`) are added to the application, they simply become new key-value pairs in the JSON. The UTF-8 JSON approach ensures existing tooling, debugging logs, and future deserializers can elegantly process the expanded model.
