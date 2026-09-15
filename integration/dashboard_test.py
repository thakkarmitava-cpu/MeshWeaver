import asyncio

from dht.node import DHTNode
from dht.network import start_node

from dashboard.monitor import run_dashboard


async def main():
    node_a = DHTNode(
        "127.0.0.1",
        9901,
    )

    node_b = DHTNode(
        "127.0.0.1",
        9902,
    )

    transport_a, protocol_a, _ = (
        await start_node(
            node_a
        )
    )

    transport_b, protocol_b, joined_future = (
        await start_node(
            node_b,
            bootstrap_address=(
                "127.0.0.1",
                9901,
            ),
        )
    )

    try:
        await asyncio.wait_for(
            joined_future,
            timeout=3.0,
        )

        print()
        print(
            "Nodes successfully connected."
        )

        print(
            "Starting MeshWeaver dashboard..."
        )

        await run_dashboard(
            node_b,
            protocol_b,
            interval=2.0,
            heartbeat_timeout=1.0,
        )

    except asyncio.CancelledError:
        pass

    finally:
        transport_a.close()
        transport_b.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print(
            "Dashboard stopped."
        )