import asyncio

from networking.server import AsyncServer
from networking.client import AsyncClient
from networking.protocol import receive_message, send_message

from serialization.serializer import (
    serialize_task,
    execute_task,
    serialize_result,
    deserialize_result,
)


HOST = "127.0.0.1"
PORT = 8888


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


async def handle_client(reader, writer):
    """Receive and execute a serialized task."""

    print("Server: Client connected")

    # Receive serialized task
    task_data = await receive_message(reader)

    print("Server: Task received")

    # Execute task
    result = execute_task(task_data)

    print("Server: Task executed")
    print("Server: Result =", result)

    # Serialize result
    result_data = serialize_result(result)

    # Send result back
    await send_message(writer, result_data)

    print("Server: Result sent")


async def run_server():
    """Start MeshWeaver server."""

    server = AsyncServer(
        HOST,
        PORT,
        handle_client,
    )

    await server.start()

    print(f"Server running on {HOST}:{PORT}")

    await server.serve_forever()


async def run_client():
    """Connect to server and send a serialized task."""

    await asyncio.sleep(1)

    client = AsyncClient(
        HOST,
        PORT,
    )

    await client.connect()

    # Create and serialize task
    task_data = serialize_task(
        multiply,
        10,
        20,
    )

    print("Client: Task serialized")
    print("Client: Sending task")

    # Send task using YOUR networking layer
    await client.send(task_data)

    # Receive result
    result_data = await client.receive()

    print("Client: Result received")

    # Deserialize result
    result = deserialize_result(result_data)

    print("Client: Final result =", result)

    await client.close()


async def main():

    # Start server in background
    server_task = asyncio.create_task(
        run_server()
    )

    try:
        # Run client
        await run_client()

    finally:
        # Stop server
        server_task.cancel()

        try:
            await server_task

        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())