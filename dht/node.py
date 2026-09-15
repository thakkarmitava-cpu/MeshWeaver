import secrets
import time
from dataclasses import dataclass


NODE_ID_BITS = 160
NODE_ID_BYTES = NODE_ID_BITS // 8


def generate_node_id() -> int:
    """Generate a random 160-bit Kademlia node ID."""
    return int.from_bytes(
        secrets.token_bytes(NODE_ID_BYTES),
        byteorder="big",
    )


@dataclass(frozen=True)
class Peer:
    """Information required to contact another DHT node."""

    node_id: int
    host: str
    port: int


class DHTNode:
    """Basic MeshWeaver Kademlia node."""

    def __init__(
        self,
        host: str,
        port: int,
        node_id: int | None = None,
    ):
        self.host = host
        self.port = port

        self.node_id = (
            node_id
            if node_id is not None
            else generate_node_id()
        )

        self.peers: dict[int, Peer] = {}

        # Track the most recent time each peer was seen.
        self.last_seen: dict[int, float] = {}

    @property
    def address(self) -> tuple[str, int]:
        """Return this node's network address."""
        return self.host, self.port

    def add_peer(self, peer: Peer) -> None:
        """Add or update a known peer."""
        if peer.node_id == self.node_id:
            return

        self.peers[peer.node_id] = peer

        self.last_seen.setdefault(
            peer.node_id,
            time.time(),
        )

    def mark_peer_seen(self, node_id: int) -> None:
        """Update the last-seen time for a peer."""
        if node_id in self.peers:
            self.last_seen[node_id] = time.time()

    def get_last_seen(self, node_id: int) -> float | None:
        """Return the last-seen timestamp for a peer."""
        return self.last_seen.get(node_id)

    def remove_peer(self, node_id: int) -> None:
        """Remove a peer and its heartbeat information."""
        self.peers.pop(node_id, None)
        self.last_seen.pop(node_id, None)

    def get_peers(self) -> list[Peer]:
        """Return all known peers."""
        return list(self.peers.values())

    def has_peer(self, node_id: int) -> bool:
        """Check whether a peer is currently known."""
        return node_id in self.peers

    def peer_count(self) -> int:
        """Return the number of currently known peers."""
        return len(self.peers)

    def __repr__(self) -> str:
        return (
            f"DHTNode("
            f"id={self.node_id:040x}, "
            f"address={self.host}:{self.port}"
            f")"
        )