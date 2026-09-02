"""PySide6 implementations of the ELI LAB desktop tools."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from eli_lab.analysis.performance import analyze_tasks
from eli_lab.analysis.tasks import Task, list_tasks, load_task, save_task
from eli_lab.assets.optimization import QUALITY_PRESETS, optimize_png
from eli_lab.assets.textures import convert_directory
from eli_lab.automation.renamer import (
    add_autonumber,
    add_datetime,
    apply_renames,
    change_extension,
    convert_case,
    plan_renames,
    replace_text,
)
from eli_lab.project.documentation import build_project_markdown, write_project_markdown
from eli_lab.project.metadata import ProjectMetadata, load_metadata, save_metadata
from eli_lab.project.structure import ProjectTemplate, create_project_structure
from eli_lab.project.templates import ProjectStructure
from eli_lab.project.validation import validate_project
from eli_lab.validation.files import compare_directory, save_snapshot

from .common import ToolWidget, browse_directory, path_row


class MessageMixin:
    def success(self, text: str) -> None:
        QMessageBox.information(self, "ELI LAB", text)

    def failure(self, text: str) -> None:
        QMessageBox.critical(self, "ELI LAB", text)


class TemplateTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.characters: list[str] = []
        self.locations: list[str] = []
        self.assets: list[str] = []
        root = QVBoxLayout(self)
        form = QFormLayout()
        self.parent_path = QLineEdit()
        self.project_name = QLineEdit()
        form.addRow(path_row(self, "Parent directory", self.parent_path))
        form.addRow("Project name", self.project_name)
        root.addLayout(form)
        tabs = QTabWidget()
        for title, store in (("Characters", self.characters), ("Locations", self.locations), ("Assets", self.assets)):
            tabs.addTab(self._name_list(title, store), title)
        root.addWidget(tabs)
        create = QPushButton("Create Project Structure")
        create.clicked.connect(self.create_project)
        root.addWidget(create)
        self.add_status(root)

    def _name_list(self, title: str, store: list[str]) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        list_widget = QListWidget()
        layout.addWidget(list_widget)
        buttons = QHBoxLayout()
        add = QPushButton("Add")
        remove = QPushButton("Remove")
        buttons.addWidget(add)
        buttons.addWidget(remove)
        layout.addLayout(buttons)
        add.clicked.connect(lambda: self._add_name(title, store, list_widget))
        remove.clicked.connect(lambda: self._remove_name(store, list_widget))
        return page

    def _add_name(self, kind: str, store: list[str], widget: QListWidget) -> None:
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, kind, f"{kind[:-1]} name:")
        if ok and name.strip():
            store.append(name.strip())
            widget.addItem(name.strip())

    def _remove_name(self, store: list[str], widget: QListWidget) -> None:
        row = widget.currentRow()
        if row >= 0:
            store.pop(row)
            widget.takeItem(row)

    def create_project(self) -> None:
        parent = self.parent_path.text().strip()
        name = self.project_name.text().strip()
        if not parent or not name:
            self.failure("Parent directory and project name are required.")
            return
        template = ProjectTemplate(project_name=name, characters=tuple(self.characters))
        try:
            created = create_project_structure(Path(parent), template=template)
        except Exception as exc:
            self.failure(str(exc))
            return
        self.success(f"Created {len(created)} directories for {name}.")


class MetadataTool(ToolWidget, MessageMixin):
    fields = (
        ("project_name", "Project name"), ("project_code", "Project code"), ("client", "Client"),
        ("pipeline_version", "Pipeline version"), ("lead_artist", "Lead artist"), ("project_status", "Status"),
        ("license", "License"), ("key_themes", "Key themes"), ("contact", "Contact"), ("crew", "Crew"),
        ("project_description", "Description"), ("acknowledgements", "Acknowledgements"),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.edits: dict[str, QLineEdit | QPlainTextEdit] = {}
        root = QVBoxLayout(self)
        path = QHBoxLayout()
        self.directory = QLineEdit()
        path.addWidget(QLabel("Project directory"))
        path.addWidget(self.directory, 1)
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: browse_directory(self, self.directory))
        path.addWidget(browse)
        root.addLayout(path)
        form = QFormLayout()
        for key, label in self.fields:
            editor: QLineEdit | QPlainTextEdit
            editor = QPlainTextEdit() if key in {"project_description", "acknowledgements", "crew"} else QLineEdit()
            if isinstance(editor, QPlainTextEdit):
                editor.setMaximumHeight(80)
            self.edits[key] = editor
            form.addRow(label, editor)
        root.addLayout(form)
        buttons = QHBoxLayout()
        load = QPushButton("Load")
        save = QPushButton("Save")
        load.clicked.connect(self.load)
        save.clicked.connect(self.save)
        buttons.addWidget(load)
        buttons.addWidget(save)
        root.addLayout(buttons)
        self.add_status(root)

    def load(self) -> None:
        try:
            metadata = load_metadata(self.directory.text())
        except Exception as exc:
            self.failure(str(exc))
            return
        values = asdict(metadata)
        for key, editor in self.edits.items():
            value = str(values.get(key, ""))
            editor.setPlainText(value) if isinstance(editor, QPlainTextEdit) else editor.setText(value)
        self.set_status("Metadata loaded.")

    def save(self) -> None:
        values: dict[str, str] = {}
        for key, editor in self.edits.items():
            values[key] = editor.toPlainText() if isinstance(editor, QPlainTextEdit) else editor.text()
        try:
            path = save_metadata(ProjectMetadata(**values), self.directory.text())
        except Exception as exc:
            self.failure(str(exc))
            return
        self.success(f"Saved {path}")


class DocumentationTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit()
        root.addWidget(path_row(self, "Project directory", self.directory))
        self.output = QLineEdit()
        root.addWidget(path_row(self, "Output file", self.output, file=True, filter="Markdown (*.md);;All files (*)"))
        self.preview = QTextBrowser()
        root.addWidget(self.preview, 1)
        buttons = QHBoxLayout()
        preview = QPushButton("Preview")
        write = QPushButton("Write README")
        preview.clicked.connect(self.render)
        write.clicked.connect(self.write)
        buttons.addWidget(preview)
        buttons.addWidget(write)
        root.addLayout(buttons)
        self.add_status(root)

    def _metadata(self) -> ProjectMetadata:
        return load_metadata(self.directory.text())

    def render(self) -> None:
        try:
            self.preview.setPlainText(build_project_markdown(self._metadata()))
            self.set_status("Preview generated.")
        except Exception as exc:
            self.failure(str(exc))

    def write(self) -> None:
        try:
            metadata = self._metadata()
            output = self.output.text().strip() or str(Path(self.directory.text()) / "README.md")
            path = write_project_markdown(metadata, output)
            self.success(f"Wrote {path}")
        except Exception as exc:
            self.failure(str(exc))


class FileValidationTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit()
        root.addWidget(path_row(self, "Project directory", self.directory))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Path", "Status"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        root.addWidget(self.tree, 1)
        buttons = QHBoxLayout()
        for label, handler in (("Analyze", self.analyze), ("Save Snapshot", self.snapshot)):
            button = QPushButton(label)
            button.clicked.connect(handler)
            buttons.addWidget(button)
        root.addLayout(buttons)
        self.add_status(root)

    def analyze(self) -> None:
        try:
            status = compare_directory(self.directory.text())
        except Exception as exc:
            self.failure(str(exc))
            return
        self.tree.clear()
        for path, state in sorted(status.items()):
            QTreeWidgetItem(self.tree, [path, state])
        self.set_status(f"Found {len(status)} changed files.")

    def snapshot(self) -> None:
        try:
            path = save_snapshot(self.directory.text())
        except Exception as exc:
            self.failure(str(exc))
            return
        self.success(f"Snapshot saved to {path}")


class ProjectValidationTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit()
        root.addWidget(path_row(self, "Project directory", self.directory))
        self.required = QPlainTextEdit("assets\nscenes\nsource\nrenders\nexports\ndocs\ntasks")
        self.required.setMaximumHeight(120)
        root.addWidget(QLabel("Required folders (one per line)"))
        root.addWidget(self.required)
        run = QPushButton("Validate Project")
        run.clicked.connect(self.validate)
        root.addWidget(run)
        self.result = QLabel()
        self.result.setWordWrap(True)
        root.addWidget(self.result)
        self.add_status(root)

    def validate(self) -> None:
        folders = tuple(line.strip() for line in self.required.toPlainText().splitlines() if line.strip())
        try:
            report = validate_project(self.directory.text(), folders)
        except Exception as exc:
            self.failure(str(exc))
            return
        self.result.setText("Valid project." if report.valid else "\n".join(f"{issue.path}: {issue.message}" for issue in report.issues))
        self.set_status("Validation complete.")


class TextureConversionTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit()
        root.addWidget(path_row(self, "Texture directory", self.directory))
        self.recursive = QCheckBox("Include subdirectories")
        self.replace = QCheckBox("Delete original files after successful conversion")
        root.addWidget(self.recursive)
        root.addWidget(self.replace)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        root.addWidget(self.progress)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        root.addWidget(self.log, 1)
        run = QPushButton("Convert Textures")
        run.clicked.connect(lambda: self._run(run))
        root.addWidget(run)
        self.add_status(root)

    def _run(self, button: QPushButton) -> None:
        self.log.clear()
        self.progress.show()
        self.run_background(button, convert_directory, self._finished, self.directory.text(), recursive=self.recursive.isChecked(), replace_original=self.replace.isChecked())

    def _finished(self, results: list) -> None:
        self.progress.hide()
        for result in results:
            self.log.appendPlainText(f"{result.source}: {'converted' if result.converted else result.error or 'skipped'}")
        self.set_status(f"Processed {len(results)} files.")


class TextureOptimizationTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.file = QLineEdit()
        root.addWidget(path_row(self, "PNG file", self.file, file=True, filter="PNG files (*.png)"))
        self.quality = QComboBox()
        self.quality.addItems(QUALITY_PRESETS)
        root.addWidget(QLabel("Quality preset"))
        root.addWidget(self.quality)
        run = QPushButton("Optimize PNG")
        run.clicked.connect(lambda: self._run(run))
        root.addWidget(run)
        self.add_status(root)

    def _run(self, button: QPushButton) -> None:
        self.run_background(button, optimize_png, self._finished, self.file.text(), quality=self.quality.currentText())

    def _finished(self, result) -> None:
        if result.error:
            self.failure(result.error)
        elif result.skipped:
            self.set_status("File skipped.")
        else:
            self.success(f"Optimized {result.source}")


class RenameTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.files = QListWidget()
        root.addWidget(self.files, 1)
        choose = QPushButton("Choose Files")
        choose.clicked.connect(self.choose_files)
        root.addWidget(choose)
        controls = QGridLayout()
        self.operation = QComboBox()
        self.operation.addItems(["Replace text", "Upper case", "Lower case", "Title case", "Sentence case", "Change extension", "Add datetime", "Add autonumber"])
        self.find = QLineEdit()
        self.replace = QLineEdit()
        self.extension = QLineEdit("png")
        self.position = QSpinBox(); self.position.setRange(1, 9999); self.position.setValue(3)
        controls.addWidget(QLabel("Operation"), 0, 0); controls.addWidget(self.operation, 0, 1)
        controls.addWidget(QLabel("Find"), 1, 0); controls.addWidget(self.find, 1, 1)
        controls.addWidget(QLabel("Replace"), 2, 0); controls.addWidget(self.replace, 2, 1)
        controls.addWidget(QLabel("Extension"), 3, 0); controls.addWidget(self.extension, 3, 1)
        controls.addWidget(QLabel("Number padding"), 4, 0); controls.addWidget(self.position, 4, 1)
        root.addLayout(controls)
        preview = QPushButton("Preview")
        apply = QPushButton("Apply Rename")
        preview.clicked.connect(self.preview)
        apply.clicked.connect(self.apply)
        row = QHBoxLayout(); row.addWidget(preview); row.addWidget(apply); root.addLayout(row)
        self.table = QTableWidget(0, 2); self.table.setHorizontalHeaderLabels(["Source", "Destination"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch); self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        root.addWidget(self.table, 1)
        self.add_status(root)

    def choose_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Select files")
        self.files.clear()
        self.files.addItems(paths)

    def transform(self, name: str, index: int = 0) -> str:
        op = self.operation.currentText()
        if op == "Replace text": return replace_text(name, self.find.text(), self.replace.text())
        if op == "Upper case": return convert_case(name, "upper")
        if op == "Lower case": return convert_case(name, "lower")
        if op == "Title case": return convert_case(name, "title")
        if op == "Sentence case": return convert_case(name, "sentence")
        if op == "Change extension": return change_extension(name, self.extension.text())
        if op == "Add datetime": return add_datetime(name)
        return add_autonumber(name, index + 1, padding=self.position.value())

    def plan(self):
        paths = [self.files.item(i).text() for i in range(self.files.count())]
        return plan_renames(paths, lambda n: self.transform(n, paths.index(str(n)) if str(n) in paths else 0))

    def preview(self) -> None:
        paths = [self.files.item(i).text() for i in range(self.files.count())]
        operations = [op for i, op in enumerate(plan_renames(paths, lambda n, i=i: self.transform(n, i))) if op.changed]
        self.table.setRowCount(len(operations))
        for row, op in enumerate(operations):
            self.table.setItem(row, 0, QTableWidgetItem(str(op.source)))
            self.table.setItem(row, 1, QTableWidgetItem(str(op.destination)))
        self.set_status(f"Preview contains {len(operations)} changes.")

    def apply(self) -> None:
        paths = [self.files.item(i).text() for i in range(self.files.count())]
        operations = plan_renames(paths, lambda n, i=0: self.transform(n, i))
        try:
            changed = apply_renames(operations)
        except Exception as exc:
            self.failure(str(exc)); return
        self.success(f"Renamed {len(changed)} files.")
        self.choose_files()


class TasksTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit(); root.addWidget(path_row(self, "Project directory", self.directory))
        form = QFormLayout()
        self.name = QLineEdit(); self.artist = QLineEdit(); self.due = QDateEdit(QDate.currentDate()); self.due.setCalendarPopup(True)
        self.status = QComboBox(); self.status.addItems(["Not Started", "In Progress", "Completed"])
        self.description = QPlainTextEdit(); self.description.setMaximumHeight(100)
        form.addRow("Task", self.name); form.addRow("Artist", self.artist); form.addRow("Due date", self.due); form.addRow("Status", self.status); form.addRow("Description", self.description)
        root.addLayout(form)
        save = QPushButton("Save Task"); save.clicked.connect(self.save)
        reload_ = QPushButton("Reload Task List"); reload_.clicked.connect(self.reload)
        row = QHBoxLayout(); row.addWidget(save); row.addWidget(reload_); root.addLayout(row)
        self.tasks = QListWidget(); self.tasks.itemClicked.connect(self.load_selected)
        root.addWidget(self.tasks, 1)
        self.add_status(root)

    def reload(self) -> None:
        self.tasks.clear()
        for path in list_tasks(self.directory.text()):
            self.tasks.addItem(path.name)
        self.set_status(f"Loaded {self.tasks.count()} tasks.")

    def load_selected(self, item: QListWidgetItem) -> None:
        try:
            task = load_task(Path(self.directory.text()) / item.text())
        except Exception as exc:
            self.failure(str(exc)); return
        self.name.setText(task.name); self.artist.setText(task.artist); self.due.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day)); self.description.setPlainText(task.description)
        self.status.setCurrentText(task.status)

    def save(self) -> None:
        task = Task(self.name.text().strip(), self.artist.text().strip(), self.due.date().toPython(), self.status.currentText(), self.description.toPlainText())
        try:
            path = save_task(task, self.directory.text())
        except Exception as exc:
            self.failure(str(exc)); return
        self.success(f"Saved {path}"); self.reload()


class PerformanceTool(ToolWidget, MessageMixin):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.directory = QLineEdit(); root.addWidget(path_row(self, "Project directory", self.directory))
        run = QPushButton("Analyze Tasks"); run.clicked.connect(self.analyze); root.addWidget(run)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True); root.addWidget(self.output, 1)
        self.add_status(root)

    def analyze(self) -> None:
        mappings = []
        try:
            for path in list_tasks(self.directory.text()):
                mappings.append(load_task(path).to_mapping())
            report = analyze_tasks(mappings)
        except Exception as exc:
            self.failure(str(exc)); return
        lines = [f"Average days from due date: {report.average_days_from_due:.2f}", "", "Tasks by artist:"]
        lines.extend(f"  {artist}: {count}" for artist, count in report.task_counts_by_artist.items())
        lines.extend(["", "Common task names:", *[f"  {name}" for name in report.common_task_names]])
        self.output.setPlainText("\n".join(lines)); self.set_status(f"Analyzed {len(mappings)} tasks.")


TOOL_WIDGETS: dict[str, type[QWidget]] = {
    "template": TemplateTool,
    "metadata": MetadataTool,
    "documentation": DocumentationTool,
    "file_validation": FileValidationTool,
    "project_validation": ProjectValidationTool,
    "texture_conversion": TextureConversionTool,
    "texture_optimization": TextureOptimizationTool,
    "renaming": RenameTool,
    "tasks": TasksTool,
    "performance": PerformanceTool,
}


def create_tool_widget(key: str, parent: QWidget | None = None) -> QWidget:
    try:
        factory = TOOL_WIDGETS[key]
    except KeyError as exc:
        raise ValueError(f"Unknown tool: {key}") from exc
    return factory(parent)


def run_standalone(widget_class: type[QWidget], title: str) -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    window.setWindowTitle(title)
    window.resize(900, 700)
    window.setCentralWidget(widget_class())
    window.show()
    return app.exec()
