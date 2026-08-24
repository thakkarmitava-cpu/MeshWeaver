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
        print("STARTING DYNAMIC PEER DISCOVERY")
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

        # Allow UDP responses to arrive.
        await asyncio.sleep(2)

        # -------------------------------------------------
        # 4. Additional discovery from bootstrap node
        # -------------------------------------------------

        for index in range(1, len(nodes)):

            current_node = nodes[index]

            peer = Peer(
                node_id=current_node.node_id,
                host=current_node.host,
                port=current_node.port,
            )

            await find_nodes(
                protocols[0],
                peer,
                current_node.node_id,
            )

        # Allow responses to arrive.
        await asyncio.sleep(2)

        # -------------------------------------------------
        # 5. Display discovery results
        # -------------------------------------------------

        print()
        print("-" * 70)
        print("DISCOVERY RESULTS")
        print("-" * 70)

        known_node_ids = {
            node.node_id
            for node in nodes
        }

        total_peer_relationships = 0
        isolated_nodes = []
        invalid_peers = []

        for node in nodes:

            peers = node.get_peers()

            total_peer_relationships += len(peers)

            print(
                f"Node {node.port}: "
                f"{len(peers)} peer(s)"
            )

            if len(peers) == 0:
                isolated_nodes.append(node)

            for peer in peers:

                print(
                    f"    -> "
                    f"{peer.host}:{peer.port}"
                )

                if peer.node_id not in known_node_ids:
                    invalid_peers.append(peer)

        # -------------------------------------------------
        # 6. Calculate audit results
        # -------------------------------------------------

        total_nodes = len(nodes)

        nodes_started = len(transports)

        nodes_with_peers = sum(
            1
            for node in nodes
            if len(node.get_peers()) > 0
        )

        # -------------------------------------------------
        # 7. Network audit verification
        # -------------------------------------------------

        audit_passed = (
            total_nodes == 10
            and nodes_started == 10
            and nodes_with_peers == 10
            and len(isolated_nodes) == 0
            and total_peer_relationships > 10
            and len(invalid_peers) == 0
        )

        print()
        print("=" * 70)
        print("MESHWEAVER NETWORK AUDIT SUMMARY")
        print("=" * 70)

        print(
            f"Nodes tested        : {total_nodes}"
        )

        print(
            f"Nodes started       : {nodes_started}"
        )

        print(
            f"Nodes with peers    : {nodes_with_peers}"
        )

        print(
            f"Peer relationships  : "
            f"{total_peer_relationships}"
        )

        print(
            f"Invalid peers       : "
            f"{len(invalid_peers)}"
        )

        print(
            f"Isolated nodes      : "
            f"{len(isolated_nodes)}"
        )

        if audit_passed:

            print(
                "Network status      : PASS"
            )

        else:

            print(
                "Network status      : FAIL"
            )

        print("=" * 70)

        # -------------------------------------------------
        # 8. Final result
        # -------------------------------------------------

        if audit_passed:

            print(
                "10-node network audit "
                "completed successfully."
            )

        else:

            print(
                "10-node network audit failed."
            )

            if isolated_nodes:
                print()
                print("Isolated nodes:")

                for node in isolated_nodes:
                    print(
                        f"    {node.host}:{node.port}"
                    )

    finally:

        for transport in transports:
            transport.close()

        await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())