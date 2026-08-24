from dht.node import DHTNode, Peer
from dht.routing import (
    xor_distance,
    bucket_index,
    RoutingTable,
)


def main():

    node_a = DHTNode(
        "127.0.0.1",
        9101,
    )

    node_b = DHTNode(
        "127.0.0.1",
        9102,
    )

    distance = xor_distance(
        node_a.node_id,
        node_b.node_id,
    )

    bucket = bucket_index(
        node_a.node_id,
        node_b.node_id,
    )

    print("Node A ID:")
    print(f"{node_a.node_id:040x}")

    print()

    print("Node B ID:")
    print(f"{node_b.node_id:040x}")

    print()

    print("XOR distance:")
    print(distance)

    print()

    print("Bucket index:")
    print(bucket)

    peer_b = Peer(
        node_id=node_b.node_id,
        host=node_b.host,
        port=node_b.port,
    )

    routing_table = RoutingTable(
        node_a.node_id
    )

    routing_table.add_peer(peer_b)

    print()

    print(
        "Routing table peer count:",
        len(routing_table),
    )

    print(
        "Node B stored in bucket:",
        bucket,
    )


if __name__ == "__main__":
    main()