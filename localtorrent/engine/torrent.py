import os
import asyncio
import hashlib
from pathlib import Path

class Torrent:
    def __init__(self, torrent_dict: dict, save_path: str):
        self.torrent_dict = torrent_dict
        self.save_path = Path(save_path)
        self.name = torrent_dict["name"]
        self.info_hash = torrent_dict["info_hash"]
        self.piece_length = torrent_dict["piece_length"]
        self.pieces_hashes = torrent_dict["pieces"]
        self.files = torrent_dict["files"]
        self.total_pieces = len(self.pieces_hashes)
        
        # Determine total size
        self.total_size = sum(f["length"] for f in self.files)
        
        # Initialize bitfield (False = downloading, True = complete)
        self.bitfield = [False] * self.total_pieces
        
        # Create save directory if needed
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)

    def _get_piece_mapping(self, piece_index: int):
        """Map a piece index to a list of (file_path, file_offset, piece_offset, length)"""
        start_byte = piece_index * self.piece_length
        end_byte = min(start_byte + self.piece_length, self.total_size)
        
        mapping = []
        current_byte = 0
        
        for file_info in self.files:
            file_len = file_info["length"]
            if current_byte + file_len > start_byte and current_byte < end_byte:
                file_path = self.save_path / file_info["path"]
                
                # Offset within the file
                file_offset = max(0, start_byte - current_byte)
                
                # Offset within the piece
                piece_offset = max(0, current_byte - start_byte)
                
                # Length to read/write from this file for this piece
                overlap_end = min(current_byte + file_len, end_byte)
                overlap_start = max(current_byte, start_byte)
                length = overlap_end - overlap_start
                
                mapping.append((file_path, file_offset, piece_offset, length))
            
            current_byte += file_len
            if current_byte >= end_byte:
                break
                
        return mapping

    def _read_piece_sync(self, piece_index: int) -> bytes:
        if piece_index < 0 or piece_index >= self.total_pieces:
            raise IndexError("Piece index out of bounds")
            
        mapping = self._get_piece_mapping(piece_index)
        expected_len = min(self.piece_length, self.total_size - piece_index * self.piece_length)
        piece_data = bytearray(expected_len)
        
        for file_path, file_offset, piece_offset, length in mapping:
            if not file_path.exists():
                return b"" # File missing, piece incomplete
            with open(file_path, "rb") as f:
                f.seek(file_offset)
                data = f.read(length)
                piece_data[piece_offset:piece_offset+length] = data
                
        return bytes(piece_data)

    async def read_piece(self, piece_index: int) -> bytes:
        return await asyncio.to_thread(self._read_piece_sync, piece_index)

    def _write_piece_sync(self, piece_index: int, data: bytes) -> bool:
        if piece_index < 0 or piece_index >= self.total_pieces:
            return False
            
        expected_hash = self.pieces_hashes[piece_index]
        actual_hash = hashlib.sha256(data).hexdigest()
        
        if actual_hash != expected_hash:
            return False # Hash mismatch
            
        mapping = self._get_piece_mapping(piece_index)
        
        for file_path, file_offset, piece_offset, length in mapping:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Ensure file exists and is large enough
            mode = "r+b" if file_path.exists() else "w+b"
            with open(file_path, mode) as f:
                f.seek(file_offset)
                f.write(data[piece_offset:piece_offset+length])
                
        self.bitfield[piece_index] = True
        return True

    async def write_piece(self, piece_index: int, data: bytes) -> bool:
        return await asyncio.to_thread(self._write_piece_sync, piece_index, data)
