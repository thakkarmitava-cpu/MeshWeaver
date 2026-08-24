import asyncio

from networking.udp import UDPServerProtocol


HOST = "127.0.0.1"
PORT = 9001


class MeshUDPServerProtocol(UDPServerProtocol):
    """MeshWeaver UDP server used for PING/PONG."""

    def datagram_received(self, data, addr):
        message = data.decode()

        print(
            f"UDP Server received from "
            f"{addr}: {message}"
        )

        if message == "PING":
            print("UDP Server sending: PONG")

            self.transport.sendto(
                b"PONG",
                addr
            )


async def main():

    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        MeshUDPServerProtocol,
        local_addr=(HOST, PORT)
    )

    try:
        await asyncio.Future()

    except asyncio.CancelledError:
        pass

    finally:
        transport.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("UDP Server stopped")