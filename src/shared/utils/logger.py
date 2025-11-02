import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Custom formatter with colors for console
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup logger with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Format for logs
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler (no colors, saves to file)
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        LOGS_DIR / f"safetravel_{today}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get or create a logger.
    
    Usage:
        from src.shared.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is an info message")
    
    Args:
        name: Logger name (use __name__ from calling module)
        level: Optional logging level override
    
    Returns:
        Logger instance
    """
    if level is None:
        # Get level from environment or default to INFO
        import os
        level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_name, logging.INFO)
    
    return setup_logger(name, level)