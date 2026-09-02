import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image


def is_already_quantized(image_path):
    """Checks if the PNG file is already quantized"""
    try:
        img = Image.open(image_path)
        return img.mode == "P"  # "P" mode indicates quantized image
    except Exception as e:
        print(f"Error opening image {image_path} for check: {e}")  # log errors
        return False  # Assume not quantized on error


def compress_textures(root_folder, quality_setting):
    """Compresses textures recursively, skipping already quantized images."""

    if not os.path.exists(root_folder):
        messagebox.showerror("Error", "Folder not found!")
        return

    quality_values = {
        "Very Low": "30-50",
        "Low": "50-70",
        "Medium": "60-80",
        "High": "70-90",
    }

    quality = quality_values.get(quality_setting, "65-85")  # Default

    all_png_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        png_files = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith(".png")]
        all_png_files.extend(png_files)  # Accumulate all PNG files

    total_files = len(all_png_files)
    if total_files == 0:
        messagebox.showinfo("Info", "No PNG files found in the selected folder or its subfolders.")
        return

    progress_bar["maximum"] = total_files  # Set the maximum value for the progress bar
    progress_bar["value"] = 0  # Reset the progress bar
    root.update_idletasks()

    for i, input_path in enumerate(all_png_files):
        if is_already_quantized(input_path):
            print(f"Skipping already quantized: {input_path}")
            progress_bar["value"] = i + 1
            root.update()
            continue  # Skip to the next file

        try:
            command = [
                "pngquant",
                "--quality", quality,
                "--force",  # Overwrite existing files
                "--ext", ".png",  # Keep the same extension
                "--skip-if-larger",  # Skip files larger than original
                input_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Compressed: {input_path}")
            print(result.stderr)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error",
                                 f"Failed to compress {os.path.basename(input_path)} in {os.path.dirname(input_path)}:\n{e.stderr}")
            print(f"Error compressing {input_path}: {e.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Error", "pngquant is not installed or not in your system's PATH.")
            return  # Stop

        progress_bar["value"] = i + 1  # Increment progress bar
        root.update()  # Force GUI update

    messagebox.showinfo("Success", "Texture compression complete!")


def browse_folder():
    """Opens a folder selection dialog."""
    folder_selected = filedialog.askdirectory()
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_selected)


def start_compression():
    """Starts the compression process."""
    folder_path = folder_path_entry.get()
    quality_setting = quality_combobox.get()

    if not folder_path:
        messagebox.showerror("Error", "Please select a folder.")
        return

    compress_textures(folder_path, quality_setting)


# --- GUI Setup ---
root = tk.Tk()
root.title("Texture Batch Optimising Tool")
root.geometry("600x350")

# --- Styling ---
style = ttk.Style(root)
style.theme_use('clam')

# Font
font_name = "Bahnschrift"

# Color scheme
bg_color = '#2e2e2e'
fg_color = 'white'
text_color = '#d3d3d3'
button_bg_color = '#4a4a4a'
entry_bg_color = "#4a4a4a"
button_active_bg_color = '#606060'

# Configure styles
style.configure('.', background=bg_color, foreground=fg_color, font=(font_name, 10))
style.configure('TLabel', background=bg_color, foreground=fg_color, padding=5, font=(font_name, 12))
style.configure('TButton', background=button_bg_color, foreground=fg_color, padding=8, relief='flat',
                font=(font_name, 11),
                borderwidth=0, focuscolor='gray',
                activebackground=button_active_bg_color, activeforeground=fg_color)
style.map('TButton',
          background=[('active', button_active_bg_color), ('disabled', button_bg_color)],
          foreground=[('disabled', 'gray')])
style.configure('TCombobox', selectbackground=button_bg_color, fieldbackground=button_bg_color,
                background=button_bg_color, foreground=text_color,
                arrowcolor=fg_color, borderwidth=0, lightcolor=button_bg_color, darkcolor=button_bg_color,
                font=(font_name, 11))  # style of ComboBox

style.map('TCombobox', fieldbackground=[('readonly', entry_bg_color)])

style.configure('TEntry', fieldbackground="#4a4a4a", foreground=text_color, font=(font_name, 11))

style.configure('Horizontal.TProgressbar', troughcolor=button_bg_color, background=fg_color)

# --- Main Frame ---
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill='both')

# --- Folder Selection ---
folder_label = ttk.Label(main_frame, text="Folder:")
folder_label.pack(pady=(0, 5), fill='x')

folder_path_entry = ttk.Entry(main_frame, width=50)
folder_path_entry.pack(pady=(0, 5), fill='x')

browse_button = ttk.Button(main_frame, text="Browse", command=browse_folder)
browse_button.pack(pady=(0, 10), fill='x')

# --- Quality Selection ---
quality_label = ttk.Label(main_frame, text="Quality Preset:")
quality_label.pack(pady=(10, 5), fill='x')

quality_values_list = ["Very Low", "Low", "Medium", "High"]
quality_combobox = ttk.Combobox(main_frame, values=quality_values_list, state="readonly")
quality_combobox.set("Medium")
quality_combobox.pack(pady=(0, 10), fill='x')

# --- Progress Bar ---
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=(10, 15), fill='x')  # Increased padding for visibility

# --- Compression Button ---
compress_button = ttk.Button(main_frame, text="Compress Textures", command=start_compression)
compress_button.pack(pady=(15, 0), fill='x')

root.mainloop()
