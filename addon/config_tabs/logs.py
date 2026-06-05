import os
import datetime
from aqt import mw
from aqt.qt import *
from ..ankiaddonconfig import ConfigWindow

class LogsTab:
    def __init__(self, conf_window: ConfigWindow):
        self.conf_window = conf_window
        self.tab = QWidget()
        layout = QVBoxLayout(self.tab)

        # Log File Text Area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        # Use a nice monospaced font
        font = QFont("Courier New" if os.name == "nt" else "Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.log_display.setFont(font)
        layout.addWidget(self.log_display)

        # Buttons and Checkbox layout
        bottom_row = QHBoxLayout()

        # Checkbox
        self.clear_on_startup_cb = QCheckBox("Clear logs on startup automatically")
        self.clear_on_startup_cb.setChecked(self.conf_window.conf.get("clear_logs_on_startup", True))
        
        def on_checkbox_toggled(state):
            self.conf_window.conf.set("clear_logs_on_startup", bool(state))
            
        self.clear_on_startup_cb.stateChanged.connect(on_checkbox_toggled)
        bottom_row.addWidget(self.clear_on_startup_cb)
        bottom_row.addStretch()

        # Copy Button
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.copy_logs)
        bottom_row.addWidget(copy_btn)

        # Clear Button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        bottom_row.addWidget(clear_btn)

        layout.addLayout(bottom_row)

        # Load logs initially
        self.refresh_logs()

        # Live update timer
        self.timer = QTimer(self.tab)
        self.timer.timeout.connect(self.refresh_logs)
        self.timer.start(1000)  # Update every 1 second

    def get_log_file_path(self) -> str:
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(addon_dir, "hotmouse.log")

    def refresh_logs(self):
        log_path = self.get_log_file_path()
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # To prevent scrolling jumping during live updates
                scrollbar = self.log_display.verticalScrollBar()
                at_bottom = scrollbar.value() == scrollbar.maximum()
                
                self.log_display.setPlainText(content)
                
                if at_bottom:
                    scrollbar.setValue(scrollbar.maximum())
            except Exception:
                pass
        else:
            self.log_display.setPlainText("Log file does not exist.")

    def copy_logs(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.log_display.toPlainText())
            # Briefly show feedback on the copy button
            btn = self.tab.sender()
            if isinstance(btn, QPushButton):
                btn.setText("Copied!")
                QTimer.singleShot(2000, lambda: btn.setText("Copy"))

    def clear_logs(self):
        log_path = self.get_log_file_path()
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")
            self.refresh_logs()
        except Exception:
            pass

def logs_tab(conf_window: ConfigWindow) -> None:
    logs_helper = LogsTab(conf_window)
    conf_window.main_tab.addTab(logs_helper.tab, "Logs")
