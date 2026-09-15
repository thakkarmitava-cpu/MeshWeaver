from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)


class SignatureError(Exception):
    """Raised when a signature operation fails."""


class NodeSigner:
    """
    Provides Ed25519 signing and verification for MeshWeaver nodes.
    """

    def __init__(
        self,
        private_key=None,
    ):
        """
        Create a signer.

        If no private key is provided, a new Ed25519
        private key is generated.
        """

        if private_key is None:
            self.private_key = (
                ed25519.Ed25519PrivateKey.generate()
            )
        else:
            self.private_key = private_key

        self.public_key = (
            self.private_key.public_key()
        )

    def sign(
        self,
        message: bytes,
    ) -> bytes:
        """
        Sign a message using the node's private key.
        """

        if not isinstance(message, bytes):
            raise SignatureError(
                "Message must be bytes."
            )

        return self.private_key.sign(
            message
        )

    def get_public_key_bytes(self) -> bytes:
        """
        Return the public key in raw byte form.
        """

        return self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )

    def verify(
        self,
        message: bytes,
        signature: bytes,
    ) -> bool:
        """
        Verify a signature using this node's public key.
        """

        if not isinstance(message, bytes):
            raise SignatureError(
                "Message must be bytes."
            )

        if not isinstance(signature, bytes):
            raise SignatureError(
                "Signature must be bytes."
            )

        try:
            self.public_key.verify(
                signature,
                message,
            )

            return True

        except InvalidSignature:
            return False


def create_signer() -> NodeSigner:
    """
    Create a new MeshWeaver node signer.
    """

    return NodeSigner()


def verify_signature(
    public_key_bytes: bytes,
    message: bytes,
    signature: bytes,
) -> bool:
    """
    Verify a signature using a supplied public key.
    """

    try:
        public_key = (
            ed25519.Ed25519PublicKey.from_public_bytes(
                public_key_bytes
            )
        )

        public_key.verify(
            signature,
            message,
        )

        return True

    except (
        InvalidSignature,
        ValueError,
    ):
        return False