import tkinter as tk
from tkinter import ttk
from gui_nmap import NmapScannerGUI
from gui_crawler import WebCrawlerGUI
from gui_nikto import NiktoScannerGUI

class IntegratedScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("Integrated Vulnerability Scanner")
        master.geometry("950x650")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        self._add_webcrawler_tab()
        self._add_nmap_tab()        
        self._add_nikto_tab()
    
    def _add_nmap_tab(self):
        nmap_tab = ttk.Frame(self.notebook)
        self.notebook.add(nmap_tab, text="Nmap Scanner")
        NmapScannerGUI(nmap_tab)

    def _add_webcrawler_tab(self):
        crawler_tab = ttk.Frame(self.notebook)
        self.notebook.add(crawler_tab, text="Web Crawler")
        WebCrawlerGUI(crawler_tab)

    def _add_nikto_tab(self):
        nikto_tab = ttk.Frame(self.notebook)
        self.notebook.add(nikto_tab, text="Nikto Scanner")
        NiktoScannerGUI(nikto_tab)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
    app = IntegratedScannerApp(root)
    root.mainloop()
