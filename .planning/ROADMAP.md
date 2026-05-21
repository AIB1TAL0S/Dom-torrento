# Roadmap

## Current Milestone: Milestone 1 - Metainfo + CLI seeder/leecher

### Phase 1: Engine Foundation & Metainfo
- Create project structure
- Implement `.ltorrent` generation, parsing, and hashing validation (`metainfo.py`)
- Implement basic `torrent.py` state and file I/O operations

### Phase 2: Wire Protocol & Basic Transfer
- Implement TCP connection handling and length-prefixed protocol parsing (`peer.py`)
- Complete Handshake, Bitfield, Request, Piece message passing
- Support transferring a file chunk between a single seeder and leecher process via CLI

## Future Milestones

### Milestone 2: Multi-peer engine
- **Phase 3: Peer Manager & Request Pipelining**
- **Phase 4: Rarity-first Piece Picker**

### Milestone 3: LAN discovery
- **Phase 5: UDP Multicast Discovery**

### Milestone 4: Basic GUI
- **Phase 6: Asyncio & GUI Threading Bridge**
- **Phase 7: Main Window & Core Controls**

### Milestone 5: Full GUI
- **Phase 8: Torrent Detail Views & Dialogs**

### Milestone 6: Polish
- **Phase 9: Rate Limiting & Persistence**
- **Phase 10: Settings, Error Handling & Tests**
