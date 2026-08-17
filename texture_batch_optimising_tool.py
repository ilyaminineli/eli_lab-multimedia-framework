"""Legacy GUI adapter for the framework texture optimization service."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from eli_lab.assets import PNGQUANT_QUALITY_PRESETS, optimize_textures


class TextureBatchOptimizerApp:
    """Tkinter frontend for :func:`eli_lab.assets.optimize_textures`."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Texture Batch Optimising Tool")
        self.root.geometry("600x350")

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Folder:").pack(pady=(0, 5), fill="x")
        self.folder_entry = ttk.Entry(frame)
        self.folder_entry.pack(pady=(0, 5), fill="x")
        ttk.Button(frame, text="Browse", command=self.browse_folder).pack(pady=(0, 10), fill="x")

        ttk.Label(frame, text="Quality Preset:").pack(pady=(10, 5), fill="x")
        self.quality = ttk.Combobox(frame, values=list(PNGQUANT_QUALITY_PRESETS), state="readonly")
        self.quality.set("Medium")
        self.quality.pack(pady=(0, 10), fill="x")

        self.replace_originals = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Replace originals after successful optimization",
            variable=self.replace_originals,
        ).pack(pady=(0, 10), fill="x")

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.pack(pady=(10, 15), fill="x")

        self.optimize_button = ttk.Button(frame, text="Optimize Textures", command=self.start_optimization)
        self.optimize_button.pack(pady=(15, 0), fill="x")

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def start_optimization(self) -> None:
        directory = self.folder_entry.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please select a folder.")
            return

        self.optimize_button["state"] = "disabled"

        def progress(current: int, total: int) -> None:
            self.root.after(
                0,
                lambda: self.progress.configure(maximum=max(total, 1), value=current),
            )

        def worker() -> None:
            try:
                results = optimize_textures(
                    directory,
                    self.quality.get(),
                    replace_original=self.replace_originals.get(),
                    progress_callback=progress,
                )
                failures = [result for result in results if not result.success]
                self.root.after(0, lambda: self.finish(failures))
            except Exception as exc:
                self.root.after(0, lambda: self.finish_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def finish(self, failures: list) -> None:
        self.optimize_button["state"] = "normal"
        self.progress["value"] = 0
        if failures:
            messagebox.showwarning("Completed with errors", f"{len(failures)} texture(s) failed to optimize.")
        else:
            messagebox.showinfo("Complete", "Texture optimization complete!")

    def finish_error(self, error: Exception) -> None:
        self.optimize_button["state"] = "normal"
        messagebox.showerror("Optimization error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    TextureBatchOptimizerApp(root)
    root.mainloop()
