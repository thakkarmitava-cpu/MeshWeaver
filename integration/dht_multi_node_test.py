import asyncio

from dht.node import DHTNode, Peer
from dht.network import start_node, find_nodes


async def main():
    ports = [9401, 9402, 9403, 9404, 9405]

    nodes = [
        DHTNode("127.0.0.1", port)
        for port in ports
    ]

    transports = []
    protocols = []
    join_futures = []

    try:
        # Start Node 1 first.
        transport, protocol, _ = await start_node(nodes[0])

        transports.append(transport)
        protocols.append(protocol)

        print()
        print("Bootstrap node started")

        # Start the remaining nodes and let each join
        # through the previous node.
        for index in range(1, len(nodes)):
            current_node = nodes[index]
            previous_node = nodes[index - 1]

            transport, protocol, joined_future = await start_node(
                current_node,
                bootstrap_address=previous_node.address,
            )

            transports.append(transport)
            protocols.append(protocol)
            join_futures.append(joined_future)

            print(
                f"Node {current_node.port} "
                f"joining through Node {previous_node.port}"
            )

            await asyncio.wait_for(
                joined_future,
                timeout=5,
            )

            print(
                f"Node {current_node.port} joined successfully"
            )

        await asyncio.sleep(1)

        print()
        print("Initial peer information:")

        for node in nodes:
            print(
                f"Node {node.port}: "
                f"{len(node.get_peers())} peer(s)"
            )

        # Ask each node to discover peers through the
        # bootstrap node.
        bootstrap = nodes[0]

        for index in range(1, len(nodes)):
            await find_nodes(
                protocols[index],
                Peer(
                    node_id=bootstrap.node_id,
                    host=bootstrap.host,
                    port=bootstrap.port,
                ),
                bootstrap.node_id,
            )

        await asyncio.sleep(1)

        print()
        print("Final peer information:")

        for node in nodes:
            print(
                f"Node {node.port}: "
                f"{len(node.get_peers())} peer(s)"
            )

        print()
        print("Multi-node DHT test completed successfully")

    finally:
        for transport in transports:
            transport.close()


if __name__ == "__main__":
    asyncio.run(main())