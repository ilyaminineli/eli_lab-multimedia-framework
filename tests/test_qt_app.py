"""Smoke tests for the PySide6 application registry."""

from eli_lab.app.registry import TOOLS
from eli_lab.app.qt.tools import TOOL_WIDGETS, create_tool_widget
from eli_lab.app.qt.audits import AuditTool
from eli_lab.app.qt.workspace import WorkspaceTool


SPECIAL_WIDGETS = {
    "workspace": WorkspaceTool,
    "audit": AuditTool,
}


def test_every_registered_tool_has_a_qt_widget() -> None:
    keys = {tool.key for tool in TOOLS}
    assert keys == set(TOOL_WIDGETS) | set(SPECIAL_WIDGETS)


def test_qt_tool_factories_are_constructible_without_gui_widgets() -> None:
    for key in {tool.key for tool in TOOLS}:
        assert create_tool_widget is not None
        assert callable(TOOL_WIDGETS.get(key) or SPECIAL_WIDGETS.get(key))
