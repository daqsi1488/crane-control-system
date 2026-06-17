"""Authentication and user management service"""

import hashlib
from datetime import datetime
from loguru import logger
from src.core.database.models import User, UserRole
from src.core.database.db_manager import DatabaseManager


class AuthService:
    """Handles user authentication and management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _create_default_users(self):
        """Create default users if none exist"""
        with self.db_manager.get_session() as session:
            if session.query(User).count() == 0:
                # Создаем администратора
                admin = User(
                    username="admin",
                    password_hash=self._hash_password("admin123"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    email="admin@cranesim.com"
                )
                
                # Создаем инструктора
                instructor = User(
                    username="instructor",
                    password_hash=self._hash_password("instructor123"),
                    full_name="John Instructor",
                    role=UserRole.INSTRUCTOR,
                    email="instructor@cranesim.com"
                )
                
                # Создаем тестового студента
                student = User(
                    username="student",
                    password_hash=self._hash_password("student123"),
                    full_name="Test Student",
                    role=UserRole.STUDENT,
                    email="student@cranesim.com"
                )
                
                session.add_all([admin, instructor, student])
                logger.info("Default users created")
    
    def authenticate(self, username: str, password: str):
        """Authenticate user - returns a detached copy of user data"""
        self._create_default_users()
        
        password_hash = self._hash_password(password)
        
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.username == username,
                User.password_hash == password_hash,
                User.is_active == True
            ).first()
            
            if user:
                # Обновляем время последнего входа
                user.last_login = datetime.now()
                session.commit()
                
                # Создаем detached копию (словарь с данными)
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'email': user.email,
                    'last_login': user.last_login
                }
                logger.info(f"User {username} authenticated successfully")
                return user_data
            
            logger.warning(f"Failed authentication attempt for {username}")
            return None
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str, email: str = None) -> bool:
        """Create new user"""
        with self.db_manager.get_session() as session:
            # Проверяем, не существует ли уже пользователь
            if session.query(User).filter(User.username == username).first():
                logger.warning(f"User {username} already exists")
                return False
            
            user = User(
                username=username,
                password_hash=self._hash_password(password),
                full_name=full_name,
                role=role,
                email=email
            )
            
            session.add(user)
            session.commit()
            logger.info(f"User {username} created successfully")
            return True
    
    def get_all_users(self):
        """Get all users as detached data"""
        with self.db_manager.get_session() as session:
            users = session.query(User).all()
            # Возвращаем список словарей вместо объектов ORM
            return [
                {
                    'id': u.id,
                    'username': u.username,
                    'full_name': u.full_name,
                    'role': u.role,
                    'email': u.email,
                    'last_login': u.last_login,
                    'is_active': u.is_active
                }
                for u in users
            ]
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID as detached data"""
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'role': user.role,
                    'email': user.email,
                    'last_login': user.last_login,
                    'is_active': user.is_active
                }
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        with self.db_manager.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                logger.info(f"User {user.username} deleted")
                return True
            return False