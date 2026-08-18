
from fastapi import APIRouter
from app.runtime import get_runtime
from app.kafka_health import check_kafka_connection

router = APIRouter(
    prefix="/api"
)


@router.get("/health")
def health():

    data = get_runtime()

    kafka_connected = check_kafka_connection()

    return {
        "status": "running" if kafka_connected else "degraded",
        "kafka_connected": kafka_connected,
        "simulation_mode": not kafka_connected,
        "workers": {
            "healthy": sum(
                1
                for worker in data["workers"]
                if worker["status"] == "Running"
            ),
            "total": len(data["workers"]),
        },
    }

@router.get("/workers")
def get_workers():

    return get_runtime()["workers"]


@router.get("/partitions")
def get_partitions():

    return get_runtime()["partitions"]


@router.get("/metrics")
def get_metrics():

    data = get_runtime()

    return {
        "events_consumed":
            data["events_consumed"],

        "events_processed":
            data["events_processed"],

        "events_filtered":
            data["events_filtered"],

        "events_per_second":
            round(
                data["events_per_second"],
                2,
            ),

        "processing_lag_seconds":
            round(
                data["processing_lag_seconds"],
                4,
            ),

        "active_workers":
            data["active_workers"],
    }


@router.get("/topology")
def get_topology():

    data = get_runtime()

    nodes = [
        {
            "id": "kafka",
            "type": "source",
            "label": "Kafka",
        }
    ]

    edges = []

    for worker in data["workers"]:

        worker_id = (
            worker["worker_id"]
        )

        nodes.append({
            "id": worker_id,
            "type": "worker",
            "label": worker_id,
            "status":
                worker["status"],
            "partition":
                worker["partition"],
        })

        edges.append({
            "source": "kafka",
            "target": worker_id,
        })

    nodes.append({
        "id": "aggregator",
        "type": "processor",
        "label": "5-Min Aggregator",
    })

    nodes.append({
        "id": "rocksdb",
        "type": "storage",
        "label": "RocksDB",
    })

    for worker in data["workers"]:

        edges.append({
            "source":
                worker["worker_id"],
            "target":
                "aggregator",
        })

    edges.append({
        "source": "aggregator",
        "target": "rocksdb",
    })

    return {
        "nodes": nodes,
        "edges": edges,
    }


@router.get("/trucks")
def get_trucks():

    data = get_runtime()

    return list(
        data["trucks"].values()
    )


@router.get("/logs")
def get_logs():

    return get_runtime()["logs"]


@router.get("/aggregations")
def get_aggregations():

    data = get_runtime()

    return list(
        data["trucks"].values()
    )
