# Phase 2 Research: Wire Protocol & Basic Transfer

## Technical Approach
- **peer.py**: This will handle TCP connections using `asyncio.StreamReader` and `asyncio.StreamWriter`. The protocol requires framing using a 4-byte big-endian length prefix.
- Messages map to IDs: `0x00` Handshake, `0x01` Bitfield, `0x02` Have, `0x03` Request, `0x04` Piece, `0x05` Cancel, `0x06` KeepAlive, `0x07` Choke, `0x08` Unchoke.
- **__main__.py**: The CLI entrypoint. Needs basic `argparse` to support `create`, `seed`, and `download` commands.
- For basic transfer (Milestone 1), `seed` command will bind to a local port using `asyncio.start_server` and handle incoming connections by sending its bitfield and answering `Request` messages with `Piece` messages reading from the `Torrent` instance.
- The `download` command will connect to the seeder, request pieces sequentially (or simple rarity-first if possible, but sequential is fine for a 1-on-1 test) and write them.

## Gotchas
- The framing protocol means we must carefully read exactly `N` bytes from the `StreamReader` using `readexactly(length)`.
- Large `Piece` payloads shouldn't block the asyncio event loop.
- Endianness is strictly Big-Endian (`>I`) for length prefixes and piece/offset indices as per BitTorrent specs.
