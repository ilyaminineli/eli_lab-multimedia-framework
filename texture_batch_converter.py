"""Legacy GUI adapter for the framework texture conversion service."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from eli_lab.assets import convert_textures


class TextureBatchConverterApp:
    """Tkinter frontend for :func:`eli_lab.assets.convert_textures`."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Texture Batch Converter")
        self.root.geometry("600x400")

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Folder:").pack(pady=(0, 5), fill="x")
        self.folder_entry = ttk.Entry(frame)
        self.folder_entry.pack(pady=(0, 5), fill="x")

        self.browse_button = ttk.Button(frame, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=(0, 10), fill="x")

        self.replace_originals = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Replace originals after successful conversion",
            variable=self.replace_originals,
        ).pack(pady=(0, 10), fill="x")

        self.progress_bar = ttk.Progressbar(frame, mode="determinate")
        self.progress_bar.pack(pady=(10, 15), fill="x")

        self.convert_button = ttk.Button(frame, text="Convert Textures", command=self.start_conversion)
        self.convert_button.pack(pady=(15, 0), fill="x")

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def start_conversion(self) -> None:
        directory = self.folder_entry.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please select a folder.")
            return

        self.convert_button["state"] = "disabled"
        self.browse_button["state"] = "disabled"

        def progress(current: int, total: int) -> None:
            def update() -> None:
                self.progress_bar.configure(maximum=max(total, 1), value=current)
            self.root.after(0, update)

        def worker() -> None:
            try:
                results = convert_textures(
                    directory,
                    replace_original=self.replace_originals.get(),
                    progress_callback=progress,
                )
                failures = [result for result in results if not result.success and result.error]
                self.root.after(0, lambda: self.finish(failures))
            except Exception as exc:
                self.root.after(0, lambda: self.finish_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def finish(self, failures: list) -> None:
        self.convert_button["state"] = "normal"
        self.browse_button["state"] = "normal"
        self.progress_bar["value"] = 0
        if failures:
            messagebox.showwarning("Completed with errors", f"{len(failures)} texture(s) could not be converted.")
        else:
            messagebox.showinfo("Complete", "Texture conversion complete!")

    def finish_error(self, error: Exception) -> None:
        self.convert_button["state"] = "normal"
        self.browse_button["state"] = "normal"
        messagebox.showerror("Conversion error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    TextureBatchConverterApp(root)
    root.mainloop()
