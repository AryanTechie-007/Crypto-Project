"""Unit tests for CryptoGuard Desktop Application Controller and Logic.

Tests the presentation logic bridge, error handling, parameter validation,
and end-to-end cryptographic operations through the AppController.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.controllers.app_controller import AppController
from src.key_fingerprint import KeyFingerprint
from src.key_manager import KeyManager

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestAppController(unittest.TestCase):
    """Test suite covering AppController business logic and error handling."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.controller = AppController()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_verify_authentic_sample_artifacts(self):
        """Verify repository sample artifacts succeed through controller."""
        doc = str(ROOT_DIR / "sample_data" / "sample_document.txt")
        sig = str(ROOT_DIR / "artifacts" / "sample_document.sig")
        pub = str(ROOT_DIR / "artifacts" / "signer_public_key.pem")

        res = self.controller.verify_document(doc, sig, pub)
        self.assertTrue(res["is_valid"])
        self.assertIn("SUCCEEDED", res["message"])
        self.assertIsNotNone(res["fingerprint"])
        self.assertTrue(res["fingerprint"].startswith("SHA256:"))

    def test_verify_tampered_document(self):
        """Verify controller flags tampered document content as invalid."""
        doc_orig = ROOT_DIR / "sample_data" / "sample_document.txt"
        sig = str(ROOT_DIR / "artifacts" / "sample_document.sig")
        pub = str(ROOT_DIR / "artifacts" / "signer_public_key.pem")

        tampered_doc = self.temp_path / "tampered.txt"
        tampered_doc.write_bytes(doc_orig.read_bytes() + b"\nModifying one byte.")

        res = self.controller.verify_document(str(tampered_doc), sig, pub)
        self.assertFalse(res["is_valid"])
        self.assertIn("FAILED", res["message"])

    def test_verify_wrong_public_key(self):
        """Verify controller flags unrelated public key as invalid."""
        doc = str(ROOT_DIR / "sample_data" / "sample_document.txt")
        sig = str(ROOT_DIR / "artifacts" / "sample_document.sig")

        _, wrong_pub = KeyManager.generate_key_pair()
        wrong_pub_path = self.temp_path / "wrong.pem"
        KeyManager.save_public_key(wrong_pub, wrong_pub_path)

        res = self.controller.verify_document(doc, sig, str(wrong_pub_path))
        self.assertFalse(res["is_valid"])

    def test_verify_missing_file_handles_gracefully(self):
        """Verify missing inputs return clear error messages without raising unhandled exceptions."""
        res = self.controller.verify_document(
            str(self.temp_path / "missing_doc.txt"),
            str(ROOT_DIR / "artifacts" / "sample_document.sig"),
            str(ROOT_DIR / "artifacts" / "signer_public_key.pem"),
        )
        self.assertFalse(res["is_valid"])
        self.assertIn("not found", res["message"].lower())

    def test_sign_and_verify_lifecycle(self):
        """Test full signing and verification cycle through controller."""
        priv_key, pub_key = KeyManager.generate_key_pair()
        priv_path = self.temp_path / "author_priv.pem"
        pub_path = self.temp_path / "author_pub.pem"
        KeyManager.save_private_key(priv_key, priv_path)
        KeyManager.save_public_key(pub_key, pub_path)

        doc = self.temp_path / "degree.txt"
        doc.write_bytes(b"Academic Degree Certificate: Test Candidate")
        out_sig = self.temp_path / "degree.sig"

        sign_res = self.controller.sign_document(
            doc_path=str(doc),
            priv_path=str(priv_path),
            out_sig_path=str(out_sig),
        )
        self.assertTrue(sign_res["success"])
        self.assertEqual(sign_res["size"], 64)
        self.assertTrue(out_sig.is_file())

        verify_res = self.controller.verify_document(
            doc_path=str(doc),
            sig_path=str(out_sig),
            pub_path=str(pub_path),
        )
        self.assertTrue(verify_res["is_valid"])

    def test_sign_with_encrypted_private_key(self):
        """Test signing with passphrase-protected private key."""
        priv_key, _ = KeyManager.generate_key_pair()
        priv_path = self.temp_path / "enc_priv.pem"
        KeyManager.save_private_key(priv_key, priv_path, password="SecretPassword123!")

        doc = self.temp_path / "data.txt"
        doc.write_bytes(b"Test data payload")
        sig = self.temp_path / "data.sig"

        # Correct password succeeds
        res_ok = self.controller.sign_document(
            doc_path=str(doc),
            priv_path=str(priv_path),
            out_sig_path=str(sig),
            password="SecretPassword123!",
        )
        self.assertTrue(res_ok["success"])

        # Incorrect password fails with descriptive message
        res_fail = self.controller.sign_document(
            doc_path=str(doc),
            priv_path=str(priv_path),
            out_sig_path=str(sig),
            password="WrongPassword!",
        )
        self.assertFalse(res_fail["success"])
        self.assertIn("passphrase", res_fail["message"].lower())

    def test_generate_keys_encrypted_and_unencrypted(self):
        """Test key generation through controller with and without encryption."""
        # Unencrypted
        priv1 = self.temp_path / "unenc.pem"
        pub1 = self.temp_path / "unenc_pub.pem"
        res1 = self.controller.generate_keys(str(priv1), str(pub1), password=None)
        self.assertTrue(res1["success"])
        self.assertFalse(res1["encrypted"])
        self.assertTrue(priv1.is_file())
        self.assertTrue(pub1.is_file())

        # Overwrite prevention without force
        res_ov = self.controller.generate_keys(str(priv1), str(pub1), password=None, force=False)
        self.assertFalse(res_ov["success"])
        self.assertIn("already exist", res_ov["message"])

        # Overwrite with force
        res_ov_force = self.controller.generate_keys(str(priv1), str(pub1), password="NewPassword123!", force=True)
        self.assertTrue(res_ov_force["success"])
        self.assertTrue(res_ov_force["encrypted"])

    def test_fingerprint_computation_and_trust_verification(self):
        """Test computing and checking fingerprints against trusted reference."""
        pub_path = str(ROOT_DIR / "artifacts" / "signer_public_key.pem")

        # Compute
        res = self.controller.compute_fingerprint(pub_path)
        self.assertTrue(res["success"])
        self.assertTrue(res["fingerprint"].startswith("SHA256:"))

        # Trust match
        res_match = self.controller.compute_fingerprint(pub_path, expected=res["fingerprint"])
        self.assertTrue(res_match["success"])
        self.assertTrue(res_match["matches"])

        # Trust mismatch
        res_mismatch = self.controller.compute_fingerprint(pub_path, expected="SHA256:00:11:22:33")
        self.assertTrue(res_mismatch["success"])
        self.assertFalse(res_mismatch["matches"])


if __name__ == "__main__":
    unittest.main()
