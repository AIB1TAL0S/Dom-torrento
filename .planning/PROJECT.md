# LocalTorrent

## What This Is
A fully local peer-to-peer file transfer system where multiple Python processes running on the same machine (or LAN) discover each other, exchange file metadata (torrent-like), and transfer file chunks in parallel — all visualised through a desktop GUI built with Tkinter or PyQt6.

## Core Value
To provide an efficient, decentralized, and fully local file-sharing solution without needing internet access or external trackers.

## Target Audience
Users needing fast, reliable file transfer across a local network or multiple processes on the same machine.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python 3.11+ | Modern Python features, specifically robust asyncio support | — Pending |
| GUI Framework | Tkinter (default) or PyQt6 for cross-platform desktop interface | — Pending |
| Network | `asyncio` + raw sockets (stdlib only) for maximum compatibility without external dependencies | — Pending |
| Discovery | UDP multicast (239.255.0.1:6771) | No central tracker required |

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Implement .ltorrent file creation and parsing
- [ ] Develop wire protocol (Handshake, Bitfield, Request, Piece, etc.)
- [ ] Create UDP multicast peer discovery
- [ ] Build Torrent Engine (piece management, SHA-256 verification, rarity-first piece picker)
- [ ] Build Peer Manager (connection pool, choke/unchoke logic)
- [ ] Implement GUI (Main Window, Torrent Details, Create/Add dialogs, Settings)
- [ ] Add rate limiting (global and per-torrent token bucket)
- [ ] Implement session persistence (`~/.localtorrent/session.json`)

### Out of Scope

- Internet-based peer discovery (LAN/localhost only)
- External trackers (Decentralized multicast used instead)
- Non-desktop platforms (Mobile, Web)

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-05 after initialization*
