---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/peer_manager.py"
  - "localtorrent/engine/peer.py"
autonomous: true
---

# Plan 1: Peer Manager

## Context
Implement a `PeerManager` class to hold and manage a pool of active `PeerConnection` objects, allowing us to connect to multiple peers concurrently.

## Tasks

<task>
  <id>1</id>
  <title>Create PeerManager</title>
  <read_first>
    - localtorrent/engine/peer.py
  </read_first>
  <action>
    Create `localtorrent/engine/peer_manager.py`.
    Implement `PeerManager` class.
    It should store `self.peers = set()` and `self.max_peers = 30`.
    Implement `async def add_peer(self, peer: PeerConnection)` which adds to the set and starts an asyncio background task `asyncio.create_task(self._peer_message_loop(peer))` to continuously read messages from the peer.
    Implement `async def remove_peer(self, peer: PeerConnection)` which closes the peer and removes it.
    Implement `async def broadcast(self, msg_id: int, payload: bytes)` to send a message to all connected peers.
  </action>
  <acceptance_criteria>
    - `localtorrent/engine/peer_manager.py` contains `class PeerManager`
    - Contains `add_peer`, `remove_peer`, `broadcast` methods
    - Uses `asyncio.create_task` to handle message reading concurrently for each peer
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Refactor PeerConnection</title>
  <read_first>
    - localtorrent/engine/peer.py
  </read_first>
  <action>
    Update `PeerConnection` in `localtorrent/engine/peer.py`.
    Add states: `am_choking = True`, `am_interested = False`, `peer_choking = True`, `peer_interested = False`.
    Add `is_connected = True` to track connection state.
  </action>
  <acceptance_criteria>
    - `PeerConnection` initialization includes choking and interested state variables.
  </acceptance_criteria>
</task>

## Verification
- Can create a `PeerManager` instance.
- Adding a peer successfully tracks it and allows broadcasting.

## Must Haves
- Multi-peer connection tracking.
- Concurrent reading from all connected peers via background tasks.
