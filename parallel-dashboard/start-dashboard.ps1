# Start backend + dashboard (run on machine with opencode installed)
# Usage: powershell -ExecutionPolicy Bypass -File start-dashboard.ps1
$ErrorActionPreference = "Stop"
$dashDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Get-Command opencode -ErrorAction SilentlyContinue)) { throw "opencode not found in PATH. Install it first, then re-run." }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "python not found in PATH. Needed for 'python -m http.server'." }
# opencode 1.18+ serve requires basic auth: keep a localhost-only password and reuse it in the dashboard header.
if (-not $env:OPENCODE_SERVER_PASSWORD) { $env:OPENCODE_SERVER_PASSWORD = 'parallel-local-01' }
Write-Host "1) Starting opencode serve on :4097 with CORS for :8000 ..."
Start-Process -FilePath "opencode" -ArgumentList "serve","--port","4097","--cors","http://localhost:8000"
Write-Host "2) Serving dashboard on :8000 ..."
Set-Location -LiteralPath $dashDir
python -m http.server 8000
