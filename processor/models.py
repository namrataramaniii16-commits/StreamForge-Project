"""
Data models used by the StreamForge Processor.

This file defines the structure of incoming truck telemetry messages.
"""

import faust


class TruckTelemetry(faust.Record):
    truck_id: str
    temperature: float
    timestamp: str