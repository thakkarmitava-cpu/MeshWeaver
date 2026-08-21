import asyncio

from .protocol import send_message, receive_message


class AsyncClient:
    """Reusable asynchronous TCP client."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None

    async def connect(self) -> None:
        """Connect to a remote MeshWeaver node."""

        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port,
        )

        print(
            f"Connected to "
            f"{self.host}:{self.port}"
        )

    async def send(self, data: bytes) -> None:
        """Send bytes to the remote node."""

        if self.writer is None:
            raise RuntimeError("Client is not connected")

        await send_message(self.writer, data)

    async def receive(self) -> bytes:
        """Receive bytes from the remote node."""

        if self.reader is None:
            raise RuntimeError("Client is not connected")

        return await receive_message(self.reader)

    async def close(self) -> None:
        """Close the connection."""

        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()

            self.reader = None
            self.writer = None

            print("Connection closed")