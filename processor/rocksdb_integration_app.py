import sys
import os
import json
import time
import logging
from datetime import datetime

from kafka import KafkaConsumer, KafkaProducer

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from processor.config import (
    KAFKA_BROKER,
    INPUT_TOPIC,
    CHANGELOG_TOPIC,
    WINDOW_SIZE_MS,
)

from processor.runtime import (
    start_metrics_server,
    read_state,
    write_state,
    add_log,
    update_event_metrics,
)

from rocksdb_state.rocksdb_state.database.database_manager import (
    DatabaseManager
)

from rocksdb_state.rocksdb_state.storage.crud import (
    CRUDEngine
)

from rocksdb_state.rocksdb_state.aggregation.aggregator import (
    AggregationUpdateAPI
)

from rocksdb_state.rocksdb_state.recovery.recovery_manager import (
    RecoveryManager
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("StreamForgeProcessor")


def parse_timestamp(timestamp):
    """
    Convert ISO timestamp to milliseconds.
    """

    if isinstance(timestamp, (int, float)):
        return int(timestamp)

    value = timestamp.replace("Z", "+00:00")

    dt = datetime.fromisoformat(value)

    return int(dt.timestamp() * 1000)


def get_window_boundaries(
    timestamp_ms,
    window_size_ms=WINDOW_SIZE_MS,
):
    """
    5-minute event-time window.
    """

    window_start = (
        timestamp_ms // window_size_ms
    ) * window_size_ms

    window_end = (
        window_start + window_size_ms
    )

    return window_start, window_end


def append_changelog(producer, state):
    """
    Backup state to Kafka changelog topic.
    """

    payload = {
        "truck_id": state.truck_id,
        "window_start": state.window_start,
        "window_end": state.window_end,
        "sum_temperature": state.sum_temperature,
        "count": state.count,
        "average_temperature": state.average_temperature,
        "last_updated": state.last_updated,
    }

    producer.send(
        CHANGELOG_TOPIC,
        key=state.truck_id.encode("utf-8"),
        value=json.dumps(payload).encode("utf-8"),
    )

    producer.flush()


def main():
    logger.info("=" * 70)
    logger.info("STREAMFORGE PROCESSOR STARTING")
    logger.info("=" * 70)

    # Prometheus
    start_metrics_server(8001)

    # RocksDB
    db = DatabaseManager(
        db_path="./streamforge_data"
    )

    db.open()

    crud = CRUDEngine(db)

    # Recovery
    recovery_manager = RecoveryManager(db)

    summary = recovery_manager.execute_recovery()

    if summary["status"] == "FATAL":
        logger.critical(
            "RocksDB recovery failed."
        )
        sys.exit(1)

    active_registry = (
        recovery_manager.active_registry
    )

    # Kafka Consumer
    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="streamforge-workers",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda x:
            json.loads(x.decode("utf-8")),
    )

    # Kafka changelog producer
    changelog_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER
    )

    logger.info(
        "Kafka connected successfully."
    )

    logger.info(
        "5-minute event-time window enabled."
    )

    add_log(
        "StreamForge processor started"
    )

    consumed = 0
    processed = 0
    filtered = 0

    started = time.time()

    for message in consumer:

        consumed += 1

        try:
            event = message.value

            truck_id = event["truck_id"]

            temperature = float(
                event["temperature"]
            )

            timestamp_ms = parse_timestamp(
                event["timestamp"]
            )

            # ------------------------------------------------
            # FILTER
            # Requirement: Temperature > 0
            # ------------------------------------------------

            if temperature <= 0:

                filtered += 1

                update_event_metrics(
                    consumed=consumed,
                    processed=processed,
                    filtered=filtered,
                )

                continue

            # ------------------------------------------------
            # MAP
            # ------------------------------------------------

            event["temperature"] = temperature
            event["timestamp_ms"] = timestamp_ms

            # ------------------------------------------------
            # EVENT-TIME WINDOW
            # ------------------------------------------------

            window_start, window_end = (
                get_window_boundaries(
                    timestamp_ms
                )
            )

            event["window_start"] = (
                window_start
            )

            event["window_end"] = (
                window_end
            )

            registry_key = (
                f"{truck_id}:"
                f"{window_start}:"
                f"{window_end}"
            )

            current_state = (
                active_registry.get(
                    registry_key
                )
            )

            # ------------------------------------------------
            # AGGREGATION
            # ------------------------------------------------

            new_state = (
                AggregationUpdateAPI.process_event(
                    event,
                    current_state
                )
            )

            active_registry[
                registry_key
            ] = new_state

            # ------------------------------------------------
            # ROCKSDB
            # ------------------------------------------------

            crud.put_state(
                new_state
            )

            # ------------------------------------------------
            # KAFKA CHANGELOG
            # ------------------------------------------------

            append_changelog(
                changelog_producer,
                new_state
            )

            processed += 1

            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            elapsed = time.time() - started

            throughput = (
                processed / elapsed
                if elapsed > 0
                else 0
            )

            event_lag = max(
                0,
                time.time()
                - (timestamp_ms / 1000)
            )

            update_event_metrics(
                consumed=consumed,
                processed=processed,
                filtered=filtered,
                throughput=throughput,
                lag=event_lag,
            )

            # ------------------------------------------------
            # TRUCK STATE FOR DASHBOARD
            # ------------------------------------------------

            state = read_state()

            state["trucks"][truck_id] = {
                "truck_id": truck_id,
                "temperature": temperature,
                "average_temperature":
                    new_state.average_temperature,
                "window_start":
                    window_start,
                "window_end":
                    window_end,
                "count":
                    new_state.count,
                "last_event":
                    timestamp_ms,
                "status": "Healthy",
            }

            write_state(state)

            if processed % 1000 == 0:

                logger.info(
                    "Processed=%s | "
                    "Throughput=%.2f/sec | "
                    "Truck=%s | "
                    "Average=%.2f",
                    processed,
                    throughput,
                    truck_id,
                    new_state.average_temperature,
                )

        except Exception as exc:

            logger.exception(
                "Processing error: %s",
                exc
            )

            add_log(
                f"Processing error: {exc}"
            )


if __name__ == "__main__":
    main()