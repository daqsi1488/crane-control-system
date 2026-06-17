"""Physics engine for portal crane simulation"""

import numpy as np
from scipy.integrate import odeint
from loguru import logger


class PhysicsEngine:
    """Realistic physics simulation for portal crane"""
    
    def __init__(self):
        # Параметры крана
        self.mass_trolley = 200.0  # кг
        self.mass_load = 1000.0    # кг
        self.cable_length = 10.0    # м
        self.gravity = 9.81         # м/с²
        self.max_speed = 2.0        # м/с
        self.max_acceleration = 1.5 # м/с²
        self.max_position = 5.0     # м (пределы перемещения)
        self.min_position = -5.0    # м
        
        # Коэффициенты сопротивления
        self.friction_coefficient = 0.05
        self.air_resistance = 0.01
        
        # Состояние системы [x, dx/dt, theta, dtheta/dt]
        # x - позиция тележки, theta - угол отклонения груза
        self.state = np.array([0.0, 0.0, 0.0, 0.0])
        
        # Управляющая сила
        self.control_force = 0.0
        
        # Время
        self.current_time = 0.0
        
        # Флаги ошибок
        self.is_overspeed = False
        self.is_overload = False
        self.limit_reached = False
        
        logger.info("Physics engine initialized")
    
    def equations_of_motion(self, state, t):
        """
        Дифференциальные уравнения движения портального крана
        state = [x, v, theta, omega]
        """
        x, v, theta, omega = state
        
        # Уравнения для крана с грузом на тросе (модель маятника)
        # M * x'' + m * L * theta'' = F_control - friction
        # L * theta'' + x'' + g * theta = 0 (линеаризованное для малых углов)
        
        M = self.mass_trolley
        m = self.mass_load
        L = self.cable_length
        g = self.gravity
        
        # Сила трения
        friction = self.friction_coefficient * v + self.air_resistance * v**2 * np.sign(v)
        
        # Матрица масс
        mass_matrix = np.array([[M + m, m * L],
                               [1, L]])
        
        # Правые части
        forces = np.array([self.control_force - friction,
                          -g * theta])
        
        try:
            # Решаем систему: mass_matrix * [v', omega'] = forces
            accelerations = np.linalg.solve(mass_matrix, forces)
            dv_dt = accelerations[0]
            domega_dt = accelerations[1]
        except np.linalg.LinAlgError:
            dv_dt = 0
            domega_dt = 0
        
        return [v, dv_dt, omega, domega_dt]
    
    def update(self, dt):
        """Update physics state using numerical integration"""
        try:
            # Решаем ОДУ для одного шага
            time_span = np.linspace(0, dt, 2)
            solution = odeint(self.equations_of_motion, self.state, time_span)
            self.state = solution[-1]
            
            # Ограничения на скорость и позицию
            self.state[1] = np.clip(self.state[1], -self.max_speed, self.max_speed)
            
            # Проверка пределов позиции
            if self.state[0] >= self.max_position:
                self.state[0] = self.max_position
                self.state[1] = 0
                self.limit_reached = True
            elif self.state[0] <= self.min_position:
                self.state[0] = self.min_position
                self.state[1] = 0
                self.limit_reached = True
            else:
                self.limit_reached = False
            
            # Проверка превышения скорости
            self.is_overspeed = abs(self.state[1]) >= self.max_speed * 0.95
            
            # Проверка перегруза
            self.is_overload = self.mass_load > 5000
            
            # Демпфирование колебаний груза
            self.state[3] *= 0.999
            
            self.current_time += dt
            
        except Exception as e:
            logger.error(f"Physics update error: {e}")
    
    def set_control_force(self, force):
        """Set control force for the trolley"""
        # Ограничиваем силу
        max_force = self.max_acceleration * (self.mass_trolley + self.mass_load)
        self.control_force = np.clip(force, -max_force, max_force)
    
    def set_load_mass(self, mass):
        """Set load mass"""
        self.mass_load = max(0, min(10000, mass))
        self.is_overload = self.mass_load > 5000
    
    def get_telemetry(self):
        """Get current telemetry data"""
        return {
            'position_x': self.state[0],
            'speed': self.state[1],
            'acceleration': self.state[2] if len(self.state) > 2 else 0,
            'cable_angle': self.state[2],
            'cable_angle_velocity': self.state[3],
            'cable_length': self.cable_length,
            'load_weight': self.mass_load,
            'is_overspeed': self.is_overspeed,
            'is_overload': self.is_overload,
            'limit_reached': self.limit_reached,
            'timestamp': self.current_time
        }
    
    def reset(self):
        """Reset physics engine to initial state"""
        self.state = np.array([0.0, 0.0, 0.0, 0.0])
        self.control_force = 0.0
        self.current_time = 0.0
        self.is_overspeed = False
        self.is_overload = False
        self.limit_reached = False
        self.mass_load = 1000.0
        logger.info("Physics engine reset")