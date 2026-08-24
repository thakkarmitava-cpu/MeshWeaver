import asyncio


class UDPServerProtocol(asyncio.DatagramProtocol):
    """Asyncio UDP server protocol."""

    def __init__(self, on_message=None):
        self.transport = None
        self.on_message = on_message

    def connection_made(self, transport):
        self.transport = transport

        address = transport.get_extra_info("sockname")

        print(f"UDP Server running on {address[0]}:{address[1]}")

    def datagram_received(self, data, addr):
        message = data.decode()

        print(f"UDP Server received from {addr}: {message}")

        if self.on_message:
            self.on_message(message, addr)

    def error_received(self, exc):
        print(f"UDP Server error: {exc}")

    def connection_lost(self, exc):
        print("UDP Server connection closed")


class UDPClientProtocol(asyncio.DatagramProtocol):
    """Asyncio UDP client protocol."""

    def __init__(self, message, on_response):
        self.message = message
        self.on_response = on_response
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

        print("UDP Client started")

        self.transport.sendto(
            self.message.encode()
        )

        print(f"UDP Client sent: {self.message}")

    def datagram_received(self, data, addr):
        message = data.decode()

        print(
            f"UDP Client received from "
            f"{addr}: {message}"
        )

        if self.on_response:
            self.on_response(message)

    def error_received(self, exc):
        print(f"UDP Client error: {exc}")

    def connection_lost(self, exc):
        print("UDP Client connection closed")