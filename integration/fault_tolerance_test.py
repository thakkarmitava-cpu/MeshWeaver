import asyncio

from dht.node import DHTNode
from dht.network import (
    start_node,
    fault_tolerant_heartbeat,
)


async def main():
    # Node A will initially be healthy.
    node_a = DHTNode(
        "127.0.0.1",
        9701,
    )

    # Node B will monitor Node A.
    node_b = DHTNode(
        "127.0.0.1",
        9702,
    )

    # Start Node A.
    transport_a, protocol_a, _ = await start_node(
        node_a
    )

    # Start Node B and bootstrap to Node A.
    transport_b, protocol_b, joined_future = (
        await start_node(
            node_b,
            bootstrap_address=(
                "127.0.0.1",
                9701,
            ),
        )
    )

    try:
        # Wait for bootstrap to complete.
        await asyncio.wait_for(
            joined_future,
            timeout=3.0,
        )

        print()
        print(
            "Bootstrap completed successfully."
        )

        print(
            "Node B peer count:",
            node_b.peer_count(),
        )

        if node_b.peer_count() != 1:
            print(
                "Initial peer setup: FAIL"
            )
            return

        print(
            "Initial peer setup: PASS"
        )

        # First health check while Node A is alive.
        print()
        print(
            "Checking healthy peer..."
        )

        healthy_results = (
            await fault_tolerant_heartbeat(
                protocol_b,
                timeout=1.0,
                failure_threshold=2,
            )
        )

        print(
            "Healthy check results:",
            healthy_results,
        )

        healthy_pass = (
            bool(healthy_results)
            and all(
                healthy_results.values()
            )
        )

        print(
            "Healthy peer test:",
            "PASS"
            if healthy_pass
            else "FAIL",
        )

        # Shut down Node A intentionally.
        print()
        print(
            "Stopping Node A..."
        )

        transport_a.close()

        # Give the socket a moment to close.
        await asyncio.sleep(0.2)

        print(
            "Node A stopped."
        )

        # Run fault-tolerant health check.
        print()
        print(
            "Checking failed peer..."
        )

        failed_results = (
            await fault_tolerant_heartbeat(
                protocol_b,
                timeout=0.5,
                failure_threshold=2,
            )
        )

        print(
            "Failed check results:",
            failed_results,
        )

        # Node A should have been removed.
        remaining_peers = (
            node_b.peer_count()
        )

        print(
            "Node B remaining peers:",
            remaining_peers,
        )

        failure_detected = (
            bool(failed_results)
            and not any(
                failed_results.values()
            )
        )

        peer_removed = (
            remaining_peers == 0
        )

        print(
            "Failure detection:",
            "PASS"
            if failure_detected
            else "FAIL",
        )

        print(
            "Failed peer removal:",
            "PASS"
            if peer_removed
            else "FAIL",
        )

        overall_pass = (
            healthy_pass
            and failure_detected
            and peer_removed
        )

        print()
        print(
            "Fault tolerance test:",
            "PASS"
            if overall_pass
            else "FAIL",
        )

    finally:
        # Node A may already be closed.
        try:
            transport_a.close()
        except Exception:
            pass

        transport_b.close()


if __name__ == "__main__":
    asyncio.run(main())