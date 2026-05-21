================================================================================
LOCALTORRENT — PYTHON P2P FILE SHARING OVER LOCALHOST
SPECIFICATION v1.0
================================================================================

PROJECT OVERVIEW
----------------
A fully local peer-to-peer file transfer system where multiple Python processes
running on the same machine (or LAN) discover each other, exchange file metadata
(torrent-like), and transfer file chunks in parallel — all visualised through a
desktop GUI built with Tkinter or PyQt6.

  Language : Python 3.11+
  GUI      : Tkinter (default) or PyQt6
  Network  : asyncio + raw sockets (stdlib only)
  Scope    : localhost / LAN — no internet, no external tracker


================================================================================
ARCHITECTURE — LAYERS
================================================================================

  GUI Layer
    Tkinter or PyQt6 window. Torrent list, peer list, progress bars,
    add/remove torrent controls, speed graph.

  Controller
    Bridges GUI <-> engine. Runs asyncio loop in background thread.
    Emits events (progress, peer joined, error) back to GUI thread
    via thread-safe queue + root.after() / signals.

  Torrent Engine
    Piece management, block scheduling, rarity-first piece picker,
    piece verification (SHA-256).

  Peer Manager
    Maintains active peer connections. Handles choke/unchoke,
    request pipelining, peer banning on bad data.

  Discovery
    UDP multicast on 239.255.0.1:6771 for LAN announce.
    Peers broadcast infohash + listen port every 30 s.
    No central tracker required.

  Wire Protocol
    Length-prefixed TCP messages. See message types below.


================================================================================
DATA FLOW — SEEDER TO LEECHER
================================================================================

  Create .ltorrent file
    -> UDP multicast announce
    -> Leecher discovers peer
    -> TCP handshake
    -> Bitfield exchange
    -> Request pieces (rarity-first)
    -> Verify SHA-256 per piece
    -> Write to disk
    -> Send Have messages to peers


================================================================================
.LTORRENT FILE FORMAT (JSON)
================================================================================

  {
    "name"          : "my_file.zip",
    "info_hash"     : "<sha256 of the info dict>",
    "piece_length"  : 524288,          // 512 KB default
    "pieces"        : ["sha256_p0", "sha256_p1", "..."],
    "files"         : [
      { "path": "relative/path/file.zip", "length": 102400 }
    ],
    "created_by"    : "LocalTorrent/1.0",
    "creation_date" : 1746000000
  }

  Notes:
  - info_hash = SHA-256 of the JSON-encoded info dict (name, piece_length,
    pieces, files)
  - piece_length selectable at creation: 256 KB, 512 KB, 1 MB, 2 MB, 4 MB
  - Multi-file torrents supported via the files array
  - Single-file torrents use a files array with one entry


================================================================================
WIRE PROTOCOL MESSAGES (TCP, length-prefixed)
================================================================================

  Frame format: [4 bytes: total length][1 byte: message ID][payload]

  ID    Name          Payload                          Direction
  ----  ------------  -------------------------------  ----------------
  0x00  Handshake     protocol_str + infohash +        both (first msg)
                      peer_id (20 bytes each)
  0x01  Bitfield      bits[0..N], one bit per piece    both, after shake
  0x02  Have          piece_index (uint32)             both
  0x03  Request       piece_index, offset, length      leecher -> seeder
  0x04  Piece         piece_index, offset, data        seeder -> leecher
  0x05  Cancel        piece_index, offset, length      leecher -> seeder
  0x06  KeepAlive     (empty)                          both, every 30 s
  0x07  Choke         (empty)                          both
  0x08  Unchoke       (empty)                          both

  All multi-byte integers are big-endian (network byte order).
  Use struct.pack(">I", value) / struct.unpack(">I", data).


================================================================================
PEER DISCOVERY — UDP MULTICAST
================================================================================

  Multicast group : 239.255.0.1
  Port            : 6771
  TTL             : 1 (LAN only, configurable)

  Announce packet (sent every 30 s):
    "LT1 <infohash_hex> <listen_port>\n"
    e.g. "LT1 a3f9...c1 6881\n"

  On receiving an announce:
  1. Parse infohash and port.
  2. If infohash matches a torrent we are downloading, connect to sender.
  3. Initiate TCP handshake on received port.

  Peers also announce on startup and on receiving a new torrent.


================================================================================
PIECE PICKER — RARITY FIRST
================================================================================

  Algorithm:
  1. Collect the bitfields of all connected peers.
  2. Count how many peers have each piece (rarity score).
  3. Among pieces we still need, pick the rarest first.
  4. Ties broken randomly to distribute load.
  5. Endgame mode: when < 5 pieces remain, request each from all peers
     simultaneously; cancel duplicates on first receipt.

  Request pipelining:
  - Keep 5 outstanding block requests per peer at all times.
  - Block size: 16 KB (standard BitTorrent convention).
  - Each piece = piece_length / 16384 blocks.


================================================================================
INTEGRITY & SECURITY
================================================================================

  - Every received piece is SHA-256 hashed and compared to .ltorrent.
  - Bad piece -> discard, re-request from different peer.
  - Peer that sent bad data gets a strike; 3 strikes = soft-ban (ignored
    for 10 minutes).
  - Completed torrent: full re-hash of all files on disk to confirm.


