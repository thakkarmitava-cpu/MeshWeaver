import asyncio
import ssl
from pathlib import Path


class TLSConfigurationError(Exception):
    """Raised when TLS configuration is invalid."""


def create_server_ssl_context(
    certificate_file: str,
    private_key_file: str,
) -> ssl.SSLContext:
    """
    Create an SSL context for a TLS server.

    Args:
        certificate_file: Path to the server certificate.
        private_key_file: Path to the server private key.

    Returns:
        Configured SSLContext.
    """

    certificate_path = Path(
        certificate_file
    )
    private_key_path = Path(
        private_key_file
    )

    if not certificate_path.exists():
        raise TLSConfigurationError(
            f"Certificate file not found: "
            f"{certificate_path}"
        )

    if not private_key_path.exists():
        raise TLSConfigurationError(
            f"Private key file not found: "
            f"{private_key_path}"
        )

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER
    )

    context.minimum_version = (
        ssl.TLSVersion.TLSv1_2
    )

    context.load_cert_chain(
        certfile=str(certificate_path),
        keyfile=str(private_key_path),
    )

    return context


def create_client_ssl_context(
    certificate_file: str | None = None,
) -> ssl.SSLContext:
    """
    Create an SSL context for a TLS client.

    For the local MeshWeaver test environment,
    certificate verification can be disabled.

    Production deployments should use proper
    certificate verification.
    """

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_CLIENT
    )

    context.minimum_version = (
        ssl.TLSVersion.TLSv1_2
    )

    if certificate_file:
        certificate_path = Path(
            certificate_file
        )

        if not certificate_path.exists():
            raise TLSConfigurationError(
                f"CA certificate file not found: "
                f"{certificate_path}"
            )

        context.load_verify_locations(
            cafile=str(certificate_path)
        )

        context.check_hostname = False
        context.verify_mode = (
            ssl.CERT_REQUIRED
        )

    else:
        # Local development/test mode.
        context.check_hostname = False
        context.verify_mode = (
            ssl.CERT_NONE
        )

    return context


async def start_tls_server(
    host: str,
    port: int,
    client_connected_cb,
    certificate_file: str,
    private_key_file: str,
):
    """
    Start an asyncio TLS server.

    Returns:
        asyncio.Server instance.
    """

    ssl_context = create_server_ssl_context(
        certificate_file,
        private_key_file,
    )

    server = await asyncio.start_server(
        client_connected_cb,
        host,
        port,
        ssl=ssl_context,
    )

    return server


async def open_tls_connection(
    host: str,
    port: int,
    server_hostname: str | None = None,
    certificate_file: str | None = None,
):
    """
    Open an asyncio TLS client connection.

    Returns:
        Tuple containing StreamReader and StreamWriter.
    """

    ssl_context = create_client_ssl_context(
        certificate_file
    )

    reader, writer = await asyncio.open_connection(
        host,
        port,
        ssl=ssl_context,
        server_hostname=server_hostname
        if server_hostname
        else None,
    )

    return reader, writer