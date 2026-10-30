
"""
Digital Signature-Based Document Verification System
P3 application entry point.

Run from the repository root:

    python -m src.main --help
    python -m src.main keygen
    python -m src.main sign
    python -m src.main verify
    python -m src.main fingerprint
    python -m src.main all
"""

import argparse
import getpass
import sys
from pathlib import Path

from src.key_manager import KeyManager
from src.document_signer import DocumentSigner
from src.signature_verifier import SignatureVerifier
from src.key_fingerprint import KeyFingerprint


# ---------------------------------------------------------
# Repository paths
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

PRIVATE_KEY_PATH = ROOT_DIR / "private" / "my_private_key.pem"
PUBLIC_KEY_PATH = ROOT_DIR / "artifacts" / "signer_public_key.pem"
SAMPLE_DOCUMENT_PATH = ROOT_DIR / "sample_data" / "sample_document.txt"
SIGNATURE_PATH = ROOT_DIR / "artifacts" / "sample_document.sig"


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def ensure_parent_directory(path: Path) -> None:
    """Create the parent directory when it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def print_heading(title: str) -> None:
    """Display a formatted section heading."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------
# 1. Key generation
# ---------------------------------------------------------

def generate_keys(args) -> None:
    """Generate an Ed25519 key pair and save both keys."""

    print_heading("ED25519 KEY GENERATION")

    private_path = Path(args.private_key)
    public_path = Path(args.public_key)

    # Do not overwrite existing keys accidentally.
    if private_path.exists() or public_path.exists():
        print("Error: One or both key files already exist.")
        print("Existing keys will not be overwritten.")
        print("Choose different output paths or handle the existing keys first.")
        return

    ensure_parent_directory(private_path)
    ensure_parent_directory(public_path)

    password = getpass.getpass(
        "Enter a password to protect the private key: "
    )

    confirmation = getpass.getpass("Confirm password: ")

    if not password:
        print("Error: A non-empty private-key password is required.")
        return

    if password != confirmation:
        print("Error: Passwords do not match.")
        return

    private_key, public_key = KeyManager.generate_key_pair()

    KeyManager.save_private_key(
        private_key,
        str(private_path),
        password
    )

    KeyManager.save_public_key(
        public_key,
        str(public_path)
    )

    print("\nKey pair generated successfully.")
    print(f"Private key saved to: {private_path}")
    print(f"Public key saved to:  {public_path}")

    print("\nKeep the private key confidential.")
    print("Do not upload or commit it to GitHub.")


# ---------------------------------------------------------
# 2. Document signing
# ---------------------------------------------------------

def sign_document(args) -> bool:
    """Create a detached Ed25519 signature for a document."""

    print_heading("DOCUMENT SIGNING")

    document_path = Path(args.document)
    private_path = Path(args.private_key)
    signature_path = Path(args.signature)

    if not document_path.is_file():
        print(f"Error: Document not found: {document_path}")
        return False

    if not private_path.is_file():
        print(f"Error: Private key not found: {private_path}")
        print("Generate a key pair first using the keygen command.")
        return False

    ensure_parent_directory(signature_path)

    password = getpass.getpass(
        "Enter the private key password: "
    )

    if not password:
        print("Error: Password cannot be empty.")
        return False

    print(f"\nDocument:     {document_path}")
    print(f"Private key:  {private_path}")
    print(f"Signature:    {signature_path}")

    DocumentSigner.sign_document(
        document_path=str(document_path),
        private_key=str(private_path),
        signature_output_path=str(signature_path),
        password=password
    )

    if not signature_path.is_file():
        print("Error: Signature output was not created.")
        return False

    signature_size = signature_path.stat().st_size

    if signature_size != 64:
        print(
            "Error: Unexpected signature size. "
            "An Ed25519 signature must be 64 bytes."
        )
        return False

    print("\nDocument signed successfully.")
    print(f"Detached signature: {signature_path}")
    print(f"Signature size: {signature_size} bytes")

    return True


# ---------------------------------------------------------
# 3. Document signature verification
# ---------------------------------------------------------

def verify_document(args) -> bool:
    """Verify a document using its detached signature and public key."""

    print_heading("DOCUMENT SIGNATURE VERIFICATION")

    document_path = Path(args.document)
    signature_path = Path(args.signature)
    public_path = Path(args.public_key)

    for description, path in (
        ("Document", document_path),
        ("Signature", signature_path),
        ("Public key", public_path),
    ):
        if not path.is_file():
            print(f"Error: {description} file not found: {path}")
            return False

    result = SignatureVerifier.verify_document(
        document_path=str(document_path),
        signature_source=str(signature_path),
        public_key_source=str(public_path)
    )

    print("\nVerification result")
    print("-" * 30)

    if result.is_valid:
        print("STATUS: AUTHENTIC")
    else:
        print("STATUS: NOT AUTHENTIC")

    print(f"Message: {result.message}")

    if result.details:
        print("\nDetails:")

        if isinstance(result.details, dict):
            for key, value in result.details.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {result.details}")

    return bool(result.is_valid)


# ---------------------------------------------------------
# 4. Public key fingerprint
# ---------------------------------------------------------

def show_fingerprint(args) -> bool:
    """Compute and display the public-key SHA-256 fingerprint."""

    print_heading("PUBLIC KEY FINGERPRINT")

    public_path = Path(args.public_key)

    if not public_path.is_file():
        print(f"Error: Public key not found: {public_path}")
        return False

    fingerprint = KeyFingerprint.compute_fingerprint(
        str(public_path)
    )

    print(f"Public key: {public_path}")
    print(f"SHA-256 fingerprint:\n{fingerprint}")

    print(
        "\nCompare this fingerprint with a value obtained "
        "through a trusted, independent channel."
    )

    return True


