import asyncio
from pathlib import Path

from dht.node import DHTNode
from dht.network import (
    start_node,
    heartbeat_once,
)

from security.signatures import (
    create_signer,
    verify_signature,
)

from networking.tls import (
    open_tls_connection,
    start_tls_server,
)


HOST = "127.0.0.1"

DHT_PORT_A = 9911
DHT_PORT_B = 9912

TLS_PORT = 9913

CERTIFICATE_FILE = Path(
    "certs/server.crt"
)

PRIVATE_KEY_FILE = Path(
    "certs/server.key"
)


def test_signatures() -> bool:
    """Test cryptographic signing and verification."""

    print()
    print(
        "[1/5] Testing cryptographic signatures..."
    )

    signer = create_signer()

    message = (
        b"MeshWeaver final integration message"
    )

    signature = signer.sign(
        message
    )

    valid = verify_signature(
        signer.get_public_key_bytes(),
        message,
        signature,
    )

    modified = verify_signature(
        signer.get_public_key_bytes(),
        b"modified message",
        signature,
    )

    success = (
        valid
        and not modified
    )

    print(
        "Signature test:",
        "PASS"
        if success
        else "FAIL",
    )

    return success


async def test_dht_and_heartbeat() -> bool:
    """Test DHT bootstrap and heartbeat."""

    print()
    print(
        "[2/5] Testing DHT and heartbeat..."
    )

    node_a = DHTNode(
        HOST,
        DHT_PORT_A,
    )

    node_b = DHTNode(
        HOST,
        DHT_PORT_B,
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
                HOST,
                DHT_PORT_A,
            ),
        )
    )

    try:
        await asyncio.wait_for(
            joined_future,
            timeout=3.0,
        )

        bootstrap_success = (
            node_b.peer_count() == 1
        )

        heartbeat_results = (
            await heartbeat_once(
                protocol_b,
                timeout=1.0,
            )
        )

        heartbeat_success = (
            bool(heartbeat_results)
            and all(
                heartbeat_results.values()
            )
        )

        success = (
            bootstrap_success
            and heartbeat_success
        )

        print(
            "DHT bootstrap:",
            "PASS"
            if bootstrap_success
            else "FAIL",
        )

        print(
            "Heartbeat:",
            "PASS"
            if heartbeat_success
            else "FAIL",
        )

        return success

    finally:
        transport_a.close()
        transport_b.close()


async def test_tls() -> bool:
    """Test TLS client/server communication."""

    print()
    print(
        "[3/5] Testing TLS communication..."
    )

    if not CERTIFICATE_FILE.exists():
        print(
            "TLS certificate missing."
        )

        return False

    if not PRIVATE_KEY_FILE.exists():
        print(
            "TLS private key missing."
        )

        return False

    received_message = (
        "MeshWeaver final TLS test"
    )

    async def handle_client(
        reader,
        writer,
    ):
        try:
            data = await reader.read(
                4096
            )

            writer.write(data)

            await writer.drain()

        finally:
            writer.close()

            await writer.wait_closed()

    server = await start_tls_server(
        HOST,
        TLS_PORT,
        handle_client,
        str(CERTIFICATE_FILE),
        str(PRIVATE_KEY_FILE),
    )

    try:
        reader, writer = (
            await open_tls_connection(
                HOST,
                TLS_PORT,
            )
        )

        writer.write(
            received_message.encode(
                "utf-8"
            )
        )

        await writer.drain()

        response = await reader.read(
            4096
        )

        response_text = (
            response.decode("utf-8")
        )

        writer.close()

        await writer.wait_closed()

        success = (
            response_text
            == received_message
        )

        print(
            "TLS communication:",
            "PASS"
            if success
            else "FAIL",
        )

        return success

    finally:
        server.close()

        await server.wait_closed()


def test_dashboard_import() -> bool:
    """Verify that the Rich dashboard layer loads."""

    print()
    print(
        "[4/5] Testing Rich dashboard..."
    )

    try:
        from dashboard.monitor import (
            MeshWeaverDashboard,
        )

        success = (
            MeshWeaverDashboard
            is not None
        )

    except ImportError:
        success = False

    print(
        "Dashboard:",
        "PASS"
        if success
        else "FAIL",
    )

    return success


def test_project_structure() -> bool:
    """Verify important project components exist."""

    print()
    print(
        "[5/5] Checking project structure..."
    )

    required_paths = [
        Path("dht/node.py"),
        Path("dht/network.py"),
        Path("dht/protocol.py"),
        Path("dht/routing.py"),
        Path("networking/client.py"),
        Path("networking/server.py"),
        Path("networking/udp.py"),
        Path("networking/tls.py"),
        Path("serialization/serializer.py"),
        Path("security/signatures.py"),
        Path("dashboard/monitor.py"),
    ]

    missing = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    success = not missing

    if missing:
        print(
            "Missing files:"
        )

        for path in missing:
            print(
                f"  - {path}"
            )

    print(
        "Project structure:",
        "PASS"
        if success
        else "FAIL",
    )

    return success


async def main():
    print()
    print(
        "=" * 60
    )
    print(
        "MESHWEAVER FINAL INTEGRATION TEST"
    )
    print(
        "=" * 60
    )

    results = []

    results.append(
        test_signatures()
    )

    results.append(
        await test_dht_and_heartbeat()
    )

    results.append(
        await test_tls()
    )

    results.append(
        test_dashboard_import()
    )

    results.append(
        test_project_structure()
    )

    print()
    print(
        "=" * 60
    )

    passed = sum(
        1
        for result in results
        if result
    )

    total = len(results)

    print(
        f"FINAL RESULT: "
        f"{passed}/{total} TEST GROUPS PASSED"
    )

    if all(results):
        print(
            "MESHWEAVER FINAL STATUS: PASS"
        )
    else:
        print(
            "MESHWEAVER FINAL STATUS: FAIL"
        )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print()
        print(
            "Final integration test interrupted."
        )