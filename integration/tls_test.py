import asyncio
from pathlib import Path

from networking.tls import (
    open_tls_connection,
    start_tls_server,
)


HOST = "127.0.0.1"
PORT = 9801

CERTIFICATE_FILE = Path(
    "certs/server.crt"
)

PRIVATE_KEY_FILE = Path(
    "certs/server.key"
)


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    """
    Handle one secure TLS client connection.
    """

    try:
        data = await reader.read(4096)

        message = data.decode(
            "utf-8"
        )

        print(
            f"TLS Server received: {message}"
        )

        response = (
            "TLS_ACK:" + message
        )

        writer.write(
            response.encode("utf-8")
        )

        await writer.drain()

        print(
            "TLS Server sent response"
        )

    finally:
        writer.close()

        await writer.wait_closed()


async def main():
    if not CERTIFICATE_FILE.exists():
        print(
            "TLS certificate not found."
        )
        print()
        print(
            "Run this command first:"
        )
        print(
            "python -m "
            "integration.generate_tls_cert"
        )
        return

    if not PRIVATE_KEY_FILE.exists():
        print(
            "TLS private key not found."
        )
        print()
        print(
            "Run this command first:"
        )
        print(
            "python -m "
            "integration.generate_tls_cert"
        )
        return

    server = await start_tls_server(
        HOST,
        PORT,
        handle_client,
        str(CERTIFICATE_FILE),
        str(PRIVATE_KEY_FILE),
    )

    print(
        f"TLS Server running on "
        f"{HOST}:{PORT}"
    )

    try:
        reader, writer = (
            await open_tls_connection(
                HOST,
                PORT,
            )
        )

        print(
            "TLS Client connected securely"
        )

        message = (
            "MeshWeaver secure message"
        )

        writer.write(
            message.encode("utf-8")
        )

        await writer.drain()

        print(
            "TLS Client sent message"
        )

        response = await reader.read(
            4096
        )

        response_text = response.decode(
            "utf-8"
        )

        print(
            f"TLS Client received: "
            f"{response_text}"
        )

        if response_text == (
            "TLS_ACK:" + message
        ):
            print()
            print(
                "TLS communication test: PASS"
            )
        else:
            print()
            print(
                "TLS communication test: FAIL"
            )

        writer.close()

        await writer.wait_closed()

    finally:
        server.close()

        await server.wait_closed()

        print(
            "TLS Server closed"
        )


if __name__ == "__main__":
    asyncio.run(main())