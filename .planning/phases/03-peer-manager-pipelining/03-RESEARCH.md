# Phase 3 Research: Peer Manager & Pipelining

## Technical Approach
- **peer_manager.py**: We need a `PeerManager` class that holds a collection of active `PeerConnection` objects. It should handle adding/removing peers and broadcasting messages (like `Have` or `Bitfield`).
- **Request Pipelining**: To keep download speeds high, we cannot wait for a block to arrive before requesting the next one. We need to keep up to 5 block requests "in-flight" per peer. This means maintaining a queue of pending block requests and a list of unacknowledged sent requests.
- **Choke/Unchoke Strategy**: Peers start out "choked" (not allowed to request pieces). The `PeerManager` should periodically evaluate peer upload/download speeds to unchoke the fastest ones (typically 4 peers) and choke the rest. 
- **Message Loop**: The message loop inside `PeerConnection` will need to dispatch incoming messages (like `Choke`, `Unchoke`, `Piece`) back to the `PeerManager` or a `DownloadContext` via callbacks or `asyncio.Queue`.

## Gotchas
- Pipelining requires careful tracking. If a peer disconnects or chokes us, any in-flight block requests must be returned to the pool of available blocks.
- The 16KB blocks require a sub-piece mapping (which we partially handled, but now we need explicit block tracking).
