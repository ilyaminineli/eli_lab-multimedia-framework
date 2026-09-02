"""Main PySide6 application and tool navigation."""

from __future__ import annotations

import signal
import subprocess
import sys

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..registry import TOOLS
from .tools import create_tool_widget


APP_STYLE = """
QMainWindow, QWidget { background: #242424; color: #f0f0f0; }
QListWidget { background: #1d1d1d; border: 0; padding: 8px; }
QListWidget::item { padding: 10px; border-radius: 5px; }
QListWidget::item:selected { background: #3d3d3d; }
QLineEdit, QPlainTextEdit, QTextBrowser, QTreeWidget, QTableWidget, QComboBox, QDateEdit, QSpinBox {
    background: #303030; color: #f0f0f0; border: 1px solid #555; border-radius: 4px; padding: 6px;
}
QPushButton { background: #404040; color: #f0f0f0; border: 0; padding: 8px 12px; border-radius: 4px; }
QPushButton:hover { background: #555; }
QGroupBox { border: 1px solid #444; border-radius: 5px; margin-top: 8px; padding-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
"""


class MainWindow(QMainWindow):
    """Single-window Qt shell containing every framework tool."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("eli_lab Multimedia Framework")
        self.resize(1200, 760)
        self.setMinimumSize(980, 640)
        self.processes: list[subprocess.Popen] = []
        self.stack = QStackedWidget()
        self.navigation = QListWidget()
        self.navigation.setFixedWidth(255)
        self._build()
        self.navigation.currentRowChanged.connect(self.stack.setCurrentIndex)

    def _build(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar_layout = QVBoxLayout(sidebar)
        title = QLabel("eli_lab\nMultimedia Framework")
        title.setStyleSheet("font-size: 18px; font-weight: 700; padding: 18px 10px;")
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(self.navigation, 1)

        for tool in TOOLS:
            item = QListWidgetItem(f"{tool.name}\n{tool.category} · {tool.description}")
            item.setToolTip(tool.description)
            self.navigation.addItem(item)
            self.stack.addWidget(create_tool_widget(tool.key, self))

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        if self.navigation.count():
            self.navigation.setCurrentRow(0)

    def closeEvent(self, event) -> None:  # noqa: N802
        for process in self.processes[:]:
            if process.poll() is None:
                try:
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    process.wait(timeout=3)
                except (OSError, subprocess.TimeoutExpired):
                    process.kill()
        event.accept()


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("eli_lab Multimedia Framework")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
