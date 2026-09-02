"""Project-first PySide6 workspace for scanning, editing and normalizing projects."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QHeaderView,
)

from eli_lab.project.documentation_presets import PRESETS, write_preset_markdown
from eli_lab.project.migration import apply_migration, build_migration_plan, generate_entity_metadata, generate_metadata, scan_project
from eli_lab.project.metadata import save_metadata
from eli_lab.project.workspace import load_entity_metadata, load_history, save_entity_metadata, scan_workspace

from .common import ToolWidget


class WorkspaceTool(ToolWidget):
    """Open any project and operate on its live production hierarchy."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root_path: Path | None = None
        self.scan = None
        self.plan = None
        self.entities: dict[str, object] = {}

        root = QVBoxLayout(self)
        header = QHBoxLayout()
        self.directory = QLineEdit()
        self.directory.setPlaceholderText("Project folder…")
        browse = QPushButton("Browse")
        scan = QPushButton("Scan Project")
        browse.clicked.connect(self.browse)
        scan.clicked.connect(self.refresh)
        header.addWidget(self.directory, 1)
        header.addWidget(browse)
        header.addWidget(scan)
        root.addLayout(header)

        self.summary = QLabel("No project loaded.")
        self.summary.setWordWrap(True)
        root.addWidget(self.summary)

        splitter = QSplitter()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Entity", "Kind"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.itemSelectionChanged.connect(self.select_entity)
        splitter.addWidget(self.tree)

        editor = QWidget()
        editor_layout = QVBoxLayout(editor)
        meta_box = QGroupBox("Entity")
        form = QFormLayout(meta_box)
        self.entity_name = QLineEdit(); self.entity_name.setReadOnly(True)
        self.entity_kind = QLineEdit(); self.entity_kind.setReadOnly(True)
        self.entity_path = QLineEdit(); self.entity_path.setReadOnly(True)
        self.entity_description = QPlainTextEdit()
        form.addRow("Name", self.entity_name)
        form.addRow("Type", self.entity_kind)
        form.addRow("Path", self.entity_path)
        form.addRow("Description", self.entity_description)
        editor_layout.addWidget(meta_box)

        buttons = QHBoxLayout()
        save = QPushButton("Save Entity")
        open_folder = QPushButton("Open Folder")
        save.clicked.connect(self.save_entity)
        open_folder.clicked.connect(self.open_folder)
        buttons.addWidget(save); buttons.addWidget(open_folder)
        editor_layout.addLayout(buttons)

        pipeline = QGroupBox("Pipeline")
        pipeline_layout = QVBoxLayout(pipeline)
        self.profile = QLabel("Profile: —")
        self.plan_label = QLabel("Normalization: —")
        pipeline_layout.addWidget(self.profile)
        pipeline_layout.addWidget(self.plan_label)
        pbuttons = QHBoxLayout()
        normalize = QPushButton("Apply Safe Normalization")
        metadata = QPushButton("Generate Metadata")
        entities = QPushButton("Generate Entity Records")
        normalize.clicked.connect(self.normalize)
        metadata.clicked.connect(self.make_metadata)
        entities.clicked.connect(self.make_entities)
        pbuttons.addWidget(normalize); pbuttons.addWidget(metadata); pbuttons.addWidget(entities)
        pipeline_layout.addLayout(pbuttons)
        editor_layout.addWidget(pipeline)

        docs = QGroupBox("Documentation")
        docs_layout = QHBoxLayout(docs)
        self.preset = QComboBox(); self.preset.addItems(list(PRESETS))
        generate = QPushButton("Generate Documentation")
        generate.clicked.connect(self.make_documentation)
        docs_layout.addWidget(self.preset, 1); docs_layout.addWidget(generate)
        editor_layout.addWidget(docs)

        history = QGroupBox("Recent History")
        history_layout = QVBoxLayout(history)
        self.history = QPlainTextEdit(); self.history.setReadOnly(True); self.history.setMaximumHeight(130)
        history_layout.addWidget(self.history)
        editor_layout.addWidget(history)
        editor_layout.addStretch(1)
        splitter.addWidget(editor)
        splitter.setSizes([360, 640])
        root.addWidget(splitter, 1)
        self.add_status(root)

    def browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select project folder")
        if path:
            self.directory.setText(path)
            self.refresh()

    def refresh(self) -> None:
        try:
            root = Path(self.directory.text()).expanduser().resolve()
            self.scan = scan_project(root)
            self.plan = build_migration_plan(self.scan)
            summary = scan_workspace(root)
            self.root_path = root
        except Exception as exc:
            QMessageBox.critical(self, "ELI LAB", str(exc))
            return
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(summary.counts.items())) or "No recognized entities"
        self.summary.setText(f"{root.name}  ·  {self.scan.files} files  ·  {self.scan.compliance}% canonical structure  ·  {counts}")
        self.profile.setText(f"Profile: {self.scan.profile}  ·  {self.scan.compliance}%")
        self.plan_label.setText(f"Normalization: {len(self.plan.operations)} proposed moves ({len(self.plan.create_directories)} directories)")
        self.tree.clear(); self.entities.clear()
        grouped = {}
        for entity in summary.entities:
            grouped.setdefault(entity.kind, []).append(entity)
            self.entities[entity.relative_path] = entity
        for kind, items in sorted(grouped.items()):
            group = QTreeWidgetItem([kind.replace('_', ' ').title(), ""])
            self.tree.addTopLevelItem(group)
            for entity in items:
                item = QTreeWidgetItem([entity.name, kind.replace('_', ' ').title()])
                item.setData(0, 32, entity.relative_path)
                group.addChild(item)
            group.setExpanded(True)
        lines = []
        for entry in load_history(root, 12):
            lines.append(f"{entry.get('timestamp', '')}  {entry.get('operation', '')}  {entry.get('target', '')}")
        self.history.setPlainText("\n".join(lines))
        self.set_status("Project scanned.")

    def select_entity(self) -> None:
        items = self.tree.selectedItems()
        if not items or not self.root_path:
            return
        relative = items[0].data(0, 32)
        entity = self.entities.get(relative)
        if entity is None:
            return
        metadata = load_entity_metadata(self.root_path / entity.path)
        self.entity_name.setText(metadata.name)
        self.entity_kind.setText(metadata.kind)
        self.entity_path.setText(str(entity.path))
        self.entity_description.setPlainText(metadata.description)

    def save_entity(self) -> None:
        if not self.root_path or not self.entity_name.text():
            return
        entity = self.entities.get(self.entity_path.text().replace('\\', '/'))
        if entity is None:
            return
        metadata = load_entity_metadata(self.root_path / entity.path)
        metadata.description = self.entity_description.toPlainText().strip()
        save_entity_metadata(self.root_path / entity.path, metadata)
        self.refresh()
        self.set_status("Entity metadata saved.")

    def open_folder(self) -> None:
        if self.root_path and self.entity_path.text():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.root_path / self.entity_path.text())))

    def make_metadata(self) -> None:
        if not self.scan:
            return
        metadata = generate_metadata(self.scan)
        save_metadata(metadata, self.scan.root)
        self.set_status("Project metadata generated.")
        self.refresh()

    def make_entities(self) -> None:
        if self.root_path:
            count = generate_entity_metadata(self.root_path)
            self.set_status(f"Generated {count} entity records.")
            self.refresh()

    def normalize(self) -> None:
        if not self.plan:
            return
        if not self.plan.operations:
            self.set_status("No safe normalization moves detected.")
            return
        preview = "\n".join(f"{op.source}  →  {op.destination}" for op in self.plan.operations[:20])
        result = QMessageBox.question(self, "Apply normalization", f"Apply {len(self.plan.high_confidence)} high-confidence moves?\n\n{preview}")
        if result != QMessageBox.StandardButton.Yes:
            return
        applied = apply_migration(self.plan)
        self.set_status(f"Applied {len(applied)} moves. Refreshing project…")
        self.refresh()

    def make_documentation(self) -> None:
        if not self.root_path:
            return
        summary = scan_workspace(self.root_path)
        preset = self.preset.currentText()
        output = self.root_path / "Docs" / {v: k for k, v in PRESETS.items()}[preset]
        output = output / ("README.md" if preset == "project" else f"{preset}.md")
        path = write_preset_markdown(summary, output, preset)
        self.set_status(f"Generated {path}")

