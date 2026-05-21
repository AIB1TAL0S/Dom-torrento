# Phase 4 Research: Rarity-first Piece Picker

## Technical Approach
- **piece_picker.py**: We will need a `PiecePicker` class to intelligently choose which pieces to download next.
- The standard BitTorrent approach is "rarity-first": request pieces that are the rarest in the swarm to ensure maximum swarm health.
- We need to track `piece_counts` (an array where index = piece, value = number of peers that have it).
- As peers connect and send `Bitfield` or `Have` messages, we increment the counts for those pieces. If a peer disconnects, we decrement.
- The picker needs to skip pieces we already have (`torrent.bitfield == True`) or pieces currently being fully downloaded (we need to track active downloads).
- To support Request Pipelining (Phase 3), the picker must provide specific block coordinates (piece_index, block_offset, block_length) to the `PeerConnection`.

## Gotchas
- When selecting a rare piece, we also need to know which peers actually have it (if we have 4 connections but only 1 has the rare piece, we must ask that specific peer).
- We must handle block-level requests properly so different peers don't duplicate the exact same 16KB blocks unless we are in "Endgame" mode.
