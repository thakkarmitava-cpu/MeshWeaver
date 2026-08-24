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
        print("=" * 70)
        print("MESHWEAVER MID-PROJECT NETWORK AUDIT")
        print("=" * 70)
        print()

        # -------------------------------------------------
        # 1. Start the bootstrap node
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
        # 2. Start remaining nodes and join the network
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

        # Allow the network to settle.
        await asyncio.sleep(1)

        # -------------------------------------------------
        # 3. Dynamic peer discovery
        # -------------------------------------------------

        print()
        print("-" * 70)
        print("Starting dynamic peer discovery")
        print("-" * 70)

        for index in range(1, len(nodes)):

            current_protocol = protocols[index]
            previous_node = nodes[index - 1]

            peer = Peer(
                node_id=previous_node.node_id,
                host=previous_node.host,
                port=previous_node.port,
            )

            await find_nodes(
                current_protocol,
                peer,
                bootstrap_node.node_id,
            )

        # Give UDP responses time to arrive.
        await asyncio.sleep(2)

        # -------------------------------------------------
        # 4. Display results
        # -------------------------------------------------

        print()
        print("-" * 70)
        print("PEER DISCOVERY RESULTS")
        print("-" * 70)

        for node in nodes:

            print(
                f"Node {node.port}: "
                f"{len(node.get_peers())} peer(s)"
            )

            for peer in node.get_peers():

                print(
                    f"    -> "
                    f"{peer.host}:{peer.port}"
                )

        # -------------------------------------------------
        # 5. Automatic audit verification
        # -------------------------------------------------

        print()
        print("-" * 70)
        print("NETWORK AUDIT VERIFICATION")
        print("-" * 70)

        total_nodes = len(nodes)

        print(
            f"Expected nodes : {total_nodes}"
        )

        print(
            f"Started nodes  : {len(transports)}"
        )

        # Check that every node has at least one peer.
        isolated_nodes = [
            node
            for node in nodes
            if len(node.get_peers()) == 0
        ]

        discovered_nodes = [
            node
            for node in nodes
            if len(node.get_peers()) > 0
        ]

        print(
            f"Nodes with peers: "
            f"{len(discovered_nodes)}"
        )

        print(
            f"Isolated nodes : "
            f"{len(isolated_nodes)}"
        )

        if isolated_nodes:

            print()
            print("Isolated node addresses:")

            for node in isolated_nodes:

                print(
                    f"    {node.host}:{node.port}"
                )

        # -------------------------------------------------
        # 6. Final PASS / FAIL
        # -------------------------------------------------

        audit_passed = (
            len(nodes) == 10
            and len(transports) == 10
            and len(isolated_nodes) == 0
        )

        print()
        print("=" * 70)

        if audit_passed:

            print(
                "NETWORK AUDIT: PASS"
            )

            print(
                "All 10 nodes started and "
                "discovered at least one peer."
            )

        else:

            print(
                "NETWORK AUDIT: FAIL"
            )

            print(
                "One or more network requirements "
                "were not satisfied."
            )

        print("=" * 70)

    finally:

        for transport in transports:
            transport.close()

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())