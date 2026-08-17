import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".tga", ".exr", ".hdr", ".bmp", ".gif", ".tiff", ".tif", ".png")


def is_image_file(filename):
    return filename.lower().endswith(ALLOWED_EXTENSIONS)


def convert_texture_to_png(filepath, output_dir, replace_original=False):
    """Convert one image to PNG without deleting the source by default."""
    if not os.path.isfile(filepath) or not is_image_file(filepath):
        return False
    if filepath.lower().endswith(".png"):
        return False

    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join(output_dir, name + ".png")

    try:
        with Image.open(filepath) as image:
            image.save(output_path, "PNG")
        if replace_original:
            os.remove(filepath)
        return True
    except (OSError, ValueError) as exc:
        print(f"Error processing '{filepath}': {exc}")
        return False


def convert_textures(directory, progress_callback, start_progress_callback, end_progress_callback, replace_original=False):
    """Convert images in a directory to PNG."""
    if not os.path.isdir(directory):
        return

    all_files = [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename)) and is_image_file(filename)
    ]
    start_progress_callback(len(all_files))

    for index, filepath in enumerate(all_files, start=1):
        convert_texture_to_png(filepath, directory, replace_original=replace_original)
        progress_callback(index)

    end_progress_callback()


root = tk.Tk()
root.title("Texture Batch Converter")
root.geometry("600x400")

style = ttk.Style(root)
style.theme_use("clam")
font_name = "Bahnschrift"
bg_color = "#2e2e2e"
fg_color = "white"
text_color = "#d3d3d3"
button_bg_color = "#4a4a4a"
entry_bg_color = "#4a4a4a"
button_active_bg_color = "#606060"
style.configure(".", background=bg_color, foreground=fg_color, font=(font_name, 10))
style.configure("TLabel", background=bg_color, foreground=fg_color, padding=5, font=(font_name, 12))
style.configure("TButton", background=button_bg_color, foreground=fg_color, padding=8, relief="flat", font=(font_name, 11), borderwidth=0, focuscolor="gray", activebackground=button_active_bg_color, activeforeground=fg_color)
style.map("TButton", background=[("active", button_active_bg_color), ("disabled", button_bg_color)], foreground=[("disabled", "gray")])
style.configure("TEntry", fieldbackground=entry_bg_color, foreground=text_color, font=(font_name, 11))

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")
folder_label = ttk.Label(main_frame, text="Folder:")
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

replace_originals = tk.BooleanVar(value=False)
ttk.Checkbutton(
    main_frame,
    text="Replace originals after successful conversion",
    variable=replace_originals,
).pack(pady=(0, 10), fill="x")

progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=(10, 15), fill="x")


def start_conversion():
    directory = folder_path_entry.get()
    if not directory:
        messagebox.showerror("Error", "Please select a folder.")
        return

    convert_button["state"] = "disabled"
    browse_button["state"] = "disabled"
    replace_originals_value = replace_originals.get()

    def update_progress(value):
        root.after(0, lambda: progress_bar.configure(value=value))

    def start_progress(max_value):
        def initialize():
            progress_bar.configure(maximum=max_value, value=0)
        root.after(0, initialize)

    def end_progress():
        def finish():
            progress_bar["value"] = 0
            convert_button["state"] = "normal"
            browse_button["state"] = "normal"
            messagebox.showinfo("Info", "Texture conversion complete!")
        root.after(0, finish)

    threading.Thread(
        target=convert_textures,
        args=(directory, update_progress, start_progress, end_progress, replace_originals_value),
        daemon=True,
    ).start()


convert_button = ttk.Button(main_frame, text="Convert Textures", command=start_conversion)
convert_button.pack(pady=(15, 0), fill="x")
root.mainloop()
