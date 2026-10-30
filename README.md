# Digital Signature-Based Document Verification System

> **A modern digital document verification system using Ed25519 digital signatures, tamper detection, public-key verification, and cryptographic trust validation with an interactive Drag-and-Drop Web Application.**

[![Algorithm](https://img.shields.io/badge/Algorithm-Ed25519%20(RFC%208032)-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](#)
[![Library](https://img.shields.io/badge/Cryptography-pyca%2Fcryptography-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

---

## 📌 Project Overview

This project implements **Project 4: Digital Signature-Based Document Verification** for the University Cryptography curriculum.

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
├── package.json                    # Web frontend package manifest (TypeScript)
├── tsconfig.json                   # TypeScript compiler configuration
├── start.bat                       # [Batchfile] Windows 1-click launcher
├── start.sh                        # [Shell] Linux/macOS 1-click launcher
├── server.py                       # [Python] In-memory HTTP cryptographic API server
├── README.md                       # Project documentation & execution guide
│
├── web/                            # Interactive Web Application (TypeScript / JS / HTML / CSS)
│   ├── index.html                  # [HTML] Semantic interface with Vertical Tabs & Dropzones
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # [CSS] Modern glassmorphic styles, animations & themes
│   │   └── js/
│   │       ├── api.js              # [JavaScript] HTTP API client module
│   │       ├── dropzone.js         # [JavaScript] Drag-and-drop file manager
│   │       └── app.js              # [JavaScript] App controller & dynamic UI renderer
│   └── src/
│       ├── types.ts                # [TypeScript] Strong type definitions
│       ├── api.ts                  # [TypeScript] Typed API client
│       ├── dropzone.ts             # [TypeScript] Drag-and-drop manager class
│       └── app.ts                  # [TypeScript] Main application orchestrator
│
├── src/                            # Core Cryptographic Engine (RFC 8032 Ed25519)
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
│   ├── test_cli.py                 # [Person 3] End-to-end CLI command and workflow tests
│   └── test_web_api.py             # [Team] In-memory Web API and static file serving tests
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

---

## 🚀 Quick Start & Launch

### 1. Launch the CryptoGuard Application

Launch the application with **Vertical Navigation Tabs** and **Drag-and-Drop Dropzones** (zero hardcoded paths):

**On Windows:**
Double-click `start.bat` or run:
```powershell
.\start.bat
# or: python server.py
```

**On Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
# or: python3 server.py
```

The application starts at **`http://localhost:8080`** and opens automatically in your default browser.

---

### 2. Run the Automated Test Suite
All 42 tests use Python's built-in `unittest` runner and are also fully compatible with `pytest`:
```bash
# Using standard Python unittest runner:
python -m unittest discover tests -v

# Or using pytest (if installed):
pytest -v
```

---

## 🖥️ Application Features & Workflows

1. **Vertical Navigation Tabs:**
   * Left-hand sidebar with tabs for **Verify Document**, **Sign Document**, **Generate Keys**, **Key Fingerprint**, and **Security Lab**.
2. **Drag-and-Drop Logic:**
   * Interactive dropzones for documents, detached `.sig` signatures, and `.pem` keys with dragover animations, file previews, and instant byte parsing.
3. **Zero Hardcoded Paths:**
   * All files are read in-memory directly in the browser and transmitted as Base64 payloads to the in-memory cryptographic core.
4. **Document Verification:**
   * Instant color-coded badges: **Green** for Authentic and unmodified documents; **Red** for tampered files, invalid keys, or corrupted signatures.
   * Auto-extracts the signer's public key fingerprint.
5. **Interactive Security Lab:**
   * Executes all 5 required university security experiments live in one click.

---

## 💻 Command-Line Interface (CLI)

The CLI orchestrator in `src/main.py` is preserved for scripting:

```bash
python -m src.main verify
python -m src.main keygen
python -m src.main sign
python -m src.main fingerprint
python -m src.main all
```

---

## 🔒 Security & Key Management (Requirement 8)

* **Private Key Protection:** In strict compliance with assignment guidelines, **private keys are never committed to this repository**.
* `.gitignore` prevents inadvertent commits of private keys (`*.key`, `*.priv`, `*private*`, `*.pkcs8`).
* The submission includes only the **sample document**, the **detached signature**, and the **public key** needed for independent verification.

---

## 📄 License
This project is developed for educational and academic assessment purposes.
