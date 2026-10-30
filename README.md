# Digital Signature-Based Document Verification System

> **A modern standalone desktop application built with Electron, TypeScript, JavaScript, HTML5, CSS3, Shell, Batchfile, and Python for Ed25519 digital signatures, tamper detection, and cryptographic trust validation with Drag-and-Drop logic and Vertical Tabs.**

[![Platform](https://img.shields.io/badge/Platform-Electron%20Desktop-blueviolet.svg)](#)
[![Algorithm](https://img.shields.io/badge/Algorithm-Ed25519%20(RFC%208032)-blue.svg)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

---

## ðŸ“Œ Project Overview

This project implements **Project 4: Digital Signature-Based Document Verification** for the University Cryptography curriculum.

The core objective is to allow an author to digitally sign a document using the **Ed25519** scheme and allow any third-party verifier to independently verify:
1. **Document Integrity:** Confirmation that not a single byte, space, or character has been modified.
2. **Signature Authenticity:** Confirmation that the detached signature was produced by the holder of the corresponding Ed25519 private key.
3. **Public-Key Trust:** Verification of the public key's fingerprint against an authenticated reference, distinguishing mathematical validity from real-world signer identity.

---

## ðŸ—ï¸ Repository Architecture

```
Crypto-Project/
â”œâ”€â”€ .gitignore                      # Excludes private keys, caches, virtual environments
â”œâ”€â”€ requirements.txt                # Python cryptographic dependencies (cryptography, pytest)
â”œâ”€â”€ package.json                    # Electron & TypeScript project manifest
â”œâ”€â”€ tsconfig.json                   # Web TypeScript compiler configuration
â”œâ”€â”€ tsconfig.electron.json          # Electron TypeScript compiler configuration
â”œâ”€â”€ start.ps1                       # [PowerShell] Native PowerShell 1-click desktop launcher
â”œâ”€â”€ start.bat                       # [Batchfile] Windows 1-click desktop launcher
â”œâ”€â”€ start.sh                        # [Shell] Linux/macOS 1-click desktop launcher
â”œâ”€â”€ server.py                       # [Python] In-memory cryptographic engine & backend service
â”œâ”€â”€ README.md                       # Project documentation & execution guide
â”‚
â”œâ”€â”€ electron/                       # Electron Desktop Application Source (TypeScript)
â”‚   â”œâ”€â”€ main.ts                     # Main process (window manager & background backend orchestrator)
â”‚   â””â”€â”€ preload.ts                  # Secure preload bridge exposing window controls
â”‚
â”œâ”€â”€ dist-electron/                  # Compiled Electron Main & Preload JavaScript
â”‚   â”œâ”€â”€ main.js
â”‚   â””â”€â”€ preload.js
â”‚
â”œâ”€â”€ web/                            # Desktop UI Layer (TypeScript / JS / HTML / CSS)
â”‚   â”œâ”€â”€ index.html                  # Semantic desktop shell with Vertical Tabs & Dropzones
â”‚   â”œâ”€â”€ static/
â”‚   â”‚   â”œâ”€â”€ css/
â”‚   â”‚   â”‚   â””â”€â”€ styles.css          # Modern glassmorphic styles, animations & themes
â”‚   â”‚   â””â”€â”€ js/
â”‚   â”‚       â”œâ”€â”€ api.js              # Native HTTP API client module
â”‚   â”‚       â”œâ”€â”€ dropzone.js         # Interactive drag-and-drop file manager
â”‚   â”‚       â””â”€â”€ app.js              # App controller & dynamic UI renderer
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ types.ts                # Strong TypeScript interfaces
â”‚       â”œâ”€â”€ api.ts                  # Strongly typed API client
â”‚       â”œâ”€â”€ dropzone.ts             # Drag-and-drop manager class
â”‚       â””â”€â”€ app.ts                  # Main UI orchestrator
â”‚
â”œâ”€â”€ src/                            # Core Cryptographic Engine (RFC 8032 Ed25519)
â”‚   â”œâ”€â”€ __init__.py                 # Package declaration and public API exports
â”‚   â”œâ”€â”€ key_manager.py              # [Person 1] Ed25519 key generation, PEM serialization & security
â”‚   â”œâ”€â”€ document_signer.py          # [Person 1] Detached document signing (exact byte preservation)
â”‚   â”œâ”€â”€ signature_verifier.py       # [Person 1/2] Safe signature verification & error handling
â”‚   â”œâ”€â”€ key_fingerprint.py          # [Person 1/2] Canonical public-key SHA-256 fingerprinting
â”‚   â””â”€â”€ main.py                     # [Person 3] CLI application and workflow orchestrator
â”‚
â”œâ”€â”€ tests/                          # Automated test suite (unittest / pytest compatible)
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ test_key_generation.py      # [Person 1] Tests key generation, serialization, passphrase protection
â”‚   â”œâ”€â”€ test_sign_verify.py         # [Person 1/2] Tests signing, verification, and tamper detection
â”‚   â”œâ”€â”€ test_security_experiments.py # [Person 2] Five required security experiments & key-trust tests
â”‚   â”œâ”€â”€ test_cli.py                 # [Person 3] End-to-end CLI command and workflow tests
â”‚   â””â”€â”€ test_web_api.py             # [Team] In-memory API and static file serving tests
â”‚
â”œâ”€â”€ sample_data/                    # Sample documents for verification
â”‚   â””â”€â”€ sample_document.txt         # Synthetic university academic credential
â”‚
â”œâ”€â”€ artifacts/                      # Public submission deliverables (Requirement 8 compliant)
â”‚   â”œâ”€â”€ README.md                   # Explanation of artifacts & private key exclusion
â”‚   â”œâ”€â”€ signer_public_key.pem       # Authentic public key (SPKI PEM format)
â”‚   â””â”€â”€ sample_document.sig         # 64-byte detached digital signature of sample_document.txt
â”‚
â””â”€â”€ docs/                           # Technical documentation & security analysis
    â”œâ”€â”€ cryptographic_architecture.md # [Person 1] Mathematical basis, threat model & API spec
    â””â”€â”€ experiments.md              # [Person 2] Security experiments log & observations
```

---

## ðŸš€ Launch the Electron Desktop Application

Launch the native desktop application with **Vertical Navigation Tabs** and **Drag-and-Drop Dropzones** (zero hardcoded paths):

### From PowerShell:
```powershell
.\start.ps1
# or: npm start
```

### From Windows Command Prompt:
```cmd
start.bat
```

### From Linux / macOS:
```bash
chmod +x start.sh
./start.sh
```

---

## ðŸ§ª Run Automated Tests
All 32 tests use Python's built-in `unittest` runner and are also fully compatible with `pytest`:
```bash
python -m unittest discover tests -v
```

---

## ðŸ–¥ï¸ Desktop Application Features

1. **Standalone Electron Window:**
   * Runs in its own dedicated, native desktop window (no browser tabs, no URL bar, native system controls).
2. **Vertical Navigation Tabs:**
   * Left-hand sidebar with tabs for **Verify Document**, **Sign Document**, **Generate Keys**, **Key Fingerprint**, and **Key Fingerprint**.
3. **Drag-and-Drop Logic:**
   * Interactive dropzones for documents, detached `.sig` signatures, and `.pem` keys with dragover animations, file previews, and instant byte parsing.
4. **Zero Hardcoded Paths:**
   * All files are read in-memory directly in the client and transmitted as Base64 payloads to the in-memory cryptographic core.
5. **Document Verification:**
   * Instant color-coded badges: **Green** for Authentic and unmodified documents; **Red** for tampered files, invalid keys, or corrupted signatures.
   * Auto-extracts the signer's public key fingerprint.


---

## ðŸ’» Command-Line Interface (CLI)

The CLI orchestrator in `src/main.py` is preserved for scripting:

```bash
python -m src.main verify
python -m src.main keygen
python -m src.main sign
python -m src.main fingerprint
python -m src.main all
```

---

## ðŸ”’ Security & Key Management (Requirement 8)

* **Private Key Protection:** In strict compliance with assignment guidelines, **private keys are never committed to this repository**.
* `.gitignore` prevents inadvertent commits of private keys (`*.key`, `*.priv`, `*private*`, `*.pkcs8`).
* The submission includes only the **sample document**, the **detached signature**, and the **public key** needed for independent verification.

---

## ðŸ“„ License
This project is developed for educational and academic assessment purposes.
