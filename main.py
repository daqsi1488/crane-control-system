#!/usr/bin/env python3
"""
Port Crane Simulator - Main Entry Point
Professional Training Software for Crane Operators
"""

import sys
import os
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from loguru import logger

from src.app.application import CraneApplication
from src.utils.logger_setup import setup_logging
from src.utils.config_loader import config


def main():
    """Основная точка входа"""
    
    # Настройка логгирования
    setup_logging()
    
    logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")
    
    # Создание необходимых директорий
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Создание QApplication с высоким DPI для красивого отображения
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(config['app']['name'])
    app.setOrganizationName(config['app']['company'])
    
    # Установка иконки приложения (если есть)
    icon_path = Path(__file__).parent / "src" / "resources" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Создание главного приложения
    crane_app = CraneApplication()
    
    # Запуск
    try:
        exit_code = app.exec()
        logger.info(f"Application exited with code {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()