import asyncio
from collections.abc import Awaitable, Callable


ClientHandler = Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Awaitable[None],
]


class AsyncServer:
    """Reusable asynchronous TCP server."""

    def __init__(
        self,
        host: str,
        port: int,
        handler: ClientHandler,
    ):
        self.host = host
        self.port = port
        self.handler = handler
        self.server = None

    async def start(self) -> None:
        """Start accepting client connections."""

        self.server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port,
        )

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:

        address = writer.get_extra_info("peername")

        print(f"Client connected: {address}")

        try:
            await self.handler(reader, writer)

        except asyncio.IncompleteReadError:
            print(f"Client disconnected: {address}")

        except Exception as exc:
            print(f"Client error: {exc}")

        finally:
            writer.close()
            await writer.wait_closed()

            print(f"Connection closed: {address}")

    async def serve_forever(self) -> None:
        """Keep the server running."""

        if self.server is None:
            raise RuntimeError("Server has not been started")

        print(
            f"Server running on "
            f"{self.host}:{self.port}"
        )

        async with self.server:
            await self.server.serve_forever()

    async def close(self) -> None:
        """Stop the server."""

        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()