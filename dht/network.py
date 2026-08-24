import asyncio

from dht.node import DHTNode, Peer
from dht.protocol import (
    PING,
    PONG,
    FIND_NODE,
    NODES,
    create_ping,
    create_pong,
    create_find_node,
    create_nodes_response,
    decode_message,
)


class DHTUDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol for MeshWeaver Kademlia communication."""

    def __init__(
        self,
        node: DHTNode,
        bootstrap_address=None,
        joined_future=None,
    ):
        self.node = node
        self.bootstrap_address = bootstrap_address
        self.joined_future = joined_future
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

        print(
            f"DHT node started at "
            f"{self.node.host}:{self.node.port}"
        )

        if self.bootstrap_address:
            print(
                f"Bootstrapping to "
                f"{self.bootstrap_address[0]}:"
                f"{self.bootstrap_address[1]}"
            )

            self.transport.sendto(
                create_ping(self.node.node_id),
                self.bootstrap_address,
            )

            print("Bootstrap PING sent")

    def datagram_received(self, data, addr):
        message = decode_message(data)

        message_type = message["type"]

        sender_id = int(
            message["sender_id"],
            16,
        )

        peer = Peer(
            node_id=sender_id,
            host=addr[0],
            port=addr[1],
        )

        self.node.add_peer(peer)

        if message_type == PING:
            self._handle_ping(peer, addr)

        elif message_type == PONG:
            self._handle_pong(peer)

        elif message_type == FIND_NODE:
            self._handle_find_node(
                message,
                addr,
            )

        elif message_type == NODES:
            self._handle_nodes(
                message
            )

    def _handle_ping(self, peer, addr):
        """Respond to a PING request."""

        print(
            f"Received PING from "
            f"{peer.host}:{peer.port}"
        )

        self.transport.sendto(
            create_pong(
                self.node.node_id
            ),
            addr,
        )

        print("PONG sent")

    def _handle_pong(self, peer):
        """Handle a PONG response."""

        print(
            f"Received PONG from "
            f"{peer.host}:{peer.port}"
        )

        print(
            "Bootstrap successful - peer added"
        )

        if (
            self.joined_future
            and not self.joined_future.done()
        ):
            self.joined_future.set_result(peer)

    def _handle_find_node(
        self,
        message,
        addr,
    ):
        """Return known peers to the requesting node."""

        target_id = int(
            message["payload"]["target_id"],
            16,
        )

        print(
            f"Received FIND_NODE request "
            f"for {target_id:040x}"
        )

        peers = []

        for peer in self.node.get_peers():
            peers.append(
                {
                    "node_id": f"{peer.node_id:040x}",
                    "host": peer.host,
                    "port": peer.port,
                }
            )

        response = create_nodes_response(
            self.node.node_id,
            peers,
        )

        self.transport.sendto(
            response,
            addr,
        )

        print(
            f"Sent {len(peers)} known peer(s)"
        )

    def _handle_nodes(self, message):
        """Add discovered nodes to the local peer list."""

        peers = message["payload"].get(
            "peers",
            [],
        )

        print(
            f"Received {len(peers)} discovered peer(s)"
        )

        for peer_data in peers:

            peer = Peer(
                node_id=int(
                    peer_data["node_id"],
                    16,
                ),
                host=peer_data["host"],
                port=peer_data["port"],
            )

            self.node.add_peer(peer)

            print(
                f"Discovered peer "
                f"{peer.host}:{peer.port}"
            )

    def error_received(self, exc):
        print(f"DHT UDP error: {exc}")

    def connection_lost(self, exc):
        print("DHT UDP connection closed")


async def start_node(
    node: DHTNode,
    bootstrap_address=None,
):
    """Start a DHT node and optionally bootstrap."""

    loop = asyncio.get_running_loop()

    joined_future = loop.create_future()

    transport, protocol = (
        await loop.create_datagram_endpoint(
            lambda: DHTUDPProtocol(
                node=node,
                bootstrap_address=bootstrap_address,
                joined_future=joined_future,
            ),
            local_addr=node.address,
        )
    )

    return transport, protocol, joined_future


async def find_nodes(
    protocol: DHTUDPProtocol,
    peer: Peer,
    target_id: int,
):
    """Ask a peer for nodes close to a target ID."""

    message = create_find_node(
        protocol.node.node_id,
        target_id,
    )

    protocol.transport.sendto(
        message,
        (peer.host, peer.port),
    )

    print(
        f"FIND_NODE sent to "
        f"{peer.host}:{peer.port}"
    )