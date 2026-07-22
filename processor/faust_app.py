"""
Main entry point for the StreamForge Stream Processing module.
"""

import faust

from config import APP_NAME, KAFKA_BROKER

# Create the Faust application
app = faust.App(
    APP_NAME,
    broker=f"kafka://{KAFKA_BROKER}"
)
# Register all Faust agents
import agents
print("Faust application initialized successfully.")