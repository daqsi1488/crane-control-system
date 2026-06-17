"""Professional logging setup with loguru"""

import sys
from pathlib import Path
from loguru import logger
from src.utils.config_loader import config


def setup_logging():
    """Configure logging for the entire application"""
    
    # Удаляем стандартный вывод
    logger.remove()
    
    # Консольный вывод (цветной)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.get('logging', {}).get('level', 'INFO'),
        colorize=True
    )
    
    # Файловый вывод с ротацией
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    logger.add(
        log_path / "crane_simulator_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=config.get('logging', {}).get('rotation', '10 MB'),
        retention=config.get('logging', {}).get('retention', '30 days'),
        compression="zip",
        encoding="utf-8",
        level="DEBUG"
    )
    
    # Отдельный лог для ошибок
    logger.add(
        log_path / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="90 days",
        level="ERROR",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logging system initialized")