from dataclasses import dataclass

from dht.node import Peer, NODE_ID_BITS


def xor_distance(node_id_a: int, node_id_b: int) -> int:
    """Calculate Kademlia XOR distance between two node IDs."""
    return node_id_a ^ node_id_b


def bucket_index(local_id: int, remote_id: int) -> int:
    """
    Determine the Kademlia routing bucket for a remote node.

    Bucket 0 represents the closest possible distance.
    Bucket 159 represents the largest distance for 160-bit IDs.
    """
    distance = xor_distance(local_id, remote_id)

    if distance == 0:
        return 0

    return distance.bit_length() - 1


@dataclass
class RoutingBucket:
    """A lightweight routing bucket."""

    index: int

    def __post_init__(self):
        self.peers: dict[int, Peer] = {}

    def add_peer(self, peer: Peer) -> None:
        """Add a peer to this bucket."""
        self.peers[peer.node_id] = peer

    def remove_peer(self, node_id: int) -> None:
        """Remove a peer from this bucket."""
        self.peers.pop(node_id, None)

    def get_peers(self) -> list[Peer]:
        """Return peers stored in this bucket."""
        return list(self.peers.values())


class RoutingTable:
    """Lightweight Kademlia routing table."""

    def __init__(self, local_node_id: int):
        self.local_node_id = local_node_id

        self.buckets = [
            RoutingBucket(index)
            for index in range(NODE_ID_BITS)
        ]

    def add_peer(self, peer: Peer) -> None:
        """Add a peer to the appropriate routing bucket."""

        if peer.node_id == self.local_node_id:
            return

        index = bucket_index(
            self.local_node_id,
            peer.node_id,
        )

        self.buckets[index].add_peer(peer)

    def remove_peer(self, peer: Peer) -> None:
        """Remove a peer from its routing bucket."""

        index = bucket_index(
            self.local_node_id,
            peer.node_id,
        )

        self.buckets[index].remove_peer(
            peer.node_id
        )

    def get_bucket(self, index: int) -> RoutingBucket:
        """Return a routing bucket."""
        return self.buckets[index]

    def get_all_peers(self) -> list[Peer]:
        """Return all peers stored in the routing table."""

        peers = []

        for bucket in self.buckets:
            peers.extend(bucket.get_peers())

        return peers

    def __len__(self):
        return sum(
            len(bucket.peers)
            for bucket in self.buckets
        )