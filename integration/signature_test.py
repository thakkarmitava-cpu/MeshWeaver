from security.signatures import (
    create_signer,
    verify_signature,
)


def main():
    print(
        "Starting MeshWeaver signature test..."
    )

    # Create two independent node identities.
    node_a = create_signer()
    node_b = create_signer()

    message = (
        b"MeshWeaver authenticated message"
    )

    # Node A signs the message.
    signature = node_a.sign(
        message
    )

    print(
        "Message signed by Node A"
    )

    print(
        f"Signature length: "
        f"{len(signature)} bytes"
    )

    # Node B verifies the message using
    # Node A's public key.
    valid_signature = verify_signature(
        node_a.get_public_key_bytes(),
        message,
        signature,
    )

    print(
        "Original message verification:",
        valid_signature,
    )

    # Make sure modified data fails verification.
    modified_message = (
        b"Modified MeshWeaver message"
    )

    modified_signature = verify_signature(
        node_a.get_public_key_bytes(),
        modified_message,
        signature,
    )

    print(
        "Modified message verification:",
        modified_signature,
    )

    # Make sure another node's public key
    # cannot verify Node A's signature.
    wrong_key_verification = verify_signature(
        node_b.get_public_key_bytes(),
        message,
        signature,
    )

    print(
        "Wrong public key verification:",
        wrong_key_verification,
    )

    success = (
        valid_signature
        and not modified_signature
        and not wrong_key_verification
    )

    print()

    if success:
        print(
            "Cryptographic signature test: PASS"
        )
    else:
        print(
            "Cryptographic signature test: FAIL"
        )


if __name__ == "__main__":
    main()