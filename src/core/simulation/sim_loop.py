"""Simulation thread for real-time physics updates"""

from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from loguru import logger
import time


class SimulationThread(QThread):
    """Separate thread for physics simulation"""
    
    telemetry_signal = Signal(dict)
    
    def __init__(self, physics_engine):
        super().__init__()
        self.physics_engine = physics_engine
        self.running = True
        self.paused = False
        self.dt = 0.02  # 50 Hz update rate
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
        logger.info("Simulation thread created")
    
    def run(self):
        """Main simulation loop"""
        logger.info("Simulation thread started")
        
        while self.running:
            # Проверка паузы
            if self.paused:
                self.mutex.lock()
                self.condition.wait(self.mutex)
                self.mutex.unlock()
                continue
            
            # Обновление физики
            start_time = time.time()
            
            self.physics_engine.update(self.dt)
            
            # Отправка телеметрии
            telemetry = self.physics_engine.get_telemetry()
            self.telemetry_signal.emit(telemetry)
            
            # Контроль времени выполнения для поддержания реального времени
            elapsed = time.time() - start_time
            if elapsed < self.dt:
                time.sleep(self.dt - elapsed)
        
        logger.info("Simulation thread stopped")
    
    def pause(self):
        """Pause simulation"""
        self.paused = True
        logger.info("Simulation paused")
    
    def resume(self):
        """Resume simulation"""
        self.paused = False
        self.condition.wakeOne()
        logger.info("Simulation resumed")
    
    def stop(self):
        """Stop simulation"""
        self.running = False
        if self.paused:
            self.resume()
        self.wait()
        logger.info("Simulation thread stopping")