---
wave: 1
depends_on: []
files_modified:
  - "localtorrent/engine/discovery.py"
autonomous: true
---

# Plan 1: Multicast Discovery Protocol

## Context
Implement the UDP multicast discovery logic allowing peers to find each other on the local network without a tracker.

## Tasks

<task>
  <id>1</id>
  <title>Create LocalDiscovery service</title>
  <read_first>
    - localtorrent/engine/peer_manager.py
  </read_first>
  <action>
    Create `localtorrent/engine/discovery.py`.
    Create a `DiscoveryProtocol(asyncio.DatagramProtocol)` class to handle incoming UDP packets.
    Create a `LocalDiscovery` class.
    It takes `my_peer_id: str`, `my_tcp_port: int`, and a callback function `on_peer_discovered(ip, port, info_hash)`.
    Implement `async def start(self)`:
      - Create a UDP socket.
      - Set `SO_REUSEADDR`.
      - Join multicast group `239.255.255.250` via `IP_ADD_MEMBERSHIP`.
      - Use `asyncio.get_running_loop().create_datagram_endpoint` to bind it to port 6882.
      - Start a background task `_announce_loop()`.
    Implement `async def _announce_loop(self)`:
      - Periodically (every 5 seconds) iterate over registered `info_hashes`.
      - Create a JSON string with `action`, `info_hash`, `peer_id`, and `port`.
      - Send it to `239.255.255.250:6882` using the UDP transport.
  </action>
  <acceptance_criteria>
    - `LocalDiscovery` successfully joins a multicast group and sends periodic announcements.
    - Incoming valid announcements trigger the `on_peer_discovered` callback.
  </acceptance_criteria>
</task>

## Verification
- Can initialize `LocalDiscovery`.
- Packets are properly formed JSON strings.

## Must Haves
- Python stdlib UDP socket configuration for multicast.
- Background announcement loop.
