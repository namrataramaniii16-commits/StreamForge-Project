import os
from dataclasses import dataclass, field

class ConfigurationError(Exception):
    """Exception raised for errors in the configuration validation."""
    pass

@dataclass(frozen=True)
class DatabaseConfig:
    database_path: str = "./data"
    database_name: str = "streamforge_rocksdb"
    create_if_missing: bool = True

    def validate(self) -> None:
        if not self.database_path:
            raise ConfigurationError("database_path must not be empty")
        try:
            os.makedirs(self.database_path, exist_ok=True)
            if not os.access(self.database_path, os.W_OK):
                raise ConfigurationError(f"database_path '{self.database_path}' is not writable")
        except Exception as e:
            raise ConfigurationError(f"Cannot access or create database_path '{self.database_path}': {e}")

@dataclass(frozen=True)
class LoggingConfig:
    log_level: str = "INFO"
    log_directory: str = "./logs"
    enable_console_logging: bool = True
    enable_file_logging: bool = True

    def validate(self) -> None:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ConfigurationError(f"log_level must be one of {valid_levels}")

@dataclass(frozen=True)
class ApplicationConfig:
    application_name: str = "StreamForge RocksDB State Storage"
    application_version: str = "0.1.0"
    debug: bool = False

@dataclass(frozen=True)
class RecoveryConfig:
    enable_recovery: bool = True
    validate_recovered_state: bool = True
    skip_corrupted_records: bool = True

@dataclass(frozen=True)
class CleanupConfig:
    cleanup_enabled: bool = True
    cleanup_interval: int = 3600
    window_retention: int = 86400

    def validate(self) -> None:
        if self.cleanup_interval <= 0:
            raise ConfigurationError("cleanup_interval must be greater than zero")
        if self.window_retention <= 0:
            raise ConfigurationError("window_retention must be greater than zero")
        if self.window_retention <= self.cleanup_interval:
            raise ConfigurationError("window_retention must be greater than cleanup_interval")

@dataclass(frozen=True)
class Config:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    application: ApplicationConfig = field(default_factory=ApplicationConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    cleanup: CleanupConfig = field(default_factory=CleanupConfig)

    def validate(self) -> None:
        self.database.validate()
        self.logging.validate()
        self.cleanup.validate()

def load_config() -> Config:
    """
    Loads and validates the configuration.
    In the future, this can be extended to load from environment variables, YAML, or TOML.
    """
    config = Config()
    config.validate()
    return config
