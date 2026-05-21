---
wave: 2
depends_on: ["1-project-structure-PLAN.md"]
files_modified:
  - "localtorrent/engine/torrent.py"
autonomous: true
---

# Plan 2: Torrent State and File I/O

## Context
Implement basic `torrent.py` state and file I/O operations for reading/writing pieces.

## Tasks

<task>
  <id>1</id>
  <title>Implement torrent.py</title>
  <read_first>
    - localtorrent/engine/metainfo.py
    - localtorrent/engine/torrent.py
  </read_first>
  <action>
    Create `localtorrent/engine/torrent.py`.
    Create a `Torrent` class that takes a loaded `.ltorrent` dictionary and a `save_path`.
    Initialize state: `bitfield` (array of booleans, all false initially for downloading, all true for seeding).
    Implement async methods `read_piece(piece_index: int) -> bytes` and `write_piece(piece_index: int, data: bytes) -> bool`.
    The methods should map the `piece_index` to the correct file and offset, using standard python file I/O inside `asyncio.to_thread` to prevent blocking the event loop.
    Verify the SHA-256 hash of the piece data against the hash from the `.ltorrent` file before returning True in `write_piece`.
  </action>
  <acceptance_criteria>
    - `localtorrent/engine/torrent.py` contains `class Torrent:`
    - `localtorrent/engine/torrent.py` contains `async def read_piece`
    - `localtorrent/engine/torrent.py` contains `async def write_piece`
  </acceptance_criteria>
</task>

## Verification
- Torrent class parses the dictionary.
- Piece reading and writing methods exist.

## Must Haves
- Basic `torrent.py` state handling.
- File I/O operations for pieces mapping to files.
