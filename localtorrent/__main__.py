import argparse
import asyncio
import logging
import os
import uuid

from localtorrent.engine.metainfo import create_torrent, write_torrent, read_torrent
from localtorrent.engine.torrent import Torrent
from localtorrent.engine.peer import PeerConnection
from localtorrent.engine.peer_manager import PeerManager
from localtorrent.engine.discovery import LocalDiscovery

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def run_node(torrent_file: str, output_dir: str, tcp_port: int, seeding: bool):
    torrent_dict = read_torrent(torrent_file)
    torrent = Torrent(torrent_dict, output_dir)
    
    if seeding:
        # Assume we have all pieces if we are explicitly seeding
        torrent.bitfield = [True] * torrent.total_pieces
        
    my_peer_id = f"-LT1000-{uuid.uuid4().hex[:12]}".encode('utf-8')
    peer_id_str = my_peer_id.decode('utf-8')
    
    peer_manager = PeerManager(torrent)
    known_peers = set()

    async def handle_incoming_connection(reader, writer):
        peer = PeerConnection(reader, writer)
        logging.info(f"Incoming connection from {peer.ip}:{peer.port}")
        
        try:
            remote_info_hash, remote_peer_id = await peer.read_handshake()
            if remote_info_hash != torrent.info_hash:
                await peer.close()
                return
            await peer.handshake(torrent.info_hash, my_peer_id)
            
            # Send Bitfield if we have any pieces
            if any(torrent.bitfield):
                import math
                bitfield_len = math.ceil(torrent.total_pieces / 8)
                bitfield_payload = bytearray(bitfield_len)
                for i, has_piece in enumerate(torrent.bitfield):
                    if has_piece:
                        byte_idx = i // 8
                        bit_idx = 7 - (i % 8)
                        bitfield_payload[byte_idx] |= (1 << bit_idx)
                await peer.send_message(0x01, bytes(bitfield_payload))
                
            await peer_manager.add_peer(peer)
            
        except Exception as e:
            logging.error(f"Handshake failed: {e}")
            await peer.close()

    def on_peer_discovered(ip, port, info_hash):
        peer_addr = (ip, port)
        if peer_addr in known_peers:
            return
            
        logging.info(f"Discovered peer at {ip}:{port}")
        known_peers.add(peer_addr)
        
        asyncio.create_task(connect_to_peer(ip, port))

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
        except Exception as e:
            logging.error(f"Failed to connect to discovered peer {ip}:{port}: {e}")
            known_peers.remove((ip, port))

    # Start TCP server
    server = await asyncio.start_server(handle_incoming_connection, '0.0.0.0', tcp_port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logging.info(f"Listening for TCP connections on {addrs}")

    # Start Discovery
    discovery = LocalDiscovery(peer_id_str, tcp_port, on_peer_discovered)
    discovery.add_info_hash(torrent.info_hash)
    await discovery.start()

    logging.info(f"Node started for '{torrent.name}' (Seeding: {seeding})")
    
    async with server:
        await server.serve_forever()

def main():
    parser = argparse.ArgumentParser(description="LocalTorrent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("path", help="Path to file or directory")
    
    parser_seed = subparsers.add_parser("seed")
    parser_seed.add_argument("torrent_file", help="Path to .ltorrent file")
    parser_seed.add_argument("--port", type=int, default=6881, help="TCP Listen Port")
    
    parser_dl = subparsers.add_parser("download")
    parser_dl.add_argument("torrent_file", help="Path to .ltorrent file")
    parser_dl.add_argument("--output", required=True, help="Output directory")
    parser_dl.add_argument("--port", type=int, default=6882, help="TCP Listen Port")
    
    parser_gui = subparsers.add_parser("gui", help="Launch the graphical interface")
    
    args = parser.parse_args()
    
    if args.command == "create":
        logging.info(f"Creating torrent for {args.path}")
        t_dict = create_torrent(args.path)
        out_name = f"{t_dict['name']}.ltorrent"
        write_torrent(t_dict, out_name)
        logging.info(f"Torrent created: {out_name}")
        
    elif args.command == "seed":
        asyncio.run(run_node(args.torrent_file, ".", args.port, True))
        
    elif args.command == "download":
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        asyncio.run(run_node(args.torrent_file, args.output, args.port, False))
        
    elif args.command == "gui":
        from localtorrent.gui.app import run_gui
        run_gui()

if __name__ == "__main__":
    main()
