import subprocess
from pathlib import Path


CERT_DIR = Path("certs")

CERTIFICATE_FILE = (
    CERT_DIR / "server.crt"
)

PRIVATE_KEY_FILE = (
    CERT_DIR / "server.key"
)


def main():
    CERT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Generating MeshWeaver TLS certificate..."
    )

    command = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-keyout",
        str(PRIVATE_KEY_FILE),
        "-out",
        str(CERTIFICATE_FILE),
        "-days",
        "365",
        "-nodes",
        "-subj",
        "/CN=localhost",
    ]

    try:
        subprocess.run(
            command,
            check=True,
        )
    except FileNotFoundError:
        print(
            "OpenSSL was not found."
        )
        print(
            "Install OpenSSL and run this "
            "script again."
        )
        return

    print()
    print(
        "TLS certificate generated successfully."
    )
    print(
        f"Certificate: {CERTIFICATE_FILE}"
    )
    print(
        f"Private key: {PRIVATE_KEY_FILE}"
    )


if __name__ == "__main__":
    main()