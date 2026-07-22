"""
Faust agents for processing Kafka streams.
"""

from faust_app import app
from topics import truck_topic


@app.agent(truck_topic)
async def process_truck_data(stream):
    """
    Consume truck telemetry messages.
    """

    async for truck in stream:
        print(truck)