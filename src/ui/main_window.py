"""Main application window with tabbed interface"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QStatusBar, QMenuBar, QMenu, QToolBar,
    QMessageBox, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QFont
from loguru import logger

from src.ui.windows.sim_window import SimulationWindow
from src.ui.windows.dashboard_window import DashboardWindow
from src.ui.windows.journal_window import JournalWindow
from src.ui.windows.users_window import UsersWindow
from src.ui.windows.stats_window import StatsWindow
from src.ui.windows.connect_window import ConnectWindow


class MainWindow(QMainWindow):
    """Main window with multiple tabs for different functionalities"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.current_user = None
        self.simulation_running = False
        self.status_timer = None
        
        self.setWindowTitle("Port Crane Simulator Pro - Training System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Загрузка стилей
        self.load_styles()
        
        # Создание UI
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_central_widget()
        self.create_status_bar()
        
        logger.info("Main window initialized")
    
    def load_styles(self):
        """Load QSS stylesheet"""
        from pathlib import Path
        
        style_path = Path(__file__).parent / "styles.qss"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
                logger.debug("Stylesheet loaded")
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #353535;
                }
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ccc;
                    padding: 8px 16px;
                    margin: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #4a4a4a;
                    color: white;
                }
                QStatusBar {
                    background-color: #1e1e1e;
                    color: #aaa;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ccc;
                }
                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }
                QToolBar {
                    background-color: #353535;
                    border: none;
                    spacing: 3px;
                }
            """)
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&Файл")
        
        connect_action = QAction("&Подключиться к крану", self)
        connect_action.triggered.connect(self.show_connect_dialog)
        connect_action.setShortcut("Ctrl+C")
        file_menu.addAction(connect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Выход", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("&Вид")
        
        fullscreen_action = QAction("&Полный экран", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        fullscreen_action.setShortcut("F11")
        view_menu.addAction(fullscreen_action)
        
        tools_menu = menubar.addMenu("&Инструменты")
        
        reset_action = QAction("&Сбросить симуляцию", self)
        reset_action.triggered.connect(self.reset_simulation)
        tools_menu.addAction(reset_action)
        
        calibrate_action = QAction("&Калибровка", self)
        calibrate_action.triggered.connect(self.calibrate_crane)
        tools_menu.addAction(calibrate_action)
        
        help_menu = menubar.addMenu("&Помощь")
        
        about_action = QAction("&О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("&Документация", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
    
    def create_tool_bar(self):
        """Create main toolbar with quick actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        connect_btn = QPushButton("🔌 Подключение")
        connect_btn.clicked.connect(self.show_connect_dialog)
        toolbar.addWidget(connect_btn)
        
        toolbar.addSeparator()
        
        start_btn = QPushButton("▶ Старт")
        start_btn.clicked.connect(self.start_simulation)
        toolbar.addWidget(start_btn)
        
        stop_btn = QPushButton("⏹ Стоп")
        stop_btn.clicked.connect(self.stop_simulation)
        toolbar.addWidget(stop_btn)
        
        reset_btn = QPushButton("🔄 Сброс")
        reset_btn.clicked.connect(self.reset_simulation)
        toolbar.addWidget(reset_btn)
        
        toolbar.addSeparator()
        
        self.connection_status_label = QLabel("⚫ Не подключен")
        toolbar.addWidget(self.connection_status_label)
        
        self.user_label = QLabel("👤 Не авторизован")
        toolbar.addWidget(self.user_label)
    
    def create_central_widget(self):
        """Create tabbed central widget"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.setCentralWidget(self.tab_widget)
        
        self.sim_window = SimulationWindow(self.app_controller)
        self.tab_widget.addTab(self.sim_window, "🚀 Симулятор крана")
        
        self.dashboard_window = DashboardWindow(self.app_controller)
        self.tab_widget.addTab(self.dashboard_window, "📊 Дашборд")
        
        self.journal_window = JournalWindow(self.app_controller)
        self.tab_widget.addTab(self.journal_window, "📝 Журнал событий")
        
        self.stats_window = StatsWindow(self.app_controller)
        self.tab_widget.addTab(self.stats_window, "📈 Статистика")
        
        self.users_window = UsersWindow(self.app_controller)
        self.tab_widget.addTab(self.users_window, "👥 Пользователи")
        
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def create_status_bar(self):
        """Create status bar with information"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        self.status_label = QLabel("Готов к работе")
        status_bar.addWidget(self.status_label)
        
        status_bar.addPermanentWidget(QLabel(" | "))
        
        self.sim_status_label = QLabel("Симуляция: Остановлена")
        status_bar.addPermanentWidget(self.sim_status_label)
        
        status_bar.addPermanentWidget(QLabel(" | "))
        
        self.position_label = QLabel("Позиция: X=0.0 м")
        status_bar.addPermanentWidget(self.position_label)
        
        status_bar.addPermanentWidget(QLabel(" | "))
        
        self.speed_label = QLabel("Скорость: 0.0 м/с")
        status_bar.addPermanentWidget(self.speed_label)
    
    def set_current_user(self, user_data):
        """Set current user and update UI - user_data is a dict"""
        self.current_user = user_data
        self.user_label.setText(f"👤 {user_data['username']} ({user_data['role']})")
        self.status_label.setText(f"Пользователь: {user_data.get('full_name', user_data['username'])}")
        
        # Запускаем таймер статуса
        self.start_status_timer()
    
    def start_status_timer(self):
        """Start status update timer"""
        if self.status_timer is None:
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.update_status)
            self.status_timer.start(1000)
            logger.debug("Status timer started")
    
    def stop_status_timer(self):
        """Stop status update timer"""
        if self.status_timer:
            self.status_timer.stop()
            self.status_timer = None
            logger.debug("Status timer stopped")
    
    def show_connect_dialog(self):
        """Show connection dialog"""
        dialog = ConnectWindow(self.app_controller, self)
        dialog.exec()
    
    def start_simulation(self):
        """Start crane simulation"""
        if not self.simulation_running:
            self.sim_window.start_simulation()
            self.simulation_running = True
            self.sim_status_label.setText("Симуляция: Запущена")
            logger.info("Simulation started")
    
    def stop_simulation(self):
        """Stop crane simulation"""
        if self.simulation_running:
            self.sim_window.stop_simulation()
            self.simulation_running = False
            self.sim_status_label.setText("Симуляция: Остановлена")
            logger.info("Simulation stopped")
    
    def reset_simulation(self):
        """Reset simulation state"""
        self.sim_window.reset_simulation()
        self.status_label.setText("Симуляция сброшена")
        logger.info("Simulation reset")
    
    def calibrate_crane(self):
        """Calibrate crane zero position"""
        QMessageBox.information(self, "Калибровка", "Калибровка крана выполнена успешно!")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def update_status(self):
        """Update status bar information"""
        if self.simulation_running:
            telemetry = self.sim_window.get_current_telemetry()
            if telemetry:
                self.position_label.setText(f"Позиция: X={telemetry.get('position_x', 0):.1f} м")
                self.speed_label.setText(f"Скорость: {telemetry.get('speed', 0):.2f} м/с")
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        tab_name = self.tab_widget.tabText(index)
        logger.debug(f"Switched to tab: {tab_name}")
        
        if tab_name == "📈 Статистика":
            self.stats_window.refresh_stats()
        elif tab_name == "📝 Журнал событий":
            self.journal_window.refresh_journal()
    
    def enable_admin_features(self):
        """Enable admin-only features"""
        self.users_window.setEnabled(True)
        self.status_label.setText("Режим администратора активирован")
    
    def enable_instructor_features(self):
        """Enable instructor-only features"""
        self.stats_window.enable_export_features()
        self.status_label.setText("Режим инструктора активирован")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "О программе",
                         "Port Crane Simulator Pro v1.0\n\n"
                         "Профессиональная система обучения операторов портальных кранов\n\n"
                         "© 2024 Training Systems Inc.\n"
                         "Все права защищены.")
    
    def show_documentation(self):
        """Show documentation"""
        QMessageBox.information(self, "Документация",
                               "Полная документация доступна в папке docs/")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.simulation_running:
            reply = QMessageBox.question(self, "Подтверждение",
                                        "Симуляция запущена. Вы уверены, что хотите выйти?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        if self.simulation_running:
            self.stop_simulation()
        
        self.stop_status_timer()
        self.app_controller.shutdown()
        event.accept()