from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.logging import get_logger

class HealthState(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

@dataclass
class HealthReport:
    status: HealthState
    timestamp: str
    database_open: bool
    initialization_status: str
    status_message: str

class HealthCheckSystem:
    """
    Centralized component for verifying the RocksDB storage layer is operational.
    """
    def __init__(self, db_manager: DatabaseManager) -> None:
        self._db_manager = db_manager
        self._logger = get_logger(self.__class__.__name__)

    def check_health(self) -> HealthReport:
        """
        Performs a complete storage health evaluation.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if not self._db_manager:
            self._logger.error("Storage health check failed: DatabaseManager is missing.")
            return HealthReport(
                status=HealthState.UNHEALTHY,
                timestamp=timestamp,
                database_open=False,
                initialization_status="FAILED",
                status_message="DatabaseManager is not provided or initialized."
            )

        is_open = self._db_manager.is_open()
        
        if not is_open:
            self._logger.error("Storage health check failed: Database is closed.")
            return HealthReport(
                status=HealthState.UNHEALTHY,
                timestamp=timestamp,
                database_open=False,
                initialization_status="INITIALIZED",
                status_message="Database is initialized but currently closed."
            )
            
        try:
            # Verify if database is accessible by getting the db handle
            db = self._db_manager.get_database()
            # If future metrics/stats are supported, we could poll them here to detect DEGRADED state.
            
            # Since no exceptions were raised, we consider it healthy.
            # Intentionally using debug log here so we don't spam the standard output on aggressive polling.
            # Alternatively, if we only log on state changes, we could use INFO. The user spec says INFO.
            self._logger.info("Storage health verified successfully.")
            return HealthReport(
                status=HealthState.HEALTHY,
                timestamp=timestamp,
                database_open=True,
                initialization_status="READY",
                status_message="Database is fully operational and accessible."
            )
        except Exception as e:
            self._logger.error(f"Storage health check failed during accessibility check: {e}")
            return HealthReport(
                status=HealthState.UNHEALTHY,
                timestamp=timestamp,
                database_open=True,
                initialization_status="ERROR",
                status_message=f"Database access failure: {str(e)}"
            )

    def is_ready(self) -> bool:
        """
        Determines whether the storage layer is ready to accept requests.
        """
        return self.check_health().status == HealthState.HEALTHY

    def get_status(self) -> str:
        """
        Returns the current storage status as a string (HEALTHY, DEGRADED, UNHEALTHY).
        """
        return self.check_health().status.value
