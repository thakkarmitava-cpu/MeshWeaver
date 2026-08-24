import asyncio
import psutil
import time
import json


from serialization.serializer import (
    serialize_task,
    deserialize_task,
    execute_task,
    serialize_result,
    deserialize_result,
)


HOST = "127.0.0.1"
PORT = 8888
GOSSIP_PORT_A = 9999
GOSSIP_PORT_B = 10000
GOSSIP_INTERVAL = 5


def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "timestamp": time.time(),
    }


class GossipProtocol(asyncio.DatagramProtocol):

    def __init__(self, node_name):
        self.node_name = node_name

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())

            print(
                f"Gossip [{self.node_name}] received from {addr}: "
                f"CPU={message['cpu']}% "
                f"RAM={message['ram']}%"
            )

        except Exception as e:
            print("Gossip receive error:", e)


async def start_gossip_node(node_name, port):
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        lambda: GossipProtocol(node_name),
        local_addr=("127.0.0.1", port),
    )

    print(f"Gossip node {node_name} running on UDP {port}")

    return transport


async def gossip_sender(node_name, transport, neighbor_port):
    while True:
        metrics = get_system_metrics()

        message = {
            "node": node_name,
            "cpu": metrics["cpu"],
            "ram": metrics["ram"],
            "timestamp": metrics["timestamp"],
        }

        data = json.dumps(message).encode()

        transport.sendto(
            data,
            ("127.0.0.1", neighbor_port),
        )

        print(
            f"Gossip [{node_name}] sent: "
            f"CPU={metrics['cpu']}% "
            f"RAM={metrics['ram']}%"
        )

        await asyncio.sleep(GOSSIP_INTERVAL)

# def get_system_metrics():
#     return {
#         "cpu": psutil.cpu_percent(interval=None),
#         "ram": psutil.virtual_memory().percent,
#         "timestamp": time.time(),
#     }
# print("System metrics:", get_system_metrics())


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

    gossip_a = await start_gossip_node("Node-A", GOSSIP_PORT_A)
    gossip_b = await start_gossip_node("Node-B", GOSSIP_PORT_B)

    gossip_a_task = asyncio.create_task(
        gossip_sender("Node-A", gossip_a, GOSSIP_PORT_B)
    )

    gossip_b_task = asyncio.create_task(
        gossip_sender("Node-B", gossip_b, GOSSIP_PORT_A)
    )

    try:
        await run_client()
        await asyncio.sleep(15)

    finally:
        gossip_a_task.cancel()
        gossip_b_task.cancel()

        gossip_a.close()
        gossip_b.close()

        server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            pass
if __name__ == "__main__":
    asyncio.run(main())        