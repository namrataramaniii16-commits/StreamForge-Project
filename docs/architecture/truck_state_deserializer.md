# TruckState Deserializer Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the architecture, workflow, and validation rules for the **TruckState Deserializer**. This component serves as the reconstruction boundary, translating raw, UTF-8 encoded JSON bytes stored in RocksDB back into a strictly validated `TruckState` domain object.

## 2. Architecture & Responsibilities
The Deserializer restricts its scope purely to data extraction, mapping, and revalidation.
- **Responsibilities:** Decoding UTF-8 byte arrays, parsing JSON strings, mapping extracted fields back into their corresponding Python primitives (including `datetime` parsing), creating the `TruckState` object, and validating domain invariants.
- **Out of Scope:** Pulling bytes from RocksDB directly, maintaining database state, recalculating averages (unless enforcing invariants), or invoking business logic.

```text
RocksDB → CRUD Engine → (UTF-8 Bytes) → Deserializer → Validated TruckState → Aggregation Engine
```

## 3. Deserialization Workflow
1. **UTF-8 Decode:** The raw `byte[]` payload is decoded using strict UTF-8 semantics.
2. **JSON Parsing:** The string is parsed into a Python dictionary.
3. **Field Extraction & Type Coercion:** Values are extracted and safely coerced to their target types. ISO-8601 strings are mapped back to `datetime` objects.
4. **Instantiation:** The `TruckState` domain object is constructed using the mapped fields.
5. **Revalidation:** The object is checked against all invariants (e.g., `window_start < window_end`, non-negative totals).
6. **Return:** Only upon successful validation is the `TruckState` yielded back to the application.

## 4. Field Reconstruction Rules
Each serialized property corresponds exactly to the domain model:

| Serialized JSON Key | Target Domain Type | Reconstruction Behavior |
|---|---|---|
| `truck_id` | String | Extracted as exact literal string. |
| `window_start` | DateTime | Parsed from ISO-8601. Must retain UTC timezone. |
| `window_end` | DateTime | Parsed from ISO-8601. Must retain UTC timezone. |
| `sum_temperature` | Float | Cast/extracted as floating-point. |
| `count` | Integer | Cast/extracted as integer. |
| `average_temperature` | Float | Cast/extracted as floating-point. |
| `last_updated` | DateTime | Parsed from ISO-8601. Must retain UTC timezone. |

## 5. Validation and Determinism Guarantee
Because `Serialize(State)` deterministically generates JSON bytes, `Deserialize(Serialize(State))` must strictly equal the original `State`. 
If any extracted fields violate invariants (e.g., if a manual database edit made `count < 0`), the Deserializer fails the object during revalidation to prevent poisoned data from circulating in the processing pipeline.

## 6. Error Handling
The deserializer never fails silently. A `DeserializationError` is thrown on:
- Malformed/Truncated UTF-8 bytes.
- Invalid JSON syntax.
- Missing required fields (e.g., no `truck_id` present).
- Type mismatch errors (e.g., `count` is a string instead of an int).
- Post-construction invariant failure.

## 7. Schema Compatibility & Forward Evolution
To support future module capabilities without breaking older data:
- The deserializer **ignores unknown fields**. If the JSON payload contains `"min_temperature": 10.0` but the current `TruckState` domain model does not yet expect it, the deserializer safely discards it instead of throwing an error.
- Required fields are strictly enforced; optional fields (if added later) fall back to defaults.

## 8. Recovery Workflow Integration
During an application crash and restart sequence, the Recovery Manager streams thousands of byte arrays from RocksDB. The Deserializer's efficient execution prevents startup bottlenecks. If a single byte array is corrupt and throws a `DeserializationError`, the Recovery Manager handles the policy (e.g., skip and log, or halt), keeping the Deserializer purely stateless.
