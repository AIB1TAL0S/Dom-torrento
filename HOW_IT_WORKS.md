# How LocalTorrent Works

LocalTorrent is a peer-to-peer (P2P) file transfer system designed entirely in Python for local networks (localhost / LAN). It allows multiple Python processes to discover each other automatically, exchange file metadata, and transfer file chunks in parallel without any central tracker or external internet connection.

This document breaks down the internal architecture, protocols, and data flow that make LocalTorrent tick.

---

## 1. System Architecture

LocalTorrent is built using a multi-threaded architecture to keep the user interface responsive while managing intense network I/O.

*   **GUI Layer (Tkinter)**: Runs on the main thread. It handles user inputs (adding/creating torrents, pausing) and displays progress bars, speed graphs, and peer lists.
*   **Controller (Bridge)**: Acts as the intermediary between the GUI and the Engine. It sends user actions to the Engine thread and receives progress updates via a thread-safe Queue, passing them to the GUI using `root.after()`.
*   **Torrent Engine (asyncio)**: Runs in a dedicated background daemon thread. This is the heart of the application, managing piece verification (SHA-256), block scheduling, and disk I/O.
*   **Peer Manager**: Maintains active TCP connections to other peers, deciding which peers to request pieces from (using pipelining) and enforcing rules like disconnecting peers that send corrupted data.
*   **Discovery Module**: Replaces the need for a central tracker. It uses UDP multicast to broadcast announcements to the local network so peers can find each other.

---

## 2. Peer Discovery (No Tracker)

Unlike traditional BitTorrent which relies on a central server (tracker) to connect peers, LocalTorrent uses **UDP Multicast**.

*   **Multicast Group**: `239.255.0.1:6771`
*   **Announcements**: Every 30 seconds (and on startup or when a new torrent is added), a peer broadcasts a short message: `LT1 <infohash_hex> <listen_port>\n`.
*   **Connecting**: When another peer running LocalTorrent receives this broadcast, it checks if it is downloading or seeding the same `infohash`. If there's a match, it initiates a TCP connection to the sender's IP address and listen port.

---

## 3. The `.ltorrent` File Format

Metadata for file transfers is stored in a `.ltorrent` file, which is a simple JSON object (unlike standard BitTorrent's Bencode). It contains:

*   **Info Hash**: A SHA-256 hash of the core information, used as the unique identifier for the torrent.
*   **Piece Length**: How large each chunk of the file is (usually 512 KB).
*   **Pieces Array**: A list of SHA-256 hashes, one for every piece of the file. This ensures data integrity.
*   **Files Array**: Supports multi-file torrents by mapping relative paths to file sizes.

---

## 4. The Wire Protocol (TCP)

Once two peers discover each other and connect over TCP, they speak the LocalTorrent Wire Protocol. It is a length-prefixed protocol where every message starts with a 4-byte total length, followed by a 1-byte Message ID, and then the payload.

1.  **Handshake (`0x00`)**: The very first message. They exchange protocol names, the infohash, and their unique Peer IDs.
2.  **Bitfield (`0x01`)**: Peers exchange which pieces they currently have (a bit array).
3.  **Request (`0x03`)**: A leecher asks for a specific block (typically 16 KB) of a piece.
4.  **Piece (`0x04`)**: A seeder responds with the actual binary data of the block.
5.  **Have (`0x02`)**: Whenever a peer successfully downloads and verifies a full piece, it broadcasts a "Have" message to all connected peers so they know it is available.
6.  **Choke/Unchoke (`0x07`, `0x08`)**: Mechanism to manage connection limits and bandwidth.

---

## 5. Rarity-First Piece Picking

To ensure the fastest possible distribution of files across the network, LocalTorrent uses a **Rarity-First** algorithm.

1.  The engine looks at the bitfields of all connected peers.
2.  It counts how many peers have each piece to calculate a "rarity score".
3.  When deciding what to download next, it requests the rarest pieces first. This ensures that rare pieces are quickly replicated across the network, preventing bottlenecks.
4.  **Pipelining**: Up to 5 block requests are kept "in flight" (pipelined) to a single peer at any time to maximize TCP throughput.
5.  **Endgame Mode**: When the torrent is almost finished (< 5 pieces remaining), the engine will aggressively request the remaining blocks from *all* peers simultaneously to prevent a single slow peer from delaying completion.

---

## 6. End-to-End Data Flow

Here is the lifecycle of a file transfer from Seeder to Leecher:

1.  **Creation**: User A selects a file in the GUI. The engine slices it into 512 KB pieces, hashes them, and creates a `.ltorrent` file.
2.  **Announcement**: User A's client starts broadcasting the infohash via UDP multicast.
3.  **Discovery**: User B loads the `.ltorrent` file. Their client hears User A's UDP broadcast and opens a TCP connection.
4.  **Handshake & Exchange**: They shake hands and exchange Bitfields.
5.  **Downloading**: User B's engine requests the rarest pieces first.
6.  **Verification**: As User B receives blocks, they are assembled into pieces. Each piece is SHA-256 hashed and verified against the `.ltorrent` file. If valid, it is written to disk.
7.  **Seeding**: User B sends `Have` messages to the network, becoming a partial seeder.
8.  **Completion**: Once all pieces are downloaded, a final whole-file check is performed, and the torrent enters a pure Seeding state.
