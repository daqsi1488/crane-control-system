"""Simulation window with crane visualization and controls"""

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox, QFrame,
    QSpinBox, QDoubleSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from loguru import logger

from src.core.simulation.physics_engine import PhysicsEngine
from src.core.simulation.sim_loop import SimulationThread
from src.ui.widgets.crane_controller import CraneControllerWidget
from src.ui.widgets.telemetry_view import TelemetryView
from src.ui.widgets.live_plot import LivePlotWidget


class SimulationWindow(QWidget):
    """Main simulation window with crane visualization and controls"""
    
    telemetry_updated = Signal(dict)
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.physics_engine = PhysicsEngine()
        self.simulation_thread = None
        self.simulation_running = False
        
        self.setup_ui()
        self.connect_signals()
        
        logger.info("Simulation window initialized")
    
    def setup_ui(self):
        """Setup the simulation UI layout"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Левая панель - 3D/2D визуализация
        left_panel = self.create_visualization_panel()
        main_layout.addWidget(left_panel, 2)
        
        # Правая панель - управление и телеметрия
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
    
    def create_visualization_panel(self):
        """Create crane visualization area"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("QFrame { background-color: #1a1a2e; border: 2px solid #333; }")
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Визуализация портального крана")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00aaff; padding: 5px;")
        layout.addWidget(title)
        
        # Кастомный виджет для отрисовки крана
        self.crane_view = CraneVisualizationWidget(self.physics_engine)
        layout.addWidget(self.crane_view, 1)
        
        # Информационная панель под визуализацией
        info_panel = QHBoxLayout()
        self.status_label = QLabel("Статус: Готов")
        self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        info_panel.addWidget(self.status_label)
        
        info_panel.addStretch()
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("color: #888;")
        info_panel.addWidget(self.fps_label)
        
        layout.addLayout(info_panel)
        panel.setLayout(layout)
        
        return panel
    
    def create_control_panel(self):
        """Create crane control panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("QFrame { background-color: #2d2d2d; }")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Панель управления краном
        control_group = QGroupBox("Управление краном")
        control_layout = QVBoxLayout()
        
        self.crane_controller = CraneControllerWidget()
        control_layout.addWidget(self.crane_controller)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Телеметрия
        telemetry_group = QGroupBox("Телеметрия в реальном времени")
        telemetry_layout = QVBoxLayout()
        
        self.telemetry_view = TelemetryView()
        telemetry_layout.addWidget(self.telemetry_view)
        
        telemetry_group.setLayout(telemetry_layout)
        layout.addWidget(telemetry_group)
        
        # Графики
        graphs_group = QGroupBox("Графики")
        graphs_layout = QVBoxLayout()
        
        self.speed_plot = LivePlotWidget("Скорость тележки", "Время (с)", "Скорость (м/с)", max_points=200)
        graphs_layout.addWidget(self.speed_plot)
        
        self.position_plot = LivePlotWidget("Позиция тележки", "Время (с)", "Позиция (м)", max_points=200)
        graphs_layout.addWidget(self.position_plot)
        
        graphs_group.setLayout(graphs_layout)
        layout.addWidget(graphs_group)
        
        # Кнопки управления симуляцией
        sim_control_group = QGroupBox("Управление симуляцией")
        sim_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Старт")
        self.start_btn.setStyleSheet("background-color: #2d6a2d; color: white; padding: 8px;")
        self.start_btn.clicked.connect(self.start_simulation)
        sim_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_simulation)
        sim_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 Сброс")
        self.reset_btn.clicked.connect(self.reset_simulation)
        sim_layout.addWidget(self.reset_btn)
        
        sim_control_group.setLayout(sim_layout)
        layout.addWidget(sim_control_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        
        return panel
    
    def connect_signals(self):
        """Connect all signals"""
        # Подключаем контроллер к физике
        self.crane_controller.control_signal.connect(self.physics_engine.set_control_force)
        
        # Подключаем обновление телеметрии
        self.telemetry_updated.connect(self.telemetry_view.update_telemetry)
        self.telemetry_updated.connect(self.update_plots)
    
    def start_simulation(self):
        """Start the simulation thread"""
        if not self.simulation_running:
            self.simulation_thread = SimulationThread(self.physics_engine)
            self.simulation_thread.telemetry_signal.connect(self.on_telemetry_received)
            self.simulation_thread.start()
            self.simulation_running = True
            
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.status_label.setText("Статус: Симуляция запущена")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            
            logger.info("Simulation thread started")
    
    def pause_simulation(self):
        """Pause simulation"""
        if self.simulation_thread:
            self.simulation_thread.pause()
            self.status_label.setText("Статус: Пауза")
            self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
            logger.info("Simulation paused")
    
    def stop_simulation(self):
        """Stop simulation"""
        if self.simulation_thread:
            self.simulation_thread.stop()
            self.simulation_thread.wait()
            self.simulation_thread = None
            self.simulation_running = False
            
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.status_label.setText("Статус: Остановлена")
            self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
            
            logger.info("Simulation stopped")
    
    def reset_simulation(self):
        """Reset simulation to initial state"""
        if self.simulation_running:
            self.stop_simulation()
        
        self.physics_engine.reset()
        self.crane_view.update()
        self.telemetry_view.reset()
        self.speed_plot.clear()
        self.position_plot.clear()
        self.status_label.setText("Статус: Сброшена")
        
        logger.info("Simulation reset")
    
    def on_telemetry_received(self, telemetry_data):
        """Handle incoming telemetry data"""
        self.telemetry_updated.emit(telemetry_data)
        self.crane_view.update_telemetry(telemetry_data)
        self.crane_view.update()
        
        # Логируем ошибки только если есть активная сессия
        if telemetry_data.get('is_overspeed', False):
            if hasattr(self.app_controller, 'current_session') and self.app_controller.current_session:
                if hasattr(self.app_controller, 'current_user') and self.app_controller.current_user:
                    self.app_controller.logging_service.log_event(
                        session_id=self.app_controller.current_session.id,
                        user_id=self.app_controller.current_user.id,
                        event_type="error",
                        description="Превышение скорости крана",
                        speed=telemetry_data.get('speed', 0)
                    )
    
    def update_plots(self, telemetry_data):
        """Update live plots"""
        import time
        current_time = time.time()
        
        self.speed_plot.add_data_point(current_time, telemetry_data.get('speed', 0))
        self.position_plot.add_data_point(current_time, telemetry_data.get('position_x', 0))
    
    def get_current_telemetry(self):
        """Get current telemetry data"""
        return self.physics_engine.get_telemetry()


class CraneVisualizationWidget(QWidget):
    """Custom widget for 2D crane visualization"""
    
    def __init__(self, physics_engine):
        super().__init__()
        self.physics_engine = physics_engine
        self.telemetry = {}
        self.setMinimumHeight(500)
        self.setStyleSheet("background-color: #1a1a2e;")
        
        # Анимация
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(33)  # ~30 FPS
        
        # Параметры отрисовки
        self.crane_width = 600
        self.crane_height = 400
        self.trolley_size = 30
        self.load_size = 15
    
    def update_telemetry(self, telemetry):
        """Update telemetry data"""
        self.telemetry = telemetry
    
    def paintEvent(self, event):
        """Draw crane visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем фон
        painter.fillRect(self.rect(), QColor(26, 26, 46))
        
        # Определяем область рисования
        margin = 50
        draw_width = self.width() - 2 * margin
        draw_height = self.height() - 2 * margin
        
        # Рисуем портал (основные опоры)
        painter.setPen(QPen(QColor(200, 200, 200), 3))
        painter.setBrush(QBrush(QColor(100, 100, 120)))
        
        # Левая опора
        painter.drawRect(margin, margin + 50, 20, draw_height - 100)
        # Правая опора
        painter.drawRect(self.width() - margin - 20, margin + 50, 20, draw_height - 100)
        # Верхняя балка (мост)
        painter.drawRect(margin, margin + 30, self.width() - 2 * margin, 20)
        
        # Рисуем тележку
        if self.telemetry:
            # Позиция тележки (0-1 отображение)
            position_normalized = (self.telemetry.get('position_x', 0) + 5) / 10
            position_normalized = max(0, min(1, position_normalized))
            
            trolley_x = margin + position_normalized * (self.width() - 2 * margin - self.trolley_size)
            trolley_y = margin + 30
            
            painter.setBrush(QBrush(QColor(255, 100, 50)))
            painter.drawRect(trolley_x, trolley_y, self.trolley_size, self.trolley_size)
            
            # Рисуем трос (примерная длина)
            cable_length_display = 80
            cable_y = trolley_y + self.trolley_size + cable_length_display
            
            painter.setPen(QPen(QColor(200, 200, 100), 2))
            painter.drawLine(
                trolley_x + self.trolley_size // 2, 
                trolley_y + self.trolley_size,
                trolley_x + self.trolley_size // 2,
                cable_y
            )
            
            # Рисуем груз с учетом угла отклонения
            angle = self.telemetry.get('cable_angle', 0)
            offset_x = np.sin(angle) * cable_length_display
            load_x = trolley_x + self.trolley_size // 2 + offset_x
            load_y = cable_y
            
            painter.setBrush(QBrush(QColor(255, 200, 50)))
            painter.drawEllipse(int(load_x - self.load_size//2), int(load_y), self.load_size, self.load_size)
            
            # Отображаем текстовую информацию
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 30, f"Позиция: {self.telemetry.get('position_x', 0):.2f} м")
            painter.drawText(10, 50, f"Скорость: {self.telemetry.get('speed', 0):.2f} м/с")
            painter.drawText(10, 70, f"Угол: {self.telemetry.get('cable_angle', 0):.2f} рад")
            painter.drawText(10, 90, f"Груз: {self.telemetry.get('load_weight', 0):.1f} кг")
        else:
            # Рисуем тележку в начальной позиции
            trolley_x = margin + (self.width() - 2 * margin - self.trolley_size) // 2
            painter.setBrush(QBrush(QColor(255, 100, 50)))
            painter.drawRect(trolley_x, margin + 30, self.trolley_size, self.trolley_size)
            
            # Начальная подпись
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 30, "Позиция: 0.00 м")
            painter.drawText(10, 50, "Скорость: 0.00 м/с")
            painter.drawText(10, 70, "Угол: 0.00 рад")
            painter.drawText(10, 90, "Груз: 1000.0 кг")
        
        painter.end()