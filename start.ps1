<#
.SYNOPSIS
    CryptoGuard - Ed25519 Document Verification System Launcher for PowerShell
#>

$Host.UI.RawUI.WindowTitle = "CryptoGuard - Ed25519 Document Verification System"
Set-Location -Path $PSScriptRoot

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " CryptoGuard - Ed25519 Document Verification System" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python was not found in PATH." -ForegroundColor Red
    Write-Host "Please ensure Python 3.9+ is installed and added to PATH." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting local application server..." -ForegroundColor Green
Write-Host "Serving Web Application at http://localhost:8080" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop.`n" -ForegroundColor DarkGray

python server.py 8080
