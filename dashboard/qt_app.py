import sys
import os

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QSystemTrayIcon, QMenu, QLabel,
                             QScrollArea, QFrame)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, pyqtSlot

from dashboard.qt_ui_components import SidebarButton, DeviceCard, CircularHealthGauge
from dashboard.qt_monitor import TelemetryWorker

class NANDGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NANDGuard+ AI Storage Utility")
        self.setMinimumSize(900, 600)
        
        # Set app icon
        icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #21252b; border-right: 1px solid #3e4451;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 15)
        sidebar_layout.setSpacing(0)
        
        # Navigation Buttons Container
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(5)
        
        self.btn_dashboard = SidebarButton("Dashboard", active=True)
        self.btn_devices = SidebarButton("Devices")
        self.btn_settings = SidebarButton("Settings")
        
        nav_layout.addWidget(self.btn_dashboard)
        nav_layout.addWidget(self.btn_devices)
        nav_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(nav_container)
        
        sidebar_layout.addStretch()
        
        # Sidebar Footer
        footer_lbl = QLabel("v1.0.0 Stable\n© 2026 NANDGuard")
        footer_lbl.setStyleSheet("font-size: 10px; color: #5c6370; margin-left: 15px;")
        sidebar_layout.addWidget(footer_lbl)
        
        main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        self.init_dashboard_page()
        
        # Style
        self.setStyleSheet("""
            QMainWindow { background-color: #282c34; }
            QLabel { color: #abb2bf; font-family: 'Segoe UI', Arial; }
        """)

        # Start Telemetry Worker
        self.worker = TelemetryWorker(interval_seconds=60)
        self.worker.health_data_ready.connect(self.on_telemetry_update)
        self.worker.notification_triggered.connect(self.on_notification)
        self.worker.start()

    def on_notification(self, title, message):
        if tray_icon:
            tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Warning, 5000)

    def init_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Device Health Overview")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Hero Section
        hero = QHBoxLayout()
        self.main_gauge = CircularHealthGauge()
        hero.addWidget(self.main_gauge)
        
        hero_info = QVBoxLayout()
        self.lbl_main_status = QLabel("Monitoring...")
        self.lbl_main_status.setStyleSheet("font-size: 18px; font-weight: bold;")
        hero_info.addWidget(self.lbl_main_status)
        
        self.lbl_stats = QLabel("Connecting to AI Engine...")
        self.lbl_stats.setStyleSheet("color: #abb2bf; font-size: 14px;")
        hero_info.addWidget(self.lbl_stats)
        
        self.lbl_updated = QLabel("Last Scan: --:--:--")
        self.lbl_updated.setStyleSheet("color: #636d83; font-size: 11px; font-style: italic;")
        hero_info.addWidget(self.lbl_updated)
        
        hero.addLayout(hero_info, 1)
        
        layout.addLayout(hero)
        layout.addSpacing(10)
        
        # Recommendations Panel
        lbl_recs_header = QLabel("Actionable Recommendations")
        lbl_recs_header.setStyleSheet("font-weight: bold; color: #abb2bf; margin-top: 5px;")
        layout.addWidget(lbl_recs_header)
        
        self.lbl_recs = QLabel("• Analyzing health patterns...")
        self.lbl_recs.setWordWrap(True)
        self.lbl_recs.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
                line-height: 180%;
                margin-top: 5px;
                padding-left: 5px;
            }
        """)
        layout.addWidget(self.lbl_recs)
        layout.addSpacing(15)
        
        # Device Cards Container (Scrollable)
        lbl_dev_header = QLabel("Physical Devices")
        lbl_dev_header.setStyleSheet("font-weight: bold; color: #abb2bf;")
        layout.addWidget(lbl_dev_header)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.devices_layout = QVBoxLayout(self.scroll_content)
        self.devices_layout.setContentsMargins(0, 5, 10, 5)
        self.devices_layout.setSpacing(10)
        self.devices_layout.addStretch() # Initial stretch
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        self.content_stack.addWidget(page)

    @pyqtSlot(list)
    def on_telemetry_update(self, devices):
        # Clear old cards
        while self.devices_layout.count() > 1: # Keep the stretch
            item = self.devices_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not devices:
            return
            
        # Update Dashboard View with first device by default
        self.update_dashboard_view(devices[0])
        
        # Add cards for all devices
        for dev in devices:
            card = DeviceCard(dev)
            card.clicked.connect(self.update_dashboard_view)
            self.devices_layout.insertWidget(self.devices_layout.count() - 1, card)

    def update_dashboard_view(self, dev):
        """Updates the hero section and recommendations for a selected device."""
        if 'health' in dev:
            score = dev['health']['score']
            self.main_gauge.set_value(score)
            
            risk = dev['health']['risk_level']
            days = dev['health']['estimated_days']
            status = dev.get('status', 'Healthy') # Default to Healthy if health exists
            anomaly = "DETECTED" if dev.get('anomaly') == -1 else "No"
            
            self.lbl_main_status.setText(f"System Health: {risk}")
            
            color = "#00ffff" if score > 75 else "#ffaa00" if score > 40 else "#ff3c3c"
            self.lbl_main_status.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
            
            source = dev.get('source', 'Unknown')
            source_color = "#4caf50" if "LIVE" in source.upper() else "#ff5252"
            
            stats_text = (f"RUL: {days} days | Status: {status} | Anomaly: {anomaly}<br>"
                         f"Source: <span style='color: {source_color};'>{source}</span>")
            self.lbl_stats.setText(stats_text)
            
            # Update Recommendations
            recs = dev.get('recommendations', [])
            if recs:
                self.lbl_recs.setText("\n".join([f"• {r}" for r in recs]))
            else:
                self.lbl_recs.setText("• Device is operating within normal parameters.")
        else:
            # Handle devices without health data (no SMART)
            self.main_gauge.set_value(0)
            self.lbl_main_status.setText("Health Unavailable")
            self.lbl_main_status.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff5252;")
            
            error = dev.get('smart_error', 'No SMART support available for this device.')
            source = dev.get('source', 'Unknown')
            
            stats_text = (f"Model: {dev['model']}<br>"
                         f"Source: <span style='color: #ff5252;'>{source}</span>")
            self.lbl_stats.setText(stats_text)
            
            # Show "Logs" / Error in recommendations area
            log_text = f"INTERNAL DEVICE LOGS:\n• {error}\n• Device path: {dev['path']}\n• Monitoring active via system polling."
            self.lbl_recs.setText(log_text)
                
        # Update Timestamp
        import time
        self.lbl_updated.setText(f"Last Scan: {time.strftime('%H:%M:%S')}")

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        if tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.worker.stop()
            event.accept()

def run_app():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Style
    app.setStyleSheet("""
        QMainWindow { background-color: #1c1f24; }
        QWidget { color: #abb2bf; font-family: 'Inter', 'Segoe UI', Arial; }
        
        /* Sidebar Styles */
        #Sidebar { background-color: #21252b; border-right: 1px solid #181a1f; }
        
        /* ScrollBar Styles */
        QScrollBar:vertical {
            border: none;
            background: #21252b;
            width: 10px;
            margin: 0px 0 0px 0;
        }
        QScrollBar::handle:vertical {
            background: #3e4451;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    window = NANDGuardApp()
    window.sidebar.setObjectName("Sidebar")
    
    # Tray Icon Setup
    global tray_icon
    tray_icon = QSystemTrayIcon(window.windowIcon(), app)
    
    menu = QMenu()
    show_action = QAction("Open Dashboard", app)
    show_action.triggered.connect(window.show)
    quit_action = QAction("Exit", app)
    quit_action.triggered.connect(app.quit)
    
    menu.addAction(show_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    
    # Handle tray click
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            window.show()
            window.raise_()
            window.activateWindow()
            
    tray_icon.activated.connect(on_tray_activated)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
