---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/gui/app.py"
autonomous: true
---

# Plan 1: Main Window Layout & Controls

## Context
Refactor the basic `LocalTorrentApp` to include a functional toolbar, a `ttk.Treeview` data grid for tracking torrents, and the polling loop to keep the UI in sync with the `EngineThread`.

## Tasks

<task>
  <id>1</id>
  <title>Refactor Main App Layout</title>
  <read_first>
    - localtorrent/gui/app.py
  </read_first>
  <action>
    Modify `localtorrent/gui/app.py`.
    Import `tkinter.ttk as ttk`.
    Inside `__init__`, build out a `ttk.Frame` for a toolbar at the top (`pack(side=tk.TOP, fill=tk.X)`).
    Add `ttk.Button` elements to the toolbar: "Add Torrent", "Create Torrent", "Remove".
    Below the toolbar, create a `ttk.Frame` to hold a `ttk.Treeview` and a `ttk.Scrollbar`.
    Configure the `ttk.Treeview` with columns: `Name`, `Size`, `Progress`, `Status`, `Peers`.
    Set the column widths and headings appropriately.
  </action>
  <acceptance_criteria>
    - GUI opens with the toolbar and an empty treeview data grid.
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Implement Engine Polling Loop</title>
  <read_first>
    - localtorrent/gui/app.py
    - localtorrent/engine/runner.py
  </read_first>
  <action>
    In `LocalTorrentApp`, add `def _poll_engine(self)`.
    Call `self.after(500, self._poll_engine)` to continuously poll.
    Inside the polling loop, access `self.engine.active_torrents` (we'll assume this contains dicts like `{"info_hash": ..., "name": ..., "size": ..., "progress": ..., "status": ..., "peers": ...}`).
    Iterate over `active_torrents` and either insert new rows into the `Treeview` using `iid=info_hash`, or update the existing `iid` with the latest values.
  </action>
  <acceptance_criteria>
    - Periodic polling loop successfully registered via `self.after`.
  </acceptance_criteria>
</task>

## Verification
- Running `python -m localtorrent gui` shows the complete layout.
- The window does not freeze.

## Must Haves
- Uses `ttk.Treeview` for data display.
- Non-blocking `_poll_engine` loop.
