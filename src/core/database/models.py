"""SQLAlchemy ORM models for database"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()


class UserRole(str, Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default=UserRole.STUDENT)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sessions = relationship("TrainingSession", back_populates="user")
    events = relationship("EventLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class TrainingSession(Base):
    __tablename__ = 'training_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    task_name = Column(String(100))
    score = Column(Float)  # 0-100
    errors_count = Column(Integer, default=0)
    avg_precision = Column(Float)  # средняя точность позиционирования
    max_speed_reached = Column(Float)
    load_dropped = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    events = relationship("EventLog", back_populates="session")
    
    def __repr__(self):
        return f"<TrainingSession(user_id={self.user_id}, score={self.score})>"


class EventType(str, Enum):
    CONNECTION = "connection"
    MOVEMENT = "movement"
    LIFT = "lift"
    ERROR = "error"
    CRASH = "crash"
    LIMIT_REACHED = "limit_reached"
    USER_ACTION = "user_action"


class EventLog(Base):
    __tablename__ = 'event_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(Integer, ForeignKey('training_sessions.id'))
    timestamp = Column(DateTime, default=datetime.now)
    event_type = Column(String(50))
    description = Column(Text)
    position_x = Column(Float)
    position_y = Column(Float)
    speed = Column(Float)
    load_weight = Column(Float)
    severity = Column(Integer, default=1)  # 1=info, 2=warning, 3=critical
    
    # Relationships
    user = relationship("User", back_populates="events")
    session = relationship("TrainingSession", back_populates="events")
    
    def __repr__(self):
        return f"<EventLog(type='{self.event_type}', timestamp={self.timestamp})>"


class TelemetryData(Base):
    __tablename__ = 'telemetry'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('training_sessions.id'))
    timestamp = Column(DateTime, default=datetime.now)
    position_x = Column(Float)
    position_y = Column(Float)
    speed = Column(Float)
    acceleration = Column(Float)
    cable_angle = Column(Float)  # угол отклонения груза
    load_weight = Column(Float)
    motor_power = Column(Float)
    is_overspeed = Column(Boolean, default=False)
    is_overload = Column(Boolean, default=False)


def init_database(db_path: str = "data/crane.db"):
    """Initialize database with all tables"""
    import os
    from pathlib import Path
    
    # Создаем директорию если её нет
    Path(db_path).parent.mkdir(exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    
    return engine