import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient, QPixmap

class CircularHealthGauge(QWidget):
    """A professional circular gauge for health score."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setMinimumSize(120, 120)

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        side = min(width, height)
        pen_width = 12
        margin = 10
        rect = QRectF(margin, margin, side - 2*margin, side - 2*margin)

        # Draw background track
        painter.setPen(QPen(QColor(40, 44, 52), pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, -90 * 16, 360 * 16)

        # Draw health arc
        color = QColor(0, 255, 255) # Cyan
        if self.value < 40:
            color = QColor(255, 60, 60) # Red
        elif self.value < 75:
            color = QColor(255, 170, 0) # Orange
            
        painter.setPen(QPen(color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        # Start from top (90 degrees)
        span_angle = int(-self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, span_angle)

        # Draw text
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.value)}%")
        
        # Draw "Health" subtext
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QPen(QColor(171, 178, 191))) # Muted gray
        painter.drawText(rect.adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, "Health")

class DeviceCard(QFrame):
    """Summary card for a storage device."""
    clicked = pyqtSignal(dict) # Emits the full device data when clicked
    
    def __init__(self, dev_data, parent=None):
        super().__init__(parent)
        self.dev_data = dev_data
        model = dev_data.get('model', 'Unknown')
        path = dev_data.get('path', 'Unknown')
        health_score = dev_data.get('health', {}).get('score', 0)
        # Default to Healthy if health data exists, matches hero section logic
        status = dev_data.get('status', 'Healthy' if 'health' in dev_data else 'Unknown')
        
        self.setFixedHeight(110)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            DeviceCard {
                background-color: #21252b;
                border-radius: 10px;
                border: 1px solid #3e4451;
                margin: 0px;
            }
            DeviceCard:hover {
                border: 1px solid #00ffff;
                background-color: #2c313a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Professional Disk Indicator with Icon
        self.icon_frame = QFrame()
        self.icon_frame.setFixedSize(48, 48)
        self.icon_frame.setStyleSheet("""
            QFrame {
                background-color: #2c313a;
                border-radius: 24px;
                border: 1px solid #3e4451;
            }
        """)
        icon_inner_layout = QVBoxLayout(self.icon_frame)
        icon_inner_layout.setContentsMargins(0, 0, 0, 0)
        
        # Dynamic Icon Selection based on device type
        self.disk_icon = QLabel()
        icon_to_use = None
        model_lower = model.lower()
        
        if "ssd" in model_lower:
            icon_to_use = "ssd.png"
        elif "pendrive" in model_lower or "usb" in model_lower:
            icon_to_use = "pendrive.png"
        elif "generic" in model_lower:
            icon_to_use = None # Use CD Emoji for generic as requested
            
        icon_loaded = False
        if icon_to_use:
            img_path = os.path.join(os.path.dirname(__file__), icon_to_use)
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.disk_icon.setPixmap(pixmap)
                icon_loaded = True

        if not icon_loaded:
            self.disk_icon.setText("💿")
            self.disk_icon.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        
        icon_inner_layout.addWidget(self.disk_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Status Dot Overlay
        self.icon_dot = QLabel(self.icon_frame)
        self.icon_dot.setFixedSize(10, 10)
        self.icon_dot.move(34, 34)
        # Fixed locals() check for bar_color
        dot_color = "#00ffff"
        if health_score < 40: dot_color = "#ff3c3c"
        elif health_score < 75: dot_color = "#ffaa00"
        
        self.icon_dot.setStyleSheet(f"background-color: {dot_color}; border-radius: 4px; border: 1px solid #21252b;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.model_label = QLabel(model)
        self.model_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        info_layout.addWidget(self.model_label)
        
        # Elide path if too long
        metrics = self.fontMetrics()
        elided_path = metrics.elidedText(path, Qt.TextElideMode.ElideMiddle, 280)
        self.path_label = QLabel(elided_path)
        self.path_label.setStyleSheet("color: #abb2bf; font-size: 11px;")
        self.path_label.setToolTip(path)
        info_layout.addWidget(self.path_label)
        
        header.addWidget(self.icon_frame, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addLayout(info_layout, 1)
        
        layout.addLayout(header)
        
        # Progress section with label
        progress_info = QHBoxLayout()
        progress_info.setSpacing(10)
        
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setValue(int(health_score))
        self.health_bar.setTextVisible(False)
        self.health_bar.setFixedHeight(8)
        
        bar_color = "#00ffff"
        if health_score < 40: bar_color = "#ff3c3c"
        elif health_score < 75: bar_color = "#ffaa00"
            
        self.health_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #282c34;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 4px;
            }}
        """)
        
        progress_info.addWidget(self.health_bar)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {bar_color}; font-size: 11px; font-weight: bold;")
        progress_info.addWidget(status_label)
        
        layout.addLayout(progress_info)
        layout.addSpacing(5)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.dev_data)
        super().mousePressEvent(event)

class SidebarButton(QFrame):
    """Custom sidebar navigation button."""
    def __init__(self, text, active=False, parent=None):
        super().__init__(parent)
        self.active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0) # Left margin 0 for the bar
        layout.setSpacing(12)
        
        # Professional Left Bar Indicator
        self.indicator_bar = QFrame()
        self.indicator_bar.setFixedWidth(4)
        self.indicator_bar.setStyleSheet(f"background-color: {'#00ffff' if self.active else 'transparent'}; border-radius: 2px;")
        
        self.text_label = QLabel(text)
        
        layout.addWidget(self.indicator_bar)
        layout.addWidget(self.text_label, 1)
        
        self.update_style()
        
        # Updated update_style for SidebarButton
    def update_style(self):
        bg = "rgba(0, 255, 255, 0.05)" if self.active else "transparent"
        color = "#00ffff" if self.active else "#abb2bf"
        
        self.setStyleSheet(f"""
            SidebarButton {{
                background-color: {bg};
                padding-left: 0px;
                border-radius: 4px;
                margin: 2px 8px;
            }}
            SidebarButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QLabel {{
                color: {color};
                font-weight: {"bold" if self.active else "normal"};
                font-size: 13px;
            }}
        """)
        if hasattr(self, 'indicator_bar'):
            self.indicator_bar.setStyleSheet(f"background-color: {'#00ffff' if self.active else 'transparent'}; border-radius: 2px;")
