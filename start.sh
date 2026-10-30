#!/usr/bin/env bash
# CryptoGuard - Ed25519 Document Verification System Launcher

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo " CryptoGuard - Ed25519 Document Verification System"
echo "======================================================================"
echo ""

if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python was not found in PATH."
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Starting local application server..."
echo "Serving Web Application at http://localhost:8080"
echo ""

$PYTHON_CMD server.py 8080
