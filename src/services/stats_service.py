"""Statistics calculation service"""

from sqlalchemy import func, and_
from datetime import datetime, timedelta
from loguru import logger
from src.core.database.models import TrainingSession, EventLog, EventType
from src.core.database.db_manager import DatabaseManager


class StatsService:
    """Calculates statistics for training sessions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_user_stats(self, user_id: int):
        """Get statistics for a specific user"""
        with self.db_manager.get_session() as session:
            sessions = session.query(TrainingSession).filter(
                TrainingSession.user_id == user_id,
                TrainingSession.completed == True
            ).all()
            
            if not sessions:
                return None
            
            total_sessions = len(sessions)
            avg_score = sum(s.score or 0 for s in sessions) / total_sessions
            total_errors = sum(s.errors_count for s in sessions)
            total_time = sum(s.duration_seconds or 0 for s in sessions)
            
            # Лучший результат
            best_session = max(sessions, key=lambda x: x.score or 0) if sessions else None
            
            return {
                'total_sessions': total_sessions,
                'avg_score': round(avg_score, 2),
                'total_errors': total_errors,
                'total_hours': round(total_time / 3600, 2),
                'best_score': best_session.score if best_session else 0,
                'best_session_date': best_session.start_time if best_session else None
            }
    
    def get_session_details(self, session_id: int):
        """Get detailed statistics for a specific session"""
        with self.db_manager.get_session() as session:
            training_session = session.query(TrainingSession).get(session_id)
            if not training_session:
                return None
            
            # Получаем события
            events = session.query(EventLog).filter(
                EventLog.session_id == session_id
            ).all()
            
            errors = [e for e in events if e.event_type == EventType.ERROR]
            movements = [e for e in events if e.event_type == EventType.MOVEMENT]
            
            return {
                'session': training_session,
                'total_events': len(events),
                'errors_count': len(errors),
                'movements_count': len(movements),
                'first_event': min(events, key=lambda x: x.timestamp) if events else None,
                'last_event': max(events, key=lambda x: x.timestamp) if events else None
            }
    
    def get_all_sessions_report(self, days: int = 30):
        """Get report for all sessions in last N days"""
        with self.db_manager.get_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            sessions = session.query(TrainingSession).filter(
                TrainingSession.start_time >= cutoff_date
            ).all()
            
            total_students = len(set(s.user_id for s in sessions))
            total_sessions = len(sessions)
            avg_score = sum(s.score or 0 for s in sessions) / total_sessions if sessions else 0
            
            return {
                'period_days': days,
                'total_students': total_students,
                'total_sessions': total_sessions,
                'avg_score': round(avg_score, 2),
                'total_errors': sum(s.errors_count for s in sessions),
                'sessions': sessions
            }