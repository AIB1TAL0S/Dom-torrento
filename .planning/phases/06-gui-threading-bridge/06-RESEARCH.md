# Phase 6 Research: Asyncio & GUI Threading Bridge

## Technical Approach
- **The Problem**: Tkinter (our chosen GUI) requires the main thread to run its `mainloop()`. However, our LocalTorrent engine relies entirely on Python's `asyncio` event loop. If `asyncio` and `Tkinter` run on the same thread, they will block each other.
- **The Solution**: We need an `EngineThread` (subclass of `threading.Thread`) that creates and manages its own background `asyncio` event loop.
- **Bridging**: 
  - The GUI can send commands to the engine using `asyncio.run_coroutine_threadsafe(coro, loop)`.
  - The engine needs to expose state (e.g., download progress, active peers) that the GUI can poll periodically via `root.after(500, update_ui)`.
  - Shared state (like a list of active torrents) should be protected by `threading.Lock()` or accessed via thread-safe queues.

## Gotchas
- Graceful shutdown: When the user closes the Tkinter window, we must signal the background asyncio loop to cancel all tasks and close gracefully, then `thread.join()`.
- Unhandled exceptions in the asyncio thread won't surface in the GUI thread automatically. We need to catch them and log them or push them to a thread-safe error queue.
