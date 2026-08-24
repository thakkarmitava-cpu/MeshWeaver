import asyncio

from dht.node import DHTNode, Peer
from dht.network import start_node, find_nodes


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
    protocols = []

    try:
        print("Starting 10-node DHT network...")
        print()

        # -------------------------------------------------
        # Start bootstrap node
        # -------------------------------------------------

        bootstrap_node = nodes[0]

        transport, protocol, _ = await start_node(
            bootstrap_node
        )

        transports.append(transport)
        protocols.append(protocol)

        print(
            f"Bootstrap node started: "
            f"{bootstrap_node.host}:{bootstrap_node.port}"
        )

        # -------------------------------------------------
        # Join remaining nodes
        # -------------------------------------------------

        for index in range(1, len(nodes)):

            current_node = nodes[index]
            previous_node = nodes[index - 1]

            transport, protocol, joined_future = await start_node(
                current_node,
                bootstrap_address=previous_node.address,
            )

            transports.append(transport)
            protocols.append(protocol)

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

        # Give the network time to settle.
        await asyncio.sleep(1)

        # -------------------------------------------------
        # Dynamic peer discovery
        # -------------------------------------------------

        print()
        print("Starting dynamic peer discovery...")
        print()

        for index in range(1, len(nodes)):

            current_protocol = protocols[index]

            # Ask the previous node for its known peers.
            previous_node = nodes[index - 1]

            peer = Peer(
                node_id=previous_node.node_id,
                host=previous_node.host,
                port=previous_node.port,
            )

            await find_nodes(
                current_protocol,
                peer,
                nodes[0].node_id,
            )

        # Allow UDP responses to arrive.
        await asyncio.sleep(2)

        # -------------------------------------------------
        # Display discovered peers
        # -------------------------------------------------

        print()
        print("Dynamic peer discovery results")
        print("-" * 60)

        for node in nodes:

            peers = node.get_peers()

            print(
                f"Node {node.port}: "
                f"{len(peers)} discovered peer(s)"
            )

            for peer in peers:

                print(
                    f"    -> "
                    f"{peer.host}:{peer.port}"
                )

        print("-" * 60)

        print()
        print(
            "10-node dynamic peer discovery completed"
        )

    finally:

        for transport in transports:
            transport.close()

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())