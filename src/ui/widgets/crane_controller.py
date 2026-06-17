"""Crane control widget with joystick and buttons"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from loguru import logger
import math


class CraneControllerWidget(QWidget):
    """Professional crane control panel with joystick"""
    
    control_signal = Signal(float)  # Сила управления (-max..max)
    
    def __init__(self):
        super().__init__()
        self.control_force = 0.0
        self.max_force = 5000.0
        self.setup_ui()
        self.setMinimumHeight(300)
        
    def setup_ui(self):
        """Setup control UI"""
        layout = QVBoxLayout()
        
        # Джойстик управления
        joystick_group = QGroupBox("Джойстик управления")
        joystick_layout = QVBoxLayout()
        
        self.joystick = JoystickWidget()
        self.joystick.force_changed.connect(self.on_joystick_moved)
        joystick_layout.addWidget(self.joystick)
        
        joystick_group.setLayout(joystick_layout)
        layout.addWidget(joystick_group)
        
        # Кнопки управления
        buttons_group = QGroupBox("Кнопки управления")
        buttons_layout = QGridLayout()
        
        # Вперед/Назад
        self.forward_btn = QPushButton("▲ ВПЕРЕД")
        self.forward_btn.setStyleSheet("background-color: #2d6a2d; font-size: 14px; padding: 10px;")
        self.forward_btn.pressed.connect(lambda: self.set_control_force(self.max_force))
        self.forward_btn.released.connect(lambda: self.set_control_force(0))
        buttons_layout.addWidget(self.forward_btn, 0, 1)
        
        self.backward_btn = QPushButton("▼ НАЗАД")
        self.backward_btn.setStyleSheet("background-color: #8b3a3a; font-size: 14px; padding: 10px;")
        self.backward_btn.pressed.connect(lambda: self.set_control_force(-self.max_force))
        self.backward_btn.released.connect(lambda: self.set_control_force(0))
        buttons_layout.addWidget(self.backward_btn, 2, 1)
        
        # Стоп
        self.stop_btn = QPushButton("● СТОП")
        self.stop_btn.setStyleSheet("background-color: #cc0000; font-size: 14px; padding: 10px; font-weight: bold;")
        self.stop_btn.clicked.connect(lambda: self.set_control_force(0))
        buttons_layout.addWidget(self.stop_btn, 1, 1)
        
        # Подъем/опускание груза
        self.up_btn = QPushButton("⬆ ПОДЪЕМ")
        self.up_btn.clicked.connect(self.lift_up)
        buttons_layout.addWidget(self.up_btn, 0, 2)
        
        self.down_btn = QPushButton("⬇ ОПУСКАНИЕ")
        self.down_btn.clicked.connect(self.lift_down)
        buttons_layout.addWidget(self.down_btn, 2, 2)
        
        # Экстренная остановка
        self.emergency_btn = QPushButton("⚠ ЭКСТРЕННАЯ ОСТАНОВКА")
        self.emergency_btn.setStyleSheet("background-color: #ff6600; color: white; font-weight: bold;")
        self.emergency_btn.clicked.connect(self.emergency_stop)
        buttons_layout.addWidget(self.emergency_btn, 3, 0, 1, 3)
        
        buttons_group.setLayout(buttons_layout)
        layout.addWidget(buttons_group)
        
        # Слайдер управления (альтернатива джойстику)
        slider_group = QGroupBox("Слайдер управления")
        slider_layout = QVBoxLayout()
        
        self.control_slider = QSlider(Qt.Horizontal)
        self.control_slider.setRange(-100, 100)
        self.control_slider.setValue(0)
        self.control_slider.valueChanged.connect(self.on_slider_moved)
        slider_layout.addWidget(self.control_slider)
        
        self.force_label = QLabel("Сила: 0 Н")
        self.force_label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(self.force_label)
        
        slider_group.setLayout(slider_layout)
        layout.addWidget(slider_group)
        
        self.setLayout(layout)
    
    def on_joystick_moved(self, force_percent):
        """Handle joystick movement"""
        force = force_percent * self.max_force / 100
        self.set_control_force(force)
        self.control_slider.setValue(int(force_percent))
    
    def on_slider_moved(self, value):
        """Handle slider movement"""
        force = value * self.max_force / 100
        self.set_control_force(force)
        self.joystick.set_force_percent(value)
    
    def set_control_force(self, force):
        """Set control force and emit signal"""
        self.control_force = max(-self.max_force, min(self.max_force, force))
        self.control_signal.emit(self.control_force)
        
        # Обновляем отображение
        force_percent = (self.control_force / self.max_force) * 100
        self.force_label.setText(f"Сила: {self.control_force:.0f} Н ({force_percent:+.0f}%)")
        
        if abs(force_percent) > 80:
            self.force_label.setStyleSheet("color: #ff6600; font-weight: bold;")
        else:
            self.force_label.setStyleSheet("color: #ffffff;")
    
    def lift_up(self):
        """Lift the load up"""
        logger.info("Lifting load up")
        # Здесь будет логика подъема груза
    
    def lift_down(self):
        """Lower the load down"""
        logger.info("Lowering load down")
        # Здесь будет логика опускания груза
    
    def emergency_stop(self):
        """Emergency stop - immediate brake"""
        self.set_control_force(0)
        logger.warning("EMERGENCY STOP ACTIVATED")


class JoystickWidget(QWidget):
    """Custom joystick widget for crane control"""
    
    force_changed = Signal(float)  # Процент силы (-100..100)
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.setMinimumHeight(150)
        self.joystick_pos = QPoint(100, 100)
        self.center = QPoint(100, 100)
        self.radius = 70
        self.is_dragging = False
        self.force_percent = 0.0
        
        self.setStyleSheet("background-color: #2d2d2d; border: 2px solid #555; border-radius: 5px;")
    
    def paintEvent(self, event):
        """Draw joystick"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем фон
        painter.fillRect(self.rect(), QColor(45, 45, 45))
        
        # Рисуем ограничительную окружность
        painter.setPen(QPen(QColor(100, 100, 120), 3))
        painter.setBrush(QBrush(QColor(60, 60, 70)))
        painter.drawEllipse(self.center, self.radius, self.radius)
        
        # Рисуем перекрестие
        painter.setPen(QPen(QColor(80, 80, 100), 1))
        painter.drawLine(self.center.x() - self.radius, self.center.y(),
                        self.center.x() + self.radius, self.center.y())
        painter.drawLine(self.center.x(), self.center.y() - self.radius,
                        self.center.x(), self.center.y() + self.radius)
        
        # Рисуем метки нейтрали
        painter.setFont(QFont("Arial", 8))
        painter.drawText(self.center.x() - 5, self.center.y() + 85, "0")
        painter.drawText(self.center.x() + 75, self.center.y() - 5, "+")
        painter.drawText(self.center.x() - 85, self.center.y() - 5, "-")
        
        # Рисуем джойстик
        painter.setPen(QPen(QColor(255, 100, 50), 2))
        
        # Цвет в зависимости от силы
        if abs(self.force_percent) > 80:
            color = QColor(255, 50, 50)
        elif abs(self.force_percent) > 50:
            color = QColor(255, 150, 50)
        else:
            color = QColor(100, 200, 255)
        
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self.joystick_pos, 20, 20)
        
        # Отображение процента силы
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(self.center.x() - 30, self.center.y() - 70,
                        f"{self.force_percent:+.0f}%")
        
        # Направление
        if abs(self.force_percent) > 10:
            direction = "ВПЕРЕД" if self.force_percent > 0 else "НАЗАД"
            painter.drawText(self.center.x() - 25, self.center.y() - 50, direction)
    
    def mousePressEvent(self, event):
        """Handle mouse press on joystick"""
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            distance = math.sqrt((pos.x() - self.center.x())**2 + 
                               (pos.y() - self.center.y())**2)
            if distance <= self.radius + 20:
                self.is_dragging = True
                self.update_joystick_position(pos)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move while dragging"""
        if self.is_dragging:
            pos = event.position().toPoint()
            self.update_joystick_position(pos)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - return to center"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.joystick_pos = self.center
            self.force_percent = 0.0
            self.force_changed.emit(self.force_percent)
            self.update()
    
    def update_joystick_position(self, pos):
        """Update joystick position and calculate force"""
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.radius:
            dx = dx * self.radius / distance
            dy = dy * self.radius / distance
            distance = self.radius
        
        # Используем только вертикальное перемещение (вперед/назад)
        self.joystick_pos = QPoint(self.center.x() + dx, self.center.y() + dy)
        
        # Сила пропорциональна вертикальному смещению
        force_percent = -dy / self.radius * 100  # Отрицательный для вперед
        self.force_percent = max(-100, min(100, force_percent))
        
        self.force_changed.emit(self.force_percent)
        self.update()
    
    def set_force_percent(self, percent):
        """Set joystick position based on force percent"""
        self.force_percent = max(-100, min(100, percent))
        dy = -self.force_percent * self.radius / 100
        self.joystick_pos = QPoint(self.center.x(), self.center.y() + dy)
        self.update()