import asyncio

from dht.node import DHTNode
from dht.network import start_node


HOST = "127.0.0.1"

PORTS = [
    9501,
    9502,
    9503,
    9504,
    9505,
    9506,
    9507,
    9508,
    9509,
    9510,
]


async def main():

    nodes = [
        DHTNode(HOST, port)
        for port in PORTS
    ]

    transports = []

    try:
        print("Starting 10-node DHT network...")
        print()

        # Start the first node as the bootstrap node.
        bootstrap_node = nodes[0]

        transport, _, _ = await start_node(
            bootstrap_node
        )

        transports.append(transport)

        print(
            f"Bootstrap node started: "
            f"{bootstrap_node.host}:{bootstrap_node.port}"
        )

        # Start every remaining node and join it
        # through the previously started node.
        for index in range(1, len(nodes)):

            current_node = nodes[index]
            previous_node = nodes[index - 1]

            transport, _, joined_future = await start_node(
                current_node,
                bootstrap_address=previous_node.address,
            )

            transports.append(transport)

            print(
                f"Node {current_node.port} "
                f"joining through "
                f"Node {previous_node.port}"
            )

            await asyncio.wait_for(
                joined_future,
                timeout=5,
            )

            print(
                f"Node {current_node.port} "
                f"joined successfully"
            )

        await asyncio.sleep(1)

        print()
        print("10-node bootstrap completed")
        print()

        print("Current peer information")
        print("-" * 50)

        for node in nodes:
            print(
                f"Node {node.port}: "
                f"{len(node.get_peers())} peer(s)"
            )

        print("-" * 50)

    finally:

        for transport in transports:
            transport.close()

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())