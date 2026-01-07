<#
.SYNOPSIS
  Serve a frontend project with smart install and package-manager detection.

.PARAMETER ForceInstall
  Force reinstall dependencies even if node_modules exists.

.PARAMETER DevScript
  Preferred dev script name (default: "dev"). Falls back to "start".
#>

param(
    [switch]$ForceInstall,
    [string]$DevScript = "dev"
)

function Write-Info($m){ Write-Host "[INFO]  $m" -ForegroundColor Cyan }
function Write-Warn($m){ Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }

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
    return $false
}

function Install-Dependencies($pm) {
    Write-Info "Installing dependencies with $pm..."
    switch ($pm) {
        "pnpm" { & pnpm install; return $LASTEXITCODE }
        "yarn" { & yarn install; return $LASTEXITCODE }
        default { & npm install; return $LASTEXITCODE }
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

# Main flow
if (Test-Path "package.json") {
    Write-Info "Detected framework-based project (package.json found)."
    $pm = Get-PackageManager
    if (-not $pm) { Write-Warn "No package manager detected; defaulting to npm."; $pm = "npm" }

    if (Needs-Install $ForceInstall) {
        $code = Install-Dependencies $pm
        if ($code -ne 0) { Write-Err "Dependency install failed (exit $code)"; exit $code }
    } else {
        Write-Info "Dependencies appear up-to-date."
    }

    $pkg = Get-Content package.json -Raw | ConvertFrom-Json
    $scriptToRun = $null
    if ($pkg.scripts -and $pkg.scripts.$DevScript) { $scriptToRun = $DevScript }
    elseif ($pkg.scripts -and $pkg.scripts.start) { $scriptToRun = "start" }

    if (-not $scriptToRun) {
        Write-Warn "No '$DevScript' or 'start' script found in package.json. Exiting."
        exit 2
    }

    Start-DevServer $pm $scriptToRun
    exit $LASTEXITCODE

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
                Write-Err 'Failed to install "serve"'
                exit $LASTEXITCODE
            }
        }
        & serve .
        exit $LASTEXITCODE
    }
}
