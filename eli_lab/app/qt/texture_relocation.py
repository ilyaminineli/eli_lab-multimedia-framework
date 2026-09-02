"""Interactive texture relocation and Blender reference repair UI for eli_lab."""

from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView

from eli_lab.production.blender_inspection import find_blender
from eli_lab.production.texture_relocation import (
    TextureRelocationCandidate,
    plan_referenced_texture_relocations,
    relocate_texture_candidate,
)

from .common import ToolWidget


class TextureRelocationTool(ToolWidget):
    """Review referenced textures outside Assets/Textures and repair them safely."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.candidates: list[TextureRelocationCandidate] = []
        root = QVBoxLayout(self)
        row = QHBoxLayout()
        self.directory = QLabel("No project selected")
        self.directory.setWordWrap(True)
        browse = QPushButton("Choose Project")
        scan = QPushButton("Scan")
        browse.clicked.connect(self.choose_project)
        scan.clicked.connect(self.scan)
        row.addWidget(self.directory, 1)
        row.addWidget(browse)
        row.addWidget(scan)
        root.addLayout(row)

        self.summary = QLabel("Scan a project to find referenced textures outside Assets/Textures.")
        self.summary.setWordWrap(True)
        root.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Texture", "Suggested location", "Used by Blender files", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        root.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        self.relocate = QPushButton("Relocate + Repair Selected")
        self.relocate.clicked.connect(self.relocate_selected)
        self.relocate.setEnabled(False)
        buttons.addWidget(self.relocate)
        root.addLayout(buttons)
        self.add_status(root)

    def choose_project(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select project folder")
        if path:
            self.directory.setText(path)
            self.scan()

    def scan(self) -> None:
        root = self.directory.text().strip()
        if not root or root == "No project selected":
            self.show_error("Choose a project folder first.")
            return
        blender = find_blender()
        if not blender:
            self.show_error("Blender was not found on PATH. Blender-aware relocation requires a local Blender executable.")
            return
        scan_button = next((button for button in self.findChildren(QPushButton) if button.text() == "Scan"), None)
        if scan_button is None:
            self.show_error("Internal UI error: Scan button not found.")
            return
        self.run_background(scan_button, plan_referenced_texture_relocations, self._show_candidates, root, blender_executable=blender)

    def _show_candidates(self, candidates: list[TextureRelocationCandidate]) -> None:
        self.candidates = candidates
        self.table.setRowCount(len(candidates))
        for row, candidate in enumerate(candidates):
            self.table.setItem(row, 0, QTableWidgetItem(str(candidate.source)))
            self.table.setItem(row, 1, QTableWidgetItem(str(candidate.destination)))
            self.table.setItem(row, 2, QTableWidgetItem(str(len(candidate.blend_files))))
            self.table.setItem(row, 3, QTableWidgetItem("Safe to review" if candidate.safe else "Needs review"))
        self.relocate.setEnabled(bool(candidates))
        self.summary.setText(f"Found {len(candidates)} referenced texture(s) outside Assets/Textures.")
        self.set_status("Texture relocation scan complete.")

    def relocate_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.candidates):
            self.show_error("Select a texture first.")
            return
        candidate = self.candidates[row]
        if not candidate.safe:
            self.show_error("This candidate is not marked safe for automatic relocation.")
            return
        if not find_blender():
            self.show_error("Blender was not found on PATH.")
            return
        message = (
            f"Relocate:\n\n{candidate.source}\n\n→ {candidate.destination}\n\n"
            f"and repair {len(candidate.blend_files)} Blender file(s)?\n\n"
            "eli_lab will back up the affected .blend files before changing them."
        )
        if QMessageBox.question(self, "Confirm texture relocation", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.run_background(
            self.relocate,
            relocate_texture_candidate,
            self._relocation_finished,
            self.directory.text().strip(),
            candidate,
            blender_executable=find_blender(),
        )

    def _relocation_finished(self, result) -> None:
        self.set_status(
            f"Relocated {result.source} → {result.destination}; repaired {len(result.repaired_blends)} Blender file(s). "
            f"Backup: {result.backup_directory}"
        )
        self.scan()
