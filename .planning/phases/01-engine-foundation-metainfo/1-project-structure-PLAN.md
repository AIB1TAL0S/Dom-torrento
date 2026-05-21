---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/__init__.py"
  - "localtorrent/engine/__init__.py"
  - "localtorrent/engine/metainfo.py"
autonomous: true
---

# Plan 1: Project Structure and Metainfo

## Context
This plan establishes the core directory structure and implements the generation, parsing, and hashing validation of `.ltorrent` files.

## Tasks

<task>
  <id>1</id>
  <title>Create Project Directories and init files</title>
  <read_first>
    - localtorrent_spec.md
  </read_first>
  <action>
    Create the `localtorrent` and `localtorrent/engine` directories.
    Create empty `__init__.py` files in both directories to make them Python packages.
  </action>
  <acceptance_criteria>
    - `ls localtorrent/__init__.py` succeeds.
    - `ls localtorrent/engine/__init__.py` succeeds.
  </acceptance_criteria>
</task>

<task>
  <id>2</id>
  <title>Implement metainfo.py</title>
  <read_first>
    - localtorrent_spec.md
    - localtorrent/engine/metainfo.py
  </read_first>
  <action>
    Create `localtorrent/engine/metainfo.py`.
    Implement `create_torrent(path: str, piece_length: int = 524288) -> dict` which:
    1. Iterates over files in `path` (or single file).
    2. Reads the files in chunks of `piece_length`.
    3. Hashes each chunk with SHA-256.
    4. Returns the dictionary structure as specified in the spec.
    Implement `hash_info_dict(info_dict: dict) -> str` which uses `json.dumps(info_dict, separators=(',', ':'), sort_keys=True)` and hashes it with SHA-256.
    Implement `read_torrent(path: str) -> dict` and `write_torrent(torrent_dict: dict, path: str)`.
  </action>
  <acceptance_criteria>
    - `localtorrent/engine/metainfo.py` contains `def create_torrent`
    - `localtorrent/engine/metainfo.py` contains `def hash_info_dict`
    - `localtorrent/engine/metainfo.py` uses `hashlib.sha256`
  </acceptance_criteria>
</task>

## Verification
- Can run a python script importing `localtorrent.engine.metainfo` without errors.
- `metainfo.py` has the required parsing and generation functions.

## Must Haves
- Project structure created.
- `.ltorrent` generation, parsing, and hashing validation implemented in `metainfo.py`.
