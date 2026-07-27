"""
Kafka topic definitions for the StreamForge processor.
"""

from config import INPUT_TOPIC
from models import TruckTelemetry
from faust_app import app

# Create a reference to the Kafka topic
truck_topic = app.topic(
    INPUT_TOPIC,
    value_type=TruckTelemetry
)