"""Desktop launcher for ELI LAB tools."""

from __future__ import annotations

import signal
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .registry import TOOLS


class Launcher:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.processes: list[subprocess.Popen] = []
        self._configure_style()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background="#2e2e2e", foreground="white", font=("Bahnschrift", 10))
        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="white", padding=10, font=("Bahnschrift", 12, "bold"))
        style.configure("TButton", background="#4a4a4a", foreground="white", padding=10, relief="flat", font=("Bahnschrift", 11), borderwidth=0)
        style.map("TButton", background=[("active", "#606060"), ("disabled", "#4a4a4a")])

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=20)
        main.pack(expand=True, fill="both")
        ttk.Label(main, text="eli_lab Multimedia Framework", anchor="center", font=("Bahnschrift", 20, "bold")).pack(fill="x", pady=(0, 20))

        categories: dict[str, list] = {}
        for tool in TOOLS:
            categories.setdefault(tool.category, []).append(tool)

        for category, tools in categories.items():
            frame = ttk.Frame(main, padding=(10, 0, 10, 10))
            frame.pack(fill="x", padx=10, pady=5)
            ttk.Label(frame, text=category, anchor="w").pack(fill="x")
            for tool in tools:
                ttk.Button(frame, text=tool.name, command=lambda item=tool: self.run_tool(item.script)).pack(fill="x", pady=2)

    def run_tool(self, script_name: str) -> None:
        root = Path(__file__).resolve().parents[2]
        script_path = root / script_name
        if not script_path.is_file():
            messagebox.showerror("Error", f"Tool script not found: {script_path}")
            return
        try:
            self.processes.append(subprocess.Popen([sys.executable, str(script_path)]))
        except OSError as exc:
            messagebox.showerror("Error", f"Could not launch {script_name}: {exc}")

    def close(self) -> None:
        for process in self.processes[:]:
            if process.poll() is None:
                try:
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    process.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    process.kill()
            self.processes.remove(process)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    root.title("eli_lab Multimedia Framework")
    root.geometry("450x820")
    Launcher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
