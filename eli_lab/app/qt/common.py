"""Shared PySide6 UI helpers."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class WorkerSignals(QObject):
    """Signals emitted by a background worker."""

    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class Worker(QRunnable):
    """Run a callable on Qt's shared thread pool."""

    def __init__(self, function: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            self.signals.result.emit(self.function(*self.args, **self.kwargs))
        except Exception as exc:  # pragma: no cover - exercised by GUI runtime
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()


class ToolWidget(QWidget):
    """Common base for all PySide6 tool panels."""

    thread_pool = QThreadPool.globalInstance()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ToolWidget")
        self._status = QLabel()
        self._status.setWordWrap(True)

    def set_status(self, text: str) -> None:
        self._status.setText(text)

    def add_status(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self._status)

    def run_background(
        self,
        button: QPushButton,
        function: Callable[..., Any],
        on_result: Callable[[Any], None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        button.setEnabled(False)
        worker = Worker(function, *args, **kwargs)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(lambda message: self.show_error(message))
        worker.signals.finished.connect(lambda: button.setEnabled(True))
        self.thread_pool.start(worker)

    def show_error(self, message: str, title: str = "ELI LAB") -> None:
        self.set_status(f"Error: {message}")
        QMessageBox.critical(self, title, message)

    def show_info(self, message: str, title: str = "ELI LAB") -> None:
        self.set_status(message)
        QMessageBox.information(self, title, message)


def browse_directory(parent: QWidget, target: Any, title: str = "Select directory") -> None:
    selected = QFileDialog.getExistingDirectory(parent, title)
    if selected:
        target.setText(selected)


def browse_file(parent: QWidget, target: Any, title: str = "Select file", filter: str = "All files (*)") -> None:
    selected, _ = QFileDialog.getOpenFileName(parent, title, filter=filter)
    if selected:
        target.setText(selected)


def path_row(
    parent: QWidget,
    label: str,
    target: Any,
    title: str = "Select directory",
    *,
    file: bool = False,
    filter: str = "All files (*)",
) -> QWidget:
    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QLabel(label))
    layout.addWidget(target, 1)
    button = QPushButton("Browse")
    if file:
        button.clicked.connect(lambda: browse_file(parent, target, title, filter))
    else:
        button.clicked.connect(lambda: browse_directory(parent, target, title))
    layout.addWidget(button)
    return container


def form_group(title: str) -> tuple[QGroupBox, QFormLayout]:
    box = QGroupBox(title)
    form = QFormLayout(box)
    return box, form
