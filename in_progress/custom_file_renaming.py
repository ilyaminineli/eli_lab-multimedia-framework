"""Legacy GUI adapter for the filename automation service.

This compatibility tool intentionally contains only UI wiring. Rename logic
lives in ``eli_lab.automation.renamer``.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from eli_lab.automation.renamer import (
    add_autonumber,
    add_datetime,
    apply_renames,
    change_extension,
    convert_case,
    insert_text,
    plan_renames,
    replace_text,
)


class FileRenamerApp(ttk.Frame):
    OPERATIONS = (
        "Add Date/Time",
        "Replace Text",
        "Insert Text",
        "Convert Case",
        "Add Auto-Number",
        "Remove Extension",
        "Change Extension",
    )

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=20)
        self.paths: list[Path] = []
        self.operations = []
        self.directory = tk.StringVar()
        self.operation = tk.StringVar(value=self.OPERATIONS[0])
        self._build()

    def _build(self) -> None:
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Directory").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.directory).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(self, text="Browse", command=self._browse).grid(row=0, column=2)
        ttk.Label(self, text="Operation").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(self, textvariable=self.operation, values=self.OPERATIONS, state="readonly").grid(row=1, column=1, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(self, text="Preview", command=self._preview).grid(row=2, column=1, sticky="w", pady=10)
        ttk.Button(self, text="Apply", command=self._apply).grid(row=2, column=2, sticky="e", pady=10)
        self.preview = tk.Listbox(self, height=20)
        self.preview.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.rowconfigure(3, weight=1)

    def _browse(self) -> None:
        selected = filedialog.askdirectory(title="Select Directory")
        if selected:
            self.directory.set(selected)
            self.paths = sorted(p for p in Path(selected).rglob("*") if p.is_file())

    def _transform(self):
        operation = self.operation.get()
        if operation == "Add Date/Time":
            return add_datetime
        if operation == "Replace Text":
            find = simpledialog.askstring("Find", "Text to replace:", parent=self)
            replacement = simpledialog.askstring("Replace", "Replacement:", parent=self)
            return lambda name: replace_text(name, find or "", replacement or "")
        if operation == "Insert Text":
            text = simpledialog.askstring("Insert", "Text:", parent=self) or ""
            position = simpledialog.askinteger("Insert", "Position:", parent=self, initialvalue=0) or 0
            return lambda name: insert_text(name, text, position)
        if operation == "Convert Case":
            mode = simpledialog.askstring("Case", "upper / lower / title / sentence:", parent=self) or "lower"
            return lambda name: convert_case(name, mode)
        if operation == "Add Auto-Number":
            start = simpledialog.askinteger("Number", "Starting number:", parent=self, initialvalue=1) or 1
            counter = [start]

            def transform(name: str) -> str:
                value = add_autonumber(name, counter[0])
                counter[0] += 1
                return value

            return transform
        if operation == "Remove Extension":
            return lambda name: Path(name).stem
        extension = simpledialog.askstring("Extension", "New extension:", parent=self) or ".png"
        return lambda name: change_extension(name, extension)

    def _preview(self) -> None:
        if not self.paths:
            messagebox.showerror("Error", "Select a directory first.")
            return
        try:
            self.operations = plan_renames(self.paths, self._transform())
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.preview.delete(0, tk.END)
        for operation in self.operations:
            self.preview.insert(tk.END, f"{operation.source.name}  ->  {operation.destination.name}")

    def _apply(self) -> None:
        if not self.operations:
            self._preview()
        if not self.operations:
            return
        try:
            apply_renames(self.operations)
        except Exception as exc:
            messagebox.showerror("Rename error", str(exc))
            return
        messagebox.showinfo("Done", f"Renamed {len(self.operations)} file(s).")
        self._browse()


def main() -> None:
    root = tk.Tk()
    root.title("ELI LAB — File Renaming")
    root.geometry("800x600")
    FileRenamerApp(root).pack(expand=True, fill="both")
    root.mainloop()


if __name__ == "__main__":
    main()
