import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from nmap_scan import NmapScanner

class NmapScannerGUI:
    def __init__(self, master):
        self.master = master
        if isinstance(master, tk.Tk):
            master.title("Python-Based Nmap Scanner")
            master.geometry("900x650")

        self.create_widgets()

        self.nmap_stop_flag = [False]
        self.nmap_results = []
        self.scanner = None

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master, bg="#6050dc")
        self.main_frame.pack(fill="both", expand=True)

        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(5, weight=1)

        title_label = tk.Label(self.main_frame, text="Python-Based Nmap Scanner", font=("Helvetica", 20, "bold"), bg="#6050dc", fg="white")
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        tk.Label(self.main_frame, text="Target IP or Host:", bg="#6050dc", fg="white", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.nmap_target_entry = tk.Entry(self.main_frame)
        self.nmap_target_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=10)

        tk.Label(self.main_frame, text="Port Range (optional):", bg="#6050dc", fg="white", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5, padx=10)
        self.nmap_ports_entry = tk.Entry(self.main_frame)
        self.nmap_ports_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=10)

        tk.Label(self.main_frame, text="Scan Type:", bg="#6050dc", fg="white", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5, padx=10)
        self.nmap_scan_type = ttk.Combobox(self.main_frame, values=["SYN Scan", "SYN + OS + Version", "Aggressive"], state="readonly")
        self.nmap_scan_type.grid(row=3, column=1, sticky="w", pady=5, padx=10)
        self.nmap_scan_type.current(0)

        btn_frame = tk.Frame(self.main_frame, bg="#6050dc")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.nmap_scan_btn = tk.Button(btn_frame, text="Scan", width=15, command=self.run_nmap_scan, bg="purple", fg="white", font=("Helvetica", 10, "bold"))
        self.nmap_scan_btn.pack(side="left", padx=5)

        self.nmap_cancel_btn = tk.Button(btn_frame, text="Cancel", width=15, command=self.cancel_nmap_scan, state=tk.DISABLED, bg="red", fg="white", font=("Helvetica", 10, "bold"))
        self.nmap_cancel_btn.pack(side="left", padx=5)

        self.nmap_save_btn = tk.Button(btn_frame, text="Save Output", width=15, command=self.save_nmap_output, state=tk.DISABLED, bg="green", fg="white", font=("Helvetica", 10, "bold"))
        self.nmap_save_btn.pack(side="left", padx=5)

        self.nmap_clear_btn = tk.Button(btn_frame, text="Clear Output", width=15, command=self.clear_nmap_output, bg="blue", fg="white", font=("Helvetica", 10, "bold"))
        self.nmap_clear_btn.pack(side="left", padx=5)

        self.nmap_output = scrolledtext.ScrolledText(self.main_frame, bg="#000000", fg="white", font=("Monospace", 11), insertbackground="white")
        self.nmap_output.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5, 5))

        self.nmap_status = tk.Label(self.main_frame, text="Status: Idle", bg="#6050dc", fg="white", anchor="w", font=("Helvetica", 10, "bold"))
        self.nmap_status.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10)

        self.nmap_progress = ttk.Progressbar(self.main_frame, mode="indeterminate", length=600, style="green.Horizontal.TProgressbar")
        self.nmap_progress.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')

    def run_nmap_scan(self):
        target = self.nmap_target_entry.get().strip()
        scan_type = self.nmap_scan_type.get()
        ports = self.nmap_ports_entry.get().strip()

        if not target:
            messagebox.showerror("Input Error", "Please enter a target IP or host.")
            return

        self.nmap_output.config(state=tk.NORMAL)
        self.nmap_output.delete("1.0", tk.END)
        self.nmap_output.config(state=tk.DISABLED)

        self.nmap_progress.start(10)
        self.nmap_stop_flag[0] = False
        self.nmap_results.clear()

        self.nmap_scan_btn.config(state=tk.DISABLED)
        self.nmap_cancel_btn.config(state=tk.NORMAL)
        self.nmap_save_btn.config(state=tk.DISABLED)
        self.nmap_status.config(text="Status: Scanning...", fg="white")

        def scan():
            self.scanner = NmapScanner()

            live_output = []

            def update_output(line):
                self.nmap_output.config(state=tk.NORMAL)
                self.nmap_output.insert(tk.END, line)
                self.nmap_output.see(tk.END)
                self.nmap_output.config(state=tk.DISABLED)
                live_output.append(line)

            final_result = self.scanner.run_scan(target, scan_type=scan_type, port_range=ports, stop_flag=self.nmap_stop_flag, live_callback=update_output)

            self.nmap_results.append(final_result)

            self.master.after(0, self.nmap_progress.stop)
            self.master.after(0, self.nmap_progress.config, {'value': 100})
            self.master.after(0, self.nmap_status.config, {'text': "Status: Completed" if not self.nmap_stop_flag[0] else "Status: Cancelled", 'fg': "white"})
            self.master.after(0, self.nmap_scan_btn.config, {'state': tk.NORMAL})
            self.master.after(0, self.nmap_cancel_btn.config, {'state': tk.DISABLED})
            self.master.after(0, self.nmap_save_btn.config, {'state': tk.NORMAL if self.nmap_results else tk.DISABLED})

        threading.Thread(target=scan).start()

    def cancel_nmap_scan(self):
        self.nmap_stop_flag[0] = True
        if self.scanner and self.scanner.process:
            self.scanner.process.terminate()
        self.nmap_status.config(text="Status: Cancelling...", fg="white")

    def save_nmap_output(self):
        if not self.nmap_results or all(not line.strip() for line in self.nmap_results):
            messagebox.showerror("Error", "No scan result available. Please run a scan first.")
            return

        file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")])
        if not file_path:
            return

        try:
            if file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(self.nmap_results)
            elif file_path.endswith(".pdf"):
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = [Paragraph("Nmap Scan Output", styles['Title'])]
                for line in self.nmap_results:
                    elements.append(Paragraph(line.replace("\n", "<br/>"), styles['Normal']))
                doc.build(elements)
            messagebox.showinfo("Saved", f"Scan results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_nmap_output(self):
        self.nmap_output.config(state=tk.NORMAL)
        self.nmap_output.delete("1.0", tk.END)
        self.nmap_output.config(state=tk.DISABLED)
        self.nmap_status.config(text="Status: Idle", fg="white")
        self.nmap_results.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = NmapScannerGUI(root)
    root.mainloop()
