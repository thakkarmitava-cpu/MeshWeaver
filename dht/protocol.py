import json


PING = "PING"
PONG = "PONG"
FIND_NODE = "FIND_NODE"
NODES = "NODES"


def encode_message(
    message_type: str,
    sender_id: int,
    **payload,
) -> bytes:
    """Encode a DHT message into bytes."""

    message = {
        "type": message_type,
        "sender_id": f"{sender_id:040x}",
        "payload": payload,
    }

    return json.dumps(message).encode("utf-8")


def decode_message(data: bytes) -> dict:
    """Decode a DHT message from bytes."""

    return json.loads(data.decode("utf-8"))


def create_ping(sender_id: int) -> bytes:
    """Create a PING message."""

    return encode_message(
        PING,
        sender_id,
    )


def create_pong(sender_id: int) -> bytes:
    """Create a PONG message."""

    return encode_message(
        PONG,
        sender_id,
    )


def create_find_node(
    sender_id: int,
    target_id: int,
) -> bytes:
    """Create a FIND_NODE message."""

    return encode_message(
        FIND_NODE,
        sender_id,
        target_id=f"{target_id:040x}",
    )


def create_nodes_response(
    sender_id: int,
    peers: list[dict],
) -> bytes:
    """Create a response containing known nodes."""

    return encode_message(
        NODES,
        sender_id,
        peers=peers,
    )