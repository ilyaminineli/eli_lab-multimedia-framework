"""Main PySide6 application and tool navigation."""

from __future__ import annotations

import signal
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QScrollArea, QStackedWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from ..registry import TOOLS
from .audits import AuditTool
from .material_library import MaterialLibraryTool
from .texture_relocation import TextureRelocationTool
from .tools import create_tool_widget
from .workspace import WorkspaceTool

APP_STYLE = """QMainWindow { background: #17191d; }
QWidget { color: #e8eaed; background: #202329; font-family: "Segoe UI", "Inter", sans-serif; font-size: 10pt; }
QFrame#Sidebar { background: #181b20; border-right: 1px solid #30343b; }
QFrame#ContentHeader { background: #24282f; border-bottom: 1px solid #353a42; }
QLabel#Brand { color: #f3f4f6; font-size: 17pt; font-weight: 700; padding: 4px 2px; }
QLabel#Eyebrow { color: #87909e; font-size: 8pt; font-weight: 700; }
QLabel#PageTitle { color: #ffffff; font-size: 18pt; font-weight: 700; }
QLabel#PageDescription { color: #9da5b1; font-size: 9pt; }
QLineEdit#NavigationSearch { background: #21252b; color: #e8eaed; border: 1px solid #343a43; border-radius: 6px; padding: 8px 9px; }
QLineEdit#NavigationSearch:focus { border-color: #64738c; }
QTreeWidget#Navigation { background: transparent; border: 0; outline: 0; padding: 4px 0 12px 0; }
QTreeWidget#Navigation::item { color: #b7bec9; min-height: 34px; padding: 7px 8px; border-radius: 6px; margin: 1px 0; }
QTreeWidget#Navigation::item:hover { background: #252a31; color: #f1f3f5; }
QTreeWidget#Navigation::item:selected { background: #343a44; color: #ffffff; font-weight: 600; }
QTreeWidget#Navigation::branch { image: none; }
QScrollArea#ToolScroll { background: #202329; border: 0; }
QWidget#ToolPage { background: #202329; }
QLineEdit, QPlainTextEdit, QTextBrowser, QTreeWidget, QTableWidget, QComboBox, QDateEdit, QSpinBox { background: #2a2f37; color: #f3f4f6; border: 1px solid #454c57; border-radius: 6px; padding: 7px 9px; selection-background-color: #46566f; selection-color: #ffffff; }
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus { border-color: #7386a7; }
QComboBox QAbstractItemView { background: #252a31; color: #eef0f3; border: 1px solid #454c57; selection-background-color: #46566f; selection-color: #ffffff; padding: 4px; }
QPushButton { background: #353b45; color: #f5f6f7; border: 1px solid #4a515d; border-radius: 6px; min-height: 30px; padding: 4px 13px; font-weight: 600; }
QPushButton:hover { background: #414954; border-color: #5a6472; }
QPushButton:pressed { background: #2d333c; }
QPushButton:disabled { color: #737b88; background: #292d33; border-color: #343941; }
QGroupBox { background: #252a31; border: 1px solid #353b44; border-radius: 8px; margin-top: 14px; padding: 16px 12px 12px 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 7px; color: #e2e6eb; background: #252a31; }
QTabWidget::pane { border: 1px solid #363c45; border-radius: 7px; background: #252a31; top: -1px; }
QTabBar::tab { background: #1d2025; color: #9ca4b0; padding: 8px 14px; margin-right: 2px; border: 1px solid #343a42; border-bottom: 0; }
QTabBar::tab:selected { color: #ffffff; background: #252a31; }
QHeaderView::section { background: #303640; color: #dfe3e8; border: 0; border-right: 1px solid #454b55; border-bottom: 1px solid #454b55; padding: 7px; font-weight: 600; }
QTreeWidget, QTableWidget { alternate-background-color: #252a31; gridline-color: #343a42; }
QProgressBar { background: #292e35; border: 1px solid #3c434d; border-radius: 5px; text-align: center; color: #e9edf2; min-height: 16px; }
QProgressBar::chunk { background: #667a9f; border-radius: 4px; }
QLabel#StatusLabel { color: #89919d; background: #1d2025; border: 1px solid #30353d; border-radius: 5px; padding: 7px 9px; }
QScrollBar:vertical { background: #1b1e23; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #3d444f; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def configure_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, "#202329"); palette.setColor(QPalette.WindowText, "#e8eaed")
    palette.setColor(QPalette.Base, "#2a2f37"); palette.setColor(QPalette.AlternateBase, "#252a31")
    palette.setColor(QPalette.Text, "#f3f4f6"); palette.setColor(QPalette.Button, "#353b45")
    palette.setColor(QPalette.ButtonText, "#f5f6f7"); palette.setColor(QPalette.Highlight, "#46566f")
    palette.setColor(QPalette.HighlightedText, "#ffffff"); palette.setColor(QPalette.ToolTipBase, "#252a31")
    palette.setColor(QPalette.ToolTipText, "#f3f4f6"); palette.setColor(QPalette.PlaceholderText, "#747d89")
    app.setPalette(palette)


class MainWindow(QMainWindow):
    """Single-window Qt shell containing project workspace and tools."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("eli_lab Multimedia Framework"); self.resize(1280, 820); self.setMinimumSize(1000, 680)
        self.processes: list[subprocess.Popen] = []; self.stack = QStackedWidget()
        self.navigation = QTreeWidget(); self.navigation.setObjectName("Navigation"); self.navigation.setHeaderHidden(True); self.navigation.setIndentation(14); self.navigation.setUniformRowHeights(False)
        self.search = QLineEdit(); self.search.setObjectName("NavigationSearch"); self.search.setPlaceholderText("Search tools…")
        self._build(); self.navigation.itemClicked.connect(self._select_tool); self.search.textChanged.connect(self._filter_tools)

    def _build(self) -> None:
        root = QWidget(); layout = QHBoxLayout(root); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(245); sidebar_layout = QVBoxLayout(sidebar); sidebar_layout.setContentsMargins(16, 16, 12, 14); sidebar_layout.setSpacing(8)
        brand = QLabel("eli_lab"); brand.setObjectName("Brand"); sidebar_layout.addWidget(brand)
        tagline = QLabel("MULTIMEDIA FRAMEWORK"); tagline.setObjectName("Eyebrow"); sidebar_layout.addWidget(tagline); sidebar_layout.addSpacing(8); sidebar_layout.addWidget(self.search); sidebar_layout.addWidget(self.navigation, 1)
        categories: dict[str, QTreeWidgetItem] = {}
        for index, tool in enumerate(TOOLS):
            category = categories.get(tool.category)
            if category is None:
                category = QTreeWidgetItem([tool.category.upper()]); category.setFlags(category.flags() & ~Qt.ItemIsSelectable); self.navigation.addTopLevelItem(category); categories[tool.category] = category
            child = QTreeWidgetItem([tool.name]); child.setData(0, Qt.UserRole, index); child.setToolTip(0, tool.description); category.addChild(child); self.stack.addWidget(self._make_tool_page(tool.key))
        for category in categories.values(): category.setExpanded(True)
        content = QFrame(); content_layout = QVBoxLayout(content); content_layout.setContentsMargins(0, 0, 0, 0); content_layout.setSpacing(0)
        header = QFrame(); header.setObjectName("ContentHeader"); header_layout = QVBoxLayout(header); header_layout.setContentsMargins(28, 20, 28, 18); header_layout.setSpacing(3)
        self.page_eyebrow = QLabel(); self.page_eyebrow.setObjectName("Eyebrow"); self.page_title = QLabel(); self.page_title.setObjectName("PageTitle"); self.page_description = QLabel(); self.page_description.setObjectName("PageDescription"); self.page_description.setWordWrap(True)
        header_layout.addWidget(self.page_eyebrow); header_layout.addWidget(self.page_title); header_layout.addWidget(self.page_description); content_layout.addWidget(header); content_layout.addWidget(self.stack, 1)
        layout.addWidget(sidebar); layout.addWidget(content, 1); self.setCentralWidget(root)
        first = self.navigation.topLevelItem(0).child(0); self.navigation.setCurrentItem(first); self._select_tool(first, 0)

    def _make_tool_page(self, key: str) -> QWidget:
        if key == "workspace": tool = WorkspaceTool(self)
        elif key == "audit": tool = AuditTool(self)
        elif key == "material_library": tool = MaterialLibraryTool(self)
        elif key == "texture_relocation": tool = TextureRelocationTool(self)
        else: tool = create_tool_widget(key, self)
        wrapper = QWidget(); wrapper.setObjectName("ToolPage"); outer = QVBoxLayout(wrapper); outer.setContentsMargins(24, 22, 24, 22); outer.setSpacing(0)
        scroll = QScrollArea(); scroll.setObjectName("ToolScroll"); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame); scroll.setWidget(tool); outer.addWidget(scroll); return wrapper

    def _select_tool(self, item: QTreeWidgetItem, _column: int) -> None:
        index = item.data(0, Qt.UserRole)
        if not isinstance(index, int): return
        self.stack.setCurrentIndex(index); tool = TOOLS[index]; self.page_eyebrow.setText(tool.category.upper()); self.page_title.setText(tool.name); self.page_description.setText(tool.description)

    def _filter_tools(self, query: str) -> None:
        needle = query.strip().casefold()
        for i in range(self.navigation.topLevelItemCount()):
            category = self.navigation.topLevelItem(i); visible_count = 0
            for j in range(category.childCount()):
                child = category.child(j); index = child.data(0, Qt.UserRole); tool = TOOLS[index] if isinstance(index, int) else None
                visible = not needle or (tool and needle in f"{tool.name} {tool.category} {tool.description}".casefold()); child.setHidden(not visible); visible_count += int(visible)
            category.setHidden(visible_count == 0)
            if needle and visible_count: category.setExpanded(True)

    def closeEvent(self, event) -> None:  # noqa: N802
        for process in self.processes[:]:
            if process.poll() is None:
                try: process.terminate() if sys.platform == "win32" else process.send_signal(signal.SIGTERM); process.wait(timeout=3)
                except (OSError, subprocess.TimeoutExpired): process.kill()
        event.accept()


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv); app.setApplicationName("eli_lab Multimedia Framework"); configure_palette(app); app.setStyleSheet(APP_STYLE); window = MainWindow(); window.show(); return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