================================================================================
GUI SCREENS
================================================================================

  Main Window
    - Torrent list table: Name | Size | Progress % | Down speed |
      Up speed | ETA | State (downloading/seeding/paused/error)
    - Toolbar: [Add Torrent] [Create Torrent] [Remove] [Pause/Resume]
    - Status bar: global download speed, upload speed, active peers

  Torrent Detail Panel (shown below list on selection)
    Tab: Peers   — table of IP:port, client, progress %, down/up speed
    Tab: Pieces  — visual grid, color-coded:
                   green=complete, yellow=in-progress, grey=missing
    Tab: Files   — tree view with per-file progress bar and priority
    Tab: Speed   — line graph of down/up speed over last 60 seconds

  Create Torrent Dialog
    - File / folder picker
    - Piece size dropdown (256 KB ... 4 MB)
    - Optional comment field
    - [Create] -> saves .ltorrent and auto-adds as seeder

  Add Torrent Dialog
    - File picker for .ltorrent
    - Save path selector
    - [Start immediately] checkbox

  Settings Dialog
    - Listen port (default 6881)
    - Max upload speed (KB/s, 0 = unlimited)
    - Max download speed (KB/s, 0 = unlimited)
    - Default save path
    - Max connections per torrent
    - Multicast TTL


================================================================================
MODULE STRUCTURE
================================================================================

  localtorrent/
  |
  |- main.py                   Entry point; starts asyncio loop + GUI
  |
  |- engine/
  |  |- __init__.py
  |  |- torrent.py             Torrent state, piece map, file I/O
  |  |- piece_picker.py        Rarity-first selection algorithm
  |  |- peer.py                asyncio Protocol — one instance per connection
  |  |- peer_manager.py        Pool management, choke strategy, request queue
  |  |- discovery.py           UDP multicast announce / listen
  |  |- metainfo.py            .ltorrent read / write / hash verification
  |  |- rate_limiter.py        Token bucket per torrent + global
  |  |- session.py             Save/restore session state to JSON
  |
  |- gui/
  |  |- __init__.py
  |  |- main_window.py         Root window, toolbar, torrent list
  |  |- detail_panel.py        Peer/piece/file/speed tabs
  |  |- dialogs.py             Create torrent, add torrent, settings
  |  |- widgets.py             PieceGrid, SpeedGraph, ProgressBar
  |
  |- tests/
     |- test_metainfo.py
     |- test_piece_picker.py
     |- test_protocol.py
     |- test_transfer.py       Integration: two in-process peers, full transfer


================================================================================
KEY DESIGN DECISIONS
================================================================================

  Threading model
    asyncio event loop runs in a daemon thread (threading.Thread).
    GUI runs on the main thread (required by Tkinter).
    Engine -> GUI: push updates via queue.Queue, consumed with root.after(100).
    GUI -> Engine: call asyncio.run_coroutine_threadsafe(coro, loop).

  No external libraries
    Everything uses Python stdlib: asyncio, socket, hashlib, struct, json,
    pathlib, threading, queue. Only test dependency is pytest.
    GUI: tkinter (stdlib) or pip install PyQt6.

  Piece size tradeoffs
    Smaller pieces (256 KB) = more granular progress, more overhead.
    Larger pieces (4 MB) = fewer round trips, coarser progress.
    Default 512 KB balances both for LAN speeds.

  Session persistence
    State file: ~/.localtorrent/session.json
    Saves: list of torrents, save paths, piece bitmaps (as hex strings).
    Loaded on startup; torrents resume automatically.

  Rate limiting
    Token bucket algorithm. Refilled every 100 ms.
    Separate buckets: per-torrent upload, per-torrent download, global.
    Prevents one torrent from starving the GUI or other torrents.

  Error handling
    Peer connection failures: log and retry after 60 s backoff.
    Disk full: pause torrent, show error in GUI, retry on resume.
    Corrupt .ltorrent: show error dialog, do not add torrent.


================================================================================
MILESTONES
================================================================================

  #1  Metainfo + CLI seeder/leecher
      Deliverable: create .ltorrent, transfer file between two terminals,
      verify pieces, no GUI yet.

  #2  Multi-peer engine
      Deliverable: peer manager, piece picker, choke/unchoke, cancellation,
      request pipelining.

  #3  LAN discovery
      Deliverable: UDP multicast announce, auto peer-connect on same LAN,
      works across separate processes.

  #4  Basic GUI
      Deliverable: torrent list, add/remove torrent, progress bar,
      peer count, pause/resume.

  #5  Full GUI
      Deliverable: detail panel with piece grid, speed graph, file tree,
      create torrent dialog.

  #6  Polish
      Deliverable: rate limiting, session persistence, settings dialog,
      comprehensive error handling, test suite.


================================================================================
DEPENDENCIES
================================================================================

  Runtime (all stdlib, no pip required):
    asyncio, socket, hashlib, struct, json, pathlib,
    threading, queue, tkinter

  Optional GUI alternative:
    PyQt6  (pip install PyQt6)

  Dev / test:
    pytest  (pip install pytest)


================================================================================
QUICK START (after milestone 1)
================================================================================

  # Terminal 1 — create torrent and seed
  python -m localtorrent create myfile.zip
  python -m localtorrent seed myfile.ltorrent

  # Terminal 2 — download
  python -m localtorrent download myfile.ltorrent --output ./downloads

  # Launch GUI
  python main.py


================================================================================
END OF SPEC
================================================================================
