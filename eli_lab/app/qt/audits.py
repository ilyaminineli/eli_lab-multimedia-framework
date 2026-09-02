"""Qt UI for the eli_lab production audit engine."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog, QHeaderView

from eli_lab.pipeline.audits import audit_project
from .common import ToolWidget


class AuditTool(ToolWidget):
    """Run project-wide production audits and inspect actionable findings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        row = QHBoxLayout()
        self.directory = QLineEdit()
        self.directory.setPlaceholderText("Project folder…")
        browse = QPushButton("Browse")
        run = QPushButton("Run Audit")
        browse.clicked.connect(self.browse)
        run.clicked.connect(self.run)
        row.addWidget(self.directory, 1)
        row.addWidget(browse)
        row.addWidget(run)
        root.addLayout(row)
        self.summary = QLabel("No audit run yet.")
        root.addWidget(self.summary)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Severity", "Rule", "Target", "Finding"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table, 1)
        self.add_status(root)

    def browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select project folder")
        if path:
            self.directory.setText(path)
            self.run()

    def run(self) -> None:
        try:
            findings = audit_project(self.directory.text())
        except Exception as exc:
            self.set_status(f"Audit failed: {exc}")
            return
        self.table.setRowCount(len(findings))
        for row, finding in enumerate(findings):
            self.table.setItem(row, 0, QTableWidgetItem(finding.severity.upper()))
            self.table.setItem(row, 1, QTableWidgetItem(finding.rule))
            self.table.setItem(row, 2, QTableWidgetItem(finding.target))
            self.table.setItem(row, 3, QTableWidgetItem(finding.message))
        self.summary.setText(f"{len(findings)} findings detected.")
        self.set_status("Production audit complete.")
