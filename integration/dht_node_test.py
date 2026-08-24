from dht.node import DHTNode, Peer


def main():
    node_a = DHTNode(
        "127.0.0.1",
        9101,
    )

    node_b = DHTNode(
        "127.0.0.1",
        9102,
    )

    peer_b = Peer(
        node_id=node_b.node_id,
        host=node_b.host,
        port=node_b.port,
    )

    node_a.add_peer(peer_b)

    print("Node A:")
    print(node_a)

    print()

    print("Node B:")
    print(node_b)

    print()

    print("Node A known peers:")

    for peer in node_a.get_peers():
        print(
            f"  {peer.node_id:040x} "
            f"-> {peer.host}:{peer.port}"
        )

    print()

    print(
        "Node A discovered Node B:",
        node_b.node_id in node_a.peers,
    )


if __name__ == "__main__":
    main()