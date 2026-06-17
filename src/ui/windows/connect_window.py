"""Connection window for crane connectivity"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QRadioButton, QSpinBox, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from loguru import logger


class ConnectWindow(QDialog):
    """Connection window for local and remote crane access"""
    
    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.connected = False
        self.setWindowTitle("Подключение к портальному крану")
        self.setFixedSize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup connection UI"""
        layout = QVBoxLayout()
        
        # Вкладки для разных типов подключения
        self.tab_widget = QTabWidget()
        
        # Вкладка локального подключения
        local_tab = self.create_local_tab()
        self.tab_widget.addTab(local_tab, "Локальное подключение")
        
        # Вкладка удаленного подключения
        remote_tab = self.create_remote_tab()
        self.tab_widget.addTab(remote_tab, "Удаленное подключение")
        
        layout.addWidget(self.tab_widget)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.connect_to_crane)
        self.connect_btn.setStyleSheet("background-color: #2d6a2d; padding: 10px;")
        button_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.clicked.connect(self.disconnect_from_crane)
        self.disconnect_btn.setEnabled(False)
        button_layout.addWidget(self.disconnect_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Статус подключения
        self.status_group = QGroupBox("Статус подключения")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("● Не подключен")
        self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.connection_details = QLabel("")
        self.connection_details.setStyleSheet("color: #aaa; font-size: 10px;")
        status_layout.addWidget(self.connection_details)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        self.status_group.setLayout(status_layout)
        layout.addWidget(self.status_group)
        
        self.setLayout(layout)
    
    def create_local_tab(self):
        """Create local connection tab (Modbus, Serial, etc.)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Протокол подключения
        protocol_group = QGroupBox("Протокол подключения")
        protocol_layout = QVBoxLayout()
        
        self.modbus_radio = QRadioButton("Modbus TCP/IP")
        self.modbus_radio.setChecked(True)
        protocol_layout.addWidget(self.modbus_radio)
        
        self.opc_radio = QRadioButton("OPC UA")
        protocol_layout.addWidget(self.opc_radio)
        
        self.serial_radio = QRadioButton("RS-485 (Serial)")
        protocol_layout.addWidget(self.serial_radio)
        
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        # Параметры Modbus
        self.modbus_group = QGroupBox("Параметры Modbus")
        modbus_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("IP адрес:"))
        self.modbus_host = QLineEdit("192.168.1.100")
        host_layout.addWidget(self.modbus_host)
        modbus_layout.addLayout(host_layout)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Порт:"))
        self.modbus_port = QSpinBox()
        self.modbus_port.setRange(1, 65535)
        self.modbus_port.setValue(502)
        port_layout.addWidget(self.modbus_port)
        modbus_layout.addLayout(port_layout)
        
        self.modbus_group.setLayout(modbus_layout)
        layout.addWidget(self.modbus_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        
        return tab
    
    def create_remote_tab(self):
        """Create remote connection tab (WebSocket, VPN, etc.)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Тип удаленного подключения
        remote_type_group = QGroupBox("Тип удаленного подключения")
        remote_type_layout = QVBoxLayout()
        
        self.websocket_radio = QRadioButton("WebSocket (Cloud)")
        self.websocket_radio.setChecked(True)
        remote_type_layout.addWidget(self.websocket_radio)
        
        self.vpn_radio = QRadioButton("VPN туннель")
        remote_type_layout.addWidget(self.vpn_radio)
        
        remote_type_group.setLayout(remote_type_layout)
        layout.addWidget(remote_type_group)
        
        # Параметры WebSocket
        self.ws_group = QGroupBox("WebSocket параметры")
        ws_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("WebSocket URL:"))
        self.ws_url = QLineEdit("wss://crane-remote.company.com:8765")
        url_layout.addWidget(self.ws_url)
        ws_layout.addLayout(url_layout)
        
        auth_layout = QHBoxLayout()
        auth_layout.addWidget(QLabel("API Key:"))
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.api_key)
        ws_layout.addLayout(auth_layout)
        
        self.ws_group.setLayout(ws_layout)
        layout.addWidget(self.ws_group)
        
        # Параметры VPN
        self.vpn_group = QGroupBox("VPN параметры")
        vpn_layout = QVBoxLayout()
        
        vpn_host_layout = QHBoxLayout()
        vpn_host_layout.addWidget(QLabel("VPN сервер:"))
        self.vpn_server = QLineEdit("vpn.company.com")
        vpn_host_layout.addWidget(self.vpn_server)
        vpn_layout.addLayout(vpn_host_layout)
        
        vpn_user_layout = QHBoxLayout()
        vpn_user_layout.addWidget(QLabel("Пользователь:"))
        self.vpn_user = QLineEdit()
        vpn_user_layout.addWidget(self.vpn_user)
        vpn_layout.addLayout(vpn_user_layout)
        
        vpn_pass_layout = QHBoxLayout()
        vpn_pass_layout.addWidget(QLabel("Пароль:"))
        self.vpn_password = QLineEdit()
        self.vpn_password.setEchoMode(QLineEdit.Password)
        vpn_pass_layout.addWidget(self.vpn_password)
        vpn_layout.addLayout(vpn_pass_layout)
        
        self.vpn_group.setLayout(vpn_layout)
        self.vpn_group.setVisible(False)
        layout.addWidget(self.vpn_group)
        
        # Подключаем переключение радио-кнопок
        self.websocket_radio.toggled.connect(lambda: self.ws_group.setVisible(True))
        self.websocket_radio.toggled.connect(lambda: self.vpn_group.setVisible(False))
        self.vpn_radio.toggled.connect(lambda: self.ws_group.setVisible(False))
        self.vpn_radio.toggled.connect(lambda: self.vpn_group.setVisible(True))
        
        layout.addStretch()
        tab.setLayout(layout)
        
        return tab
    
    def connect_to_crane(self):
        """Handle connection to crane"""
        current_tab = self.tab_widget.currentIndex()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.connect_btn.setEnabled(False)
        
        # Имитация процесса подключения
        QTimer.singleShot(2000, self.simulate_connection)
    
    def simulate_connection(self):
        """Simulate connection process"""
        # Здесь будет реальная логика подключения
        self.connected = True
        self.status_label.setText("● Подключен к крану")
        self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            connection_info = f"Modbus TCP: {self.modbus_host.text()}:{self.modbus_port.value()}"
        else:
            connection_info = f"WebSocket: {self.ws_url.text()}"
        
        self.connection_details.setText(connection_info)
        
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "Успех", f"Подключение к крану установлено!\n{connection_info}")
        logger.info(f"Crane connected via {connection_info}")
    
    def disconnect_from_crane(self):
        """Handle disconnection from crane"""
        self.connected = False
        self.status_label.setText("● Отключен от крана")
        self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        self.connection_details.setText("")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        
        QMessageBox.information(self, "Отключение", "Соединение с краном разорвано")
        logger.info("Crane disconnected")