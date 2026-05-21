import asyncio
import json
import logging
import socket
import struct

logger = logging.getLogger(__name__)

MULTICAST_GROUP = '239.255.255.250'
MULTICAST_PORT = 6882

class DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, callback):
        self.callback = callback

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode('utf-8'))
            if msg.get("action") == "announce":
                info_hash = msg.get("info_hash")
                peer_id = msg.get("peer_id")
                port = msg.get("port")
                if info_hash and peer_id and port:
                    self.callback(addr[0], port, info_hash, peer_id)
        except Exception as e:
            logger.debug(f"Invalid discovery packet from {addr}: {e}")

class LocalDiscovery:
    def __init__(self, my_peer_id: str, my_tcp_port: int, on_peer_discovered):
        self.my_peer_id = my_peer_id
        self.my_tcp_port = my_tcp_port
        self.on_peer_discovered = on_peer_discovered
        self.info_hashes = set()
        self.transport = None
        self._task = None

    def add_info_hash(self, info_hash: str):
        self.info_hashes.add(info_hash)

    def _handle_packet(self, ip, port, info_hash, peer_id):
        if peer_id == self.my_peer_id:
            return # Ignore our own announcements
        if info_hash in self.info_hashes:
            self.on_peer_discovered(ip, port, info_hash)

    async def start(self):
        loop = asyncio.get_running_loop()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('', MULTICAST_PORT))
        except OSError as e:
            logger.error(f"Failed to bind UDP port {MULTICAST_PORT}: {e}")
            return

        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        except OSError as e:
            logger.warning(f"Failed to set multicast options (might be running on loopback): {e}")

        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: DiscoveryProtocol(self._handle_packet),
            sock=sock
        )
        
        logger.info(f"Started UDP Multicast Discovery on {MULTICAST_GROUP}:{MULTICAST_PORT}")
        self._task = asyncio.create_task(self._announce_loop())

    async def _announce_loop(self):
        while True:
            if self.transport:
                for info_hash in self.info_hashes:
                    msg = {
                        "action": "announce",
                        "info_hash": info_hash,
                        "peer_id": self.my_peer_id,
                        "port": self.my_tcp_port
                    }
                    payload = json.dumps(msg).encode('utf-8')
                    try:
                        self.transport.sendto(payload, (MULTICAST_GROUP, MULTICAST_PORT))
                    except OSError:
                        pass
            await asyncio.sleep(5)

    async def stop(self):
        if self._task:
            self._task.cancel()
        if self.transport:
            self.transport.close()
