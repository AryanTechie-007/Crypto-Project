# Digital Signature-Based Document Verification System

> **A Python-based digital document verification system using Ed25519 digital signatures, tamper detection, public-key verification, and cryptographic trust validation.**

[![Algorithm](https://img.shields.io/badge/Algorithm-Ed25519%20(RFC%208032)-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](#)
[![Library](https://img.shields.io/badge/Cryptography-pyca%2Fcryptography-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

---

## 📌 Project Overview

This project implements **Digital Signature-Based Document Verification** for the University Cryptography curriculum.

The core objective is to allow an author to digitally sign a document using the **Ed25519** scheme and allow any third-party verifier to independently verify:
1. **Document Integrity:** Confirmation that not a single byte, space, or character has been modified.
2. **Signature Authenticity:** Confirmation that the detached signature was produced by the holder of the corresponding Ed25519 private key.
3. **Public-Key Trust:** Verification of the public key's fingerprint against an authenticated reference, distinguishing mathematical validity from real-world signer identity.

---

## 🏗️ Repository Architecture

```
Crypto-Project/
├── .gitignore                      # Excludes private keys, caches, virtual environments
├── requirements.txt                # Project dependencies (cryptography, pytest)
├── README.md                       # Project documentation & execution guide
│
├── src/                            # Core source code
│   ├── __init__.py                 # Package declaration and public API exports
│   ├── key_manager.py              # [Person 1] Ed25519 key generation, PEM serialization & security
│   ├── document_signer.py          # [Person 1] Detached document signing (exact byte preservation)
│   ├── signature_verifier.py       # [Person 1/2] Safe signature verification & error handling
│   ├── key_fingerprint.py          # [Person 1/2] Canonical public-key SHA-256 fingerprinting
│   └── main.py                     # [Person 3] CLI application and workflow orchestrator
│
├── tests/                          # Automated test suite (unittest / pytest compatible)
│   ├── __init__.py
│   ├── test_key_generation.py      # [Person 1] Tests key generation, serialization, passphrase protection
│   ├── test_sign_verify.py         # [Person 1/2] Tests signing, verification, and tamper detection
│   ├── test_security_experiments.py # [Person 2] Five required security experiments & key-trust tests
│   └── test_cli.py                 # [Person 3] End-to-end CLI command and workflow tests
│
├── sample_data/                    # Sample documents for verification
│   └── sample_document.txt         # Synthetic university academic credential
│
├── artifacts/                      # Public submission deliverables (Requirement 8 compliant)
│   ├── README.md                   # Explanation of artifacts & private key exclusion
│   ├── signer_public_key.pem       # Authentic public key (SPKI PEM format)
│   └── sample_document.sig         # 64-byte detached digital signature of sample_document.txt
│
└── docs/                           # Technical documentation & security analysis
    ├── cryptographic_architecture.md # [Person 1] Mathematical basis, threat model & API spec
    └── experiments.md              # [Person 2] Security experiments log & observations
```


## 🚀 Quick Start & Installation

### 1. Prerequisites
* Python 3.9+ (Python 3.11+ recommended)
* `pip` package manager

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/AryanTechie-007/Crypto-Project.git
cd Crypto-Project

# (Optional) Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Automated Test Suite
All 34 tests use Python's built-in `unittest` runner (no external test runner required) and are also fully compatible with `pytest`:
```bash
# Using standard Python unittest runner:
python -m unittest discover tests -v

# Or using pytest (if installed):
pytest -v
```

---

## 💻 Command-Line Interface (CLI)

The application provides a unified CLI orchestrator in `src/main.py`:

```bash
python -m src.main --help
```

### 1. Verify Sample Document (Default Submission Artifacts)
Verify the repository's pre-signed document against its detached signature and public key:
```bash
python -m src.main verify
```
Or specify explicit file paths:
```bash
python -m src.main verify \
    --document sample_data/sample_document.txt \
    --signature artifacts/sample_document.sig \
    --public-key artifacts/signer_public_key.pem
```

### 2. Display and Check Public-Key Fingerprint (Trust Validation)
Compute the canonical SHA-256 fingerprint:
```bash
python -m src.main fingerprint --public-key artifacts/signer_public_key.pem
```
Optionally verify the public key against an expected, trusted reference to detect substitution attacks:
```bash
python -m src.main fingerprint \
    --public-key artifacts/signer_public_key.pem \
    --expected "SHA256:56:fe:17:fc:1f:68:09:4e:93:34:a6:9f:9b:fe:fc:30:d9:4b:f9:37:94:43:82:d1:72:d7:79:fc:8f:db:c2:c3"
```

### 3. Generate a New Key Pair
Generate a new Ed25519 private key (optionally passphrase encrypted) and SPKI public key:
```bash
# Prompted interactively for passphrase:
python -m src.main keygen --private-key private/new_key.pem --public-key keys/new_pub.pem

# Or without passphrase (unencrypted):
python -m src.main keygen --private-key private/unenc.pem --public-key keys/unenc.pem --no-password
```

### 4. Sign a Document (Detached Signature)
Generate an exact 64-byte detached `.sig` file for any document:
```bash
python -m src.main sign \
    --document sample_data/sample_document.txt \
    --private-key private/new_key.pem \
    --signature my_doc.sig
```

### 5. Run Complete Demonstration Workflow
Runs the entire 3-phase demonstration: auditing repository artifacts, generating a demo key pair, signing, verifying, fingerprint trust matching, and demonstrating tamper detection:
```bash
python -m src.main all
```

---

## 🔑 Core Python API Usage

### 1. Generating an Ed25519 Key Pair
```python
from src.key_manager import KeyManager

# Generate keys in memory
private_key, public_key = KeyManager.generate_key_pair()

# Save public key (safe for distribution)
KeyManager.save_public_key(public_key, "artifacts/signer_public_key.pem")

# Save private key securely (optionally password-protected)
KeyManager.save_private_key(private_key, "private/my_private_key.pem", password="MySecurePassword!")
```

### 2. Signing a Document (Detached Signature)
```python
from src.document_signer import DocumentSigner

# Generates a 64-byte detached .sig file, leaving original document unchanged
signature = DocumentSigner.sign_document(
    document_path="sample_data/sample_document.txt",
    private_key="private/my_private_key.pem",
    signature_output_path="artifacts/sample_document.sig",
    password="MySecurePassword!"
)
```

### 3. Verifying a Document Signature
```python
from src.signature_verifier import SignatureVerifier

result = SignatureVerifier.verify_document(
    document_path="sample_data/sample_document.txt",
    signature_source="artifacts/sample_document.sig",
    public_key_source="artifacts/signer_public_key.pem"
)

print("Is Authentic:", result.is_valid)
print("Details:", result.message)
```

### 4. Computing Public-Key Fingerprint (Trust Verification)
```python
from src.key_fingerprint import KeyFingerprint

fingerprint = KeyFingerprint.compute_fingerprint("artifacts/signer_public_key.pem")
print("Public Key Fingerprint:", fingerprint)
# Output: SHA256:xx:xx:xx:...
```

---

## 🔒 Security & Key Management (Requirement 8)

* **Private Key Protection:** In strict compliance with assignment guidelines, **private keys are never committed to this repository**.
* `.gitignore` prevents inadvertent commits of private keys (`*.key`, `*.priv`, `*private*`, `*.pkcs8`).
* The submission includes only the **sample document**, the **detached signature**, and the **public key** needed for independent verification.

---

## 📄 License
This project is developed for educational and academic assessment purposes.
