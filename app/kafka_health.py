from kafka import KafkaAdminClient
from kafka.errors import KafkaError


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"


def check_kafka_connection() -> bool:
    client = None

    try:
        client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=3000,
            client_id="streamforge-fastapi-health",
        )

        return True

    except KafkaError:
        return False

    except Exception:
        return False

    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass