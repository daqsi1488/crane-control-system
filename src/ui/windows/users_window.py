"""User management window for admin"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QDialog, QFormLayout,
    QLineEdit, QComboBox, QMessageBox, QGroupBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from loguru import logger


class UsersWindow(QWidget):
    """User management interface for administrators"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.setup_ui()
        
        logger.info("Users window initialized")
    
    def setup_ui(self):
        """Setup users management UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Добавить пользователя")
        self.add_btn.clicked.connect(self.add_user)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏ Редактировать")
        self.edit_btn.clicked.connect(self.edit_user)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑 Удалить")
        self.delete_btn.clicked.connect(self.delete_user)
        self.delete_btn.setStyleSheet("background-color: #8b3a3a;")
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.load_users)
        buttons_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(
            ["ID", "Логин", "Полное имя", "Роль", "Email", "Последний вход"]
        )
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSortingEnabled(True)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                alternate-background-color: #353535;
                gridline-color: #444;
            }
            QTableWidget::item {
                color: #ddd;
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #aaa;
                padding: 8px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.users_table)
        
        # Информационная панель
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Выберите пользователя для просмотра деталей")
        self.info_label.setStyleSheet("color: #aaa;")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.setLayout(layout)
        
        # Подключаем сигнал выбора
        self.users_table.itemSelectionChanged.connect(self.on_user_selected)
        
        # Загружаем пользователей после создания UI
        self.load_users()
    
    def load_users(self):
        """Load users into table"""
        # Проверяем, есть ли пользователь и БД
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            self.users_table.setRowCount(0)
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        users = self.app_controller.auth_service.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # ID
            id_item = QTableWidgetItem(str(user['id']))
            id_item.setData(Qt.UserRole, user['id'])
            self.users_table.setItem(row, 0, id_item)
            
            # Логин
            login_item = QTableWidgetItem(user['username'])
            self.users_table.setItem(row, 1, login_item)
            
            # Полное имя
            name_item = QTableWidgetItem(user.get('full_name') or "")
            self.users_table.setItem(row, 2, name_item)
            
            # Роль
            role_item = QTableWidgetItem(self.get_role_text(user['role']))
            if user['role'] == 'admin':
                role_item.setBackground(QBrush(QColor(139, 58, 58, 100)))
                role_item.setForeground(QBrush(QColor(255, 150, 150)))
            elif user['role'] == 'instructor':
                role_item.setBackground(QBrush(QColor(58, 139, 58, 100)))
            self.users_table.setItem(row, 3, role_item)
            
            # Email
            email_item = QTableWidgetItem(user.get('email') or "")
            self.users_table.setItem(row, 4, email_item)
            
            # Последний вход
            last_login = user.get('last_login')
            last_login_str = last_login.strftime("%Y-%m-%d %H:%M") if last_login else "Никогда"
            last_login_item = QTableWidgetItem(last_login_str)
            self.users_table.setItem(row, 5, last_login_item)
        
        self.users_table.resizeColumnsToContents()
        self.users_table.horizontalHeader().setStretchLastSection(True)
        
        logger.info(f"Loaded {len(users)} users")
        
        # Обновляем доступность функций
        if self.app_controller.current_user:
            is_admin = self.app_controller.current_user.get('role') == 'admin'
            self.add_btn.setEnabled(is_admin)
            self.edit_btn.setEnabled(is_admin)
            self.delete_btn.setEnabled(is_admin)
            self.setEnabled(True)
        else:
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def get_role_text(self, role):
        """Convert role to Russian text"""
        roles = {
            'admin': '👑 Администратор',
            'instructor': '👨‍🏫 Инструктор',
            'student': '🎓 Студент'
        }
        return roles.get(role, role)
    
    def on_user_selected(self):
        """Handle user selection"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        selected = self.users_table.selectedItems()
        if selected:
            row = selected[0].row()
            user_id = self.users_table.item(row, 0).data(Qt.UserRole)
            username = self.users_table.item(row, 1).text()
            role = self.users_table.item(row, 3).text()
            
            stats = self.app_controller.stats_service.get_user_stats(user_id)
            
            if stats:
                info_text = f"""
                <b>Пользователь:</b> {username}<br>
                <b>Роль:</b> {role}<br>
                <b>Всего сессий:</b> {stats['total_sessions']}<br>
                <b>Средний балл:</b> {stats['avg_score']:.1f}%<br>
                <b>Всего ошибок:</b> {stats['total_errors']}<br>
                <b>Общее время:</b> {stats['total_hours']:.1f} часов<br>
                """
            else:
                info_text = f"<b>Пользователь:</b> {username}<br>Нет данных о тренировках"
            
            self.info_label.setText(info_text)
    
    def add_user(self):
        """Add new user dialog"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        dialog = UserDialog(self.app_controller, parent=self)
        if dialog.exec():
            self.load_users()
            logger.info("User added successfully")
    
    def edit_user(self):
        """Edit selected user"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        selected = self.users_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для редактирования")
            return
        
        row = selected[0].row()
        user_id = self.users_table.item(row, 0).data(Qt.UserRole)
        
        user_data = self.app_controller.auth_service.get_user_by_id(user_id)
        
        if user_data:
            dialog = UserDialog(self.app_controller, user_data, parent=self)
            if dialog.exec():
                self.load_users()
                logger.info(f"User {user_data['username']} edited")
    
    def delete_user(self):
        """Delete selected user"""
        if not hasattr(self.app_controller, 'current_user') or not self.app_controller.current_user:
            return
        
        selected = self.users_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для удаления")
            return
        
        row = selected[0].row()
        user_id = self.users_table.item(row, 0).data(Qt.UserRole)
        username = self.users_table.item(row, 1).text()
        
        # Нельзя удалить самого себя
        if user_id == self.app_controller.current_user.get('id'):
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить самого себя")
            return
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    f"Вы уверены, что хотите удалить пользователя '{username}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.app_controller.auth_service.delete_user(user_id)
            if success:
                self.load_users()
                logger.info(f"User {username} deleted")
                QMessageBox.information(self, "Успех", "Пользователь удален")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить пользователя")


class UserDialog(QDialog):
    """Dialog for adding/editing users"""
    
    def __init__(self, app_controller, user_data=None, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.user_data = user_data
        self.setWindowTitle("Добавление пользователя" if not user_data else "Редактирование пользователя")
        self.setFixedSize(400, 350)
        
        self.setup_ui()
        
        if user_data:
            self.load_user_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Логин
        self.username_edit = QLineEdit()
        form_layout.addRow("Логин:", self.username_edit)
        
        # Пароль
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        if self.user_data:
            self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять")
        form_layout.addRow("Пароль:", self.password_edit)
        
        # Полное имя
        self.fullname_edit = QLineEdit()
        form_layout.addRow("Полное имя:", self.fullname_edit)
        
        # Роль
        self.role_combo = QComboBox()
        self.role_combo.addItems(["student", "instructor", "admin"])
        self.role_combo.setCurrentText("student")
        form_layout.addRow("Роль:", self.role_combo)
        
        # Email
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_user_data(self):
        """Load user data into form"""
        self.username_edit.setText(self.user_data['username'])
        self.fullname_edit.setText(self.user_data.get('full_name') or "")
        self.role_combo.setCurrentText(self.user_data['role'])
        self.email_edit.setText(self.user_data.get('email') or "")
    
    def save_user(self):
        """Save user data"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        fullname = self.fullname_edit.text().strip()
        role = self.role_combo.currentText()
        email = self.email_edit.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Ошибка", "Логин обязателен")
            return
        
        if not self.user_data and not password:
            QMessageBox.warning(self, "Ошибка", "Пароль обязателен для нового пользователя")
            return
        
        if self.user_data:
            # Редактирование существующего пользователя
            with self.app_controller.db_manager.get_session() as session:
                from src.core.database.models import User
                db_user = session.query(User).get(self.user_data['id'])
                
                if db_user:
                    db_user.username = username
                    db_user.full_name = fullname
                    db_user.role = role
                    db_user.email = email
                    
                    if password:
                        import hashlib
                        db_user.password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    session.commit()
                    logger.info(f"User {username} updated")
                    self.accept()
        else:
            # Создание нового пользователя
            success = self.app_controller.auth_service.create_user(
                username=username,
                password=password,
                full_name=fullname,
                role=role,
                email=email
            )
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", f"Пользователь '{username}' уже существует")