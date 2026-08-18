import json
import os
import threading
import time
from prometheus_client import (
    Counter,
    Gauge,
    start_http_server,
)

RUNTIME_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "runtime_state.json",
    )
)

_lock = threading.Lock()

events_consumed = Counter(
    "streamforge_events_consumed_total",
    "Total events consumed from Kafka",
)

events_processed = Counter(
    "streamforge_events_processed_total",
    "Total events successfully processed",
)

events_filtered = Counter(
    "streamforge_events_filtered_total",
    "Events filtered because temperature was <= 0",
)

processing_lag = Gauge(
    "streamforge_processing_lag_seconds",
    "Processing lag in seconds",
)

active_workers = Gauge(
    "streamforge_active_workers",
    "Number of active workers",
)

events_per_second = Gauge(
    "streamforge_throughput_events_per_sec",
    "Current processing throughput",
)


def start_metrics_server(port=8001):
    start_http_server(port)


def _default_state():
    workers = []

    for i in range(1, 21):
        workers.append({
            "id": i,
            "worker_id": f"Worker-{i}",
            "status": "Running",
            "partition": i - 1,
            "events_processed": 0,
            "events_per_sec": 0,
            "processing_lag_seconds": 0,
        })

    return {
        "status": "running",
        "kafka_connected": True,
        "simulation_mode": False,
        "events_consumed": 0,
        "events_processed": 0,
        "events_filtered": 0,
        "events_per_second": 0,
        "processing_lag_seconds": 0,
        "active_workers": 20,
        "workers": workers,
        "partitions": [
            {
                "partition": i,
                "worker": f"Worker-{i + 1}",
                "status": "Active",
            }
            for i in range(20)
        ],
        "trucks": {},
        "logs": [],
        "last_updated": time.time(),
    }


def read_state():
    with _lock:
        if not os.path.exists(RUNTIME_FILE):
            return _default_state()

        try:
            with open(RUNTIME_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return _default_state()


def write_state(state):
    with _lock:
        state["last_updated"] = time.time()

        temp_file = RUNTIME_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        os.replace(temp_file, RUNTIME_FILE)


def add_log(message):
    state = read_state()

    state["logs"].insert(
        0,
        {
            "timestamp": time.time(),
            "message": message,
        },
    )

    state["logs"] = state["logs"][:100]

    write_state(state)


def update_event_metrics(
    consumed=None,
    processed=None,
    filtered=None,
    throughput=None,
    lag=None,
):
    state = read_state()

    if consumed is not None:
        state["events_consumed"] = consumed

    if processed is not None:
        state["events_processed"] = processed

    if filtered is not None:
        state["events_filtered"] = filtered

    if throughput is not None:
        state["events_per_second"] = throughput

    if lag is not None:
        state["processing_lag_seconds"] = lag

    write_state(state)

    active_workers.set(state["active_workers"])

    if throughput is not None:
        events_per_second.set(throughput)

    if lag is not None:
        processing_lag.set(lag)