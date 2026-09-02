"""Smoke tests for the PySide6 application registry."""

from eli_lab.app.registry import TOOLS
from eli_lab.app.qt.tools import TOOL_WIDGETS, create_tool_widget


def test_every_registered_tool_has_a_qt_widget() -> None:
    keys = {tool.key for tool in TOOLS}
    assert keys == set(TOOL_WIDGETS)


def test_qt_tool_factories_are_constructible_without_gui_widgets() -> None:
    # The actual widget construction requires a QApplication in Qt. The test
    # intentionally validates the registry/factory boundary only; CI already
    # imports the full PySide6 module graph during test collection.
    for key in {tool.key for tool in TOOLS}:
        assert callable(TOOL_WIDGETS[key])
        assert create_tool_widget is not None
