import asyncio

from dht.node import DHTNode
from dht.network import (
    start_node,
    find_nodes,
)


async def main():

    # Node A - requester
    node_a = DHTNode(
        "127.0.0.1",
        9301,
    )

    # Node B - knows Node C
    node_b = DHTNode(
        "127.0.0.1",
        9302,
    )

    # Node C - peer that Node B already knows
    node_c = DHTNode(
        "127.0.0.1",
        9303,
    )

    # Start all nodes
    transport_a, protocol_a, _ = await start_node(
        node_a
    )

    transport_b, protocol_b, _ = await start_node(
        node_b
    )

    transport_c, protocol_c, _ = await start_node(
        node_c
    )

    try:
        # Make Node B know Node C.
        from dht.node import Peer

        node_b.add_peer(
            Peer(
                node_id=node_c.node_id,
                host=node_c.host,
                port=node_c.port,
            )
        )

        print()
        print(
            "Node B initially knows:",
            len(node_b.get_peers()),
            "peer(s)",
        )

        # Node A asks Node B for known nodes.
        await find_nodes(
            protocol_a,
            Peer(
                node_id=node_b.node_id,
                host=node_b.host,
                port=node_b.port,
            ),
            node_c.node_id,
        )

        # Give UDP time to deliver response.
        await asyncio.sleep(1)

        print()
        print(
            "Node A discovered peers:",
            len(node_a.get_peers()),
        )

        discovered = (
            node_c.node_id in node_a.peers
        )

        print(
            "Node A discovered Node C:",
            discovered,
        )

    finally:
        transport_a.close()
        transport_b.close()
        transport_c.close()


if __name__ == "__main__":
    asyncio.run(main())