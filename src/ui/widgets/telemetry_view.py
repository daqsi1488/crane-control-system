"""Telemetry display widget"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, 
                               QLabel, QProgressBar, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor


class TelemetryView(QWidget):
    """Professional telemetry display with gauges"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setMinimumHeight(250)
    
    def setup_ui(self):
        """Setup telemetry UI"""
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # Создаем индикаторы
        self.gauges = {}
        
        # Позиция X
        self.add_gauge(layout, 0, 0, "Позиция X", "м", -5, 5, 0)
        
        # Скорость
        self.add_gauge(layout, 0, 1, "Скорость", "м/с", -2, 2, 0)
        
        # Ускорение
        self.add_gauge(layout, 1, 0, "Ускорение", "м/с²", -2, 2, 0)
        
        # Угол груза
        self.add_gauge(layout, 1, 1, "Угол груза", "рад", -0.5, 0.5, 0)
        
        # Груз
        self.add_gauge(layout, 2, 0, "Вес груза", "кг", 0, 10000, 1000)
        
        # Нагрузка на двигатель
        self.add_gauge(layout, 2, 1, "Нагрузка", "%", 0, 100, 0)
        
        # Индикаторы ошибок
        error_frame = QFrame()
        error_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 5px;")
        error_layout = QVBoxLayout()
        
        self.overspeed_label = QLabel("⚠️ ПРЕВЫШЕНИЕ СКОРОСТИ")
        self.overspeed_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        self.overspeed_label.setVisible(False)
        error_layout.addWidget(self.overspeed_label)
        
        self.overload_label = QLabel("⚠️ ПЕРЕГРУЗ")
        self.overload_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        self.overload_label.setVisible(False)
        error_layout.addWidget(self.overload_label)
        
        self.limit_label = QLabel("⚠️ ПРЕДЕЛ ДОСТИГНУТ")
        self.limit_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.limit_label.setVisible(False)
        error_layout.addWidget(self.limit_label)
        
        error_frame.setLayout(error_layout)
        layout.addWidget(error_frame, 3, 0, 1, 2)
        
        self.setLayout(layout)
    
    def add_gauge(self, layout, row, col, name, unit, min_val, max_val, initial):
        """Add a gauge widget"""
        gauge_widget = QFrame()
        gauge_widget.setStyleSheet("background-color: #2d2d2d; border-radius: 5px; padding: 5px;")
        gauge_layout = QVBoxLayout()
        
        # Название
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #aaa; font-size: 10px;")
        name_label.setAlignment(Qt.AlignCenter)
        gauge_layout.addWidget(name_label)
        
        # Значение
        value_label = QLabel(f"{initial:.1f} {unit}")
        value_label.setStyleSheet("color: #00aaff; font-size: 16px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        gauge_layout.addWidget(value_label)
        
        # Прогресс-бар
        progress = QProgressBar()
        progress.setRange(int(min_val * 100), int(max_val * 100))
        progress.setValue(int(initial * 100))
        progress.setTextVisible(False)
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #1a1a1a;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:0.5 #ffff00, stop:1 #ff0000);
                border-radius: 2px;
            }
        """)
        gauge_layout.addWidget(progress)
        
        gauge_widget.setLayout(gauge_layout)
        layout.addWidget(gauge_widget, row, col)
        
        # Сохраняем ссылки
        self.gauges[name] = {
            'value_label': value_label,
            'progress': progress,
            'min': min_val,
            'max': max_val,
            'unit': unit
        }
    
    def update_telemetry(self, telemetry):
        """Update all telemetry displays"""
        # Обновляем позицию
        self.update_gauge("Позиция X", telemetry.get('position_x', 0))
        
        # Обновляем скорость
        speed = telemetry.get('speed', 0)
        self.update_gauge("Скорость", speed)
        
        # Обновляем ускорение
        self.update_gauge("Ускорение", telemetry.get('acceleration', 0))
        
        # Обновляем угол груза
        self.update_gauge("Угол груза", telemetry.get('cable_angle', 0))
        
        # Обновляем вес груза
        self.update_gauge("Вес груза", telemetry.get('load_weight', 1000))
        
        # Обновляем нагрузку
        load_percent = abs(speed) / 2.0 * 100 if speed != 0 else 0
        self.update_gauge("Нагрузка", load_percent)
        
        # Обновляем индикаторы ошибок
        self.overspeed_label.setVisible(telemetry.get('is_overspeed', False))
        self.overload_label.setVisible(telemetry.get('is_overload', False))
        self.limit_label.setVisible(telemetry.get('limit_reached', False))
        
        # Меняем цвет при ошибках
        if telemetry.get('is_overspeed', False):
            self.update_gauge_color("Скорость", "#ff4444")
        else:
            self.update_gauge_color("Скорость", "#00aaff")
    
    def update_gauge(self, name, value):
        """Update specific gauge value"""
        if name in self.gauges:
            gauge = self.gauges[name]
            clamped_value = max(gauge['min'], min(gauge['max'], value))
            percent = (clamped_value - gauge['min']) / (gauge['max'] - gauge['min']) * 100
            
            gauge['value_label'].setText(f"{clamped_value:.1f} {gauge['unit']}")
            gauge['progress'].setValue(int(clamped_value * 100 if gauge['min'] == 0 else 
                                          (clamped_value - gauge['min']) / (gauge['max'] - gauge['min']) * 100))
    
    def update_gauge_color(self, name, color):
        """Update gauge value color"""
        if name in self.gauges:
            self.gauges[name]['value_label'].setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
    
    def reset(self):
        """Reset all gauges to zero"""
        for name in self.gauges:
            self.update_gauge(name, 0)
        self.overspeed_label.setVisible(False)
        self.overload_label.setVisible(False)
        self.limit_label.setVisible(False)