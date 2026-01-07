<#
.SYNOPSIS
  Serve a frontend project with smart install, package-manager detection, and optional watch/restart.

.PARAMETER ForceInstall
  Force reinstall dependencies even if node_modules exists.

.PARAMETER DevScript
  Preferred dev script name (default: "dev"). Falls back to "start".

.PARAMETER Watch
  If set, watch package.json and lockfiles and restart the dev server on changes.
#>

param(
    [switch]$ForceInstall,
    [string]$DevScript = "dev",
    [switch]$Watch
)

function Write-Info($m){ Write-Host "[INFO]  $m" -ForegroundColor Cyan }
function Write-Warn($m){ Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }

# Run from script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($scriptDir) { Set-Location $scriptDir }

# Detect package manager
function Get-PackageManager {
    if (Test-Path "pnpm-lock.yaml") { return "pnpm" }
    if (Test-Path "yarn.lock") { return "yarn" }
    if (Test-Path "package-lock.json") { return "npm" }
    if (Get-Command pnpm -ErrorAction SilentlyContinue) { return "pnpm" }
    if (Get-Command yarn -ErrorAction SilentlyContinue) { return "yarn" }
    if (Get-Command npm -ErrorAction SilentlyContinue) { return "npm" }
    return $null
}

function Needs-Install {
    param($Force)
    if ($Force) { return $true }
    if (-not (Test-Path "node_modules")) { return $true }
    $lockFiles = @("package-lock.json","yarn.lock","pnpm-lock.yaml") | Where-Object { Test-Path $_ }
    if ($lockFiles) {
        foreach ($lf in $lockFiles) {
            if ((Get-Item $lf).LastWriteTime -gt (Get-Item "node_modules").LastWriteTime) { return $true }
        }
    }
    return $false
}

function Install-Dependencies($pm) {
    Write-Info "Installing dependencies with $pm..."
    switch ($pm) {
        "pnpm" {
            if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
                Write-Warn "pnpm not found, falling back to npm"
                & npm install
                return $LASTEXITCODE
            }
            & pnpm install
            return $LASTEXITCODE
        }
        "yarn" {
            if (-not (Get-Command yarn -ErrorAction SilentlyContinue)) {
                Write-Warn "yarn not found, falling back to npm"
                & npm install
                return $LASTEXITCODE
            }
            & yarn install
            return $LASTEXITCODE
        }
        default {
            & npm ci 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "npm ci failed, trying npm install"
                & npm install
            }
            return $LASTEXITCODE
        }
    }
}

function Start-DevServer($pm, $scriptName) {
    Write-Info "Starting dev server using script '$scriptName' with $pm..."
    switch ($pm) {
        "pnpm" { & pnpm run $scriptName; return $LASTEXITCODE }
        "yarn" { & yarn $scriptName; return $LASTEXITCODE }
        default { & npm run $scriptName; return $LASTEXITCODE }
    }
}

# Watch mode helper
function Watch-And-Restart($pm, $scriptName) {
    $filesToWatch = @("package.json","package-lock.json","yarn.lock","pnpm-lock.yaml") | Where-Object { Test-Path $_ }
    if (-not $filesToWatch) { Write-Warn "No files to watch. Exiting watch mode."; return }

    Write-Info "Starting watch mode. Dev server will restart on changes."
    $fsw = New-Object System.IO.FileSystemWatcher
    $fsw.Path = Get-Location
    $fsw.Filter = "*.*"
    $fsw.IncludeSubdirectories = $false
    $fsw.EnableRaisingEvents = $true

    $debounce = $false

    $action = {
        param($source, $event)
        if ($debounce) { return }
        $debounce = $true
        Write-Info "Detected change in $($event.Name). Restarting dev server..."
        if ($global:devProcess) { Stop-Process -Id $global:devProcess.Id -Force }
        Start-Job -ScriptBlock {
            param($pm,$scriptName)
            $p = Start-Process -FilePath $pm -ArgumentList "run $scriptName" -NoNewWindow -PassThru
            $global:devProcess = $p
        } -ArgumentList $pm,$scriptName | Out-Null
        Start-Sleep -Seconds 1
        $debounce = $false
    }

    Register-ObjectEvent $fsw "Changed" -Action $action | Out-Null
    Register-ObjectEvent $fsw "Created" -Action $action | Out-Null
    Register-ObjectEvent $fsw "Deleted" -Action $action | Out-Null
    Register-ObjectEvent $fsw "Renamed" -Action $action | Out-Null

    # Start the initial dev server
    $global:devProcess = Start-Process -FilePath $pm -ArgumentList "run $scriptName" -NoNewWindow -PassThru

    Write-Info "Press Ctrl+C to stop watch mode."
    while ($true) { Start-Sleep -Seconds 1 }
}

# Main flow
if (Test-Path "package.json") {
    Write-Info "Detected framework-based project (package.json found)."
    $pm = Get-PackageManager
    if (-not $pm) {
        Write-Warn "No package manager detected; defaulting to npm."
        $pm = "npm"
    } else { Write-Info "Using package manager: $pm" }

    if (Needs-Install $ForceInstall) {
        $code = Install-Dependencies $pm
        if ($code -ne 0) { Write-Err "Dependency install failed (exit $code)"; exit $code }
    } else {
        Write-Info "Dependencies appear up-to-date."
    }

    # pick script
    try {
        $pkg = Get-Content package.json -Raw | ConvertFrom-Json
    } catch {
        Write-Err "Failed to parse package.json: $_"
        exit 3
    }

    $scriptToRun = $null
    if ($pkg.scripts -and $pkg.scripts.$DevScript) { $scriptToRun = $DevScript }
    elseif ($pkg.scripts -and $pkg.scripts.start) { $scriptToRun = "start" }

    if (-not $scriptToRun) {
        Write-Warn "No '$DevScript' or 'start' script found in package.json. Exiting."
        exit 2
    }

    if ($Watch) {
        Watch-And-Restart $pm $scriptToRun
    } else {
        Start-DevServer $pm $scriptToRun
        exit $LASTEXITCODE
    }

} else {
    Write-Info "No package.json found — serving static files."
    Write-Info "Attempting to use 'npx serve .'"

    & npx --yes serve . 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "'npx serve' failed. Trying global 'serve'..."
        if (-not (Get-Command serve -ErrorAction SilentlyContinue)) {
            Write-Info "Installing 'serve' globally..."
            & npm install -g serve
            if ($LASTEXITCODE -ne 0) {
                Write-Err "Failed to install 'serve'"
                exit $LASTEXITCODE
            }
        }
        & serve .
        exit $LASTEXITCODE
    }
}
