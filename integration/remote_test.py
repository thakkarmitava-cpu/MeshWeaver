import asyncio

from serialization.serializer import (
    serialize_task,
    deserialize_task,
    execute_task,
    serialize_result,
    deserialize_result,
)


HOST = "127.0.0.1"
PORT = 8888


def add(a, b):
    return a + b
def multiply(a, b):
    return a * b


async def handle_client(reader, writer):
    print("Server: Client connected")

    # Receive task size
    size_data = await reader.readexactly(4)
    task_size = int.from_bytes(size_data, byteorder="big")

    # Receive serialized task
    task_data = await reader.readexactly(task_size)

    # Execute remote task
    result = execute_task(task_data)

    # Serialize result
    result_data = serialize_result(result)

    # Send result size + result
    writer.write(len(result_data).to_bytes(4, byteorder="big"))
    writer.write(result_data)

    await writer.drain()

    print("Server: Task executed")
    print("Server: Result =", result)

    writer.close()
    await writer.wait_closed()


async def run_server():
    server = await asyncio.start_server(
        handle_client,
        HOST,
        PORT,
    )

    print(f"Server running on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()


async def run_client():
    await asyncio.sleep(1)

    reader, writer = await asyncio.open_connection(
        HOST,
        PORT,
    )

    print("Client: Connected to server")

    # Create and serialize task
    task_data = serialize_task(multiply, 10, 20)

    # Send task size + task
    writer.write(len(task_data).to_bytes(4, byteorder="big"))
    writer.write(task_data)

    await writer.drain()

    print("Client: Task sent")

    # Receive result size
    size_data = await reader.readexactly(4)
    result_size = int.from_bytes(size_data, byteorder="big")

    # Receive result
    result_data = await reader.readexactly(result_size)

    # Deserialize result
    result = deserialize_result(result_data)

    print("Client: Result received =", result)

    writer.close()
    await writer.wait_closed()


async def main():
    server_task = asyncio.create_task(run_server())

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