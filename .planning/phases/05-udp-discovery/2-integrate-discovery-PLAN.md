---
wave: 2
depends_on: ["1-udp-discovery-PLAN.md"]
files_modified:
  - "localtorrent/__main__.py"
autonomous: true
---

# Plan 2: Integrate Discovery with Engine

## Context
Hook up the newly created `LocalDiscovery` service into the main execution flow so the seeder and leecher naturally find each other.

## Tasks

<task>
  <id>1</id>
  <title>Integrate Discovery in main</title>
  <read_first>
    - localtorrent/__main__.py
    - localtorrent/engine/discovery.py
  </read_first>
  <action>
    In `localtorrent/__main__.py`, import `LocalDiscovery`.
    Update the `seed` and `download` functions.
    When setting up the torrent, initialize `LocalDiscovery(my_peer_id, 6881, callback)`.
    The `callback(ip, port, info_hash)` should verify `info_hash == torrent.info_hash`.
    If it matches, it should spawn a task to `asyncio.open_connection(ip, port)` and add the resulting `PeerConnection` to the `PeerManager`.
    (Make sure to maintain a `known_peers` set to avoid connecting to the same IP/Port twice).
    Call `await discovery.start()` and register the torrent's `info_hash` with it.
  </action>
  <acceptance_criteria>
    - Running `seed` and `download` automatically discovers peers without hardcoding `127.0.0.1` locally if on the same LAN.
    - Successfully filters duplicate connection attempts.
  </acceptance_criteria>
</task>

## Verification
- Starting two instances with the same `.ltorrent` file automatically links them and begins transfer.

## Must Haves
- TCP connection bridging from UDP discovery callbacks.
