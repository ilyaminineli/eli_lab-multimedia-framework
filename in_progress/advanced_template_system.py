"""Legacy Tkinter adapter for the project template service."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path

from eli_lab.project.structure import ProjectTemplate, create_project_structure


class FolderAutomationApp(ttk.Frame):
    """GUI-only adapter around ``eli_lab.project.structure``."""

    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.project_path = tk.StringVar()
        self.project_name = tk.StringVar()
        self.characters: list[str] = []
        self.locations: dict[str, list[str]] = {}
        self.assets: dict[str, list[str]] = {}
        self.columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Project Path:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.project_path).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(self, text="Browse", command=self.browse_folder).grid(row=0, column=2)

        ttk.Label(self, text="Project Name:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(self, textvariable=self.project_name).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.characters_frame = self._section("Characters", 2, self.characters, self.add_character, self.delete_character)
        self.locations_frame = self._section("Locations", 3, self.locations, self.add_location, self.delete_location)
        self.assets_frame = self._section("Assets", 4, self.assets, self.add_asset, self.delete_asset)

        ttk.Button(self, text="Create Structure", command=self.create_folders).grid(row=5, column=1, sticky="e", pady=12)

    def _section(self, title, row, collection, add_command, delete_command):
        frame = ttk.LabelFrame(self, text=title, padding=6)
        frame.grid(row=row, column=1, sticky="ew", pady=5)
        frame.columnconfigure(0, weight=1)
        ttk.Button(frame, text=f"+ {title[:-1]}", command=add_command).grid(row=0, column=1, padx=4)
        return frame

    def browse_folder(self):
        selected = filedialog.askdirectory(title="Select project parent directory")
        if selected:
            self.project_path.set(selected)

    def add_character(self):
        name = simpledialog.askstring("Character", "Enter character name:")
        if name:
            self.characters.append(name.strip())
            self._refresh()

    def delete_character(self, index):
        del self.characters[index]
        self._refresh()

    def add_location(self):
        name = simpledialog.askstring("Location", "Enter location name:")
        if name:
            self.locations[name.strip()] = []
            self._refresh()

    def delete_location(self, name):
        self.locations.pop(name, None)
        self._refresh()

    def add_asset(self):
        name = simpledialog.askstring("Asset", "Enter asset name:")
        if name:
            self.assets[name.strip()] = []
            self._refresh()

    def delete_asset(self, name):
        self.assets.pop(name, None)
        self._refresh()

    def _refresh(self):
        for frame in (self.characters_frame, self.locations_frame, self.assets_frame):
            for widget in frame.winfo_children()[1:]:
                widget.destroy()
        for i, name in enumerate(self.characters, 1):
            ttk.Label(self.characters_frame, text=name).grid(row=i, column=0, sticky="w")
            ttk.Button(self.characters_frame, text="Delete", command=lambda idx=i - 1: self.delete_character(idx)).grid(row=i, column=2)
        for i, name in enumerate(self.locations, 1):
            ttk.Label(self.locations_frame, text=name).grid(row=i, column=0, sticky="w")
            ttk.Button(self.locations_frame, text="Delete", command=lambda n=name: self.delete_location(n)).grid(row=i, column=2)
        for i, name in enumerate(self.assets, 1):
            ttk.Label(self.assets_frame, text=name).grid(row=i, column=0, sticky="w")
            ttk.Button(self.assets_frame, text="Delete", command=lambda n=name: self.delete_asset(n)).grid(row=i, column=2)

    def create_folders(self):
        parent = self.project_path.get().strip()
        name = self.project_name.get().strip()
        if not parent or not name:
            messagebox.showerror("Error", "Project Path and Project Name are required.")
            return
        template = ProjectTemplate(
            project_name=name,
            characters=tuple(self.characters),
            locations=tuple((key, tuple(value)) for key, value in self.locations.items()),
            assets=tuple((key, tuple(value)) for key, value in self.assets.items()),
        )
        try:
            created = create_project_structure(Path(parent), template=template)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        messagebox.showinfo("Success", f"Created {len(created)} directories for {name}.")


def main():
    root = tk.Tk()
    root.title("ELI LAB — Advanced Template System")
    root.geometry("700x600")
    app = FolderAutomationApp(root)
    app.pack(expand=True, fill="both")
    root.mainloop()


if __name__ == "__main__":
    main()
