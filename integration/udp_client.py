import asyncio

from networking.udp import UDPClientProtocol


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9001


async def main():

    loop = asyncio.get_running_loop()

    finished = loop.create_future()

    def handle_response(message):
        if message == "PONG":
            print("UDP PING/PONG test successful!")

        if not finished.done():
            finished.set_result(None)

    transport, _ = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(
            "PING",
            handle_response
        ),
        remote_addr=(
            SERVER_HOST,
            SERVER_PORT
        )
    )

    try:
        await asyncio.wait_for(
            finished,
            timeout=5
        )

    except asyncio.TimeoutError:
        print("UDP Client: No response received")

    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())