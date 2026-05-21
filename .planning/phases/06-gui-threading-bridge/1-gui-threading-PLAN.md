---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/runner.py"
  - "localtorrent/gui/app.py"
autonomous: true
---

# Plan 1: Background Engine Thread

## Context
Implement the bridge between the synchronous Tkinter GUI main thread and the asynchronous P2P engine background thread.

## Tasks

<task>
  <id>1</id>
  <title>Create Engine Runner</title>
  <read_first>
    - localtorrent/__main__.py
  </read_first>
  <action>
    Create `localtorrent/engine/runner.py`.
    Implement `class EngineThread(threading.Thread)`:
      - Override `run()` to create a new event loop (`asyncio.new_event_loop()`), set it, and `loop.run_forever()`.
      - Implement `def submit_task(self, coro)` wrapping `asyncio.run_coroutine_threadsafe(coro, self.loop)`.
      - Implement `def stop(self)` that calls `self.loop.call_soon_threadsafe(self.loop.stop)`.
      - Maintain a thread-safe state dictionary or structure that tracks active torrents and their completion percentage.
  </action>
  <acceptance_criteria>
    - `EngineThread` properly initializes and spins up a background asyncio loop.
    - Provides a thread-safe way to submit coroutines.
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Create Base Tkinter App</title>
  <read_first>
    - localtorrent/engine/runner.py
  </read_first>
  <action>
    Create `localtorrent/gui/__init__.py`.
    Create `localtorrent/gui/app.py`.
    Implement a simple Tkinter window `class LocalTorrentApp(tk.Tk)`:
      - Start the `EngineThread` upon initialization.
      - Bind the `WM_DELETE_WINDOW` protocol to cleanly stop the `EngineThread` and call `self.destroy()`.
      - Add a simple "Engine Status: Running" label to verify the window opens.
  </action>
  <acceptance_criteria>
    - Running `app.py` opens a GUI window.
    - Closing the window cleanly terminates the background thread without hanging.
  </acceptance_criteria>
</task>

## Verification
- Can start the GUI.
- The background thread starts and stops gracefully when the GUI is closed.

## Must Haves
- Thread-safe bridging mechanism.
- Clean shutdown procedure avoiding hanging asyncio loops.
