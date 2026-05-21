---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/peer.py"
autonomous: true
---

# Plan 1: Wire Protocol Implementation

## Context
This plan establishes the peer connection and wire protocol framing logic for communicating between peers over TCP.

## Tasks

<task>
  <id>1</id>
  <title>Implement PeerConnection class</title>
  <read_first>
    - localtorrent_spec.md
  </read_first>
  <action>
    Create `localtorrent/engine/peer.py`.
    Implement `PeerConnection` wrapping `asyncio.StreamReader` and `asyncio.StreamWriter`.
    Implement `async def send_message(self, msg_id: int, payload: bytes = b"")`:
      - Calculate total length (1 byte for msg_id + len(payload)).
      - Pack length into 4 big-endian bytes using `struct.pack(">I", length)`.
      - Write to the stream.
    Implement `async def read_message(self) -> tuple[int, bytes]`:
      - Read 4 bytes for length prefix using `reader.readexactly(4)`.
      - If length is 0, return `(0x06, b"")` (KeepAlive).
      - Read 1 byte for `msg_id`.
      - Read remaining `length - 1` bytes for payload.
      - Return `(msg_id, payload)`.
    Add `async def close(self)` to close the stream.
  </action>
  <acceptance_criteria>
    - `localtorrent/engine/peer.py` contains `class PeerConnection`
    - `localtorrent/engine/peer.py` contains `async def send_message`
    - `localtorrent/engine/peer.py` contains `async def read_message`
    - Uses `struct.pack` and `>I` for big-endian length prefixes.
  </acceptance_criteria>
</task>

## Verification
- Can import `PeerConnection` from `localtorrent.engine.peer`.
- Proper framing with length-prefix matching the specification.

## Must Haves
- TCP connection wrapper.
- Message framing logic accurately implemented using big-endian 4-byte prefixes.
