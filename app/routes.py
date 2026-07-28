from fastapi import APIRouter
from app.data import workers, partitions, metrics, topology, logs

router = APIRouter()

@router.get("/workers")
def get_workers():
    return workers

@router.get("/partitions")
def get_partitions():
    return partitions

@router.get("/metrics")
def get_metrics():
    return metrics

@router.get("/topology")
def get_topology():
    return topology

@router.get("/health")
def health():
    return {
        "status": "Healthy"
    }

@router.get("/logs")
def get_logs():
    return logs