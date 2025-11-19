import json
import logging
import os
from logging.handlers import RotatingFileHandler

def load_config(config_path: str = "config.json") -> dict:
    """
    Loads and validates the JSON configuration file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")

    required_keys = ["backup_tasks", "logging", "robocopy_options"]
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

    return config

def setup_logging(config: dict):
    """
    Configures logging based on the provided configuration.
    """
    log_config = config.get("logging", {})
    log_level_str = log_config.get("level", "INFO").upper()
    log_file = log_config.get("file", "e:\\logs\\backup.log")

    log_level = getattr(logging, log_level_str, logging.INFO)

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create handlers
    # RotatingFileHandler: 2MB max size, keep 5 backups (arbitrary default if not specified, 
    # though spec says "numbered log files", RotatingFileHandler does .1, .2 etc)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2*1024*1024, backupCount=5
    )
    
    console_handler = logging.StreamHandler()

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info("Logging initialized.")
