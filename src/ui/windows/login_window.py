"""Login dialog window with professional and clear interface"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from loguru import logger


class LoginDialog(QDialog):
    """Professional login dialog with clear interface"""
    
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.authenticated_user = None
        
        self.setWindowTitle("Авторизация - Crane Simulator Pro")
        self.setFixedSize(500, 550)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup login UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок с иконкой
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        title_label = QLabel("🏗️ ПОРТАЛЬНЫЙ КРАН")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("СИМУЛЯТОР - ПРОФЕССИОНАЛЬНАЯ СИСТЕМА ОБУЧЕНИЯ")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Форма входа
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Логин
        login_label = QLabel("ЛОГИН")
        login_label.setFont(QFont("Arial", 11, QFont.Bold))
        form_layout.addWidget(login_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите ваш логин")
        self.username_edit.setMinimumHeight(40)
        self.username_edit.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(self.username_edit)
        
        form_layout.addSpacing(10)
        
        # Пароль
        password_label = QLabel("ПАРОЛЬ")
        password_label.setFont(QFont("Arial", 11, QFont.Bold))
        form_layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(40)
        self.password_edit.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(self.password_edit)
        
        layout.addLayout(form_layout)
        
        layout.addSpacing(10)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_btn = QPushButton("ВОЙТИ В СИСТЕМУ")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_btn.clicked.connect(self.attempt_login)
        self.login_btn.setDefault(True)
        button_layout.addWidget(self.login_btn)
        
        cancel_btn = QPushButton("ОТМЕНА")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setFont(QFont("Arial", 12))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Разделитель
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)
        
        # Информационная панель с тестовыми данными
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 10px;")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_title = QLabel("📋 ТЕСТОВЫЕ УЧЕТНЫЕ ЗАПИСИ")
        info_title.setAlignment(Qt.AlignCenter)
        info_title.setFont(QFont("Arial", 11, QFont.Bold))
        info_title.setStyleSheet("color: #ffaa00;")
        info_layout.addWidget(info_title)
        
        # Администратор
        admin_row = QHBoxLayout()
        admin_row.setSpacing(10)
        admin_icon = QLabel("👑")
        admin_icon.setFont(QFont("Arial", 14))
        admin_row.addWidget(admin_icon)
        admin_label = QLabel("АДМИНИСТРАТОР:")
        admin_label.setFont(QFont("Arial", 10, QFont.Bold))
        admin_row.addWidget(admin_label)
        admin_row.addStretch()
        admin_code = QLabel("admin / admin123")
        admin_code.setFont(QFont("Courier", 10))
        admin_code.setStyleSheet("color: #00ff00;")
        admin_row.addWidget(admin_code)
        info_layout.addLayout(admin_row)
        
        # Инструктор
        instructor_row = QHBoxLayout()
        instructor_row.setSpacing(10)
        instructor_icon = QLabel("👨‍🏫")
        instructor_icon.setFont(QFont("Arial", 14))
        instructor_row.addWidget(instructor_icon)
        instructor_label = QLabel("ИНСТРУКТОР:")
        instructor_label.setFont(QFont("Arial", 10, QFont.Bold))
        instructor_row.addWidget(instructor_label)
        instructor_row.addStretch()
        instructor_code = QLabel("instructor / instructor123")
        instructor_code.setFont(QFont("Courier", 10))
        instructor_code.setStyleSheet("color: #00ff00;")
        instructor_row.addWidget(instructor_code)
        info_layout.addLayout(instructor_row)
        
        # Студент
        student_row = QHBoxLayout()
        student_row.setSpacing(10)
        student_icon = QLabel("🎓")
        student_icon.setFont(QFont("Arial", 14))
        student_row.addWidget(student_icon)
        student_label = QLabel("СТУДЕНТ:")
        student_label.setFont(QFont("Arial", 10, QFont.Bold))
        student_row.addWidget(student_label)
        student_row.addStretch()
        student_code = QLabel("student / student123")
        student_code.setFont(QFont("Courier", 10))
        student_code.setStyleSheet("color: #00ff00;")
        student_row.addWidget(student_code)
        info_layout.addLayout(student_row)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Подсказка
        hint_label = QLabel("💡 Подсказка: Нажмите Enter для быстрого входа")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
        
        # Устанавливаем фокус на поле логина
        self.username_edit.setFocus()
    
    def apply_styles(self):
        """Apply modern styles to login dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 10px 15px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
            }
            QPushButton {
                background-color: #4a9eff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6aafff;
            }
            QPushButton:pressed {
                background-color: #3a7ecc;
            }
            QPushButton:last-child {
                background-color: #555;
            }
            QPushButton:last-child:hover {
                background-color: #666;
            }
        """)
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(
                self, 
                "Ошибка", 
                "❌ Пожалуйста, заполните оба поля!\n\n"
                "Введите логин и пароль для входа в систему."
            )
            return
        
        user = self.auth_service.authenticate(username, password)
        
        if user:
            self.authenticated_user = user
            logger.info(f"User {username} logged in successfully")
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                "Ошибка авторизации", 
                "❌ НЕВЕРНЫЙ ЛОГИН ИЛИ ПАРОЛЬ!\n\n"
                "Пожалуйста, проверьте введенные данные.\n\n"
                "📋 ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ВХОДА:\n"
                "• Логин: admin | Пароль: admin123\n"
                "• Логин: student | Пароль: student123\n"
                "• Логин: instructor | Пароль: instructor123"
            )
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def get_authenticated_user(self):
        """Return authenticated user object"""
        return self.authenticated_user