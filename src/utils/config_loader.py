"""Configuration loader with YAML support"""

import yaml
from pathlib import Path
from loguru import logger


class ConfigLoader:
    """Singleton config loader"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {config_path}")
            return self._config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Возвращаем дефолтную конфигурацию
            return self._get_default_config()
    
    def _get_default_config(self):
        """Default configuration if YAML is missing"""
        return {
            'app': {'name': 'Crane Simulator', 'version': '1.0.0'},
            'database': {'path': 'data/crane.db', 'echo': False},
            'simulation': {'dt': 0.02, 'gravity': 9.81},
            'ui': {'theme': 'dark'}
        }
    
    @property
    def config(self):
        if self._config is None:
            self.load()
        return self._config


# Глобальный экземпляр
config_loader = ConfigLoader()
config = config_loader.config