import asyncio

from dht.node import DHTNode
from dht.network import start_node


async def main():

    # Existing node
    node_b = DHTNode(
        "127.0.0.1",
        9201,
    )

    # New node
    node_a = DHTNode(
        "127.0.0.1",
        9202,
    )

    # Start existing node
    transport_b, _, _ = await start_node(
        node_b
    )

    print()

    # Start new node and bootstrap to node B
    transport_a, _, joined_future = await start_node(
        node_a,
        bootstrap_address=node_b.address,
    )

    try:
        peer = await asyncio.wait_for(
            joined_future,
            timeout=5,
        )

        print()
        print("Bootstrap completed successfully")
        print(
            f"New node discovered peer: "
            f"{peer.host}:{peer.port}"
        )

        print()
        print(
            "New node peer count:",
            len(node_a.get_peers()),
        )

        print(
            "New node joined mesh:",
            node_b.node_id in node_a.peers,
        )

    finally:
        transport_a.close()
        transport_b.close()


if __name__ == "__main__":
    asyncio.run(main())