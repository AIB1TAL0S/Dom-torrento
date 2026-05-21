import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PiecePicker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.piece_counts = [0] * self.torrent.total_pieces
        self.block_size = 16384
        
        # Track which blocks of a piece have been requested
        # Format: { piece_index: set([block_offset1, block_offset2, ...]) }
        self.requested_blocks = {}

    def add_peer_bitfield(self, bitfield_bytes: bytes):
        for i in range(self.torrent.total_pieces):
            byte_idx = i // 8
            bit_idx = 7 - (i % 8)
            if byte_idx < len(bitfield_bytes):
                if bitfield_bytes[byte_idx] & (1 << bit_idx):
                    self.piece_counts[i] += 1

    def add_peer_have(self, piece_index: int):
        if 0 <= piece_index < self.torrent.total_pieces:
            self.piece_counts[piece_index] += 1

    def remove_peer_bitfield(self, bitfield_bytes: bytes):
        for i in range(self.torrent.total_pieces):
            byte_idx = i // 8
            bit_idx = 7 - (i % 8)
            if byte_idx < len(bitfield_bytes):
                if bitfield_bytes[byte_idx] & (1 << bit_idx):
                    self.piece_counts[i] = max(0, self.piece_counts[i] - 1)

    def get_next_block_request(self, peer_bitfield: list[bool]) -> Optional[tuple[int, int, int]]:
        """Return the (piece_index, offset, length) of the next block to request, prioritized by rarity."""
        
        # Build list of available, needed pieces
        candidates = []
        for i in range(self.torrent.total_pieces):
            # We don't have it, peer has it, and there is at least one peer that has it
            if not self.torrent.bitfield[i] and peer_bitfield[i] and self.piece_counts[i] > 0:
                candidates.append((self.piece_counts[i], i))
                
        if not candidates:
            return None
            
        # Sort by rarity (ascending count)
        candidates.sort(key=lambda x: x[0])
        
        for count, piece_index in candidates:
            # How large is this piece?
            expected_len = min(self.torrent.piece_length, self.torrent.total_size - piece_index * self.torrent.piece_length)
            
            # Which blocks have we already requested?
            requested = self.requested_blocks.get(piece_index, set())
            
            # Find next block
            offset = 0
            while offset < expected_len:
                if offset not in requested:
                    length = min(self.block_size, expected_len - offset)
                    
                    # Mark requested
                    if piece_index not in self.requested_blocks:
                        self.requested_blocks[piece_index] = set()
                    self.requested_blocks[piece_index].add(offset)
                    
                    return (piece_index, offset, length)
                offset += self.block_size
                
        return None
        
    def block_received(self, piece_index: int, offset: int):
        """Called when a block is actually received so we know it's permanently handled."""
        pass
        
    def cancel_requested_block(self, piece_index: int, offset: int):
        """Return a block to the pool of unrequested blocks."""
        if piece_index in self.requested_blocks:
            if offset in self.requested_blocks[piece_index]:
                self.requested_blocks[piece_index].remove(offset)
