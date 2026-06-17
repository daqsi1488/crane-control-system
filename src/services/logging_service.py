"""Event logging service for training sessions"""

from datetime import datetime
from loguru import logger
from src.core.database.models import TrainingSession, EventLog, EventType
from src.core.database.db_manager import DatabaseManager


class LoggingService:
    """Handles logging of training events and sessions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_session = None
    
    def start_session(self, user_id: int, task_name: str = "Free Practice") -> TrainingSession:
        """Start a new training session"""
        with self.db_manager.get_session() as session:
            training_session = TrainingSession(
                user_id=user_id,
                task_name=task_name,
                start_time=datetime.now()
            )
            session.add(training_session)
            session.flush()
            self.current_session = training_session
            logger.info(f"Started training session {training_session.id} for user {user_id}")
            return training_session
    
    def end_session(self, session_id: int, completed: bool = True):
        """End current training session"""
        with self.db_manager.get_session() as session:
            training_session = session.query(TrainingSession).get(session_id)
            if training_session:
                training_session.end_time = datetime.now()
                training_session.duration_seconds = int(
                    (training_session.end_time - training_session.start_time).total_seconds()
                )
                training_session.completed = completed
                logger.info(f"Ended training session {session_id}, duration: {training_session.duration_seconds}s")
    
    def log_event(self, session_id: int, user_id: int, event_type: EventType,
                  description: str, position_x: float = 0, position_y: float = 0,
                  speed: float = 0, load_weight: float = 0, severity: int = 1):
        """Log an event during training"""
        with self.db_manager.get_session() as session:
            event = EventLog(
                user_id=user_id,
                session_id=session_id,
                event_type=event_type,
                description=description,
                position_x=position_x,
                position_y=position_y,
                speed=speed,
                load_weight=load_weight,
                severity=severity,
                timestamp=datetime.now()
            )
            session.add(event)
            
            # Если это ошибка, обновляем счетчик ошибок в сессии
            if event_type == EventType.ERROR or severity >= 2:
                training_session = session.query(TrainingSession).get(session_id)
                if training_session:
                    training_session.errors_count += 1
            
            logger.debug(f"Event logged: {event_type} - {description}")