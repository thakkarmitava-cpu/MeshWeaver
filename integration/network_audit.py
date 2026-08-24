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
        print("Starting 10 DHT nodes...")
        print()

        for node in nodes:

            transport, _, _ = await start_node(node)

            transports.append(transport)

            print(
                f"Node started: "
                f"{node.host}:{node.port}"
            )

        print()
        print("All 10 DHT nodes started successfully")

        print()
        print("Node Summary")

        print("-" * 60)

        for index, node in enumerate(nodes, start=1):

            print(
                f"Node {index:02d} | "
                f"Address: {node.host}:{node.port} | "
                f"ID: {node.node_id:040x}"
            )

        print("-" * 60)

        await asyncio.sleep(1)

    finally:

        for transport in transports:
            transport.close()

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())