"""Legacy Tkinter adapter for :mod:`eli_lab.project.metadata`."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from eli_lab.project.metadata import ProjectMetadata, load_metadata, save_metadata


class MetadataForm(ttk.Frame):
    """GUI-only adapter; metadata models and persistence live in the package."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.metadata_dir: Path | None = None
        self.fields = {
            "project_name": tk.StringVar(),
            "project_code": tk.StringVar(),
            "client": tk.StringVar(),
            "pipeline_version": tk.StringVar(),
            "lead_artist": tk.StringVar(),
            "project_description": tk.StringVar(),
            "project_status": tk.StringVar(value="In Development"),
            "license": tk.StringVar(value="MIT"),
            "key_themes": tk.StringVar(),
            "contact": tk.StringVar(),
            "crew": tk.StringVar(),
            "acknowledgements": tk.StringVar(),
        }
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        row = 0
        for name, variable in self.fields.items():
            ttk.Label(self, text=name.replace("_", " ").title()).grid(row=row, column=0, sticky="w", padx=5, pady=3)
            ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
            row += 1

        ttk.Button(self, text="Select Directory", command=self.browse_directory).grid(row=row, column=0, padx=5, pady=10)
        ttk.Button(self, text="Load Metadata", command=self.load_metadata).grid(row=row, column=1, sticky="w", padx=5, pady=10)
        ttk.Button(self, text="Save Metadata", command=self.save_metadata).grid(row=row, column=1, sticky="e", padx=5, pady=10)

    def browse_directory(self):
        selected = filedialog.askdirectory(title="Select Metadata Directory")
        self.metadata_dir = Path(selected) if selected else None

    def load_metadata(self):
        if self.metadata_dir is None:
            messagebox.showerror("Load Error", "Please select a metadata directory first.")
            return
        try:
            metadata = load_metadata(self.metadata_dir)
        except FileNotFoundError:
            messagebox.showinfo("Metadata Load", "No metadata file found.")
            return
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))
            return
        for name, variable in self.fields.items():
            variable.set(getattr(metadata, name))

    def save_metadata(self):
        if self.metadata_dir is None:
            messagebox.showerror("Save Error", "Please select a metadata directory first.")
            return
        try:
            path = save_metadata(
                ProjectMetadata(**{name: variable.get() for name, variable in self.fields.items()}),
                self.metadata_dir,
            )
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))
            return
        messagebox.showinfo("Success", f"Project metadata saved to:\n{path}")


def main():
    root = tk.Tk()
    root.title("ELI LAB — Project Metadata")
    root.geometry("700x500")
    MetadataForm(root, padding=20).pack(expand=True, fill="both")
    root.mainloop()


if __name__ == "__main__":
    main()