# ---------------------------------------------------------
# 5. Run all operations
# ---------------------------------------------------------

def run_all(args) -> None:
    """Run the complete key generation, signing and verification workflow."""

    print_heading("COMPLETE DIGITAL SIGNATURE WORKFLOW")

    # Check the sample document first.
    if not SAMPLE_DOCUMENT_PATH.is_file():
        print(f"Error: Sample document not found: {SAMPLE_DOCUMENT_PATH}")
        return

    # Check whether the key pair already exists.
    private_exists = PRIVATE_KEY_PATH.is_file()
    public_exists = PUBLIC_KEY_PATH.is_file()

    if private_exists != public_exists:
        print("\nWorkflow stopped.")
        print("Only one key file exists.")
        print("Check your key files before continuing.")
        return

    # Generate keys only if neither exists.
    if not private_exists and not public_exists:

        print("\nNo existing key pair found.")
        print("Generating a new key pair...")

        keygen_args = argparse.Namespace(
            private_key=str(PRIVATE_KEY_PATH),
            public_key=str(PUBLIC_KEY_PATH)
        )

        generate_keys(keygen_args)

        if not (
            PRIVATE_KEY_PATH.is_file()
            and PUBLIC_KEY_PATH.is_file()
        ):
            print("\nWorkflow stopped: Key generation failed.")
            return

    else:
        print("\nExisting key pair found.")
        print("Using existing keys without overwriting them.")

    # Sign the sample document.
    sign_args = argparse.Namespace(
        document=str(SAMPLE_DOCUMENT_PATH),
        private_key=str(PRIVATE_KEY_PATH),
        signature=str(SIGNATURE_PATH)
    )

    # Remove an old signature so it cannot be mistaken
    # for the result of this signing operation.
    if SIGNATURE_PATH.exists():
        SIGNATURE_PATH.unlink()

    signing_success = sign_document(sign_args)

    if not signing_success:
        print("\nWorkflow stopped: Document signing failed.")
        return

    # Verify the newly generated signature.
    verify_args = argparse.Namespace(
        document=str(SAMPLE_DOCUMENT_PATH),
        signature=str(SIGNATURE_PATH),
        public_key=str(PUBLIC_KEY_PATH)
    )

    verification_success = verify_document(verify_args)

    if not verification_success:
        print("\nWorkflow completed with verification failure.")
        return

    # Calculate and display the public-key fingerprint.
    fingerprint_args = argparse.Namespace(
        public_key=str(PUBLIC_KEY_PATH)
    )

    fingerprint_success = show_fingerprint(fingerprint_args)

    if not fingerprint_success:
        print("\nWorkflow completed, but fingerprinting failed.")
        return

    print_heading("WORKFLOW COMPLETED SUCCESSFULLY")

    print("1. Key pair available.")
    print("2. Document signed successfully.")
    print("3. Digital signature verified successfully.")
    print("4. Public-key fingerprint calculated successfully.")


# ---------------------------------------------------------
# 6. Command-line argument parser
# ---------------------------------------------------------

def build_parser():

    parser = argparse.ArgumentParser(
        description=(
            "Ed25519-based document signing, verification "
            "and public-key fingerprint utility."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Key generation command
    keygen_parser = subparsers.add_parser(
        "keygen",
        help="Generate an Ed25519 key pair."
    )

    keygen_parser.add_argument(
        "--private-key",
        default=str(PRIVATE_KEY_PATH),
        help="Output path for the private key."
    )

    keygen_parser.add_argument(
        "--public-key",
        default=str(PUBLIC_KEY_PATH),
        help="Output path for the public key."
    )

    keygen_parser.set_defaults(func=generate_keys)

    # Document signing command
    sign_parser = subparsers.add_parser(
        "sign",
        help="Sign a document and create a detached signature."
    )

    sign_parser.add_argument(
        "--document",
        default=str(SAMPLE_DOCUMENT_PATH),
        help="Path to the document to sign."
    )

    sign_parser.add_argument(
        "--private-key",
        default=str(PRIVATE_KEY_PATH),
        help="Path to the private key."
    )

    sign_parser.add_argument(
        "--signature",
        default=str(SIGNATURE_PATH),
        help="Output path for the detached signature."
    )

    sign_parser.set_defaults(func=sign_document)

    # Signature verification command
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify a document's detached signature."
    )

    verify_parser.add_argument(
        "--document",
        default=str(SAMPLE_DOCUMENT_PATH),
        help="Path to the document."
    )

    verify_parser.add_argument(
        "--signature",
        default=str(SIGNATURE_PATH),
        help="Path to the detached signature."
    )

    verify_parser.add_argument(
        "--public-key",
        default=str(PUBLIC_KEY_PATH),
        help="Path to the public key."
    )

    verify_parser.set_defaults(func=verify_document)

    # Fingerprint command
    fingerprint_parser = subparsers.add_parser(
        "fingerprint",
        help="Compute a public-key SHA-256 fingerprint."
    )

    fingerprint_parser.add_argument(
        "--public-key",
        default=str(PUBLIC_KEY_PATH),
        help="Path to the public key."
    )

    fingerprint_parser.set_defaults(func=show_fingerprint)

    # Complete workflow command
    all_parser = subparsers.add_parser(
        "all",
        help="Run the complete digital signature workflow."
    )

    all_parser.set_defaults(func=run_all)

    return parser


# ---------------------------------------------------------
# 7. Application entry point
# ---------------------------------------------------------

def main():

    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)

    except Exception as exc:
        # Never print private-key contents or passwords.
        print(
            f"\nOperation failed: {type(exc).__name__}: {exc}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
