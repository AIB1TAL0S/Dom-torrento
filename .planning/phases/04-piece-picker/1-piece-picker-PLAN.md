---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/piece_picker.py"
autonomous: true
---

# Plan 1: Rarity-first Piece Picker

## Context
Implement the core `PiecePicker` logic to manage block distribution and piece rarity tracking across the swarm.

## Tasks

<task>
  <id>1</id>
  <title>Create PiecePicker class</title>
  <read_first>
    - localtorrent/engine/torrent.py
  </read_first>
  <action>
    Create `localtorrent/engine/piece_picker.py`.
    Implement `class PiecePicker`.
    Initialize with `self.piece_counts = [0] * torrent.total_pieces`.
    Implement `def add_peer_bitfield(self, bitfield_bytes: bytes)` to parse the bitfield payload and increment counts.
    Implement `def add_peer_have(self, piece_index: int)` to increment a single count.
    Implement `def remove_peer_bitfield(self, bitfield_bytes: bytes)` to decrement counts if a peer drops.
  </action>
  <acceptance_criteria>
    - `PiecePicker` correctly tracks global piece availability.
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Implement Block Request Selection</title>
  <read_first>
    - localtorrent/engine/piece_picker.py
  </read_first>
  <action>
    In `PiecePicker`, add tracking for incomplete/requested pieces (e.g., `self.active_pieces = {}`).
    Implement `def get_next_block_request(self, peer_bitfield: list[bool]) -> tuple[int, int, int] | None`.
    - Find the rarest piece (lowest non-zero count in `self.piece_counts`) that we DON'T have and the given peer DOES have.
    - If a piece is found, find the next 16KB block `(offset, length)` that hasn't been requested yet.
    - Return `(piece_index, offset, length)`.
  </action>
  <acceptance_criteria>
    - Picker returns specific block boundaries based on the 16KB chunk size.
    - Picker prioritizes rarest pieces correctly.
  </acceptance_criteria>
</task>

## Verification
- Can initialize `PiecePicker` and provide peer bitfields.
- `get_next_block_request` returns correct offsets without duplicating block requests.

## Must Haves
- Rarity-first logic implemented via `piece_counts`.
- Block-level tracking to prevent duplicate requests.
