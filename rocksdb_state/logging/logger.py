import logging
import os
import sys
from typing import Optional
from rocksdb_state.config import LoggingConfig

# Singleton base logger instance tracker
_logger_configured: bool = False

def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a configured logger for a specific module.
    Ensure `configure_logging` has been called at application startup.
    If called before configuration, it returns a logger with basic default settings.
    """
    return logging.getLogger(f"streamforge.{module_name}")

def configure_logging(config: LoggingConfig) -> None:
    """
    Configures the centralized logging system based on the LoggingConfig.
    Must be called once during application initialization.
    """
    global _logger_configured
    
    # Target the base namespace for all our loggers
    base_logger = logging.getLogger("streamforge")
    
    # Set the logging level from config
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    base_logger.setLevel(level)
    
    # Clear existing handlers to prevent duplicates if configured multiple times
    if base_logger.hasHandlers():
        base_logger.handlers.clear()
        
    # Prevent propagation to the root logger to avoid duplicate prints
    base_logger.propagate = False

    # Standardized Formatter: [Timestamp] LEVEL ModuleName - Message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if config.enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        base_logger.addHandler(console_handler)

    if config.enable_file_logging:
        if config.log_directory:
            os.makedirs(config.log_directory, exist_ok=True)
            log_file_path = os.path.join(config.log_directory, "streamforge_rocksdb.log")
            
            # Standard file handler. In the future, this can be swapped to a RotatingFileHandler.
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            base_logger.addHandler(file_handler)

    _logger_configured = True
    base_logger.debug("Centralized logging configured successfully.")
