"""Security experiments and fingerprint trust tests (Person 2).

These tests distinguish mathematical signature verification from trust in
the identity claimed for a public key.
"""
import tempfile
import unittest
from pathlib import Path

from src.document_signer import DocumentSigner
from src.key_fingerprint import KeyFingerprint
from src.key_manager import KeyManager
from src.signature_verifier import SignatureVerifier


class TestPublicKeyTrustAndExperiments(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.author_private, self.author_public = KeyManager.generate_key_pair()
        self.attacker_private, self.attacker_public = KeyManager.generate_key_pair()

        self.document = self.root / "document.txt"
        self.document.write_bytes(b"University credential: Alice, ID 12345")

        self.signature = self.root / "document.sig"
        DocumentSigner.sign_document(
            self.document,
            self.author_private,
            signature_output_path=self.signature,
        )

        self.author_public_path = self.root / "author_public.pem"
        self.attacker_public_path = self.root / "attacker_public.pem"
        KeyManager.save_public_key(self.author_public, self.author_public_path)
        KeyManager.save_public_key(self.attacker_public, self.attacker_public_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_original_document_verifies(self):
        result = SignatureVerifier.verify_document(
            self.document, self.signature, self.author_public_path
        )
        self.assertTrue(result.is_valid)

    def test_wrong_public_key_is_rejected(self):
        result = SignatureVerifier.verify_document(
            self.document, self.signature, self.attacker_public_path
        )
        self.assertFalse(result.is_valid)

    def test_attacker_key_substitution_is_cryptographically_valid_but_untrusted(self):
        """Attacker's own signature verifies, but their key fails Alice's trusted pin."""
        replacement_document = self.root / "replacement.txt"
        replacement_document.write_bytes(
            b"University credential: Alice, ID 12345 [attacker replacement]"
        )
        replacement_signature = self.root / "replacement.sig"
        DocumentSigner.sign_document(
            replacement_document,
            self.attacker_private,
            signature_output_path=replacement_signature,
        )

        # Mathematics alone succeeds under the attacker's supplied public key.
        crypto_result = SignatureVerifier.verify_document(
            replacement_document,
            replacement_signature,
            self.attacker_public_path,
        )
        self.assertTrue(crypto_result.is_valid)

        # The verifier already knows Alice's fingerprint through a trusted channel.
        alice_trusted_fingerprint = KeyFingerprint.compute_fingerprint(
            self.author_public_path
        )
        self.assertFalse(
            KeyFingerprint.verify_fingerprint(
                self.attacker_public_path, alice_trusted_fingerprint
            )
        )

    def test_fingerprint_matches_across_supported_key_representations(self):
        pem_fingerprint = KeyFingerprint.compute_fingerprint(self.author_public_path)
        raw_public_key = KeyManager.export_public_key_raw(self.author_public)
        raw_fingerprint = KeyFingerprint.compute_fingerprint(raw_public_key)
        object_fingerprint = KeyFingerprint.compute_fingerprint(self.author_public)

        self.assertEqual(pem_fingerprint, raw_fingerprint)
        self.assertEqual(pem_fingerprint, object_fingerprint)

    def test_different_keys_have_different_fingerprints(self):
        author_fp = KeyFingerprint.compute_fingerprint(self.author_public)
        attacker_fp = KeyFingerprint.compute_fingerprint(self.attacker_public)
        self.assertNotEqual(author_fp, attacker_fp)

    def test_fingerprint_mismatch_returns_false(self):
        trusted = KeyFingerprint.compute_fingerprint(self.author_public)
        self.assertFalse(
            KeyFingerprint.verify_fingerprint(self.attacker_public, trusted)
        )

    def test_fingerprint_comparison_is_case_and_whitespace_tolerant(self):
        fingerprint = KeyFingerprint.compute_fingerprint(self.author_public)
        self.assertTrue(
            KeyFingerprint.verify_fingerprint(
                self.author_public, "  " + fingerprint.lower() + "  "
            )
        )

    def test_malformed_fingerprint_inputs_fail_safely(self):
        self.assertFalse(
            KeyFingerprint.verify_fingerprint(b"not a public key", "SHA256:00")
        )
        self.assertFalse(
            KeyFingerprint.verify_fingerprint(self.author_public, None)
        )

    def test_verifier_rejects_invalid_argument_types_without_raising(self):
        bad_document = SignatureVerifier.verify_document(
            None, self.signature, self.author_public
        )
        self.assertFalse(bad_document.is_valid)
        self.assertIn("Invalid document path", bad_document.message)

        bad_signature = SignatureVerifier.verify_document(
            self.document, object(), self.author_public
        )
        self.assertFalse(bad_signature.is_valid)
        self.assertIn("Invalid signature source type", bad_signature.message)

        bad_key = SignatureVerifier.verify_document(
            self.document, self.signature, object()
        )
        self.assertFalse(bad_key.is_valid)
        self.assertIn("Invalid public key source type", bad_key.message)


if __name__ == "__main__":
    unittest.main()
