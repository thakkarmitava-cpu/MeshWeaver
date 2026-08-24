import asyncio


HEADER_SIZE = 4
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 MB


async def send_message(writer: asyncio.StreamWriter, data: bytes) -> None:
    """Send a length-prefixed byte message."""

    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("message is too large")

    header = len(data).to_bytes(HEADER_SIZE, byteorder="big")

    writer.write(header)
    writer.write(data)

    await writer.drain()


async def receive_message(reader: asyncio.StreamReader) -> bytes:
    """Receive a length-prefixed byte message."""

    header = await reader.readexactly(HEADER_SIZE)

    message_size = int.from_bytes(
        header,
        byteorder="big"
    )

    if message_size > MAX_MESSAGE_SIZE:
        raise ValueError("message is too large")

    return await reader.readexactly(message_size)