"""Real-time plotting widget using PyQtGraph"""

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
import numpy as np
from collections import deque


class LivePlotWidget(QWidget):
    """Real-time plotting widget for telemetry data"""
    
    def __init__(self, title, xlabel, ylabel, max_points=500):
        super().__init__()
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.max_points = max_points
        
        self.setup_ui()
        self.data_x = deque(maxlen=max_points)
        self.data_y = deque(maxlen=max_points)
    
    def setup_ui(self):
        """Setup plot widget"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем график
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2d2d2d')
        self.plot_widget.setTitle(self.title, color='#ffffff', size='12pt')
        self.plot_widget.setLabel('left', self.ylabel, color='#aaa', size='10pt')
        self.plot_widget.setLabel('bottom', self.xlabel, color='#aaa', size='10pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Настройка осей
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#aaa'))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#aaa'))
        self.plot_widget.getAxis('left').setTextPen('#aaa')
        self.plot_widget.getAxis('bottom').setTextPen('#aaa')
        
        # Создаем кривую
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#00aaff', width=2))
        
        # Добавляем зоны предупреждений
        self.warning_zone = pg.LinearRegionItem([0, 0], brush=pg.mkBrush(255, 100, 50, 50))
        self.warning_zone.setVisible(False)
        self.plot_widget.addItem(self.warning_zone)
        
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
    
    def add_data_point(self, x, y):
        """Add a data point to the plot"""
        self.data_x.append(x)
        self.data_y.append(y)
        self.update_plot()
    
    def add_data_points(self, x_values, y_values):
        """Add multiple data points"""
        for x, y in zip(x_values, y_values):
            self.data_x.append(x)
            self.data_y.append(y)
        self.update_plot()
    
    def update_plot(self):
        """Update the plot with current data"""
        if len(self.data_x) > 1:
            self.curve.setData(list(self.data_x), list(self.data_y))
            self.plot_widget.autoRange()
    
    def set_warning_zone(self, y_min, y_max):
        """Set a warning zone on the plot"""
        self.warning_zone.setRegion([y_min, y_max])
        self.warning_zone.setVisible(True)
    
    def clear(self):
        """Clear all data from plot"""
        self.data_x.clear()
        self.data_y.clear()
        self.curve.clear()
        self.warning_zone.setVisible(False)
    
    def set_title(self, title):
        """Set plot title"""
        self.title = title
        self.plot_widget.setTitle(title, color='#ffffff')
    
    def export_data(self, filepath):
        """Export plot data to CSV"""
        import pandas as pd
        df = pd.DataFrame({
            self.xlabel: list(self.data_x),
            self.ylabel: list(self.data_y)
        })
        df.to_csv(filepath, index=False)