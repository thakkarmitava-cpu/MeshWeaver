from dht.node import DHTNode
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


def main():

    node_a = DHTNode(
        "127.0.0.1",
        9101,
    )

    node_b = DHTNode(
        "127.0.0.1",
        9102,
    )

    print("Testing PING")

    ping_data = create_ping(
        node_a.node_id
    )

    ping_message = decode_message(
        ping_data
    )

    print(ping_message)

    assert ping_message["type"] == PING

    print("PING test passed")

    print()

    print("Testing PONG")

    pong_data = create_pong(
        node_b.node_id
    )

    pong_message = decode_message(
        pong_data
    )

    print(pong_message)

    assert pong_message["type"] == PONG

    print("PONG test passed")

    print()

    print("Testing FIND_NODE")

    find_data = create_find_node(
        node_a.node_id,
        node_b.node_id,
    )

    find_message = decode_message(
        find_data
    )

    print(find_message)

    assert find_message["type"] == FIND_NODE

    print("FIND_NODE test passed")

    print()

    print("Testing NODES")

    peers = [
        {
            "node_id": f"{node_b.node_id:040x}",
            "host": node_b.host,
            "port": node_b.port,
        }
    ]

    nodes_data = create_nodes_response(
        node_a.node_id,
        peers,
    )

    nodes_message = decode_message(
        nodes_data
    )

    print(nodes_message)

    assert nodes_message["type"] == NODES
    assert len(nodes_message["payload"]["peers"]) == 1

    print("NODES test passed")

    print()
    print("All DHT protocol tests passed!")


if __name__ == "__main__":
    main()