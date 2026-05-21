import asyncio
import struct
import logging

logger = logging.getLogger(__name__)

class PeerConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.peer_id = None
        self.ip = None
        self.port = None
        # get extra info if available
        addr = writer.get_extra_info('peername')
        if addr:
            self.ip, self.port = addr
            
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        self.is_connected = True
        self.pending_requests = []
        self.max_pending_requests = 5

    async def send_message(self, msg_id: int, payload: bytes = b""):
        """Send a length-prefixed message."""
        length = 1 + len(payload)
        # >I is big-endian unsigned int (4 bytes), >B is big-endian unsigned char (1 byte)
        header = struct.pack(">IB", length, msg_id)
        self.writer.write(header + payload)
        await self.writer.drain()

    async def read_message(self) -> tuple[int, bytes]:
        """Read a length-prefixed message. Returns (msg_id, payload)."""
        try:
            length_bytes = await self.reader.readexactly(4)
        except asyncio.IncompleteReadError:
            return -1, b"" # Connection closed
            
        length = struct.unpack(">I", length_bytes)[0]
        
        if length == 0:
            return 0x06, b"" # KeepAlive
            
        try:
            msg_id_byte = await self.reader.readexactly(1)
            msg_id = struct.unpack(">B", msg_id_byte)[0]
            
            payload = b""
            if length > 1:
                payload = await self.reader.readexactly(length - 1)
                
            return msg_id, payload
        except asyncio.IncompleteReadError:
            return -1, b"" # Connection closed

    async def handshake(self, info_hash: str, peer_id: bytes):
        """Send a BitTorrent-style handshake."""
        # protocol string: "LocalTorrent/1.0"
        pstr = b"LocalTorrent/1.0"
        pstrlen = bytes([len(pstr)])
        reserved = b"\x00" * 8
        
        # info_hash is hex string, let's just use it as bytes.
        # Actually in standard BT, it's 20 bytes. We use SHA256 which is 32 bytes.
        # So our handshake is slightly non-standard: 32 bytes for info_hash.
        # Let's pack exactly what we have.
        info_hash_bytes = bytes.fromhex(info_hash) 
        
        handshake_msg = pstrlen + pstr + reserved + info_hash_bytes + peer_id
        self.writer.write(handshake_msg)
        await self.writer.drain()

    async def read_handshake(self) -> tuple[str, bytes]:
        """Read a BitTorrent-style handshake."""
        pstrlen_byte = await self.reader.readexactly(1)
        pstrlen = pstrlen_byte[0]
        
        pstr = await self.reader.readexactly(pstrlen)
        reserved = await self.reader.readexactly(8)
        
        info_hash_bytes = await self.reader.readexactly(32)
        info_hash = info_hash_bytes.hex()
        
        peer_id = await self.reader.readexactly(20)
        
        self.peer_id = peer_id
        return info_hash, peer_id

    async def close(self):
        self.is_connected = False
        self.writer.close()
        await self.writer.wait_closed()
