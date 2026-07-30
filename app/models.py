from pydantic import BaseModel

class Worker(BaseModel):
    id: int
    status: str

class Partition(BaseModel):
    partition: int
    worker: str

class Metrics(BaseModel):
    events_per_second: int
    lag: str
    uptime: str