import json
import os
import time


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

RUNTIME_FILE = os.path.join(
    BASE_DIR,
    "runtime_state.json",
)


def default_state():

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
        "status": "starting",
        "kafka_connected": False,
        "simulation_mode": True,
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


def get_runtime():

    if not os.path.exists(RUNTIME_FILE):
        return default_state()

    try:

        with open(
            RUNTIME_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except Exception:

        return default_state()