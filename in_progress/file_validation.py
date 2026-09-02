import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- Constants ---
VALIDATION_FILE = "folder_validation.json"
DEFAULT_FONT = ("Bahnschrift", 10)


# --- Helper Functions ---
def get_folder_size(start_path='.'):
    """Calculates the total size of files in a directory (in bytes)."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):  # Skip symbolic links
                total_size += os.path.getsize(fp)
    return total_size


def analyze_directory(root_directory):
    """Analyzes a directory and its subdirectories, returning file metadata."""
    files = {}
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # Calculate relative path
            relative_path = os.path.relpath(filepath, root_directory)
            try:
                files[relative_path] = {
                    "size": os.path.getsize(filepath),
                    "modified": os.path.getmtime(filepath)
                }
            except Exception as e:
                print(f"Error analyzing file {filepath}: {e}")
    return files


def load_validation_data(directory):
    """Loads validation data from a JSON file in the given directory."""
    filepath = os.path.join(directory, VALIDATION_FILE)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"files": {}}  # Default empty state if no JSON
    except Exception as e:
        print(f"Error loading validation {e}")
        return {"files": {}}


def save_validation_data(directory, data):
    """Saves validation data to a JSON file in the given directory."""
    filepath = os.path.join(directory, VALIDATION_FILE)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving validation data to {filepath}: {e}")


def compare_directory(directory):
    """Compares directory content (incl. subdirs) to the saved validation data."""
    current_files = analyze_directory(directory)
    validation_data = load_validation_data(directory)
    status = {}

    # Ensure "files" key exists
    if "files" not in validation_data:
        validation_data["files"] = {}

    # Check for new, modified, or deleted files
    for filepath, details in current_files.items():
        if filepath not in validation_data["files"]:
            status[filepath] = "new"
        else:
            # Get data from validation file (old)
            file_data = validation_data["files"][filepath]
            # Get the data with name from analysis dir (new)
            if details["size"] != file_data["size"] or details["modified"] != file_data["modified"]:
                status[filepath] = "modified"  # set to modified file

    # Check for deleted files
    for filepath in validation_data["files"]:
        if filepath not in current_files:
            status[filepath] = "deleted"  # it was deleted

    return status


def chip_directory(directory):
    """Chips the directory by creating/updating the validation JSON."""
    directory_data = analyze_directory(directory)
    files = {}
    for item, details in directory_data.items():
        # no type
        files[item] = {
            "size": details["size"],
            "modified": details["modified"]
        }

    # Load project metadata from project_metadata.json if it exists
    metadata = {}
    metadata_path = os.path.join(directory, "project_metadata.json")  # Assuming metadata is in same directory for now
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print("project_metadata.json not found in this directory. Skipping.")  # Inform if it was not found
    except Exception as e:
        print(f"Error loading project_metadata.json: {e}")

    # Save validation data, including metadata and version, in a structured way
    validation_data = {
        "version": "1.0",  # Add a version number for future compatibility
        "metadata": metadata,  # Project Metadata (if available)
        "files": files,  # List of files and their metadata
    }
    save_validation_data(directory, validation_data)
    messagebox.showinfo("Info", f"Directory '{os.path.basename(directory)}' chipped successfully.")


# --- GUI Integration ---
def display_directory_structure(root_directory, tree):
    """Populates the Tkinter Treeview with the project structure and statuses."""
    tree.delete(*tree.get_children())
    status_cache = {}  # Cache status for each directory to avoid repeated calculations

    def add_node(parent, directory):
        """Recursively add directory structure to Treeview, displaying file statuses."""
        try:
            status = status_cache[directory] if directory in status_cache else compare_directory(
                directory)  # Compare whole directory at once
        except Exception as e:  # handle errors in directories and write
            print(f"Error during analysis: {e}")
            return

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            tag = "valid"
            if item == VALIDATION_FILE:
                continue
            if item in status:
                tag = status[item]

            text = item  # Default text is just the item name
            # Add tag to display in tkinter

            if os.path.isfile(item_path):
                if tag != "valid":  # Check for not valid (new, modified, deleted)
                    text = f"[{tag.upper()}] {text}"  # Prepend status to the file name
                tree.insert(parent, 'end', text=text, tags=(tag,))
            elif os.path.isdir(item_path):
                node_id = tree.insert(parent, 'end', text=text, open=False, tags=(tag,))
                add_node(node_id, item_path)

    add_node("", root_directory)


# --- GUI Setup ---
root = tk.Tk()
root.title("Project Analyzer")
root.geometry("800x600")

# --- Styling ---
style = ttk.Style(root)
style.theme_use('clam')

# Color scheme
bg_color = '#2e2e2e'
fg_color = 'white'
text_color = '#d3d3d3'
button_bg_color = '#4a4a4a'
entry_bg_color = "#4a4a4a"
button_active_bg_color = '#606060'
new_color = '#A9A9A9'  # Dark Gray
modified_color = '#FFFF00'  # Yellow
deleted_color = '#FF0000'  # Red
valid_color = '#00FF00'  # Green

style.configure('.', background=bg_color, foreground=fg_color, font=DEFAULT_FONT)
style.configure('TLabel', background=bg_color, foreground=fg_color, padding=5, font=("Bahnschrift", 12))
style.configure('TButton', background=button_bg_color, foreground=fg_color, padding=8, relief='flat',
                font=("Bahnschrift", 11), borderwidth=0, focuscolor='gray',
                activebackground=button_active_bg_color, activeforeground=fg_color)
style.map('TButton',
          background=[('active', button_active_bg_color), ('disabled', button_bg_color)],
          foreground=[('disabled', 'gray')])
style.configure('TEntry', fieldbackground=entry_bg_color, foreground=text_color, font=("Bahnschrift", 11))
style.configure('Horizontal.TProgressbar', troughcolor=button_bg_color, background=fg_color)

# --- Main Frame ---
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill='both')

# --- Folder Selection ---
folder_label = ttk.Label(main_frame, text="Project Folder:")
folder_label.pack(pady=(0, 5), fill='x')

folder_path_entry = ttk.Entry(main_frame, width=50)
folder_path_entry.pack(pady=(0, 5), fill='x')


def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)


browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.pack(pady=(0, 10), fill='x')

# --- Treeview Widget ---
tree = ttk.Treeview(main_frame, show="tree", padding=5)
tree.pack(expand=True, fill='both')

# Define treeview tags and colors
tree.tag_configure('new', foreground=new_color)
tree.tag_configure('modified', foreground=modified_color)
tree.tag_configure('deleted', foreground=deleted_color)
tree.tag_configure('valid', foreground=valid_color)  # if it's checked and no changes, show


# --- Button Functions ---
def analyze_project():
    project_directory = folder_path_entry.get()
    if not project_directory:
        messagebox.showerror("Error", "Please select a project folder.")
        return

    # GUI DISABLE
    analyze_button["state"] = "disabled"
    chip_button["state"] = "disabled"
    browse_button["state"] = "disabled"
    refresh_button["state"] = "disabled"  # Disable the refresh

    # Update in the GUI with thread process
    def after_action():
        # Now list the directory and display to gui
        display_directory_structure(project_directory, tree)
        # after
        analyze_button["state"] = "normal"
        chip_button["state"] = "normal"
        browse_button["state"] = "normal"
        refresh_button["state"] = "normal"  # Enable the refresh

    threading.Thread(target=after_action, daemon=True).start()  # update to GUI


def chip_selected_directory():
    project_directory = folder_path_entry.get()  # gets the dirr
    if not project_directory:
        messagebox.showerror("Error", "Please select a project folder.")  # message
        return

    def after_action():
        chip_directory(project_directory)  # Just "chip" the main directory
        display_directory_structure(project_directory, tree)  # display directory

        # after
        analyze_button["state"] = "normal"
        chip_button["state"] = "normal"
        browse_button["state"] = "normal"
        refresh_button["state"] = "normal"  # Enable the refresh

    # Disabe the buttons
    analyze_button["state"] = "disabled"
    chip_button["state"] = "disabled"
    browse_button["state"] = "disabled"
    refresh_button["state"] = "disabled"  # Disable the refresh

    threading.Thread(target=after_action, daemon=True).start()  # update in the gui display


# --- GUI Buttons ---
analyze_button = ttk.Button(main_frame, text="Analyze Project", command=analyze_project)
analyze_button.pack(pady=(15, 0), fill='x')

chip_button = ttk.Button(main_frame, text="Chip Directory", command=chip_selected_directory)
chip_button.pack(pady=(5, 0), fill='x')

refresh_button = ttk.Button(main_frame, text="Refresh View", command=analyze_project)
refresh_button.pack(pady=(5, 0), fill='x')  # refresh view

# --- Run the GUI ---
root.mainloop()
