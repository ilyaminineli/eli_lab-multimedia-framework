"""Legacy GUI adapter for Blender template validation.

New reusable logic lives in ``eli_lab.project.blender``. This file remains as
an executable compatibility entry point for existing workflows.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from eli_lab.core.paths import BLENDER_TEMPLATES_ROOT
from eli_lab.project.blender import TEMPLATE_FILES, provision_blender_file


def create_blender_file(directory, template_path):
    """Compatibility helper retained for old imports."""
    directory = Path(directory)
    template_path = Path(template_path)
    output_path = directory / f"{directory.name.lower().replace(' ', '_')}.blend"
    if output_path.exists():
        return False
    try:
        import shutil
        shutil.copy2(template_path, output_path)
    except OSError:
        return False
    return True


def validate_project(root_directory, progress_callback=None, start_progress_callback=None, end_progress_callback=None):
    """Create missing Blender files in recognized asset leaves."""
    root_directory = Path(root_directory).expanduser().resolve()
    leaf_folders = [Path(root) for root, dirs, _files in os.walk(root_directory) if not dirs]

    if start_progress_callback:
        start_progress_callback(len(leaf_folders))

    for processed, leaf_folder in enumerate(leaf_folders, start=1):
        categories = set(TEMPLATE_FILES)
        category = next((name for name in categories if name in {parent.name for parent in leaf_folder.parents}), None)
        if category:
            try:
                provision_blender_file(leaf_folder, category)
            except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
                print(f"Skipping {leaf_folder}: {exc}")
        if progress_callback:
            progress_callback(processed)

    if end_progress_callback:
        end_progress_callback()


root = tk.Tk()
root.title("Project Validation Tool")
root.geometry("600x350")

style = ttk.Style(root)
style.theme_use("clam")
style.configure(".", background="#2e2e2e", foreground="white", font=("Bahnschrift", 10))
style.configure("TLabel", background="#2e2e2e", foreground="white", padding=5, font=("Bahnschrift", 12))
style.configure("TButton", background="#4a4a4a", foreground="white", padding=8, relief="flat", font=("Bahnschrift", 11), borderwidth=0)
style.configure("TEntry", fieldbackground="#4a4a4a", foreground="#d3d3d3", font=("Bahnschrift", 11))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")
ttk.Label(main_frame, text="Project Folder:").pack(pady=(0, 5), fill="x")
folder_path_entry = ttk.Entry(main_frame, width=50)
folder_path_entry.pack(pady=(0, 5), fill="x")


def browse_folder():
    selected = filedialog.askdirectory()
    if selected:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, selected)


browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.pack(pady=(0, 10), fill="x")
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=(10, 15), fill="x")


def start_validation():
    project_directory = folder_path_entry.get().strip()
    if not project_directory:
        messagebox.showerror("Error", "Please select a project folder.")
        return

    validate_button["state"] = "disabled"
    browse_button["state"] = "disabled"

    def update_progress(value):
        root.after(0, lambda: progress_bar.configure(value=value))

    def start_progress(maximum):
        root.after(0, lambda: progress_bar.configure(maximum=maximum, value=0))

    def end_progress():
        def finish():
            progress_bar["value"] = 0
            validate_button["state"] = "normal"
            browse_button["state"] = "normal"
            messagebox.showinfo("Info", f"Validation complete. Templates source: {BLENDER_TEMPLATES_ROOT}")
        root.after(0, finish)

    threading.Thread(
        target=validate_project,
        args=(project_directory,),
        kwargs={
            "progress_callback": update_progress,
            "start_progress_callback": start_progress,
            "end_progress_callback": end_progress,
        },
        daemon=True,
    ).start()


validate_button = ttk.Button(main_frame, text="Validate Project", command=start_validation)
validate_button.pack(pady=(15, 0), fill="x")
root.mainloop()
