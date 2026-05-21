# Phase 5 Research: UDP Multicast Discovery

## Technical Approach
- **Multicast Mechanics**: The LocalTorrent scope explicitly focuses on localhost/LAN. Instead of relying on a centralized tracker or manual IP typing, peers will find each other using UDP Multicast.
- We will bind a UDP socket to a well-known local multicast group (e.g., `239.255.255.250`) on a specific port (e.g., `6882`).
- Python's `asyncio` handles UDP natively via `loop.create_datagram_endpoint` using a `DatagramProtocol`.
- **Payload**: The payload can be a simple JSON string broadcasted every few seconds.
  ```json
  {
    "action": "announce",
    "info_hash": "<target_info_hash>",
    "peer_id": "<our_peer_id>",
    "port": 6881
  }
  ```
- When a `DatagramProtocol` receives a packet, it will parse the JSON. If the `info_hash` matches a torrent we are actively managing, and the `peer_id` is NOT our own, we should attempt an `asyncio.open_connection` to the sender's IP and reported `port`.

## Gotchas
- Multi-NIC environments: Multicast routing can sometimes be tricky depending on the OS routing tables. Standard IP_ADD_MEMBERSHIP via `struct` works for most cases.
- We must prevent connecting to ourselves. The `peer_id` comparison handles this.
- If we see an announcement from a peer we are *already* connected to, we should drop it. A simple IP/Port or PeerID tracking cache is required in the discovery manager.
