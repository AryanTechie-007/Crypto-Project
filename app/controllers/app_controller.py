"""Application Controller for CryptoGuard Desktop Application.

Acts as the presentation logic bridge connecting GUI view events with the
underlying cryptographic core (src/ modules) without altering core code.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.document_signer import DocumentSigner, SigningError
from src.key_fingerprint import KeyFingerprint
from src.key_manager import (
    CryptographicError,
    InvalidPassphraseError,
    KeyFormatError,
    KeyManagementError,
    KeyManager,
    PassphraseError,
)
from src.signature_verifier import SignatureVerifier, VerificationResult


class AppController:
    """Controller handling business logic and cryptographic orchestration for the UI."""

    @staticmethod
    def verify_document(doc_path: str, sig_path: str, pub_path: str) -> Dict[str, Any]:
        """Verify a document's detached signature and compute public key fingerprint.

        Returns a dictionary with status, message, details, and signer fingerprint.
        """
        # Validate file existence before proceeding
        for label, path_str in [("Document", doc_path), ("Signature", sig_path), ("Public Key", pub_path)]:
            if not path_str or not path_str.strip():
                return {
                    "is_valid": False,
                    "message": f"Missing input: Please select a {label} file.",
                    "details": None,
                    "fingerprint": None,
                }
            if not Path(path_str).is_file():
                return {
                    "is_valid": False,
                    "message": f"{label} file not found.",
                    "details": f"Path does not exist: {path_str}",
                    "fingerprint": None,
                }

        try:
            result = SignatureVerifier.verify_document(
                document_path=doc_path,
                signature_source=sig_path,
                public_key_source=pub_path,
            )

            # Compute fingerprint for authenticated trust inspection
            fingerprint = None
            try:
                fingerprint = KeyFingerprint.compute_fingerprint(pub_path)
            except Exception:
                pass

            return {
                "is_valid": result.is_valid,
                "message": result.message,
                "details": result.details,
                "fingerprint": fingerprint,
            }

        except Exception as e:
            return {
                "is_valid": False,
                "message": "Verification encountered an unexpected error.",
                "details": str(e),
                "fingerprint": None,
            }

    @staticmethod
    def sign_document(
        doc_path: str,
        priv_path: str,
        out_sig_path: str,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sign a document and create a 64-byte detached signature file."""
        if not doc_path or not Path(doc_path).is_file():
            return {
                "success": False,
                "message": "Please select a valid document file to sign.",
            }
        if not priv_path or not Path(priv_path).is_file():
            return {
                "success": False,
                "message": "Please select a valid private key file.",
            }
        if not out_sig_path or not out_sig_path.strip():
            return {
                "success": False,
                "message": "Please specify an output path for the signature file.",
            }

        pass_clean = password if password else None

        try:
            signature = DocumentSigner.sign_document(
                document_path=doc_path,
                private_key=priv_path,
                signature_output_path=out_sig_path,
                password=pass_clean,
            )

            sig_file = Path(out_sig_path)
            sig_size = sig_file.stat().st_size if sig_file.is_file() else len(signature)

            return {
                "success": True,
                "message": "Document signed successfully!",
                "signature_path": str(sig_file.resolve()),
                "size": sig_size,
            }

        except InvalidPassphraseError:
            return {
                "success": False,
                "message": "Incorrect passphrase supplied for private key.",
            }
        except PassphraseError as e:
            return {
                "success": False,
                "message": f"Private key requires a passphrase: {e}",
            }
        except (SigningError, KeyFormatError, KeyManagementError, OSError) as e:
            return {
                "success": False,
                "message": f"Signing failed: {e}",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error during signing: {e}",
            }

    @staticmethod
    def generate_keys(
        priv_path: str,
        pub_path: str,
        password: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Generate a new Ed25519 key pair and save to specified disk paths."""
        if not priv_path or not priv_path.strip():
            return {"success": False, "message": "Private key destination path required."}
        if not pub_path or not pub_path.strip():
            return {"success": False, "message": "Public key destination path required."}

        priv = Path(priv_path)
        pub = Path(pub_path)

        if not force and (priv.exists() or pub.exists()):
            existing = []
            if priv.exists():
                existing.append(str(priv))
            if pub.exists():
                existing.append(str(pub))
            return {
                "success": False,
                "message": f"Files already exist. Enable overwrite to replace:\n" + "\n".join(existing),
            }

        pass_clean = password if password else None

        try:
            private_key, public_key = KeyManager.generate_key_pair()

            saved_priv = KeyManager.save_private_key(private_key, priv, password=pass_clean)
            saved_pub = KeyManager.save_public_key(public_key, pub)

            fingerprint = KeyFingerprint.compute_fingerprint(public_key)

            return {
                "success": True,
                "message": "Ed25519 key pair generated successfully!",
                "priv_path": str(saved_priv),
                "pub_path": str(saved_pub),
                "encrypted": pass_clean is not None,
                "fingerprint": fingerprint,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to generate keys: {e}",
            }

    @staticmethod
    def compute_fingerprint(pub_path: str, expected: Optional[str] = None) -> Dict[str, Any]:
        """Compute public-key SHA-256 fingerprint and optionally verify trust match."""
        if not pub_path or not Path(pub_path).is_file():
            return {
                "success": False,
                "message": "Public key file not found.",
                "fingerprint": None,
                "matches": None,
            }

        try:
            fingerprint = KeyFingerprint.compute_fingerprint(pub_path)

            matches = None
            if expected and expected.strip():
                matches = KeyFingerprint.verify_fingerprint(pub_path, expected.strip())

            return {
                "success": True,
                "message": "Fingerprint computed successfully.",
                "fingerprint": fingerprint,
                "matches": matches,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to compute fingerprint: {e}",
                "fingerprint": None,
                "matches": None,
            }
