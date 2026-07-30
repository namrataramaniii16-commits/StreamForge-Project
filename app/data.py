workers = [
    {"id": 1, "status": "Running"},
    {"id": 2, "status": "Running"},
    {"id": 3, "status": "Running"},
    {"id": 4, "status": "Stopped"}
]

partitions = [
    {"partition": 0, "worker": "Worker-1"},
    {"partition": 1, "worker": "Worker-2"},
    {"partition": 2, "worker": "Worker-3"},
    {"partition": 3, "worker": "Worker-4"}
]

metrics = {
    "events_per_second": 100000,
    "lag": "12 ms",
    "uptime": "5 hours"
}

topology = {
    "nodes": [
        "Kafka",
        "Worker-1",
        "Worker-2",
        "Worker-3",
        "Aggregator",
        "Output"
    ]
}

logs = [
    "Kafka Connected",
    "Worker-1 Started",
    "Worker-2 Processing",
    "Worker-4 Recovered"
]