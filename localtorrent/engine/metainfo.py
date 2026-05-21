import os
import json
import hashlib
from pathlib import Path

def hash_info_dict(info_dict: dict) -> str:
    """Calculate the SHA-256 info hash of the info dictionary."""
    encoded_dict = json.dumps(info_dict, separators=(',', ':'), sort_keys=True).encode('utf-8')
    return hashlib.sha256(encoded_dict).hexdigest()

def create_torrent(path: str, piece_length: int = 524288) -> dict:
    """Create a torrent dictionary from a file or directory."""
    target_path = Path(path)
    if not target_path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    files = []
    if target_path.is_file():
        files.append({"path": target_path.name, "length": target_path.stat().st_size})
        file_paths = [target_path]
    else:
        file_paths = []
        for root, _, filenames in os.walk(target_path):
            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(target_path).as_posix()
                files.append({"path": rel_path, "length": file_path.stat().st_size})
                file_paths.append(file_path)

    pieces = []
    buf = b""
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(piece_length - len(buf))
                if not chunk:
                    break
                buf += chunk
                if len(buf) == piece_length:
                    pieces.append(hashlib.sha256(buf).hexdigest())
                    buf = b""
    if buf:
        pieces.append(hashlib.sha256(buf).hexdigest())

    info_dict = {
        "name": target_path.name,
        "piece_length": piece_length,
        "pieces": pieces,
        "files": files
    }

    torrent_dict = {
        "name": target_path.name,
        "info_hash": hash_info_dict(info_dict),
        "piece_length": piece_length,
        "pieces": pieces,
        "files": files,
        "created_by": "LocalTorrent/1.0",
        "creation_date": int(os.stat(target_path).st_mtime)
    }
    
    return torrent_dict

def read_torrent(path: str) -> dict:
    """Read a .ltorrent file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_torrent(torrent_dict: dict, path: str):
    """Write a .ltorrent file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(torrent_dict, f, indent=2)
