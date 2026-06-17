"""Statistics window with detailed analytics and reports"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from loguru import logger
import pyqtgraph as pg
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class StatsWindow(QWidget):
    """Professional statistics and analytics dashboard"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.setup_ui()
        
        logger.info("Statistics window initialized")
    
    def setup_ui(self):
        """Setup statistics UI"""
        layout = QVBoxLayout()
        
        # Вкладки статистики
        self.tab_widget = QTabWidget()
        
        # Вкладка общей статистики
        overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(overview_tab, "Общая статистика")
        
        # Вкладка пользователей
        users_tab = self.create_users_stats_tab()
        self.tab_widget.addTab(users_tab, "Статистика пользователей")
        
        # Вкладка отчетов
        reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(reports_tab, "Отчеты")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_overview_tab(self):
        """Create overview statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Период фильтрации
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Период:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Последние 7 дней", "Последние 30 дней", "Последние 90 дней", "Все время"])
        self.period_combo.currentTextChanged.connect(self.refresh_stats)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # KPI карточки
        kpi_layout = QHBoxLayout()
        
        self.total_sessions_card = self.create_stat_card("Всего сессий", "0")
        kpi_layout.addWidget(self.total_sessions_card)
        
        self.avg_score_card = self.create_stat_card("Средний балл", "0%")
        kpi_layout.addWidget(self.avg_score_card)
        
        self.total_errors_card = self.create_stat_card("Всего ошибок", "0")
        kpi_layout.addWidget(self.total_errors_card)
        
        self.total_hours_card = self.create_stat_card("Общее время", "0 ч")
        kpi_layout.addWidget(self.total_hours_card)
        
        layout.addLayout(kpi_layout)
        
        # Графики
        graphs_layout = QHBoxLayout()
        
        # График прогресса
        self.progress_plot = self.create_stat_plot("Прогресс обучения", "Сессия", "Баллы")
        graphs_layout.addWidget(self.progress_plot)
        
        # График ошибок
        self.errors_plot = self.create_stat_plot("Ошибки по типам", "Тип ошибки", "Количество")
        graphs_layout.addWidget(self.errors_plot)
        
        layout.addLayout(graphs_layout)
        
        # Таблица лучших результатов
        top_group = QGroupBox("Лучшие результаты")
        top_layout = QVBoxLayout()
        
        self.top_scores_table = QTableWidget()
        self.top_scores_table.setColumnCount(4)
        self.top_scores_table.setHorizontalHeaderLabels(["Пользователь", "Баллы", "Ошибки", "Дата"])
        self.top_scores_table.setAlternatingRowColors(True)
        top_layout.addWidget(self.top_scores_table)
        
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        
        return tab
    
    def create_users_stats_tab(self):
        """Create per-user statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Выбор пользователя
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Пользователь:"))
        
        self.user_combo = QComboBox()
        self.load_users()
        self.user_combo.currentTextChanged.connect(self.refresh_user_stats)
        user_layout.addWidget(self.user_combo)
        
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        # Детальная статистика пользователя
        self.user_details_frame = QFrame()
        user_details_layout = QVBoxLayout()
        
        # KPI пользователя
        user_kpi_layout = QHBoxLayout()
        
        self.user_sessions_card = self.create_stat_card("Сессий", "0")
        user_kpi_layout.addWidget(self.user_sessions_card)
        
        self.user_avg_score_card = self.create_stat_card("Средний балл", "0%")
        user_kpi_layout.addWidget(self.user_avg_score_card)
        
        self.user_best_score_card = self.create_stat_card("Лучший результат", "0")
        user_kpi_layout.addWidget(self.user_best_score_card)
        
        self.user_total_errors_card = self.create_stat_card("Всего ошибок", "0")
        user_kpi_layout.addWidget(self.user_total_errors_card)
        
        user_details_layout.addLayout(user_kpi_layout)
        
        # График прогресса пользователя
        self.user_progress_plot = self.create_stat_plot("Прогресс пользователя", "Дата", "Баллы")
        user_details_layout.addWidget(self.user_progress_plot)
        
        # Таблица сессий пользователя
        self.user_sessions_table = QTableWidget()
        self.user_sessions_table.setColumnCount(5)
        self.user_sessions_table.setHorizontalHeaderLabels(["Дата", "Длительность", "Баллы", "Ошибки", "Завершена"])
        user_details_layout.addWidget(self.user_sessions_table)
        
        self.user_details_frame.setLayout(user_details_layout)
        layout.addWidget(self.user_details_frame)
        
        tab.setLayout(layout)
        return tab
    
    def create_reports_tab(self):
        """Create reports generation tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Тип отчета
        report_group = QGroupBox("Параметры отчета")
        report_layout = QVBoxLayout()
        
        report_type_layout = QHBoxLayout()
        report_type_layout.addWidget(QLabel("Тип отчета:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Общий отчет по обучению",
            "Детальный по пользователям",
            "Анализ ошибок",
            "Тренды производительности"
        ])
        report_type_layout.addWidget(self.report_type_combo)
        report_layout.addLayout(report_type_layout)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("С:"))
        self.report_start_date = QDateEdit()
        self.report_start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.report_start_date)
        
        date_layout.addWidget(QLabel("По:"))
        self.report_end_date = QDateEdit()
        self.report_end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.report_end_date)
        report_layout.addLayout(date_layout)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # Кнопки генерации
        buttons_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("📊 Сгенерировать отчет")
        self.generate_btn.clicked.connect(self.generate_report)
        buttons_layout.addWidget(self.generate_btn)
        
        self.export_pdf_btn = QPushButton("📄 Экспорт в PDF")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        buttons_layout.addWidget(self.export_pdf_btn)
        
        self.export_csv_btn = QPushButton("📈 Экспорт в CSV")
        self.export_csv_btn.clicked.connect(self.export_stats_to_csv)
        buttons_layout.addWidget(self.export_csv_btn)
        
        layout.addLayout(buttons_layout)
        
        # Предпросмотр отчета
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        
        self.report_preview = QLabel("Нажмите 'Сгенерировать отчет' для предпросмотра")
        self.report_preview.setStyleSheet("background-color: #2d2d2d; padding: 20px;")
        self.report_preview.setWordWrap(True)
        preview_layout.addWidget(self.report_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_stat_card(self, title, value):
        """Create statistics card widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #aaa; font-size: 11px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #00aaff; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label
        
        return card
    
    def create_stat_plot(self, title, xlabel, ylabel):
        """Create statistics plot"""
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#2d2d2d')
        plot_widget.setTitle(title, color='#ffffff', size='10pt')
        plot_widget.setLabel('left', ylabel, color='#aaa')
        plot_widget.setLabel('bottom', xlabel, color='#aaa')
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        return plot_widget
    
    def load_users(self):
        """Load users into combo box"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        users = self.app_controller.auth_service.get_all_users()
        self.user_combo.clear()
        for user in users:
            self.user_combo.addItem(f"{user.username} ({user.role})", user.id)
    
    def refresh_stats(self):
        """Refresh all statistics"""
        # Проверяем, есть ли пользователь
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        # Получаем общую статистику
        period = self.period_combo.currentText()
        days_map = {"Последние 7 дней": 7, "Последние 30 дней": 30, "Последние 90 дней": 90, "Все время": 3650}
        days = days_map.get(period, 30)
        
        report = self.app_controller.stats_service.get_all_sessions_report(days)
        
        # Обновляем KPI
        self.total_sessions_card.value_label.setText(str(report['total_sessions']))
        self.avg_score_card.value_label.setText(f"{report['avg_score']:.1f}%")
        self.total_errors_card.value_label.setText(str(report['total_errors']))
        
        # Обновляем таблицу лучших результатов
        self.update_top_scores_table(report['sessions'])
        
        # Обновляем графики
        self.update_progress_plot(report['sessions'])
    
    def update_top_scores_table(self, sessions):
        """Update top scores table"""
        # Сортируем по баллам
        sorted_sessions = sorted(sessions, key=lambda x: x.score or 0, reverse=True)[:10]
        
        self.top_scores_table.setRowCount(len(sorted_sessions))
        
        for row, session in enumerate(sorted_sessions):
            user_name = session.user.username if session.user else "Unknown"
            self.top_scores_table.setItem(row, 0, QTableWidgetItem(user_name))
            self.top_scores_table.setItem(row, 1, QTableWidgetItem(f"{session.score:.1f}" if session.score else "0"))
            self.top_scores_table.setItem(row, 2, QTableWidgetItem(str(session.errors_count)))
            self.top_scores_table.setItem(row, 3, QTableWidgetItem(session.start_time.strftime("%Y-%m-%d")))
        
        self.top_scores_table.resizeColumnsToContents()
    
    def update_progress_plot(self, sessions):
        """Update progress plot"""
        if sessions:
            # Сортируем по дате
            sorted_sessions = sorted(sessions, key=lambda x: x.start_time)
            
            dates = [s.start_time for s in sorted_sessions]
            scores = [s.score or 0 for s in sorted_sessions]
            
            x = np.arange(len(dates))
            
            self.progress_plot.clear()
            self.progress_plot.plot(x, scores, pen=pg.mkPen(color='#00aaff', width=2))
            self.progress_plot.plot(x, scores, symbol='o', symbolPen='#00aaff', symbolBrush='#00aaff')
    
    def refresh_user_stats(self):
        """Refresh statistics for selected user"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        current_index = self.user_combo.currentIndex()
        if current_index >= 0:
            user_id = self.user_combo.itemData(current_index)
            stats = self.app_controller.stats_service.get_user_stats(user_id)
            
            if stats:
                self.user_sessions_card.value_label.setText(str(stats['total_sessions']))
                self.user_avg_score_card.value_label.setText(f"{stats['avg_score']:.1f}%")
                self.user_best_score_card.value_label.setText(f"{stats['best_score']:.1f}")
                self.user_total_errors_card.value_label.setText(str(stats['total_errors']))
                
                # Обновляем таблицу сессий пользователя
                self.update_user_sessions_table(user_id)
    
    def update_user_sessions_table(self, user_id):
        """Update user sessions table"""
        with self.app_controller.db_manager.get_session() as session:
            from src.core.database.models import TrainingSession
            user_sessions = session.query(TrainingSession).filter(
                TrainingSession.user_id == user_id
            ).order_by(TrainingSession.start_time.desc()).all()
            
            self.user_sessions_table.setRowCount(len(user_sessions))
            
            for row, sess in enumerate(user_sessions):
                self.user_sessions_table.setItem(row, 0, QTableWidgetItem(sess.start_time.strftime("%Y-%m-%d %H:%M")))
                
                duration = sess.duration_seconds or 0
                duration_str = f"{duration // 60}:{duration % 60:02d}"
                self.user_sessions_table.setItem(row, 1, QTableWidgetItem(duration_str))
                
                self.user_sessions_table.setItem(row, 2, QTableWidgetItem(f"{sess.score:.1f}" if sess.score else "0"))
                self.user_sessions_table.setItem(row, 3, QTableWidgetItem(str(sess.errors_count)))
                
                completed = "Да" if sess.completed else "Нет"
                self.user_sessions_table.setItem(row, 4, QTableWidgetItem(completed))
            
            self.user_sessions_table.resizeColumnsToContents()
    
    def generate_report(self):
        """Generate report based on selected type"""
        report_type = self.report_type_combo.currentText()
        start_date = self.report_start_date.date().toPython()
        end_date = self.report_end_date.date().toPython()
        
        # Получаем данные за период
        with self.app_controller.db_manager.get_session() as session:
            from src.core.database.models import TrainingSession, User
            
            sessions = session.query(TrainingSession).join(User).filter(
                TrainingSession.start_time >= start_date,
                TrainingSession.start_time <= end_date
            ).all()
            
            if report_type == "Общий отчет по обучению":
                report_text = self.generate_general_report(sessions, start_date, end_date)
            elif report_type == "Детальный по пользователям":
                report_text = self.generate_user_detail_report(sessions)
            elif report_type == "Анализ ошибок":
                report_text = self.generate_errors_report(sessions)
            else:
                report_text = self.generate_trends_report(sessions)
            
            self.report_preview.setText(report_text)
    
    def generate_general_report(self, sessions, start_date, end_date):
        """Generate general training report"""
        total_sessions = len(sessions)
        if total_sessions == 0:
            return "Нет данных за выбранный период"
        
        total_students = len(set(s.user_id for s in sessions))
        avg_score = sum(s.score or 0 for s in sessions) / total_sessions
        total_errors = sum(s.errors_count for s in sessions)
        total_hours = sum(s.duration_seconds or 0 for s in sessions) / 3600
        
        report = f"""
        <b>ОТЧЕТ ПО ОБУЧЕНИЮ</b><br>
        Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}<br>
        <br>
        <b>Общие показатели:</b><br>
        • Всего сессий: {total_sessions}<br>
        • Всего студентов: {total_students}<br>
        • Средний балл: {avg_score:.1f}%<br>
        • Всего ошибок: {total_errors}<br>
        • Общее время обучения: {total_hours:.1f} часов<br>
        <br>
        <b>Эффективность обучения:</b><br>
        • Успеваемость: {"Высокая" if avg_score > 80 else "Средняя" if avg_score > 60 else "Низкая"}<br>
        • Ошибок на сессию: {total_errors/total_sessions:.1f}<br>
        """
        
        return report
    
    def generate_user_detail_report(self, sessions):
        """Generate detailed per-user report"""
        if not sessions:
            return "Нет данных"
        
        from collections import defaultdict
        user_stats = defaultdict(lambda: {'sessions': 0, 'total_score': 0, 'errors': 0})
        
        for session in sessions:
            username = session.user.username if session.user else "Unknown"
            user_stats[username]['sessions'] += 1
            user_stats[username]['total_score'] += session.score or 0
            user_stats[username]['errors'] += session.errors_count
        
        report = "<b>ДЕТАЛЬНЫЙ ОТЧЕТ ПО ПОЛЬЗОВАТЕЛЯМ</b><br><br>"
        
        for username, stats in user_stats.items():
            avg_score = stats['total_score'] / stats['sessions']
            report += f"""
            <b>{username}:</b><br>
            • Сессий: {stats['sessions']}<br>
            • Средний балл: {avg_score:.1f}%<br>
            • Всего ошибок: {stats['errors']}<br>
            • Ошибок на сессию: {stats['errors']/stats['sessions']:.1f}<br>
            <br>
            """
        
        return report
    
    def generate_errors_report(self, sessions):
        """Generate errors analysis report"""
        if not sessions:
            return "Нет данных"
        
        total_errors = sum(s.errors_count for s in sessions)
        
        report = f"""
        <b>АНАЛИЗ ОШИБОК</b><br>
        <br>
        <b>Общая статистика ошибок:</b><br>
        • Всего ошибок: {total_errors}<br>
        • Ошибок на сессию: {total_errors/len(sessions):.1f}<br>
        <br>
        <b>Рекомендации по улучшению:</b><br>
        • Основные ошибки: Превышение скорости, неточное позиционирование<br>
        • Рекомендуется: Дополнительные тренировки по плавному управлению<br>
        """
        
        return report
    
    def generate_trends_report(self, sessions):
        """Generate performance trends report"""
        if not sessions:
            return "Нет данных"
        
        # Сортируем по дате
        sorted_sessions = sorted(sessions, key=lambda x: x.start_time)
        
        # Анализируем тренд
        scores = [s.score or 0 for s in sorted_sessions]
        if len(scores) > 1:
            trend = scores[-1] - scores[0]
            trend_text = "положительный" if trend > 0 else "отрицательный" if trend < 0 else "стабильный"
        else:
            trend_text = "недостаточно данных"
        
        report = f"""
        <b>АНАЛИЗ ТРЕНДОВ ПРОИЗВОДИТЕЛЬНОСТИ</b><br>
        <br>
        <b>Тренды:</b><br>
        • Начальный средний балл: {scores[0]:.1f}%<br>
        • Конечный средний балл: {scores[-1]:.1f}%<br>
        • Тренд: {trend_text}<br>
        <br>
        <b>Прогноз:</b><br>
        • При сохранении текущего тренда ожидается улучшение результатов на {abs(trend):.1f}%<br>
        """
        
        return report
    
    def export_to_pdf(self):
        """Export report to PDF"""
        QMessageBox.information(self, "Экспорт в PDF", 
                               "Функция экспорта в PDF будет доступна в следующей версии")
    
    def export_stats_to_csv(self):
        """Export statistics to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить статистику", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            with self.app_controller.db_manager.get_session() as session:
                from src.core.database.models import TrainingSession, User
                
                sessions = session.query(TrainingSession).join(User).all()
                
                data = []
                for sess in sessions:
                    data.append({
                        'Пользователь': sess.user.username if sess.user else '',
                        'Дата начала': sess.start_time,
                        'Дата окончания': sess.end_time,
                        'Длительность (сек)': sess.duration_seconds,
                        'Баллы': sess.score,
                        'Ошибки': sess.errors_count,
                        'Завершена': sess.completed
                    })
                
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                QMessageBox.information(self, "Успех", f"Статистика экспортирована в {file_path}")
                logger.info(f"Statistics exported to {file_path}")
    
    def enable_export_features(self):
        """Enable export features for instructors"""
        self.export_csv_btn.setEnabled(True)
        self.export_pdf_btn.setEnabled(True)