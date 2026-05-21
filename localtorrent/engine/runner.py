import asyncio
import threading
import logging
import uuid
import os
import math

from localtorrent.engine.metainfo import read_torrent
from localtorrent.engine.torrent import Torrent
from localtorrent.engine.peer import PeerConnection
from localtorrent.engine.peer_manager import PeerManager
from localtorrent.engine.discovery import LocalDiscovery

logger = logging.getLogger(__name__)

class EngineThread(threading.Thread):
    def __init__(self):
        super().__init__(name="LocalTorrentEngine", daemon=True)
        self.loop = None
        self._loop_ready = threading.Event()
        self.active_torrents = {} 
        self._lock = threading.Lock()
        
        self.torrent_tasks = {}
        self.tcp_port_counter = 6881

    def run(self):
        """Runs in the background thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self._loop_ready.set()
        logger.info("Engine Thread started")
        
        try:
            self.loop.run_forever()
        finally:
            logger.info("Engine Thread shutting down tasks...")
            
            # Cancel all pending tasks
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
                
            if pending:
                self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
            logger.info("Engine Thread stopped")

    def submit_task(self, coro):
        """Submit an asyncio coroutine to run on the background loop."""
        self._loop_ready.wait()
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        """Stop the background loop."""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

    def add_torrent(self, torrent_file: str, output_dir: str):
        self.submit_task(self._run_torrent(torrent_file, output_dir))

    def remove_torrent(self, info_hash: str):
        with self._lock:
            if info_hash in self.torrent_tasks:
                for task in self.torrent_tasks[info_hash]:
                    self.loop.call_soon_threadsafe(task.cancel)
                del self.torrent_tasks[info_hash]
            if info_hash in self.active_torrents:
                del self.active_torrents[info_hash]

    async def _run_torrent(self, torrent_file: str, output_dir: str):
        try:
            # Setup
            torrent_dict = read_torrent(torrent_file)
            torrent = Torrent(torrent_dict, output_dir)
            
            # Basic seeding check
            if os.path.exists(output_dir):
                expected_path = os.path.join(output_dir, torrent.name)
                if os.path.exists(expected_path):
                    # Mark all pieces complete if the file/folder exists 
                    # A robust implementation would hash check the file here
                    torrent.bitfield = [True] * torrent.total_pieces

            my_peer_id = f"-LT1000-{uuid.uuid4().hex[:12]}".encode('utf-8')
            peer_id_str = my_peer_id.decode('utf-8')
            
            peer_manager = PeerManager(torrent)
            known_peers = set()
            
            tcp_port = self.tcp_port_counter
            self.tcp_port_counter += 1

            async def handle_incoming_connection(reader, writer):
                peer = PeerConnection(reader, writer)
                try:
                    remote_info_hash, remote_peer_id = await peer.read_handshake()
                    if remote_info_hash != torrent.info_hash:
                        await peer.close()
                        return
                    await peer.handshake(torrent.info_hash, my_peer_id)
                    
                    if any(torrent.bitfield):
                        bitfield_len = math.ceil(torrent.total_pieces / 8)
                        bitfield_payload = bytearray(bitfield_len)
                        for i, has_piece in enumerate(torrent.bitfield):
                            if has_piece:
                                byte_idx = i // 8
                                bit_idx = 7 - (i % 8)
                                bitfield_payload[byte_idx] |= (1 << bit_idx)
                        await peer.send_message(0x01, bytes(bitfield_payload))
                        
                    await peer_manager.add_peer(peer)
                except Exception:
                    await peer.close()

            def on_peer_discovered(ip, port, info_hash):
                if (ip, port) in known_peers:
                    return
                known_peers.add((ip, port))
                task = asyncio.create_task(connect_to_peer(ip, port))
                with self._lock:
                    if torrent.info_hash in self.torrent_tasks:
                        self.torrent_tasks[torrent.info_hash].append(task)

            async def connect_to_peer(ip, port):
                try:
                    reader, writer = await asyncio.open_connection(ip, port)
                    peer = PeerConnection(reader, writer)
                    await peer.handshake(torrent.info_hash, my_peer_id)
                    remote_info_hash, remote_peer_id = await peer.read_handshake()
                    if remote_info_hash == torrent.info_hash:
                        await peer_manager.add_peer(peer)
                    else:
                        await peer.close()
                except Exception:
                    known_peers.remove((ip, port))

            # Start TCP Server
            server = await asyncio.start_server(handle_incoming_connection, '0.0.0.0', tcp_port)
            
            # Start Discovery
            discovery = LocalDiscovery(peer_id_str, tcp_port, on_peer_discovered)
            discovery.add_info_hash(torrent.info_hash)
            await discovery.start()

            # Background Status Loop
            async def status_loop():
                while True:
                    with self._lock:
                        pieces_have = sum(1 for b in torrent.bitfield if b)
                        progress = (pieces_have / torrent.total_pieces) * 100 if torrent.total_pieces > 0 else 0
                        status = "Seeding" if pieces_have == torrent.total_pieces else "Downloading"
                        
                        self.active_torrents[torrent.info_hash] = {
                            "name": torrent.name,
                            "size": f"{torrent.total_size / (1024*1024):.2f} MB",
                            "progress": progress,
                            "status": status,
                            "peers": len(peer_manager.peers)
                        }
                    await asyncio.sleep(1)

            status_task = asyncio.create_task(status_loop())
            server_task = asyncio.create_task(server.serve_forever())
            
            with self._lock:
                self.torrent_tasks[torrent.info_hash] = [status_task, server_task, discovery._task]

        except Exception as e:
            logger.error(f"Failed to run torrent {torrent_file}: {e}")
