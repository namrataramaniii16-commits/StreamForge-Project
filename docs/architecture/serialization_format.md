# RocksDB Serialization Strategy: JSON

## 1. Objective and Design Principles

This document defines the standardized serialization strategy for converting `TruckState` objects into byte sequences for storage in RocksDB, and for reconstructing those objects upon retrieval. Since RocksDB stores only raw key-value byte pairs, a robust serialization layer is required to bridge the gap between Python objects and persistent storage.

The serialization format adheres to the following principles:
- **Human-readable:** Easy to inspect in logs or via command-line tools.
- **Deterministic:** The same state always produces the same serialized output.
- **Lightweight:** Low overhead for storage and parsing.
- **Platform/Language-independent:** Accessible beyond Python if necessary.
- **Version-friendly:** Capable of evolving without breaking backward compatibility.
- **Extensible:** Flexible enough to support new fields or structures.

## 2. Why JSON?

After evaluating common serialization formats, JSON was selected because it offers the optimal balance between readability, portability, and simplicity for the StreamForge project requirements.

### Advantages
- Human-readable and extremely easy to debug.
- Supported universally across almost every programming language.
- Requires no additional dependencies in Python (built-in `json` module).
- Easy inspection using standard logging and troubleshooting tools.
- Perfectly suited for the small to medium-sized state objects represented by `TruckState`.

### Alternative Formats Considered

| Format | Advantages | Disadvantages | Decision |
| :--- | :--- | :--- | :--- |
| **JSON** | Readable, portable, easy debugging | Slightly larger size compared to binary | ✅ **Selected** |
| **Pickle** | Fast for Python | Python-specific, potential security concerns | ❌ Rejected |
| **MessagePack** | Compact, fast | Harder to inspect manually without tools | ❌ Future Option |
| **Protocol Buffers**| Very efficient | Complex schema management and tooling overhead | ❌ Not required |
| **Avro** | Good for distributed systems | Higher complexity, requires schema registry | ❌ Overkill |

## 3. Serialization and Deserialization Workflows

The process of moving data between the application and RocksDB follows a strict transformation pipeline:

### Data Transformation Pipeline
```text
TruckState Object ↔ Dictionary ↔ JSON String ↔ UTF-8 Bytes ↔ RocksDB
```

### Serialization Workflow
When persisting state to RocksDB:
1. **TruckState Object:** Start with the Python object representing the state.
2. **Dictionary Representation:** Convert the object properties into a standard Python dictionary.
3. **JSON String:** Serialize the dictionary into a JSON formatted string.
4. **UTF-8 Encoding:** Encode the string into a sequence of UTF-8 bytes.
5. **RocksDB Storage:** Persist the byte sequence into the database using the generated key.

### Deserialization Workflow
When retrieving state from RocksDB:
1. **RocksDB Bytes:** Retrieve the raw byte sequence for a specific key.
2. **UTF-8 Decode:** Decode the bytes into a UTF-8 string.
3. **JSON Parse:** Parse the JSON string into a Python dictionary.
4. **Validation:** Ensure required fields are present and correctly typed.
5. **TruckState Object:** Reconstruct and return the original `TruckState` object.

## 4. Example Transformation

### Original JSON (Logical)
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

### Compact Serialized JSON String
```json
{"truck_id":"TRUCK-101","window_start":"2026-07-23T10:00:00Z","window_end":"2026-07-23T10:05:00Z","sum_temperature":175.6,"count":5,"average_temperature":35.12,"last_updated":"2026-07-23T10:03:25Z"}
```

### RocksDB Stored Byte Representation
```text
b'{"truck_id":"TRUCK-101","window_start":"2026-07-23T10:00:00Z","window_end":"2026-07-23T10:05:00Z","sum_temperature":175.6,"count":5,"average_temperature":35.12,"last_updated":"2026-07-23T10:03:25Z"}'
```

## 5. Component Responsibilities

To maintain clean architecture, the serialization logic is abstracted into dedicated components.

### Serializer Responsibilities
- Accept a valid `TruckState` object.
- Convert it into a dictionary representation.
- Serialize the dictionary into JSON string format.
- Encode the JSON string into UTF-8 bytes.
- Ensure deterministic output (e.g., sorting keys or ensuring stable float representations, if strictly required).
- Raise meaningful errors for invalid or un-serializable objects.

### Deserializer Responsibilities
- Accept a UTF-8 encoded byte sequence from RocksDB.
- Decode the bytes back into a JSON string.
- Parse the JSON into a dictionary.
- Validate that all required fields are present and valid.
- Reconstruct the `TruckState` object.
- Raise meaningful errors for corrupted data or invalid schemas.

## 6. Error Handling Strategy

The serialization layer must act as a strict boundary, preventing corrupted data from entering the storage or the application. It should detect and report the following error scenarios clearly:

- **Invalid Object Type:** Attempting to serialize an unsupported object.
- **Missing Required Fields:** Dictionary lacks expected keys during deserialization.
- **Unsupported Data Types:** Attempting to serialize elements like custom classes, sets, or complex dates without converters.
- **Invalid JSON:** The string payload is malformed.
- **Corrupted Byte Sequence:** Byte array cannot be read or processed.
- **UTF-8 Decoding Failures:** The stored bytes are not valid UTF-8.

Errors should be descriptive and propagated up, enabling higher-level components (like the stream processor) to react appropriately, log failures, or trigger dead-letter queues.

## 7. Versioning Strategy

To future-proof the storage layer and support seamless schema evolution, serialized data should be designed with backward compatibility in mind.

Future enhancements should introduce a schema version field:
```json
{
    "schema_version": 1,
    "truck_id": "TRUCK-101",
    "...": "..."
}
```
This enables future versions of the application to conditionally apply migration logic or safely interpret older state formats without breaking the deserialization pipeline.
