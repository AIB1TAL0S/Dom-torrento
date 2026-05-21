---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/runner.py"
  - "localtorrent/gui/app.py"
autonomous: true
---

# Plan 1: Engine Integration & Controls

## Context
Connect the Tkinter GUI buttons to the underlying EngineThread, utilizing file dialogs to allow the user to easily create, add, and remove torrents.

## Tasks

<task>
  <id>1</id>
  <title>Implement Engine Torrent Management</title>
  <read_first>
    - localtorrent/engine/runner.py
    - localtorrent/__main__.py
  </read_first>
  <action>
    Modify `localtorrent/engine/runner.py`.
    Add `self.torrent_tasks = {}` to track `asyncio.Task` instances.
    Implement `def add_torrent(self, torrent_file: str, output_dir: str)`:
      - This method must invoke a coroutine on the event loop (via `self.submit_task()`).
      - The coroutine should parse the torrent, start the `PeerManager`, `LocalDiscovery`, and the TCP server (similar to `run_node` in `__main__.py`).
      - It should store the running asyncio tasks in `self.torrent_tasks[info_hash]`.
      - It should spawn a periodic task that updates `self.active_torrents[info_hash]` with `name`, `size`, `progress`, `status`, and `peers` so the GUI can read it.
    Implement `def remove_torrent(self, info_hash: str)`:
      - Looks up the task in `self.torrent_tasks`, cancels it, and removes the entry from `self.active_torrents`.
  </action>
  <acceptance_criteria>
    - `EngineThread` exposes robust methods to dynamically add and remove torrents while the loop is running.
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Connect GUI File Dialogs</title>
  <read_first>
    - localtorrent/gui/app.py
  </read_first>
  <action>
    Modify `localtorrent/gui/app.py`.
    Import `tkinter.filedialog` and `tkinter.messagebox`.
    In `on_add_torrent(self)`:
      - Use `askopenfilename(filetypes=[("LocalTorrent", "*.ltorrent")])` to pick a file.
      - Use `askdirectory()` to pick a download location.
      - Call `self.engine.add_torrent(file_path, dest_path)`.
    In `on_create_torrent(self)`:
      - Use `askdirectory()` to select a target directory or file.
      - Call `localtorrent.engine.metainfo.create_torrent()` and `write_torrent()`.
      - Show an `showinfo` messagebox on success.
    In `on_remove_torrent(self)`:
      - Get the selected item from `self.tree.selection()`.
      - The `iid` is the `info_hash`. Call `self.engine.remove_torrent(info_hash)`.
  </action>
  <acceptance_criteria>
    - Clicking the toolbar buttons opens native file dialogs.
    - Added torrents appear in the Treeview shortly after being submitted to the engine.
  </acceptance_criteria>
</task>

## Verification
- Can click "Create Torrent", select a folder, and see a `.ltorrent` generated.
- Can click "Add Torrent", select the `.ltorrent`, pick a download folder, and see it populate in the UI with a "Downloading" or "Seeding" status.

## Must Haves
- Safe task cancellation on `remove_torrent`.
- Background status updater coroutine for each active torrent.
