# Phase 7 Research: Main Window & Core Controls

## Technical Approach
- **GUI Framework**: Tkinter natively looks outdated if standard `tk` widgets are used. We will exclusively use `tkinter.ttk` (Themed Tkinter) widgets, which hook into the native OS theme.
- **Layout**:
  - A simple `pack()` or `grid()` layout works best.
  - Top Toolbar: A frame holding action buttons (Add Torrent, Create Torrent, Start/Pause, Remove).
  - Main Area: A `ttk.Treeview` widget configured with columns (`Name`, `Size`, `Progress`, `Status`, `Peers`). This acts as our torrent list.
- **Data Binding**:
  - Tkinter does not have automatic data binding like modern web frameworks. We must manually push updates to the UI.
  - The `LocalTorrentApp` will schedule a periodic polling method via `self.after(500, self.update_torrents)`.
  - In `update_torrents`, the app reads `self.engine.active_torrents` (a thread-safe dict tracking state) and updates the corresponding rows in the `ttk.Treeview`.

## Gotchas
- `ttk.Treeview` updates can be slow if we clear and re-insert every item. We should update the values of existing items (using the torrent's `info_hash` as the treeview item `iid`) rather than rebuilding the list from scratch.
- File dialogs for adding or creating torrents (`tkinter.filedialog`) will block the Tkinter `mainloop()`, which is perfectly fine because the `EngineThread` runs asynchronously in the background and won't be paused.
