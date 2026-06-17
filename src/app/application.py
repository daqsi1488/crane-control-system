"""Main application class - orchestrates all components"""

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QObject, Signal, QTimer
from loguru import logger

from src.ui.main_window import MainWindow
from src.core.database.db_manager import DatabaseManager
from src.core.database.models import init_database
from src.services.auth_service import AuthService
from src.services.logging_service import LoggingService
from src.services.stats_service import StatsService
from src.utils.config_loader import config


class CraneApplication(QObject):
    """Main application orchestrator"""
    
    # Сигналы для глобальных событий
    user_logged_in = Signal(object)
    user_logged_out = Signal()
    connection_status_changed = Signal(bool, str)
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing Crane Application")
        
        # Инициализация БД
        db_path = config['database']['path']
        init_database(db_path)
        self.db_manager = DatabaseManager(db_path)
        
        # Инициализация сервисов
        self.auth_service = AuthService(self.db_manager)
        self.logging_service = LoggingService(self.db_manager)
        self.stats_service = StatsService(self.db_manager)
        
        # Текущий пользователь и сессия
        self.current_user = None
        self.current_session = None
        
        # Таймеры (будут созданы после логина)
        self.auto_save_timer = None
        
        # Создание главного окна
        self.main_window = MainWindow(self)
        
        # Подключение сигналов
        self.user_logged_in.connect(self.on_user_logged_in)
        self.user_logged_out.connect(self.on_user_logged_out)
        
        # Показываем окно входа
        self.show_login_dialog()
    
    def show_login_dialog(self):
        """Show login dialog before main window"""
        from src.ui.windows.login_window import LoginDialog
        
        login_dialog = LoginDialog(self.auth_service, self.main_window)
        result = login_dialog.exec()
        
        if result and login_dialog.get_authenticated_user():
            user_data = login_dialog.get_authenticated_user()
            self.current_user = user_data
            self.user_logged_in.emit(user_data)
            self.main_window.show()
            logger.info(f"User {user_data['username']} logged in successfully")
        else:
            logger.info("Login cancelled, exiting application")
            self.shutdown()
            import sys
            sys.exit(0)
    
    def on_user_logged_in(self, user_data):
        """Handle user login - user_data is a dict, not an ORM object"""
        self.current_user = user_data
        self.main_window.set_current_user(user_data)
        
        # Начинаем новую тренировочную сессию
        self.current_session = self.logging_service.start_session(user_data['id'])
        
        # Запускаем таймер автосохранения
        self.start_auto_save_timer()
        
        # Обновляем UI в зависимости от роли
        if user_data['role'] == 'admin':
            self.main_window.enable_admin_features()
        elif user_data['role'] == 'instructor':
            self.main_window.enable_instructor_features()
    
    def start_auto_save_timer(self):
        """Start auto-save timer"""
        if self.auto_save_timer is None:
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save_state)
            auto_save_interval = config['ui'].get('auto_save_interval', 30) * 1000
            self.auto_save_timer.start(auto_save_interval)
            logger.debug(f"Auto-save timer started ({auto_save_interval}ms)")
    
    def stop_auto_save_timer(self):
        """Stop auto-save timer"""
        if self.auto_save_timer:
            self.auto_save_timer.stop()
            self.auto_save_timer = None
            logger.debug("Auto-save timer stopped")
    
    def on_user_logged_out(self):
        """Handle user logout"""
        if self.current_session:
            self.logging_service.end_session(self.current_session.id)
            self.current_session = None
        
        self.stop_auto_save_timer()
        self.current_user = None
        self.show_login_dialog()
    
    def auto_save_state(self):
        """Auto-save current application state"""
        if self.current_session and hasattr(self.main_window, 'simulation_running') and self.main_window.simulation_running:
            logger.debug("Auto-saving simulation state")
    
    def shutdown(self):
        """Clean shutdown of application"""
        logger.info("Shutting down application")
        
        self.stop_auto_save_timer()
        
        if self.current_session:
            self.logging_service.end_session(self.current_session.id)
            self.current_session = None
        
        self.db_manager.close()
        logger.info("Application shutdown complete")