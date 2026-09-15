import asyncio

from dht.node import DHTNode
from dht.network import (
    start_node,
    heartbeat_once,
)


async def main():
    # Node A - heartbeat target
    node_a = DHTNode(
        "127.0.0.1",
        9601,
    )

    # Node B - heartbeat requester
    node_b = DHTNode(
        "127.0.0.1",
        9602,
    )

    # Start Node A first.
    transport_a, protocol_a, _ = await start_node(
        node_a
    )

    # Start Node B and bootstrap to Node A.
    transport_b, protocol_b, joined_future = (
        await start_node(
            node_b,
            bootstrap_address=(
                "127.0.0.1",
                9601,
            ),
        )
    )

    try:
        # Wait for Node B to successfully join.
        await asyncio.wait_for(
            joined_future,
            timeout=3.0,
        )

        print()
        print(
            "Bootstrap completed successfully."
        )

        print(
            "Node B known peers:",
            len(node_b.get_peers()),
        )

        # Perform one heartbeat round.
        print()
        print("Starting heartbeat test...")

        results = await heartbeat_once(
            protocol_b,
            timeout=2.0,
        )

        print()
        print(
            "Heartbeat results:",
            results,
        )

        # Verify that every known peer responded.
        heartbeat_success = (
            bool(results)
            and all(results.values())
        )

        print(
            "Heartbeat test:",
            "PASS"
            if heartbeat_success
            else "FAIL",
        )

    finally:
        transport_a.close()
        transport_b.close()


if __name__ == "__main__":
    asyncio.run(main())