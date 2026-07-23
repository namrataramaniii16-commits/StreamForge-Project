"""
Faust agents for processing Kafka streams.
"""

from faust_app import app
from topics import truck_topic
from rocksdb_state.rocksdb_state.aggregation.aggregator import AggregationUpdateAPI
import time
from datetime import datetime

def get_window_boundaries(timestamp_str: str, window_size_ms: int = 10000):
    """Calculates window start and end (e.g., 10-second windows)."""
    try:
        # Python 3.7+ support for ISO strings. Replace Z with +00:00 for strict compat.
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        timestamp_ms = int(dt.timestamp() * 1000)
    except Exception:
        timestamp_ms = int(time.time() * 1000)
    
    window_start = (timestamp_ms // window_size_ms) * window_size_ms
    window_end = window_start + window_size_ms
    return window_start, window_end

@app.agent(truck_topic)
async def process_truck_data(stream):
    """
    Consume truck telemetry messages.
    """
    async for truck in stream:
        event = {
            "truck_id": truck.truck_id,
            "temperature": truck.temperature,
        }
        
        w_start, w_end = get_window_boundaries(truck.timestamp)
        event["window_start"] = w_start
        event["window_end"] = w_end
        
        registry_key = f"{truck.truck_id}:{w_start}:{w_end}"
        
        # Load from RocksDB Registry
        current_state = app.rocksdb_registry.get(registry_key)
        
        try:
            # Aggregate
            new_state = AggregationUpdateAPI.process_event(event, current_state)
            
            # Persist memory and disk
            app.rocksdb_registry[registry_key] = new_state
            app.rocksdb_crud.put_state(new_state)
            
            print(f"Aggregated {truck.truck_id} | Window: {w_start} | Sum: {new_state.sum_temperature:.2f} | Count: {new_state.count} | Avg: {new_state.average_temperature:.2f}")
        except Exception as e:
            print(f"Aggregation Failed for {truck.truck_id}: {e}")