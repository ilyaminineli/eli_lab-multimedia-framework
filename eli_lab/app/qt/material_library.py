"""Qt interface for the eli_lab material and texture library."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QHeaderView,
)

from eli_lab.production.materials import (
    discover_material_records,
    plan_texture_relocation,
)
from .common import ToolWidget


class MaterialLibraryTool(ToolWidget):
    """Inspect material sources and misplaced textures without destructive edits."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        row = QHBoxLayout()
        self.directory = QLineEdit()
        self.directory.setPlaceholderText("Project folder…")
        browse = QPushButton("Browse")
        scan = QPushButton("Scan Library")
        browse.clicked.connect(self.browse)
        scan.clicked.connect(self.scan)
        row.addWidget(self.directory, 1)
        row.addWidget(browse)
        row.addWidget(scan)
        root.addLayout(row)
        self.summary = QLabel("No scan yet.")
        root.addWidget(self.summary)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Material", "Source", "Texture sets"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table, 1)
        self.misplaced = QLabel()
        self.misplaced.setWordWrap(True)
        root.addWidget(self.misplaced)
        self.add_status(root)

    def browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select project folder")
        if path:
            self.directory.setText(path)
            self.scan()

    def scan(self) -> None:
        try:
            records = discover_material_records(self.directory.text())
            relocations = plan_texture_relocation(self.directory.text())
        except Exception as exc:
            self.set_status(f"Material scan failed: {exc}")
            return
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(record.name))
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(", ".join(str(path) for path in record.source_files)),
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(", ".join(record.texture_sets) or "—")
            )
        self.summary.setText(f"{len(records)} material source(s) detected.")
        if relocations:
            examples = "\n".join(
                f"{source}  →  {destination}"
                for source, destination in relocations[:12]
            )
            suffix = (
                f"\n…and {len(relocations) - 12} more." if len(relocations) > 12 else ""
            )
            self.misplaced.setText(
                f"Misplaced textures: {len(relocations)}\n{examples}{suffix}\n\nRelocation is intentionally planned separately because Blender references must be repaired before files are moved."
            )
        else:
            self.misplaced.setText("No textures outside Assets/Textures were detected.")
        self.set_status("Material and texture library scan complete.")
