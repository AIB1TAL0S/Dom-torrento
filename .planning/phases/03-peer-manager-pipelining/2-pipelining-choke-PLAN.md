---
wave: 2
depends_on: ["1-peer-manager-PLAN.md"]
files_modified:
  - "localtorrent/engine/peer_manager.py"
autonomous: true
---

# Plan 2: Choke Strategy and Request Pipelining

## Context
Implement the logic for choke/unchoke and basic request pipelining (5 outstanding requests) inside the Peer Manager.

## Tasks

<task>
  <id>1</id>
  <title>Implement Choke/Unchoke Logic</title>
  <read_first>
    - localtorrent/engine/peer_manager.py
  </read_first>
  <action>
    In `localtorrent/engine/peer_manager.py`, add `async def choke_peer(self, peer)` and `async def unchoke_peer(self, peer)` methods.
    `choke_peer` sends msg_id `0x07` (Choke) and sets `peer.am_choking = True`.
    `unchoke_peer` sends msg_id `0x08` (Unchoke) and sets `peer.am_choking = False`.
    Implement `async def _choke_loop(self)` which runs periodically (e.g., every 10 seconds), sorting peers by download speed (we can mock speed for now or just pick 4 random peers if speed tracking isn't fully ready), unchoking the top 4 and choking the rest.
  </action>
  <acceptance_criteria>
    - `PeerManager` has `choke_peer` and `unchoke_peer`.
    - Periodic loop exists to manage unchoked peers (max 4).
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Implement Request Pipelining structure</title>
  <read_first>
    - localtorrent/engine/peer.py
  </read_first>
  <action>
    In `PeerConnection`, add `self.pending_requests = []` (list of (piece_index, offset, length) tuples).
    Add `self.max_pending_requests = 5`.
    When we want to request blocks, we should only send `Request` messages (0x03) if `len(self.pending_requests) < self.max_pending_requests`.
    When a `Piece` (0x04) message is received in the message loop, remove the corresponding request from `self.pending_requests`.
  </action>
  <acceptance_criteria>
    - `PeerConnection` tracks `pending_requests`.
    - Pipelining limit is set to 5.
  </acceptance_criteria>
</task>

## Verification
- Code can send choke/unchoke messages.
- Request pipelining tracking mechanism allows up to 5 concurrent block requests.

## Must Haves
- Choke strategy (max 4 unchoked peers).
- 5 outstanding block requests logic.
