import os
import signal
import subprocess
import sys
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk

processes = []


def run_script(script_name):
    """Launch a legacy GUI tool with the active Python interpreter."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name + ".py")
    if not os.path.isfile(script_path):
        tk.messagebox.showerror("Error", f"{script_name}.py not found.")
        return
    try:
        process = subprocess.Popen([sys.executable, script_path])
        processes.append(process)
    except OSError as exc:
        tk.messagebox.showerror("Error", f"Error running {script_name}.py: {exc}")


def on_closing():
    """Terminate child tools before closing the launcher."""
    for process in processes[:]:
        if process.poll() is None:
            try:
                if sys.platform == "win32":
                    process.terminate()
                else:
                    process.send_signal(signal.SIGTERM)
                process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                process.kill()
        processes.remove(process)
    root.destroy()


root = tk.Tk()
root.title("eli_lab Multimedia Framework")
root.geometry("450x820")

style = ttk.Style()
style.theme_use("clam")
font_name = "Bahnschrift"
style.configure(".", background="#2e2e2e", foreground="white", font=(font_name, 10))
style.configure("TFrame", background="#2e2e2e")
style.configure("TLabel", background="#2e2e2e", foreground="white", padding=10, font=(font_name, 12, "bold"))
style.configure("TButton", background="#4a4a4a", foreground="white", padding=10, relief="flat", font=(font_name, 11), borderwidth=0, focuscolor="gray", activebackground="#606060", activeforeground="white")
style.map("TButton", background=[("active", "#606060"), ("disabled", "#4a4a4a")], foreground=[("disabled", "gray")])

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill="both")
title_label = ttk.Label(main_frame, text="eli_lab Multimedia Framework", font=(font_name, 20, "bold"), anchor="center")
title_label.pack(pady=(0, 20))

categories = {
    "Project Structure Management": [("Advanced Template System", "advanced_template_system"), ("Project Metadata Integration", "project_metadata_integration"), ("Project Documentation Generator", "project_documentation_generator")],
    "Project Automation": [("Texture Batch Optimising Tool", "texture_batch_optimising_tool"), ("Texture Batch Converter", "texture_batch_converter"), ("Custom File Renaming", "custom_file_renaming")],
    "Data Management": [("File Validation", "file_validation"), ("Project Validation", "project_validation")],
    "Control": [("Automated Task Management & Reporting", "task_assigner"), ("Historical Performance Analyzer", "historical_performance_analyzer")],
}

for category, scripts in categories.items():
    category_frame = ttk.Frame(main_frame, padding=(10, 0, 10, 10))
    category_frame.pack(fill="x", padx=10, pady=5)
    ttk.Label(category_frame, text=category, anchor="w").pack(fill="x")
    for func_name, script_name in scripts:
        ttk.Button(category_frame, text=func_name, command=lambda script=script_name: run_script(script)).pack(fill="x", pady=2)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
