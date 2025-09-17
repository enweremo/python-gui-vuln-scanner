import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import time
import subprocess
import threading
import os

class NiktoScannerGUI:
    def __init__(self, master):
        self.master = master
        if isinstance(master, tk.Tk):
            master.title("Python-Based Nikto Scanner")
            master.geometry("850x650")
        
        self._build_ui()
        self._style()

        self.is_scanning = False
        self.scan_output = ""
        self.nikto_process = None
        self.output_file_path = None

    def _build_ui(self):
        self.main_frame = tk.Frame(self.master, bg="#739BD0")
        self.main_frame.pack(fill="both", expand=True)

        self.main_frame.rowconfigure(4, weight=1)  # Make row 4 (output window) expandable
        self.main_frame.columnconfigure(0, weight=1)

        header = tk.Label(self.main_frame, text="Python-Based Nikto Scanner", font=("Helvetica", 20, "bold"), fg="white", bg="#739BD0")
        header.grid(row=0, column=0, pady=10)

        form_frame = tk.Frame(self.main_frame, bg="#739BD0")
        form_frame.grid(row=1, column=0, sticky="ew", padx=10)

        labels = [
            ("Target URL/IP:", 0), ("Port(s) (optional):", 1),
            ("Tuning Options (dropdown):", 2), ("Custom Tuning Code:", 3),
            ("Plugins (optional):", 4), ("Evasion Option (optional):", 5),
            ("Save Format:", 6)
        ]

        for text, row in labels:
            tk.Label(form_frame, text=text, bg="#739BD0", anchor="w", font=("Helvetica", 10, "bold"), fg="white").grid(row=row, column=0, sticky="w", pady=3)

        self.target_entry = tk.Entry(form_frame)
        self.target_entry.grid(row=0, column=1, sticky="ew", pady=3)

        self.port_entry = tk.Entry(form_frame)
        self.port_entry.grid(row=1, column=1, sticky="ew", pady=3)

        self.tuning_var = tk.StringVar()
        self.tuning_combo = ttk.Combobox(form_frame, textvariable=self.tuning_var, state="readonly")
        self.tuning_combo['values'] = [
            "", "0 - File Upload", "1 - Interesting File", "2 - Misconfiguration", "3 - Info Disclosure",
            "4 - Injection", "5 - Remote File Retrieval", "6 - DoS", "7 - Server Wide File Access",
            "8 - RCE / Shells", "9 - SQL Injection", "a - Auth Bypass", "b - Software ID",
            "c - Source Inclusion", "d - Web Services", "e - Admin Consoles", "x - All Except Specified"
        ]
        self.tuning_combo.grid(row=2, column=1, sticky="ew", pady=3)

        self.tuning_entry = tk.Entry(form_frame)
        self.tuning_entry.grid(row=3, column=1, sticky="ew", pady=3)

        self.plugins_entry = tk.Entry(form_frame)
        self.plugins_entry.grid(row=4, column=1, sticky="ew", pady=3)

        self.evasion_combo = ttk.Combobox(form_frame, state="readonly")
        self.evasion_combo['values'] = ["", "1 - Random URI encoding", "2 - Dir self-ref", "3 - Premature URL ending",
                                        "4 - Long random string", "5 - Fake param", "6 - TAB spacer", "7 - Change case",
                                        "8 - Windows slash", "A - Carriage return", "B - Binary"]
        self.evasion_combo.grid(row=5, column=1, sticky="ew", pady=3)

        self.format_combo = ttk.Combobox(form_frame, values=["txt", "html", "csv", "xml"], state="readonly")
        self.format_combo.grid(row=6, column=1, sticky="w", pady=3)
        self.format_combo.set("txt")

        form_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.main_frame, bg="#739BD0")
        btn_frame.grid(row=2, column=0, pady=5)

        self.scan_btn = tk.Button(btn_frame, text="Scan", width=15, bg="purple", fg="white", font=("Helvetica", 10, "bold"), command=self.start_scan)
        self.scan_btn.pack(side="left", padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="Cancel", width=15, bg="red", fg="white", font=("Helvetica", 10, "bold"), command=self.cancel_scan, state=tk.DISABLED)
        self.cancel_btn.pack(side="left", padx=5)

        self.save_btn = tk.Button(btn_frame, text="Save Output", width=15, bg="green", fg="white", font=("Helvetica", 10, "bold"), command=self.save_result, state=tk.DISABLED)
        self.save_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear Output", width=15, bg="blue", fg="white", font=("Helvetica", 10, "bold"), command=self.clear_output)
        self.clear_btn.pack(side="left", padx=5)

        self.output_text = scrolledtext.ScrolledText(self.main_frame, height=18, bg="#000000", fg="white", font=("Monospace", 11), insertbackground="white")
        self.output_text.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        self.output_text.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.main_frame, text="Status: Idle", font=("Helvetica", 10, "bold"), fg="white", bg="#739BD0", anchor="w")
        self.status_label.grid(row=5, column=0, sticky="ew", padx=10)

        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate', length=300)
        self.progress_bar.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

    def _style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress_bar.configure(style="green.Horizontal.TProgressbar")

    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Target IP/URL is required.")
            return

        format_selected = self.format_combo.get().strip()
        ext = "htm" if format_selected == "html" else format_selected
        filetypes = [(f"{format_selected.upper()} files", f"*.{ext}")]

        base_path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=filetypes)
        if not base_path:
            return

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        name, ext_part = os.path.splitext(base_path)
        self.output_file_path = f"{name}_{timestamp}.{ext.strip()}"

        self._reset_output()
        self.status_label.config(text="Status: Scanning...")
        self.progress_bar.start(10)
        self.is_scanning = True

        cmd = self._build_nikto_command()
        self.nikto_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self._run_nikto, daemon=True).start()

    def _build_nikto_command(self):
        cmd = ["nikto", "-h", self.target_entry.get()]
        if self.port_entry.get():
            cmd += ["-p", self.port_entry.get()]
        tuning = self.tuning_combo.get().split(" - ")[0] + self.tuning_entry.get()
        if tuning.strip():
            cmd += ["-Tuning", tuning.strip()]
        plugins = self.plugins_entry.get().strip()
        if plugins:
            cmd += ["-Plugins", plugins]
        evasion = self.evasion_combo.get().split(" - ")[0].strip()
        if evasion:
            cmd += ["-evasion", evasion]

        format_selected = self.format_combo.get().strip()
        ext = "htm" if format_selected == "html" else format_selected
        cmd += ["-Format", ext, "-output", self.output_file_path]

        return cmd

    def _run_nikto(self):
        self.output_text.config(state=tk.NORMAL)
        try:
            for line in self.nikto_process.stdout:
                if not self.is_scanning:
                    self.nikto_process.terminate()
                    break
                self._append_output(line.strip())

            _, stderr = self.nikto_process.communicate()
            if stderr:
                self._append_output("\n[!] Error:\n" + stderr)

        finally:
            self.output_text.config(state=tk.DISABLED)
            self.is_scanning = False
            self._scan_complete_ui()

    def cancel_scan(self):
        if self.is_scanning and self.nikto_process:
            self.is_scanning = False
            self.nikto_process.terminate()
            self._append_output("\n[!] Scan cancelled by user.")
            self._scan_complete_ui()

    def _reset_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.scan_output = ""
        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)

    def _append_output(self, text):
        if text.strip():
            at_bottom = self.output_text.yview()[1] >= 0.95
            self.output_text.insert(tk.END, text + "\n")
            if at_bottom:
                self.output_text.see(tk.END)
        self.scan_output += text + "\n"

    def _scan_complete_ui(self):
        self.master.after(0, self.progress_bar.stop)
        self.master.after(0, self.scan_btn.config, {'state': tk.NORMAL})
        self.master.after(0, self.cancel_btn.config, {'state': tk.DISABLED})
        self.master.after(0, self.save_btn.config, {'state': tk.NORMAL})
        self.master.after(0, self.status_label.config, {'text': "Status: Completed"})

    def save_result(self):
        if not self.output_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "No scan result available. Please run a scan first.")
            return

        if self.output_file_path:
            messagebox.showinfo("Result Saved", f"Results were saved automatically to:\n\n{self.output_file_path}")
        else:
            messagebox.showwarning("No Scan Result", "Please run a scan first.")

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.scan_output = ""

if __name__ == "__main__":
    root = tk.Tk()
    app = NiktoScannerGUI(root)
    root.mainloop()
