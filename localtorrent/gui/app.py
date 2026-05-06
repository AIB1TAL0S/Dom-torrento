import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
import sys
from pathlib import Path
from localtorrent.engine.runner import EngineThread
from localtorrent.engine.metainfo import create_torrent, write_torrent

logger = logging.getLogger(__name__)


def _setup_gui_logging() -> Path:
    """Log to a file so GUI launchers (Gear Lever, file managers) don't open a terminal."""
    log_dir = Path.home() / ".local" / "share" / "localtorrent"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "localtorrent.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )
    # Silence stdout/stderr so no terminal is spawned by the launcher
    if not sys.stdout or not sys.stdout.isatty():
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    return log_file

class LocalTorrentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LocalTorrent")
        self.geometry("800x600")
        
        self.engine = EngineThread()
        self.engine.start()
        
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start polling loop
        self.after(500, self._poll_engine)
        
    def _build_ui(self):
        # Apply a basic ttk theme if available
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        # Toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        btn_add = ttk.Button(toolbar, text="Add Torrent", command=self.on_add_torrent)
        btn_add.pack(side=tk.LEFT, padx=2)
        
        btn_create = ttk.Button(toolbar, text="Create Torrent", command=self.on_create_torrent)
        btn_create.pack(side=tk.LEFT, padx=2)
        
        btn_remove = ttk.Button(toolbar, text="Remove", command=self.on_remove_torrent)
        btn_remove.pack(side=tk.LEFT, padx=2)
        
        # Main Area
        main_frame = ttk.Frame(self, padding=5)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        columns = ("name", "size", "progress", "status", "peers")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("status", text="Status")
        self.tree.heading("peers", text="Peers")
        
        self.tree.column("name", width=300)
        self.tree.column("size", width=100)
        self.tree.column("progress", width=100)
        self.tree.column("status", width=100)
        self.tree.column("peers", width=80)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_add_torrent(self):
        file_path = filedialog.askopenfilename(filetypes=[("LocalTorrent", "*.ltorrent")])
        if not file_path:
            return
            
        dest_path = filedialog.askdirectory(title="Select Download Location")
        if not dest_path:
            return
            
        logger.info(f"Adding torrent: {file_path} to {dest_path}")
        self.engine.add_torrent(file_path, dest_path)

    def on_create_torrent(self):
        target_path = filedialog.askdirectory(title="Select File/Folder to share")
        if not target_path:
            return
            
        t_dict = create_torrent(target_path)
        out_name = f"{t_dict['name']}.ltorrent"
        write_torrent(t_dict, out_name)
        
        messagebox.showinfo("Success", f"Torrent created: {out_name}")

    def on_remove_torrent(self):
        selection = self.tree.selection()
        if not selection:
            return
            
        for item in selection:
            info_hash = item
            self.engine.remove_torrent(info_hash)
            logger.info(f"Removed torrent {info_hash}")

    def _poll_engine(self):
        # The engine maintains a dictionary: { "info_hash": { "name": ..., "size": ..., ... } }
        with self.engine._lock:
            torrents = dict(self.engine.active_torrents)
            
        existing_items = self.tree.get_children()
        
        for info_hash, data in torrents.items():
            values = (
                data.get("name", "Unknown"),
                data.get("size", "0 B"),
                f"{data.get('progress', 0.0):.1f}%",
                data.get("status", "Stopped"),
                data.get("peers", 0)
            )
            
            if info_hash in existing_items:
                self.tree.item(info_hash, values=values)
            else:
                self.tree.insert("", tk.END, iid=info_hash, values=values)
                
        # Remove deleted torrents
        for item_id in existing_items:
            if item_id not in torrents:
                self.tree.delete(item_id)
                
        self.after(500, self._poll_engine)

    def on_closing(self):
        logger.info("GUI closing, stopping engine...")
        # Disable window to prevent interaction during shutdown
        self.attributes('-disabled', True)
        self.update() 
        
        self.engine.stop()
        self.engine.join(timeout=3.0) 
        
        if self.engine.is_alive():
            logger.warning("Engine thread did not close gracefully in time.")
            
        self.destroy()

def run_gui():
    log_file = _setup_gui_logging()
    # Log where the log file is (only visible in the log file itself)
    logging.getLogger(__name__).info("LocalTorrent GUI starting. Log: %s", log_file)
    app = LocalTorrentApp()
    app.mainloop()
