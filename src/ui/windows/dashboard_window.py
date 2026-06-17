"""Dashboard window with real-time charts and KPIs"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from loguru import logger
from datetime import datetime
import pyqtgraph as pg
import numpy as np


class DashboardWindow(QWidget):
    """Professional dashboard with real-time metrics"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.history_data = []
        self.setup_ui()
        self.setup_timer()
        
        logger.info("Dashboard window initialized")
    
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Верхняя панель с KPI
        kpi_layout = QGridLayout()
        
        # KPI карточки
        self.kpi_widgets = {}
        kpis = [
            ("Текущая сессия", "00:00:00", "duration"),
            ("Средняя скорость", "0.00 м/с", "avg_speed"),
            ("Макс. скорость", "0.00 м/с", "max_speed"),
            ("Ошибок за сессию", "0", "errors"),
            ("Точность", "0%", "precision"),
            ("Загруженность", "0%", "load_factor")
        ]
        
        for i, (title, value, key) in enumerate(kpis):
            card = self.create_kpi_card(title, value)
            self.kpi_widgets[key] = card
            kpi_layout.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(kpi_layout)
        
        # Графики производительности
        graphs_layout = QHBoxLayout()
        
        # График скорости
        self.speed_history_plot = self.create_history_plot("История скорости", "Время", "Скорость (м/с)")
        graphs_layout.addWidget(self.speed_history_plot)
        
        # График точности
        self.precision_plot = self.create_history_plot("Точность позиционирования", "Попытка", "Отклонение (м)")
        graphs_layout.addWidget(self.precision_plot)
        
        layout.addLayout(graphs_layout)
        
        # Нижняя панель - активность и тренды
        bottom_layout = QHBoxLayout()
        
        # Текущие задачи
        tasks_group = QGroupBox("Текущие задачи")
        tasks_layout = QVBoxLayout()
        
        self.current_task_label = QLabel("Задача: Свободное упражнение")
        self.current_task_label.setStyleSheet("color: #00aaff; font-size: 14px;")
        tasks_layout.addWidget(self.current_task_label)
        
        self.task_progress = QLabel("Прогресс: 0%")
        tasks_layout.addWidget(self.task_progress)
        
        tasks_group.setLayout(tasks_layout)
        bottom_layout.addWidget(tasks_group)
        
        # Рекомендации
        tips_group = QGroupBox("Советы по улучшению")
        tips_layout = QVBoxLayout()
        
        self.tips_label = QLabel("• Плавно управляйте джойстиком\n"
                                 "• Избегайте резких ускорений\n"
                                 "• Следите за ограничениями скорости")
        tips_layout.addWidget(self.tips_label)
        
        tips_group.setLayout(tips_layout)
        bottom_layout.addWidget(tips_group)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def create_kpi_card(self, title, value):
        """Create KPI card widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #aaa; font-size: 11px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #00aaff; font-size: 20px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        
        return card
    
    def create_history_plot(self, title, xlabel, ylabel):
        """Create history plot widget"""
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#2d2d2d')
        plot_widget.setTitle(title, color='#ffffff', size='10pt')
        plot_widget.setLabel('left', ylabel, color='#aaa')
        plot_widget.setLabel('bottom', xlabel, color='#aaa')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.getAxis('left').setPen(pg.mkPen(color='#aaa'))
        plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#aaa'))
        
        return plot_widget
    
    def setup_timer(self):
        """Setup timer for real-time updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def update_dashboard(self):
        """Update dashboard with latest data"""
        if self.app_controller.current_session:
            # Обновляем KPI
            session = self.app_controller.current_session
            duration = datetime.now() - session.start_time
            duration_str = str(duration).split('.')[0]
            
            self.kpi_widgets['duration'].value_label.setText(duration_str)
            
            # Получаем статистику сессии
            stats = self.app_controller.stats_service.get_session_details(session.id)
            
            if stats:
                errors = stats.get('errors_count', 0)
                self.kpi_widgets['errors'].value_label.setText(str(errors))
                
                # Обновляем прогресс задачи
                if session.task_name == "Free Practice":
                    progress = 50  # Просто для примера
                else:
                    progress = min(100, (errors * 10))
                
                self.task_progress.setText(f"Прогресс: {progress}%")
                
                # Обновляем графики
                self.update_speed_history()
                self.update_precision_history()
    
    def update_speed_history(self):
        """Update speed history plot"""
        if hasattr(self, 'speed_history_plot') and hasattr(self, 'speed_data'):
            self.speed_history_plot.clear()
            # Здесь будет реальная логика отображения истории скоростей
            pass
    
    def update_precision_history(self):
        """Update precision history plot"""
        if hasattr(self, 'precision_plot'):
            self.precision_plot.clear()
            # Здесь будет реальная логика отображения точности
            pass
    
    def refresh_data(self):
        """Manually refresh dashboard data"""
        self.update_dashboard()