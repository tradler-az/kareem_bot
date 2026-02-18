"""
Bosco Core - JARVIS-Style Desktop UI
Full desktop application with JARVIS-like interface
"""

import sys
import os
import time
import subprocess
import threading
from pathlib import Path

# Try importing GUI and automation libraries
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                   QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                                   QLineEdit, QFrame, QSystemTrayIcon, QMenu, QAction,
                                   QSlider, QComboBox, QCheckBox, QProgressBar, QTabWidget)
    from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QSize, QThread, pyqtSignal
    from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QLinearGradient, QConicalGradient, QBrush, QPen
    PYQT5_AVAILABLE = True
except ImportError:
    print("PyQt5 not available. Install with: pip install PyQt5")
    PYQT5_AVAILABLE = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False


# Import existing modules
try:
    sys.path.insert(0, '/home/tradler/Desktop/bosco-core')
    from bosco_os.brain.llm_client import get_llm
    from bosco_os.capabilities.system.pc_control import PCControl
    pc_control = PCControl()
    llm = get_llm()
except:
    pc_control = None
    llm = None


class ArcReactorWidget(QWidget):
    """JARVIS-style Arc Reactor visualization"""
    
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.status = "idle"  # idle, listening, processing, speaking
        self.pulse_size = 0
        self.pulse_direction = 1
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
    
    def set_status(self, status):
        self.status = status
    
    def animate(self):
        self.angle = (self.angle + 2) % 360
        if self.status == "speaking":
            self.pulse_size = (self.pulse_size + self.pulse_direction * 2) % 20
            if self.pulse_size > 15 or self.pulse_size < 0:
                self.pulse_direction *= -1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        size = min(self.width(), self.height()) // 2
        
        # Background glow
        if self.status == "listening":
            color = QColor(0, 255, 136)
        elif self.status == "processing":
            color = QColor(255, 215, 0)
        elif self.status == "speaking":
            color = QColor(0, 212, 255)
        else:
            color = QColor(0, 212, 255)
        
        # Outer glow
        for i in range(5):
            radius = size - i * 8
            alpha = 30 - i * 5
            glow_color = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, radius, radius)
        
        # Main ring
        painter.setPen(QPen(color, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, size - 10, size - 10)
        
        # Inner ring
        inner_size = size - 25
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(center, inner_size, inner_size)
        
        # Core
        core_color = QColor(color.red(), color.green(), color.blue(), 200)
        painter.setBrush(QBrush(core_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, 15 + self.pulse_size, 15 + self.pulse_size)
        
        # Arc segments (rotating)
        painter.setPen(QPen(color, 4))
        for i in range(6):
            arc_angle = self.angle + i * 60
            rad = arc_angle * 3.14159 / 180
            x1 = center.x() + (size - 15) * 0.3 * 0.5
            y1 = center.y()
            x2 = center.x() + (size - 15) * 0.7
            y2 = center.y()
            
            # Draw arc segment
            painter.drawArc(int(center.x() - inner_size), int(center.y() - inner_size), 
                          int(inner_size*2), int(inner_size*2), 
                          int(arc_angle * 16), int(30 * 16))


class JARVISWindow(QMainWindow):
    """Main JARVIS-style window"""
    
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()
        self.status = "idle"
        
        # Setup window
        self.setWindowTitle("BOSCO - AI Assistant")
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with border
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 15, 30, 240),
                    stop:1 rgba(20, 30, 50, 240));
                border: 2px solid #00d4ff;
                border-radius: 15px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title bar
        title_bar = self.create_title_bar()
        container_layout.addWidget(title_bar)
        
        # Arc Reactor
        self.arc_reactor = ArcReactorWidget()
        self.arc_reactor.setFixedHeight(150)
        container_layout.addWidget(self.arc_reactor)
        
        # Status label
        self.status_label = QLabel("READY")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #00d4ff;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        """)
        container_layout.addWidget(self.status_label)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00d4ff;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 5px;
            }
            QTabBar::tab {
                background: rgba(0, 212, 255, 0.2);
                color: #00d4ff;
                padding: 8px 15px;
                border: 1px solid #00d4ff;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: rgba(0, 212, 255, 0.4);
            }
        """)
        
        # Chat tab
        self.chat_tab = self.create_chat_tab()
        self.tabs.addTab(self.chat_tab, "💬 Chat")
        
        # Control tab
        self.control_tab = self.create_control_tab()
        self.tabs.addTab(self.control_tab, "🎮 Control")
        
        # System tab
        self.system_tab = self.create_system_tab()
        self.tabs.addTab(self.system_tab, "⚙️ System")
        
        container_layout.addWidget(self.tabs)
        
        main_layout.addWidget(self.container)
        
        # System tray
        self.setup_tray()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(100)
    
    def create_title_bar(self):
        title_bar = QFrame()
        title_bar.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo/Title
        title = QLabel("🤖 BOSCO")
        title.setStyleSheet("color: #00d4ff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Minimize button
        min_btn = QPushButton("─")
        min_btn.setFixedSize(30, 25)
        min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 215, 0, 0.3);
                color: #ffd700;
                border: 1px solid #ffd700;
                border-radius: 3px;
            }
            QPushButton:hover { background: rgba(255, 215, 0, 0.6); }
        """)
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 50, 50, 0.3);
                color: #ff3232;
                border: 1px solid #ff3232;
                border-radius: 3px;
            }
            QPushButton:hover { background: rgba(255, 50, 50, 0.6); }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        return title_bar
    
    def create_chat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.5);
                color: #00ff88;
                border: 1px solid #00d4ff;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        self.chat_display.append("<b style='color:#00d4ff'>🤖 Bosco:</b> Hello! I'm your AI assistant. How can I help?")
        layout.addWidget(self.chat_display)
        
        # Input
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.5);
                color: white;
                border: 1px solid #00d4ff;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_chat)
        input_layout.addWidget(self.chat_input)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background: #00d4ff;
                color: #1a1a2e;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background: #00ff88; }
        """)
        send_btn.clicked.connect(self.send_chat)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        return widget
    
    def create_control_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # App control
        group = QFrame()
        group.setStyleSheet("border: 1px solid #00d4ff; border-radius: 5px; padding: 10px;")
        group_layout = QVBoxLayout(group)
        
        label = QLabel("🎯 Application Control")
        label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        group_layout.addWidget(label)
        
        app_layout = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("App name (notepad, vscode, etc)")
        self.app_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0.5);
                color: white;
                border: 1px solid #00d4ff;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        app_layout.addWidget(self.app_input)
        
        open_btn = QPushButton("Open")
        open_btn.setStyleSheet("background: #00d4ff; color: #1a1a2e; border: none; border-radius: 3px; padding: 5px 10px;")
        open_btn.clicked.connect(lambda: self.run_command("open"))
        app_layout.addWidget(open_btn)
        
        group_layout.addLayout(app_layout)
        
        # Type text
        type_layout = QHBoxLayout()
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Text to type...")
        self.type_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0.5);
                color: white;
                border: 1px solid #00d4ff;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        type_layout.addWidget(self.type_input)
        
        type_btn = QPushButton("Type")
        type_btn.setStyleSheet("background: #00ff88; color: #1a1a2e; border: none; border-radius: 3px; padding: 5px 10px;")
        type_btn.clicked.connect(lambda: self.run_command("type"))
        type_layout.addWidget(type_btn)
        
        group_layout.addLayout(type_layout)
        
        layout.addWidget(group)
        
        # Terminal
        group2 = QFrame()
        group2.setStyleSheet("border: 1px solid #00d4ff; border-radius: 5px; padding: 10px;")
        group2_layout = QVBoxLayout(group2)
        
        label2 = QLabel("💻 Terminal Command")
        label2.setStyleSheet("color: #00d4ff; font-weight: bold;")
        group2_layout.addWidget(label2)
        
        cmd_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Command (ls, dir, etc)")
        self.cmd_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0.5);
                color: white;
                border: 1px solid #ffd700;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        cmd_layout.addWidget(self.cmd_input)
        
        run_btn = QPushButton("Run")
        run_btn.setStyleSheet("background: #ffd700; color: #1a1a2e; border: none; border-radius: 3px; padding: 5px 10px;")
        run_btn.clicked.connect(lambda: self.run_command("terminal"))
        cmd_layout.addWidget(run_btn)
        
        group2_layout.addLayout(cmd_layout)
        layout.addWidget(group2)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        screenshot_btn = QPushButton("📸 Screenshot")
        screenshot_btn.setStyleSheet("background: rgba(0,212,255,0.3); color: #00d4ff; border: 1px solid #00d4ff; border-radius: 5px; padding: 10px;")
        screenshot_btn.clicked.connect(lambda: self.run_command("screenshot"))
        quick_layout.addWidget(screenshot_btn)
        
        desktop_btn = QPushButton("🖥️ Desktop")
        desktop_btn.setStyleSheet("background: rgba(0,255,136,0.3); color: #00ff88; border: 1px solid #00ff88; border-radius: 5px; padding: 10px;")
        desktop_btn.clicked.connect(lambda: self.run_command("desktop"))
        quick_layout.addWidget(desktop_btn)
        
        layout.addLayout(quick_layout)
        
        layout.addStretch()
        
        return widget
    
    def create_system_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Always on top
        self.always_on_top = QCheckBox("Always on Top")
        self.always_on_top.setChecked(True)
        self.always_on_top.setStyleSheet("color: #00d4ff;")
        self.always_on_top.stateChanged.connect(self.toggle_always_on_top)
        layout.addWidget(self.always_on_top)
        
        # Startup
        self.auto_start = QCheckBox("Start with System")
        self.auto_start.setStyleSheet("color: #00d4ff;")
        layout.addWidget(self.auto_start)
        
        # Voice output
        voice_layout = QHBoxLayout()
        voice_label = QLabel("Voice:")
        voice_label.setStyleSheet("color: #00d4ff;")
        voice_layout.addWidget(voice_label)
        
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Enabled", "Disabled"])
        self.voice_combo.setStyleSheet("background: rgba(0,0,0,0.5); color: white; border: 1px solid #00d4ff;")
        voice_layout.addWidget(self.voice_combo)
        
        layout.addLayout(voice_layout)
        
        # Volume
        vol_layout = QHBoxLayout()
        vol_label = QLabel("Volume:")
        vol_label.setStyleSheet("color: #00d4ff;")
        vol_layout.addWidget(vol_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #00d4ff;
                height: 8px;
                background: rgba(0,0,0,0.5);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00d4ff;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        vol_layout.addWidget(self.volume_slider)
        
        layout.addLayout(vol_layout)
        
        # Info
        info = QLabel("BOSCO AI v2.1\nFull PC Control Enabled")
        info.setStyleSheet("color: #888; font-size: 11px; padding: 10px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        
        return widget
    
    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("BOSCO AI Assistant")
        
        # Create tray menu
        menu = QMenu()
        
        show_action = QAction("Show BOSCO", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()
    
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()
    
    def toggle_always_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
    
    def quit_app(self):
        self.tray.hide()
        QApplication.quit()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
    
    def send_chat(self):
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Add user message
        self.chat_display.append(f"<b style='color:#00d4ff'>👤 You:</b> {message}")
        self.chat_input.clear()
        
        # Set processing status
        self.set_status("processing")
        
        # Process command
        response = self.process_message(message)
        
        # Add response
        self.chat_display.append(f"<b style='color:#00ff88'>🤖 Bosco:</b> {response}")
        
        # Reset status
        self.set_status("idle")
        
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def process_message(self, message):
        msg = message.lower()
        
        # Automation commands
        if 'open' in msg and 'write' in msg:
            # Extract app and text
            parts = msg.replace('open', '').replace('write', '').split()
            if len(parts) >= 2:
                app = parts[0]
                text = ' '.join(parts[1:])
                self.run_automation(f"open {app}")
                time.sleep(1)
                self.run_automation(f"type {text}")
                return f"Opened {app} and typed: {text}"
        
        if msg.startswith('open '):
            app = msg.replace('open ', '').strip()
            self.run_automation(f"open {app}")
            return f"Opening {app}..."
        
        if msg.startswith('type ') or msg.startswith('write '):
            text = msg.replace('type ', '').replace('write ', '').strip()
            self.run_automation(f"type {text}")
            return f"Typed: {text}"
        
        if msg.startswith('run '):
            cmd = msg.replace('run ', '').strip()
            result = self.run_automation(f"run {cmd}")
            return f"Result: {result}"
        
        if 'screenshot' in msg:
            result = self.run_automation("screenshot")
            return result
        
        # Use LLM for other messages
        if llm:
            try:
                response = llm.chat(message, "You are Bosco, a helpful AI assistant.")
                return response
            except Exception as e:
                return f"I'm ready to help! Try commands like 'open notepad' or 'type hello world'"
        
        return "I'm ready! Try commands like:\n• open notepad\n• type hello world\n• run ls\n• screenshot"
    
    def run_command(self, cmd_type):
        if cmd_type == "open":
            app = self.app_input.text().strip()
            if app:
                self.run_automation(f"open {app}")
                self.app_input.clear()
        elif cmd_type == "type":
            text = self.type_input.text().strip()
            if text:
                self.run_automation(f"type {text}")
                self.type_input.clear()
        elif cmd_type == "terminal":
            cmd = self.cmd_input.text().strip()
            if cmd:
                result = self.run_automation(f"run {cmd}")
                self.chat_display.append(f"<b style='color:#ffd700'>💻 Output:</b><br><pre style='color:#aaa'>{result[:200]}</pre>")
                self.cmd_input.clear()
        elif cmd_type == "screenshot":
            result = self.run_automation("screenshot")
            self.chat_display.append(f"📸 {result}")
        elif cmd_type == "desktop":
            self.run_automation("desktop")
    
    def run_automation(self, command):
        try:
            if command.startswith("open "):
                app = command.replace("open ", "").strip()
                apps = {
                    'notepad': 'notepad', 'vscode': 'code', 'chrome': 'google-chrome',
                    'terminal': 'gnome-terminal', 'firefox': 'firefox'
                }
                cmd = apps.get(app, app)
                subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opened {app}"
            
            elif command.startswith("type "):
                text = command.replace("type ", "").strip()
                if PYPERCLIP_AVAILABLE:
                    pyperclip.copy(text)
                    if PYAUTOGUI_AVAILABLE:
                        pyautogui.hotkey('ctrl', 'v')
                    return f"Typed: {text}"
                elif PYAUTOGUI_AVAILABLE:
                    pyautogui.write(text)
                    return f"Typed: {text}"
                return "No typing method available"
            
            elif command.startswith("run "):
                cmd = command.replace("run ", "").strip()
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                return result.stdout[:300] if result.stdout else result.stderr[:300] or "Done"
            
            elif command == "screenshot":
                if PYAUTOGUI_AVAILABLE:
                    path = f"{os.path.expanduser('~')}/Pictures/bosco_{int(time.time())}.png"
                    pyautogui.screenshot(path)
                    return f"Saved: {path}"
                return "Screenshot not available"
            
            elif command == "desktop":
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.hotkey('super', 'd')
                return "Desktop shown"
            
            return "Command executed"
        except Exception as e:
            return f"Error: {e}"
    
    def set_status(self, status):
        self.status = status
        self.arc_reactor.set_status(status)
    
    def update_status_display(self):
        status_map = {
            "idle": "READY",
            "listening": "LISTENING...",
            "processing": "PROCESSING...",
            "speaking": "SPEAKING..."
        }
        self.status_label.setText(status_map.get(self.status, "READY"))


def main():
    if not PYQT5_AVAILABLE:
        print("Please install PyQt5: pip install PyQt5")
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName("BOSCO AI")
    
    # Set dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 15, 30))
    palette.setColor(QPalette.WindowText, QColor(0, 212, 255))
    app.setPalette(palette)
    
    window = JARVISWindow()
    window.show()
    
    print("\n" + "="*50)
    print("🤖 BOSCO CORE - JARVIS UI")
    print("="*50)
    print("\n💡 Features:")
    print("   • Floating JARVIS-style interface")
    print("   • Arc reactor animation")
    print("   • Full PC control")
    print("   • System tray support")
    print("   • Always on top")
    print("\n⚠️  Click and drag to move window")
    print("="*50 + "\n")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
