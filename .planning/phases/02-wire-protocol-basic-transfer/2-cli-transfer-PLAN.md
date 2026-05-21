---
wave: 2
depends_on: ["1-wire-protocol-PLAN.md"]
files_modified:
  - "localtorrent/__main__.py"
autonomous: true
---

# Plan 2: CLI Seeder and Leecher

## Context
Implement a CLI entry point to test the torrent metainfo and the basic transfer using the wire protocol.

## Tasks

<task>
  <id>1</id>
  <title>Implement CLI Entry Point</title>
  <read_first>
    - localtorrent/engine/metainfo.py
    - localtorrent/engine/torrent.py
    - localtorrent/engine/peer.py
  </read_first>
  <action>
    Create `localtorrent/__main__.py`.
    Implement `argparse` with subparsers: `create`, `seed`, `download`.
    - `create <path>`: calls `create_torrent` and writes output `.ltorrent` file.
    - `seed <torrent_file>`: Loads `.ltorrent`, creates `Torrent` object with all `True` bitfield (assuming files exist).
      Sets up `asyncio.start_server` to listen on port 6881. On incoming connection, sends its Bitfield (msg id `0x01`). Responds to `Request` (msg id `0x03`) by parsing `piece_index, offset, length` using `struct.unpack(">III", payload)`, calling `await torrent.read_piece(piece_index)`, slicing the data, and sending `Piece` (msg id `0x04`) packed as `>II` + data.
    - `download <torrent_file> --output <dir>`: Loads `.ltorrent`, creates `Torrent` object.
      Connects to localhost:6881 via `asyncio.open_connection`.
      Listens for the Bitfield message.
      Requests piece by piece. For each piece, requests in blocks of 16KB until piece is full.
      Writes piece to `torrent.write_piece`.
  </action>
  <acceptance_criteria>
    - `localtorrent/__main__.py` uses `argparse`.
    - `create`, `seed`, and `download` subcommands exist.
    - Basic one-to-one transfer logic is implemented using the `PeerConnection` and `Torrent` APIs.
  </acceptance_criteria>
</task>

## Verification
- Running `python -m localtorrent create` produces a `.ltorrent` file.
- Running `python -m localtorrent seed` starts a server.
- Running `python -m localtorrent download` connects and downloads the file.

## Must Haves
- Working CLI to test milestone 1 features.
- Basic functional transfer between a single seeder and leecher locally.
