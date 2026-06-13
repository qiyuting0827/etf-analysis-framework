"""
Logging configuration
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import LOG_DIR, LOG_LEVEL


def setup_logging():
    """
    Setup logging configuration
    """
    # Create logger
    logger = logging.getLogger('etf_framework')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # File handler
    log_file = LOG_DIR / 'etf_framework.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Setup logging on module import
logger = setup_logging()
