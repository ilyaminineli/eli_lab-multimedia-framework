import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Resolve bundled templates relative to this repository instead of a developer-specific path.
BLENDER_FILES_DIR = Path(__file__).resolve().parent / "blender_files"
TEMPLATE_FILES = {
    "eli_lab territory_assets": "Asset.blend",
    "eli_lab territory_characters": "Character.blend",
    "eli_lab territory_locations": "Location.blend",
}
OUTPUT_FILE_EXTENSION = ".blend"
TOP_LEVEL_FOLDERS = list(TEMPLATE_FILES)


def create_blender_file(directory, template_path):
    """Copy a Blender template into a leaf project directory."""
    directory = Path(directory)
    template_path = Path(template_path)
    folder_name = directory.name.lower().replace(" ", "_")
    output_path = directory / f"{folder_name}{OUTPUT_FILE_EXTENSION}"

    try:
        if output_path.exists():
            print(f"Skipping existing Blender file: {output_path}")
            return False
        shutil.copy2(template_path, output_path)
        print(f"Created Blender file '{output_path.name}' in '{directory}'")
        return True
    except OSError as exc:
        print(f"Error creating Blender file in '{directory}': {exc}")
        return False


def validate_project(root_directory, progress_callback=None, start_progress_callback=None, end_progress_callback=None):
    """Create missing Blender template files in matching leaf directories."""
    root_directory = Path(root_directory)
    leaf_folders = []

    for root, dirs, _files in os.walk(root_directory):
        if not dirs:
            leaf_folders.append(Path(root))

    total_folders = len(leaf_folders)
    if start_progress_callback:
        start_progress_callback(total_folders)

    for processed_folders, leaf_folder in enumerate(leaf_folders, start=1):
        parents = [path.name for path in leaf_folder.parents if path != leaf_folder]
        top_level_parent = next((parent for parent in parents if parent in TEMPLATE_FILES), None)

        if top_level_parent is not None:
            template_path = BLENDER_FILES_DIR / TEMPLATE_FILES[top_level_parent]
            if not template_path.is_file():
                print(f"Error: template Blender file '{template_path}' not found.")
            else:
                create_blender_file(leaf_folder, template_path)
        else:
            print(f"Skipping '{leaf_folder}': no matching template category.")

        if progress_callback:
            progress_callback(processed_folders)

    if end_progress_callback:
        end_progress_callback()


root = tk.Tk()
root.title("Project Validation Tool")
root.geometry("600x350")

style = ttk.Style(root)
style.theme_use("clam")
bg_color = "#2e2e2e"
fg_color = "white"
text_color = "#d3d3d3"
button_bg_color = "#4a4a4a"
entry_bg_color = "#4a4a4a"
button_active_bg_color = "#606060"
style.configure(".", background=bg_color, foreground=fg_color, font=("Bahnschrift", 10))
style.configure("TLabel", background=bg_color, foreground=fg_color, padding=5, font=("Bahnschrift", 12))
style.configure("TButton", background=button_bg_color, foreground=fg_color, padding=8, relief="flat", font=("Bahnschrift", 11), borderwidth=0, focuscolor="gray", activebackground=button_active_bg_color, activeforeground=fg_color)
style.map("TButton", background=[("active", button_active_bg_color), ("disabled", button_bg_color)], foreground=[("disabled", "gray")])
style.configure("TEntry", fieldbackground=entry_bg_color, foreground=text_color, font=("Bahnschrift", 11))
style.configure("Horizontal.TProgressbar", troughcolor=button_bg_color)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")
folder_label = ttk.Label(main_frame, text="Project Folder:")
folder_label.pack(pady=(0, 5), fill="x")
folder_path_entry = ttk.Entry(main_frame, width=50)
folder_path_entry.pack(pady=(0, 5), fill="x")


def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)


browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.pack(pady=(0, 10), fill="x")
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=(10, 15), fill="x")


def start_validation():
    project_directory = folder_path_entry.get()
    if not project_directory:
        messagebox.showerror("Error", "Please select a project folder.")
        return

    validate_button["state"] = "disabled"
    browse_button["state"] = "disabled"

    def update_progress(value):
        root.after(0, lambda: progress_bar.configure(value=value))

    def start_progress(max_value):
        root.after(0, lambda: (progress_bar.configure(maximum=max_value), progress_bar.configure(value=0)))

    def end_progress():
        def finish():
            progress_bar["value"] = 0
            messagebox.showinfo("Info", "Project validation complete!")
            validate_button["state"] = "normal"
            browse_button["state"] = "normal"
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
