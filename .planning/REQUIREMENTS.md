# Requirements

## Milestone 1: Metainfo + CLI seeder/leecher
- [ ] Create .ltorrent file
- [ ] Implement TCP handshake and basic Bitfield/Request/Piece/Cancel protocol messages
- [ ] Transfer file between two terminals
- [ ] Verify pieces via SHA-256

## Milestone 2: Multi-peer engine
- [ ] Implement Peer Manager
- [ ] Implement Piece Picker algorithm (Rarity-first)
- [ ] Support Choke/Unchoke strategy
- [ ] Implement request pipelining (5 outstanding block requests per peer)

## Milestone 3: LAN discovery
- [ ] Implement UDP multicast announce on 239.255.0.1:6771
- [ ] Auto-connect to peers announcing same infohash on same LAN

## Milestone 4: Basic GUI
- [ ] Implement Tkinter/PyQt6 Main Window
- [ ] Show Torrent list (Name, Size, Progress, Speeds, ETA, State)
- [ ] Toolbar controls (Add, Create, Remove, Pause/Resume)
- [ ] Asyncio event loop running in a daemon thread bridging with GUI

## Milestone 5: Full GUI
- [ ] Create Torrent Detail Panel (Peers, Pieces grid, Files tree, Speed graph)
- [ ] Implement Create Torrent Dialog
- [ ] Implement Add Torrent Dialog

## Milestone 6: Polish
- [ ] Rate limiting (per-torrent and global)
- [ ] Session persistence (~/.localtorrent/session.json)
- [ ] Settings Dialog
- [ ] Comprehensive error handling (Peer connection failures, Disk full, Corrupt .ltorrent)
- [ ] Test suite integration
