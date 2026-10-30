@echo off
setlocal
title CryptoGuard - Ed25519 Document Verification System
cd /d "%~dp0"

echo ======================================================================
echo  CryptoGuard - Ed25519 Document Verification System
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 was not found in PATH.
    echo Please install Python 3.9+ from https://python.org and add to PATH.
    pause
    exit /b 1
)

echo Starting local application server...
echo Serving Web Application at http://localhost:8080
echo.

python server.py 8080

pause
