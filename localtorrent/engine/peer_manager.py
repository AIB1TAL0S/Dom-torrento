import asyncio
import logging
import struct
from localtorrent.engine.peer import PeerConnection

logger = logging.getLogger(__name__)

class PeerManager:
    def __init__(self, torrent):
        self.torrent = torrent
        self.peers = set()
        self.max_peers = 30
        self._choke_task = asyncio.create_task(self._choke_loop())

    async def add_peer(self, peer: PeerConnection):
        if len(self.peers) >= self.max_peers:
            logger.info("Max peers reached, rejecting peer")
            await peer.close()
            return

        self.peers.add(peer)
        logger.info(f"Added peer {peer.ip}:{peer.port}. Total peers: {len(self.peers)}")
        asyncio.create_task(self._peer_message_loop(peer))

    async def remove_peer(self, peer: PeerConnection):
        if peer in self.peers:
            self.peers.remove(peer)
            if peer.is_connected:
                await peer.close()
            logger.info(f"Removed peer {peer.ip}:{peer.port}. Total peers: {len(self.peers)}")

    async def broadcast(self, msg_id: int, payload: bytes):
        for peer in self.peers:
            if peer.is_connected:
                try:
                    await peer.send_message(msg_id, payload)
                except Exception as e:
                    logger.error(f"Error broadcasting to {peer.ip}: {e}")

    async def choke_peer(self, peer: PeerConnection):
        if not peer.am_choking:
            await peer.send_message(0x07) # Choke
            peer.am_choking = True
            logger.debug(f"Choked peer {peer.ip}")

    async def unchoke_peer(self, peer: PeerConnection):
        if peer.am_choking:
            await peer.send_message(0x08) # Unchoke
            peer.am_choking = False
            logger.debug(f"Unchoked peer {peer.ip}")

    async def _choke_loop(self):
        while True:
            await asyncio.sleep(10)
            if not self.peers:
                continue

            # In a real implementation, sort by download/upload speed.
            # Here we just pick up to 4 peers to unchoke.
            connected_peers = [p for p in self.peers if p.is_connected]
            
            # Simple strategy: unchoke first 4, choke the rest
            to_unchoke = connected_peers[:4]
            to_choke = connected_peers[4:]

            for p in to_unchoke:
                await self.unchoke_peer(p)
            for p in to_choke:
                await self.choke_peer(p)

    async def _peer_message_loop(self, peer: PeerConnection):
        try:
            while peer.is_connected:
                msg_id, payload = await peer.read_message()
                
                if msg_id == -1: # Disconnected
                    break
                    
                if msg_id == 0x07: # Choke
                    peer.peer_choking = True
                    # If choked, clear pending requests to re-request elsewhere
                    peer.pending_requests.clear()
                elif msg_id == 0x08: # Unchoke
                    peer.peer_choking = False
                elif msg_id == 0x04: # Piece
                    if len(payload) >= 8:
                        piece_index, offset = struct.unpack(">II", payload[:8])
                        length = len(payload) - 8
                        
                        # Remove from pending requests
                        req = (piece_index, offset, length)
                        if req in peer.pending_requests:
                            peer.pending_requests.remove(req)
                            
                # Further message handling (Bitfield, Have, Request) would be implemented here
                
        except Exception as e:
            logger.error(f"Error in message loop for {peer.ip}: {e}")
        finally:
            await self.remove_peer(peer)
