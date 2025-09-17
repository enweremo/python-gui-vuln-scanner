import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from webcrawler import WebCrawler

class WebCrawlerGUI:
    def __init__(self, master):
        self.master = master
        if isinstance(master, tk.Tk):
            master.title("Python-Based Web Crawler")
            master.geometry("900x650")
        
        self._build_ui()
        self._style()

        self.web_stop_flag = [False]
        self.web_results = []

    def _build_ui(self):
        self.main_frame = tk.Frame(self.master, bg="#007BFF")
        self.main_frame.pack(fill="both", expand=True)

        header = tk.Label(self.main_frame, text="Python-Based Web Crawler", font=("Helvetica", 20, "bold"), fg="white", bg="#007BFF")
        header.pack(pady=10)

        form_frame = tk.Frame(self.main_frame, bg="#007BFF")
        form_frame.pack(fill="x", padx=10)

        tk.Label(form_frame, text="Enter URL or IP:", bg="#007BFF", anchor="w", font=("Helvetica", 10, "bold"), fg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.web_url = tk.Entry(form_frame)
        self.web_url.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="Max Pages (optional):", bg="#007BFF", anchor="w", font=("Helvetica", 10, "bold"), fg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.web_max_pages = tk.Entry(form_frame)
        self.web_max_pages.grid(row=1, column=1, sticky="w", pady=5)

        form_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.main_frame, bg="#007BFF")
        btn_frame.pack(pady=5)

        self.scan_btn = tk.Button(btn_frame, text="Crawl", width=15, bg="purple", fg="white", font=("Helvetica", 10, "bold"), command=self.run_webcrawler)
        self.scan_btn.pack(side="left", padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="Cancel", width=15, bg="red", fg="white", font=("Helvetica", 10, "bold"), command=self.cancel_webcrawler, state=tk.DISABLED)
        self.cancel_btn.pack(side="left", padx=5)

        self.save_btn = tk.Button(btn_frame, text="Save Output", width=15, bg="green", fg="white", font=("Helvetica", 10, "bold"), command=self.save_output, state=tk.DISABLED)
        self.save_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear Output", width=15, bg="blue", fg="white", font=("Helvetica", 10, "bold"), command=self.clear_output)
        self.clear_btn.pack(side="left", padx=5)

        self.web_output = scrolledtext.ScrolledText(self.main_frame, height=18, bg="#000000", fg="white", font=("Monospace", 11), insertbackground="white")
        self.web_output.pack(fill="both", expand=True, padx=10, pady=5)
        self.web_output.config(state=tk.DISABLED)

        self.web_status = tk.Label(self.main_frame, text="Status: Idle", font=("Helvetica", 10, "bold"), fg="white", bg="#007BFF", anchor="w")
        self.web_status.pack(fill="x", padx=10)

        self.web_progress = ttk.Progressbar(self.main_frame, mode="determinate", length=300)
        self.web_progress.pack(fill="x", padx=10, pady=5)

    def _style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.web_progress.configure(style="green.Horizontal.TProgressbar")

    def run_webcrawler(self):
        self.web_output.config(state=tk.NORMAL)
        self.web_output.delete("1.0", tk.END)
        self.web_output.config(state=tk.DISABLED)
        self.web_status.config(text="Status: Crawling...", fg="white")
        self.web_progress['value'] = 0
        self.web_stop_flag[0] = False
        self.web_results.clear()

        self.scan_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        self.save_btn.config(state=tk.DISABLED)

        def crawl():
            url = self.web_url.get().strip()
            if not url:
                messagebox.showerror("Input Error", "Please enter a URL or IP to crawl.")
                self.reset_buttons()
                return

            try:
                max_pages = int(self.web_max_pages.get()) if self.web_max_pages.get().strip() else None
            except ValueError:
                messagebox.showerror("Error", "Max Pages must be a number")
                self.reset_buttons()
                return

            crawler = WebCrawler(max_pages=max_pages, stop_flag=self.web_stop_flag)
            total = max_pages if max_pages else 100
            count = 0

            for result in crawler.crawl(url):
                if self.web_stop_flag[0]:
                    break

                count += 1
                self.web_results.append(result)
                self.master.after(0, self.display_result, result)
                self.master.after(0, self.web_status.config, {'text': f"Status: Crawling ({count})", 'fg': "white"})
                self.master.after(0, self.web_progress.config, {'value': int((count / total) * 100)})
                time.sleep(0.1)

            if self.web_stop_flag[0]:
                self.master.after(0, self.web_status.config, {'text': "Status: Cancelled", 'fg': "white"})
            else:
                self.master.after(0, self.web_status.config, {'text': "Status: Completed", 'fg': "white"})

            self.master.after(0, self.web_progress.stop)
            self.master.after(0, self.reset_buttons)

        self.crawler_thread = threading.Thread(target=crawl)
        self.crawler_thread.start()

    def display_result(self, result):
        self.web_output.config(state=tk.NORMAL)
        self.web_output.insert(tk.END, f"URL: {result['URL']}\nTitle: {result['Title']}\nDescription: {result['Description']}\n{'-'*50}\n")
        self.web_output.see(tk.END)
        self.web_output.config(state=tk.DISABLED)

    def cancel_webcrawler(self):
        self.web_stop_flag[0] = True
        self.web_status.config(text="Status: Cancelling...", fg="white")
        self.cancel_btn.config(state=tk.DISABLED)

    def reset_buttons(self):
        self.scan_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL if self.web_results else tk.DISABLED)

    def save_output(self):
        if not self.web_results:
            messagebox.showwarning("No Data", "No scan result available. Please run a crawl first.")
            return

        file_path = filedialog.asksaveasfilename(
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    for result in self.web_results:
                        f.write(f"URL: {result['URL']}\nTitle: {result['Title']}\nDescription: {result['Description']}\n{'-'*50}\n")
            elif file_path.endswith(".csv"):
                with open(file_path, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["URL", "Title", "Description"])
                    writer.writeheader()
                    writer.writerows(self.web_results)
            elif file_path.endswith(".pdf"):
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = [Paragraph("Web Crawler Results", styles['Title'])]

                data = [["URL", "Title", "Description"]]
                for result in self.web_results:
                    data.append([result['URL'], result['Title'], result['Description']])

                table = Table(data, colWidths=[250, 150, 150])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))

                elements.append(table)
                doc.build(elements)

            messagebox.showinfo("Success", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_output(self):
        self.web_output.config(state=tk.NORMAL)
        self.web_output.delete("1.0", tk.END)
        self.web_output.config(state=tk.DISABLED)
        self.web_status.config(text="Status: Idle", fg="white")
        self.web_results.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebCrawlerGUI(root)
    root.mainloop()
