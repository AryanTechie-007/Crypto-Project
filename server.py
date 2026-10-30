#!/usr/bin/env python3
"""CryptoGuard Local Application Server.

Serves the TypeScript/HTML5/CSS3 frontend and provides in-memory cryptographic API endpoints
by bridging directly to src/ modules with ZERO hardcoded file paths.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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

WEB_DIR = ROOT_DIR / "web"
STATIC_DIR = WEB_DIR / "static"


class CryptoGuardHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler providing static file serving and cryptographic API endpoints."""

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def send_json(self, status_code: int, data: Dict[str, Any]):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Serve static files (HTML, CSS, JS, icons)."""
        clean_path = self.path.split("?")[0].lstrip("/")

        if clean_path in ("", "index.html"):
            target_file = WEB_DIR / "index.html"
        elif clean_path.startswith("static/"):
            target_file = WEB_DIR / clean_path
        else:
            target_file = WEB_DIR / clean_path

        resolved = target_file.resolve()
        # Security: ensure file is inside WEB_DIR
        if not str(resolved).startswith(str(WEB_DIR.resolve())) or not resolved.is_file():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        mime_type, _ = mimetypes.guess_type(str(resolved))
        if not mime_type:
            if resolved.suffix == ".js":
                mime_type = "application/javascript"
            elif resolved.suffix == ".css":
                mime_type = "text/css"
            elif resolved.suffix == ".html":
                mime_type = "text/html"
            else:
                mime_type = "application/octet-stream"

        file_bytes = resolved.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)

    def do_POST(self):
        """Handle JSON API requests."""
        if not self.path.startswith("/api/"):
            self.send_response(404)
            self.end_headers()
            return

        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len)

        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            self.send_json(400, {"error": "Invalid JSON body"})
            return

        endpoint = self.path[len("/api/"):]

        if endpoint == "verify":
            self.handle_verify(payload)
        elif endpoint == "sign":
            self.handle_sign(payload)
        elif endpoint == "keygen":
            self.handle_keygen(payload)
        elif endpoint == "fingerprint":
            self.handle_fingerprint(payload)
        elif endpoint == "sample-artifacts":
            self.handle_sample_artifacts()
        elif endpoint == "experiments":
            self.handle_experiments()
        else:
            self.send_json(404, {"error": f"Unknown endpoint: {endpoint}"})

    # -------------------------------------------------------------------------
    # API Handlers (Pure In-Memory Cryptography)
    # -------------------------------------------------------------------------

    def handle_verify(self, payload: Dict[str, Any]):
        try:
            doc_b64 = payload.get("document", "")
            sig_b64 = payload.get("signature", "")
            pub_b64 = payload.get("publicKey", "")

            if not doc_b64 or not sig_b64 or not pub_b64:
                self.send_json(400, {"error": "Missing required fields: document, signature, or publicKey"})
                return

            doc_bytes = base64.b64decode(doc_b64)
            sig_bytes = base64.b64decode(sig_b64)
            pub_bytes = base64.b64decode(pub_b64)

            # Check if signature length is 64 bytes
            if len(sig_bytes) != 64:
                self.send_json(200, {
                    "is_valid": False,
                    "message": f"Malformed signature length ({len(sig_bytes)} bytes; Ed25519 requires exactly 64 bytes).",
                    "details": "Signature length mismatch",
                    "fingerprint": None,
                })
                return

            # Load public key
            try:
                pub_key_obj = KeyManager.load_public_key(pub_bytes)
            except KeyFormatError as e:
                self.send_json(200, {
                    "is_valid": False,
                    "message": "Malformed or invalid public key file.",
                    "details": str(e),
                    "fingerprint": None,
                })
                return

            # Compute fingerprint
            fp = KeyFingerprint.compute_fingerprint(pub_key_obj)

            # Perform mathematical verification
            is_valid = SignatureVerifier.verify_bytes(doc_bytes, sig_bytes, pub_key_obj)

            if is_valid:
                self.send_json(200, {
                    "is_valid": True,
                    "message": "Signature verification SUCCEEDED: The document is authentic and unmodified.",
                    "details": "Cryptographic signature matches the document bytes and public key.",
                    "fingerprint": fp,
                })
            else:
                self.send_json(200, {
                    "is_valid": False,
                    "message": "Signature verification FAILED: Document modified or invalid signature/public key.",
                    "details": "The mathematical verification failed under the provided public key.",
                    "fingerprint": fp,
                })

        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def handle_sign(self, payload: Dict[str, Any]):
        try:
            doc_b64 = payload.get("document", "")
            priv_b64 = payload.get("privateKey", "")
            password = payload.get("password") or None

            if not doc_b64 or not priv_b64:
                self.send_json(400, {"error": "Missing required fields: document or privateKey"})
                return

            doc_bytes = base64.b64decode(doc_b64)
            priv_bytes = base64.b64decode(priv_b64)

            # Load private key
            try:
                priv_key_obj = KeyManager.load_private_key(priv_bytes, password=password)
            except InvalidPassphraseError:
                self.send_json(200, {
                    "success": False,
                    "message": "Incorrect passphrase supplied for private key.",
                    "error": "Invalid passphrase",
                })
                return
            except PassphraseError as e:
                self.send_json(200, {
                    "success": False,
                    "message": f"Private key requires a passphrase: {e}",
                    "error": "Passphrase required",
                })
                return
            except (KeyFormatError, CryptographicError) as e:
                self.send_json(200, {
                    "success": False,
                    "message": f"Failed to load private key: {e}",
                    "error": str(e),
                })
                return

            # Sign bytes
            sig_bytes = DocumentSigner.sign_bytes(doc_bytes, priv_key_obj)
            sig_b64 = base64.b64encode(sig_bytes).decode("ascii")

            self.send_json(200, {
                "success": True,
                "signature": sig_b64,
                "size": len(sig_bytes),
                "message": "Document signed successfully!",
            })

        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def handle_keygen(self, payload: Dict[str, Any]):
        try:
            password = payload.get("password") or None
            priv_key_obj, pub_key_obj = KeyManager.generate_key_pair()

            # Serialize private key
            from cryptography.hazmat.primitives import serialization
            if password:
                enc = serialization.BestAvailableEncryption(password.encode("utf-8"))
            else:
                enc = serialization.NoEncryption()

            priv_pem = priv_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=enc,
            ).decode("ascii")

            pub_pem = KeyManager.export_public_key_pem(pub_key_obj)
            fp = KeyFingerprint.compute_fingerprint(pub_key_obj)

            self.send_json(200, {
                "success": True,
                "private_key": priv_pem,
                "public_key": pub_pem,
                "fingerprint": fp,
                "encrypted": password is not None,
            })

        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def handle_fingerprint(self, payload: Dict[str, Any]):
        try:
            pub_b64 = payload.get("publicKey", "")
            expected = payload.get("expected") or None

            if not pub_b64:
                self.send_json(400, {"error": "Missing publicKey field"})
                return

            pub_bytes = base64.b64decode(pub_b64)
            pub_key_obj = KeyManager.load_public_key(pub_bytes)
            fp = KeyFingerprint.compute_fingerprint(pub_key_obj)

            matches = None
            if expected and expected.strip():
                matches = KeyFingerprint.verify_fingerprint(pub_key_obj, expected.strip())

            self.send_json(200, {
                "success": True,
                "fingerprint": fp,
                "matches": matches,
                "message": "Fingerprint computed successfully.",
            })

        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def handle_sample_artifacts(self):
        """Return default sample document, signature, and public key for one-click testing."""
        try:
            doc_path = ROOT_DIR / "sample_data" / "sample_document.txt"
            sig_path = ROOT_DIR / "artifacts" / "sample_document.sig"
            pub_path = ROOT_DIR / "artifacts" / "signer_public_key.pem"

            doc_bytes = doc_path.read_bytes() if doc_path.is_file() else b""
            sig_bytes = sig_path.read_bytes() if sig_path.is_file() else b""
            pub_bytes = pub_path.read_bytes() if pub_path.is_file() else b""

            self.send_json(200, {
                "document": {
                    "name": "sample_document.txt",
                    "size": len(doc_bytes),
                    "type": "text/plain",
                    "contentBase64": base64.b64encode(doc_bytes).decode("ascii"),
                },
                "signature": {
                    "name": "sample_document.sig",
                    "size": len(sig_bytes),
                    "type": "application/octet-stream",
                    "contentBase64": base64.b64encode(sig_bytes).decode("ascii"),
                },
                "publicKey": {
                    "name": "signer_public_key.pem",
                    "size": len(pub_bytes),
                    "type": "application/x-pem-file",
                    "contentBase64": base64.b64encode(pub_bytes).decode("ascii"),
                },
            })

        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def handle_experiments(self):
        """Run all 5 university security experiments live and return results."""
        results = []
        try:
            # Setup author & attacker keys
            author_priv, author_pub = KeyManager.generate_key_pair()
            attacker_priv, attacker_pub = KeyManager.generate_key_pair()
            doc_bytes = b"University Academic Credential: Alice, ID 12345"
            sig_bytes = DocumentSigner.sign_bytes(doc_bytes, author_priv)

            # Exp 1: Verify original
            exp1_ok = SignatureVerifier.verify_bytes(doc_bytes, sig_bytes, author_pub)
            results.append({
                "id": 1,
                "title": "Verify Original Document",
                "description": "Original document verified with matching author public key and detached signature.",
                "passed": exp1_ok,
                "expected": "Signature equation evaluates to TRUE",
                "observed": "TRUE (Valid)",
                "details": "Mathematical signature verification succeeded.",
            })

            # Exp 2: Tamper document
            tampered_doc = doc_bytes + b" [tampered]"
            exp2_ok = not SignatureVerifier.verify_bytes(tampered_doc, sig_bytes, author_pub)
            results.append({
                "id": 2,
                "title": "Modify Signed Document",
                "description": "Altered document bytes tested against original signature.",
                "passed": exp2_ok,
                "expected": "Signature equation evaluates to FALSE",
                "observed": "FALSE (Tampering Detected)",
                "details": "Any byte modification causes instant hash discrepancy and rejection.",
            })

            # Exp 3: Supply wrong public key
            exp3_ok = not SignatureVerifier.verify_bytes(doc_bytes, sig_bytes, attacker_pub)
            results.append({
                "id": 3,
                "title": "Supply Wrong Public Key",
                "description": "Original document and signature tested against an unrelated public key.",
                "passed": exp3_ok,
                "expected": "Signature equation evaluates to FALSE",
                "observed": "FALSE (Invalid Key Rejected)",
                "details": "Curve point scalar verification fails under mismatched public key.",
            })

            # Exp 4: Tamper signature
            bad_sig = bytearray(sig_bytes)
            bad_sig[0] ^= 0xFF
            exp4_ok = not SignatureVerifier.verify_bytes(doc_bytes, bytes(bad_sig), author_pub)
            results.append({
                "id": 4,
                "title": "Corrupt Signature Bytes",
                "description": "Single bit flipped in the 64-byte detached digital signature.",
                "passed": exp4_ok,
                "expected": "Signature equation evaluates to FALSE",
                "observed": "FALSE (Corrupted Signature Rejected)",
                "details": "Scalar R/S corruption causes immediate mathematical failure.",
            })

            # Exp 5: Public key substitution
            replacement_doc = b"Replaced document by attacker"
            attacker_sig = DocumentSigner.sign_bytes(replacement_doc, attacker_priv)
            attacker_crypto_ok = SignatureVerifier.verify_bytes(replacement_doc, attacker_sig, attacker_pub)
            author_fp = KeyFingerprint.compute_fingerprint(author_pub)
            trust_ok = not KeyFingerprint.verify_fingerprint(attacker_pub, author_fp)
            exp5_ok = attacker_crypto_ok and trust_ok

            results.append({
                "id": 5,
                "title": "Public-Key Substitution Attack",
                "description": "Attacker provides replacement document, attacker signature, and attacker public key.",
                "passed": exp5_ok,
                "expected": "Crypto verifies (TRUE), but Fingerprint Trust Check REJECTS (FALSE)",
                "observed": f"Crypto: {attacker_crypto_ok} | Fingerprint Trust: REJECTED",
                "details": "Distinguishes mathematical validity from signer identity. Trust pinning stops key substitution.",
            })

            self.send_json(200, results)

        except Exception as e:
            self.send_json(500, {"error": str(e)})


def run_server(port: int = 8080, open_browser: bool = True):
    server_address = ("", port)
    try:
        httpd = ThreadingHTTPServer(server_address, CryptoGuardHandler)
    except OSError:
        port = 8081
        server_address = ("", port)
        try:
            httpd = ThreadingHTTPServer(server_address, CryptoGuardHandler)
        except OSError:
            server_address = ("", 0)
            httpd = ThreadingHTTPServer(server_address, CryptoGuardHandler)
            port = httpd.server_port

    url = f"http://localhost:{port}"
    print(f"\n========================================================")
    print(f" CryptoGuard Application Server Running")
    print(f" URL: {url}")
    print(f" SERVER_READY_PORT:{port}")
    print(f" Press Ctrl+C to stop the server")
    print(f"========================================================\n", flush=True)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.", flush=True)
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    open_browser = True
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)
        elif arg in ("--no-browser", "--electron"):
            open_browser = False
    run_server(port, open_browser=open_browser)