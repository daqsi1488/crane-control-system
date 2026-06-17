"""Event journal window with filtering and export"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QDateTimeEdit,
    QLabel, QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor, QBrush
from loguru import logger
from src.core.database.models import EventLog, EventType
from datetime import datetime, timedelta
import pandas as pd


class JournalWindow(QWidget):
    """Event journal with advanced filtering"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.events = []
        self.setup_ui()
        
        logger.info("Journal window initialized")
    
    def setup_ui(self):
        """Setup journal UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Фильтры
        filter_group = QGroupBox("Фильтры событий")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Тип события:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все", "Движение", "Подъем", "Ошибка", "Соединение", "Предел"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("От:"))
        self.start_date = QDateTimeEdit()
        self.start_date.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("До:"))
        self.end_date = QDateTimeEdit()
        self.end_date.setDateTime(QDateTime.currentDateTime())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)
        
        filter_layout.addStretch()
        
        self.apply_btn = QPushButton("Применить фильтр")
        self.apply_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.apply_btn)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Таблица событий
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(6)
        self.journal_table.setHorizontalHeaderLabels(
            ["Время", "Пользователь", "Тип", "Описание", "Позиция X", "Скорость"]
        )
        self.journal_table.setAlternatingRowColors(True)
        self.journal_table.setSortingEnabled(True)
        self.journal_table.horizontalHeader().setStretchLastSection(True)
        self.journal_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                alternate-background-color: #353535;
                gridline-color: #444;
            }
            QTableWidget::item {
                color: #ddd;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #aaa;
                padding: 5px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.journal_table)
        
        # Кнопки экспорта
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.export_csv_btn = QPushButton("📊 Экспорт в CSV")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        export_layout.addWidget(self.export_csv_btn)
        
        self.export_excel_btn = QPushButton("📈 Экспорт в Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        export_layout.addWidget(self.export_excel_btn)
        
        self.clear_btn = QPushButton("🗑 Очистить журнал")
        self.clear_btn.clicked.connect(self.clear_journal)
        self.clear_btn.setStyleSheet("background-color: #8b3a3a;")
        export_layout.addWidget(self.clear_btn)
        
        layout.addLayout(export_layout)
        
        # Статус
        self.status_label = QLabel("Записей: 0")
        self.status_label.setStyleSheet("color: #aaa;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def refresh_journal(self):
        """Refresh journal data from database"""
        # Проверяем, есть ли пользователь
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        with self.app_controller.db_manager.get_session() as session:
            events = session.query(EventLog).filter(
                EventLog.user_id == self.app_controller.current_user.id
            ).order_by(EventLog.timestamp.desc()).limit(500).all()
            
            self.events = events
            self.update_table()
    
    def apply_filters(self):
        """Apply filters to journal"""
        # Проверяем, есть ли пользователь
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        event_type_map = {
            "Все": None,
            "Движение": "movement",
            "Подъем": "lift",
            "Ошибка": "error",
            "Соединение": "connection",
            "Предел": "limit_reached"
        }
        
        selected_type = self.type_filter.currentText()
        filter_type = event_type_map.get(selected_type)
        
        start_dt = self.start_date.dateTime().toPython()
        end_dt = self.end_date.dateTime().toPython()
        
        with self.app_controller.db_manager.get_session() as session:
            query = session.query(EventLog).filter(
                EventLog.user_id == self.app_controller.current_user.id,
                EventLog.timestamp >= start_dt,
                EventLog.timestamp <= end_dt
            )
            
            if filter_type:
                query = query.filter(EventLog.event_type == filter_type)
            
            events = query.order_by(EventLog.timestamp.desc()).all()
            self.events = events
            self.update_table()
    
    def update_table(self):
        """Update table with current events"""
        self.journal_table.setRowCount(len(self.events))
        
        for row, event in enumerate(self.events):
            # Время
            time_item = QTableWidgetItem(event.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self.journal_table.setItem(row, 0, time_item)
            
            # Пользователь
            user_item = QTableWidgetItem(event.user.username if event.user else "Unknown")
            self.journal_table.setItem(row, 1, user_item)
            
            # Тип
            type_text = self.get_event_type_text(event.event_type)
            type_item = QTableWidgetItem(type_text)
            
            # Цвет для ошибок
            if event.event_type == "error":
                type_item.setBackground(QBrush(QColor(139, 58, 58, 100)))
                type_item.setForeground(QBrush(QColor(255, 100, 100)))
            elif event.severity >= 2:
                type_item.setBackground(QBrush(QColor(255, 170, 0, 80)))
            
            self.journal_table.setItem(row, 2, type_item)
            
            # Описание
            desc_item = QTableWidgetItem(event.description or "")
            self.journal_table.setItem(row, 3, desc_item)
            
            # Позиция
            pos_item = QTableWidgetItem(f"{event.position_x:.2f} м" if event.position_x else "")
            self.journal_table.setItem(row, 4, pos_item)
            
            # Скорость
            speed_item = QTableWidgetItem(f"{event.speed:.2f} м/с" if event.speed else "")
            self.journal_table.setItem(row, 5, speed_item)
        
        # Настройка ширины колонок
        self.journal_table.resizeColumnsToContents()
        self.status_label.setText(f"Записей: {len(self.events)}")
    
    def get_event_type_text(self, event_type):
        """Convert event type to Russian text"""
        types = {
            "connection": "🔌 Соединение",
            "movement": "🚚 Движение",
            "lift": "🏗 Подъем",
            "error": "⚠ Ошибка",
            "crash": "💥 Столкновение",
            "limit_reached": "⛔ Предел",
            "user_action": "👤 Действие"
        }
        return types.get(event_type, event_type)
    
    def export_to_csv(self):
        """Export journal to CSV file"""
        if not self.events:
            QMessageBox.warning(self, "Нет данных", "Нет событий для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            data = []
            for event in self.events:
                data.append({
                    'timestamp': event.timestamp,
                    'user': event.user.username if event.user else '',
                    'event_type': event.event_type,
                    'description': event.description,
                    'position_x': event.position_x,
                    'speed': event.speed,
                    'severity': event.severity
                })
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            QMessageBox.information(self, "Успех", f"Экспортировано {len(data)} записей")
            logger.info(f"Journal exported to {file_path}")
    
    def export_to_excel(self):
        """Export journal to Excel file"""
        if not self.events:
            QMessageBox.warning(self, "Нет данных", "Нет событий для экспорта")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить Excel", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            data = []
            for event in self.events:
                data.append({
                    'Время': event.timestamp,
                    'Пользователь': event.user.username if event.user else '',
                    'Тип': event.event_type,
                    'Описание': event.description,
                    'Позиция X': event.position_x,
                    'Скорость': event.speed,
                    'Вес груза': event.load_weight,
                    'Важность': event.severity
                })
            
            df = pd.DataFrame(data)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Журнал событий', index=False)
                
                worksheet = writer.sheets['Журнал событий']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            QMessageBox.information(self, "Успех", f"Экспортировано {len(data)} записей в Excel")
            logger.info(f"Journal exported to {file_path}")
    
    def clear_journal(self):
        """Clear journal (admin only)"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        if self.app_controller.current_user.role != 'admin':
            QMessageBox.warning(self, "Доступ запрещен", "Только администратор может очищать журнал")
            return
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите очистить весь журнал?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with self.app_controller.db_manager.get_session() as session:
                session.query(EventLog).delete()
                logger.warning(f"Journal cleared by {self.app_controller.current_user.username}")
            
            self.refresh_journal()
            QMessageBox.information(self, "Успех", "Журнал очищен")