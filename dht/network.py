import asyncio

from dht.node import DHTNode, Peer
from dht.protocol import (
    PING,
    PONG,
    create_ping,
    create_pong,
    decode_message,
)


class DHTUDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol for basic Kademlia node communication."""

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
                create_ping(
                    self.node.node_id
                ),
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

        if message_type == PING:
            self._handle_ping(peer, addr)

        elif message_type == PONG:
            self._handle_pong(peer)

    def _handle_ping(self, peer, addr):
        """Handle a PING from another node."""

        print(
            f"Received PING from "
            f"{peer.host}:{peer.port}"
        )

        self.node.add_peer(peer)

        self.transport.sendto(
            create_pong(
                self.node.node_id
            ),
            addr,
        )

        print("PONG sent")

    def _handle_pong(self, peer):
        """Handle a PONG from another node."""

        print(
            f"Received PONG from "
            f"{peer.host}:{peer.port}"
        )

        self.node.add_peer(peer)

        print(
            "Bootstrap successful - peer added"
        )

        if (
            self.joined_future
            and not self.joined_future.done()
        ):
            self.joined_future.set_result(peer)

    def error_received(self, exc):
        print(f"DHT UDP error: {exc}")

    def connection_lost(self, exc):
        print("DHT UDP connection closed")


async def start_node(
    node: DHTNode,
    bootstrap_address=None,
):
    """Start a DHT node and optionally bootstrap to another node."""

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