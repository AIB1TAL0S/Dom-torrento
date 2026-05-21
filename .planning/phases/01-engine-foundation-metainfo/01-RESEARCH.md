# Phase 1 Research

## Technical Approach
- **metainfo.py**: Needs functions to create an `.ltorrent` file from a target directory or file, and parse an `.ltorrent` file. The format is JSON. We need to calculate the SHA-256 info hash correctly.
- **torrent.py**: Represents the state of the torrent. Needs file I/O operations (async read/write chunks).

## Gotchas
- When creating the info hash, ensure the dictionary is serialized with sorted keys and no extra spaces to guarantee consistent hashing.
- File I/O should use `asyncio` if possible, but basic `open()` in standard python blocks. We might need `asyncio.to_thread` for file operations or just standard non-blocking chunks since piece sizes are 512KB.
