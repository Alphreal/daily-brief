# orca_watchdog.ps1 — keep the Orca runtime alive.
# Runs every 15 min via Task Scheduler ("Orca-Watchdog").
# Healthy (runtime reachable) -> silent exit 0. Down -> log + fire `orca open`, exit 1.
$ErrorActionPreference = "SilentlyContinue"
$logDir = Join-Path $env:TEMP "opencode"
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$status = (& orca status 2>&1 | Out-String)
if ($status -match "runtimeReachable:\s*true") { exit 0 }
Add-Content -Path (Join-Path $logDir "orca-watchdog.log") -Value ("$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') runtime down, restarting via orca open")
Start-Process -FilePath "orca" -ArgumentList "open" -WindowStyle Hidden
exit 1
