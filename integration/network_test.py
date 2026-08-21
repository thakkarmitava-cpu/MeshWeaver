import asyncio

from networking.server import AsyncServer
from networking.client import AsyncClient
from networking.protocol import receive_message, send_message


HOST = "127.0.0.1"
PORT = 9000


async def handle_client(reader, writer):
    """Handle a simple test message."""

    data = await receive_message(reader)

    print("Server received:", data.decode())

    response = b"Hello from MeshWeaver server"

    await send_message(writer, response)


async def run_server():
    """Start the test server."""

    server = AsyncServer(
        HOST,
        PORT,
        handle_client,
    )

    await server.start()

    await server.serve_forever()


async def run_client():
    """Start the test client."""

    await asyncio.sleep(1)

    client = AsyncClient(
        HOST,
        PORT,
    )

    await client.connect()

    await client.send(
        b"Hello from MeshWeaver client"
    )

    response = await client.receive()

    print(
        "Client received:",
        response.decode()
    )

    await client.close()


async def main():

    server_task = asyncio.create_task(
        run_server()
    )

    try:
        await run_client()

    finally:
        server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())