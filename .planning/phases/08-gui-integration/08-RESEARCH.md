# Phase 8 Research: File Dialogs & Engine Integration

## Technical Approach
- **File Dialogs**: Tkinter provides built-in dialogs via `tkinter.filedialog` (`askopenfilename`, `askdirectory`, `asksaveasfilename`). These are perfect for prompting the user for `.ltorrent` files and download locations.
- **Engine Methods**: The `EngineThread` currently has a generic `submit_task()` method. We need to implement concrete methods on it, like `start_torrent(torrent_file_path, output_dir, seeding)` and `remove_torrent(info_hash)`.
- **Refactoring Engine Start**: The code currently living in `localtorrent/__main__.run_node` that creates the TCP server, Torrent object, PeerManager, and Discovery service needs to be adapted or wrapped inside `EngineThread.start_torrent` so it can track multiple torrents concurrently within the same `asyncio` loop.
- **State Updates**: Once a torrent is running, we need a periodic background asyncio task inside the engine loop that updates the `self.active_torrents` dictionary with the latest progress, status, and peer counts. The GUI's existing `_poll_engine` loop will automatically pick these up and reflect them.

## Gotchas
- Tkinter's `filedialog` calls are completely synchronous and block the `mainloop()`. Since our engine is safely isolated in another thread, this blocking behavior is perfectly acceptable and won't interrupt ongoing transfers!
- When removing a torrent, we need to carefully cancel its background task using `task.cancel()` to ensure no zombie transfers continue in the background.
