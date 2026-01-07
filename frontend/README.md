<#
.SYNOPSIS
  Smart frontend development server with automatic package manager detection,
  dependency management, hot-reload, and backend health monitoring.

.DESCRIPTION
  This script provides a production-ready development server for frontend projects.
  Features include:
  - Automatic package manager detection (pnpm, yarn, npm)
  - Smart dependency installation
  - Hot-reload with file watching
  - Backend API health monitoring
  - Graceful error handling and recovery
  - Support for both framework and static projects

.PARAMETER ForceInstall
  Force reinstall dependencies even if node_modules exists.

.PARAMETER DevScript
  Preferred dev script name (default: "dev"). Falls back to "start".

.PARAMETER Watch
  Enable watch mode to restart server on package.json or lockfile changes.

.PARAMETER BackendUrl
  Backend API URL to monitor (default: "http://127.0.0.1:8000").
  If provided, script will check backend health before starting.

.PARAMETER CheckBackend
  Check backend health and display status.

.PARAMETER Port
  Override the default port for the dev server.

.PARAMETER Open
  Automatically open browser after server starts.

.PARAMETER Verbose
  Enable verbose logging for debugging.

.EXAMPLE
  .\serve.ps1
  Start the development server with default settings.

.EXAMPLE
  .\serve.ps1 -ForceInstall
  Force reinstall dependencies and start server.

.EXAMPLE
  .\serve.ps1 -Watch -CheckBackend
  Start in watch mode and monitor backend health.

.EXAMPLE
  .\serve.ps1 -BackendUrl "http://localhost:8000" -Port 5173 -Open
  Start server on port 5173, check backend, and open browser.

.NOTES
  Author: Improved for SPMS Project
  Version: 2.0
  Compatible with: Node.js 16+, PowerShell 5.1+
#>

[CmdletBinding()]
param(
    [switch]$ForceInstall,
    [string]$DevScript = "dev",
    [switch]$Watch,
    [string]$BackendUrl = "http://127.0.0.1:8000",
    [switch]$CheckBackend,
    [int]$Port,
    [switch]$Open,
    [switch]$Verbose
)

# -------------------------
# Configuration
# -------------------------

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Config = @{
    MaxRetries = 3
    RetryDelay = 2
    BackendTimeout = 5
    WatchDebounce = 500
    SupportedPMs = @("pnpm", "yarn", "npm")
}

# -------------------------
# Logging Functions
# -------------------------

function Write-Info {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host "INFO  " -NoNewline -ForegroundColor Cyan
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host "✓     " -NoNewline -ForegroundColor Green
    Write-Host $Message -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host "WARN  " -NoNewline -ForegroundColor Yellow
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host "ERROR " -NoNewline -ForegroundColor Red
    Write-Host $Message -ForegroundColor Red
}

function Write-Debug {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
        Write-Host "DEBUG " -NoNewline -ForegroundColor Magenta
        Write-Host $Message -ForegroundColor DarkGray
    }
}

function Write-Banner {
    param([string]$Title)
    $line = "=" * 60
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

# -------------------------
# Utility Functions
# -------------------------

function Test-Command {
    param([string]$Name)
    try {
        $null = Get-Command $Name -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Get-ProjectName {
    if (Test-Path "package.json") {
        try {
            $pkg = Get-Content "package.json" -Raw | ConvertFrom-Json
            return $pkg.name
        } catch {
            return (Get-Item .).Name
        }
    }
    return (Get-Item .).Name
}

# -------------------------
# Package Manager Functions
# -------------------------

function Get-PackageManager {
    Write-Debug "Detecting package manager..."
    
    # Check for lockfiles first (most reliable)
    if (Test-Path "pnpm-lock.yaml") {
        Write-Debug "Found pnpm-lock.yaml"
        if (Test-Command "pnpm") {
            Write-Success "Detected package manager: pnpm"
            return "pnpm"
        }
        Write-Warn "pnpm lockfile found but pnpm not installed"
    }
    
    if (Test-Path "yarn.lock") {
        Write-Debug "Found yarn.lock"
        if (Test-Command "yarn") {
            Write-Success "Detected package manager: yarn"
            return "yarn"
        }
        Write-Warn "yarn lockfile found but yarn not installed"
    }
    
    if (Test-Path "package-lock.json") {
        Write-Debug "Found package-lock.json"
        if (Test-Command "npm") {
            Write-Success "Detected package manager: npm"
            return "npm"
        }
    }
    
    # Fallback to checking installed package managers
    foreach ($pm in $Config.SupportedPMs) {
        if (Test-Command $pm) {
            Write-Info "No lockfile found, using installed package manager: $pm"
            return $pm
        }
    }
    
    Write-Warn "No package manager detected, defaulting to npm"
    return "npm"
}

function Test-NeedsInstall {
    param([bool]$Force)
    
    if ($Force) {
        Write-Info "Force install requested"
        return $true
    }
    
    if (-not (Test-Path "node_modules")) {
        Write-Info "node_modules not found"
        return $true
    }
    
    $nodeModulesTime = (Get-Item "node_modules").LastWriteTime
    $lockFiles = @("package-lock.json", "yarn.lock", "pnpm-lock.yaml") | Where-Object { Test-Path $_ }
    
    if ($lockFiles) {
        foreach ($lockFile in $lockFiles) {
            $lockTime = (Get-Item $lockFile).LastWriteTime
            if ($lockTime -gt $nodeModulesTime) {
                Write-Info "Lockfile $lockFile is newer than node_modules"
                return $true
            }
        }
    }
    
    # Check if package.json is newer
    if (Test-Path "package.json") {
        $pkgTime = (Get-Item "package.json").LastWriteTime
        if ($pkgTime -gt $nodeModulesTime) {
            Write-Info "package.json is newer than node_modules"
            return $true
        }
    }
    
    Write-Success "Dependencies are up-to-date"
    return $false
}

function Install-Dependencies {
    param(
        [string]$PackageManager,
        [int]$Attempt = 1
    )
    
    if ($Attempt -gt $Config.MaxRetries) {
        Write-Err "Failed to install dependencies after $($Config.MaxRetries) attempts"
        return $false
    }
    
    if ($Attempt -gt 1) {
        Write-Info "Retry attempt $Attempt of $($Config.MaxRetries)..."
        Start-Sleep -Seconds $Config.RetryDelay
    }
    
    Write-Info "Installing dependencies with $PackageManager..."
    
    try {
        switch ($PackageManager) {
            "pnpm" {
                if (-not (Test-Command "pnpm")) {
                    Write-Warn "pnpm not found, falling back to npm"
                    return Install-Dependencies "npm" $Attempt
                }
                & pnpm install
            }
            "yarn" {
                if (-not (Test-Command "yarn")) {
                    Write-Warn "yarn not found, falling back to npm"
                    return Install-Dependencies "npm" $Attempt
                }
                & yarn install
            }
            default {
                # Try npm ci first (faster and more reliable)
                & npm ci 2>$null
                if ($LASTEXITCODE -ne 0) {
                    Write-Debug "npm ci failed, trying npm install"
                    & npm install
                }
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully"
            return $true
        } else {
            Write-Warn "Installation failed with exit code $LASTEXITCODE"
            return Install-Dependencies $PackageManager ($Attempt + 1)
        }
    } catch {
        Write-Err "Exception during installation: $_"
        return Install-Dependencies $PackageManager ($Attempt + 1)
    }
}

# -------------------------
# Backend Health Check
# -------------------------

function Test-BackendHealth {
    param([string]$Url)
    
    Write-Info "Checking backend health at $Url..."
    
    try {
        $healthUrl = "$Url/health"
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec $Config.BackendTimeout -ErrorAction Stop
        
        if ($response.status -eq "healthy") {
            Write-Success "Backend is healthy"
            Write-Host "  Version: $($response.version)" -ForegroundColor Green
            Write-Host "  Environment: $($response.environment)" -ForegroundColor Green
            
            if ($response.checks.database.status -eq "connected") {
                Write-Host "  Database: Connected" -ForegroundColor Green
            } else {
                Write-Warn "  Database: Not connected"
            }
            
            return $true
        } else {
            Write-Warn "Backend status: $($response.status)"
            return $false
        }
    } catch {
        Write-Warn "Backend health check failed: $($_.Exception.Message)"
        Write-Info "Make sure the backend is running at $Url"
        return $false
    }
}

# -------------------------
# Development Server Functions
# -------------------------

function Get-DevScript {
    param([string]$PreferredScript)
    
    if (-not (Test-Path "package.json")) {
        return $null
    }
    
    try {
        $pkg = Get-Content "package.json" -Raw | ConvertFrom-Json
        
        if (-not $pkg.scripts) {
            Write-Warn "No scripts found in package.json"
            return $null
        }
        
        # Check preferred script
        if ($pkg.scripts.$PreferredScript) {
            Write-Success "Found '$PreferredScript' script"
            return $PreferredScript
        }
        
        # Fallback scripts
        $fallbacks = @("start", "serve", "dev-server")
        foreach ($script in $fallbacks) {
            if ($pkg.scripts.$script) {
                Write-Info "Using fallback script: $script"
                return $script
            }
        }
        
        Write-Warn "No dev script found. Available scripts:"
        $pkg.scripts.PSObject.Properties | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor Gray
        }
        
        return $null
    } catch {
        Write-Err "Error reading package.json: $_"
        return $null
    }
}

function Start-DevServer {
    param(
        [string]$PackageManager,
        [string]$ScriptName,
        [hashtable]$EnvVars = @{}
    )
    
    Write-Info "Starting development server..."
    Write-Host "  Script: $ScriptName" -ForegroundColor Cyan
    Write-Host "  Package Manager: $PackageManager" -ForegroundColor Cyan
    
    if ($Port) {
        $EnvVars["PORT"] = $Port
        Write-Host "  Port: $Port" -ForegroundColor Cyan
    }
    
    # Set environment variables
    foreach ($key in $EnvVars.Keys) {
        [System.Environment]::SetEnvironmentVariable($key, $EnvVars[$key], "Process")
    }
    
    try {
        switch ($PackageManager) {
            "pnpm" {
                & pnpm run $ScriptName
            }
            "yarn" {
                & yarn $ScriptName
            }
            default {
                & npm run $ScriptName
            }
        }
        return $LASTEXITCODE
    } catch {
        Write-Err "Failed to start dev server: $_"
        return 1
    }
}

# -------------------------
# Watch Mode Functions
# -------------------------

function Start-WatchMode {
    param(
        [string]$PackageManager,
        [string]$ScriptName
    )
    
    Write-Banner "WATCH MODE ENABLED"
    Write-Info "Watching for changes in package.json and lockfiles..."
    Write-Info "Press Ctrl+C to stop"
    
    $filesToWatch = @("package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml") | 
                    Where-Object { Test-Path $_ }
    
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = (Get-Location).Path
    $watcher.Filter = "*.*"
    $watcher.IncludeSubdirectories = $false
    $watcher.EnableRaisingEvents = $true
    
    $global:restartRequested = $false
    $global:debounceTimer = $null
    
    $onChange = {
        param($sender, $eventArgs)
        $fileName = Split-Path $eventArgs.FullPath -Leaf
        
        if ($filesToWatch -contains $fileName) {
            Write-Info "Change detected in $fileName"
            
            if ($global:debounceTimer) {
                $global:debounceTimer.Stop()
                $global:debounceTimer.Dispose()
            }
            
            $global:debounceTimer = New-Object Timers.Timer $Config.WatchDebounce
            $global:debounceTimer.AutoReset = $false
            $global:debounceTimer.Add_Elapsed({
                $global:restartRequested = $true
                $global:debounceTimer.Dispose()
                $global:debounceTimer = $null
            })
            $global:debounceTimer.Start()
        }
    }
    
    $handlers = @()
    $handlers += Register-ObjectEvent $watcher "Created" -Action $onChange
    $handlers += Register-ObjectEvent $watcher "Changed" -Action $onChange
    $handlers += Register-ObjectEvent $watcher "Renamed" -Action $onChange
    $handlers += Register-ObjectEvent $watcher "Deleted" -Action $onChange
    
    try {
        while ($true) {
            Write-Info "Launching dev server..."
            
            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
            $startInfo.FileName = (Get-Command $PackageManager).Source
            $startInfo.WorkingDirectory = (Get-Location).Path
            $startInfo.UseShellExecute = $false
            
            switch ($PackageManager) {
                "pnpm" { $startInfo.Arguments = "run $ScriptName" }
                "yarn" { $startInfo.Arguments = $ScriptName }
                default { $startInfo.Arguments = "run $ScriptName" }
            }
            
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $startInfo
            $process.Start() | Out-Null
            
            while (-not $global:restartRequested) {
                Start-Sleep -Seconds 1
                
                if ($process.HasExited) {
                    Write-Warn "Dev server exited with code $($process.ExitCode)"
                    if ($process.ExitCode -ne 0) {
                        Write-Info "Waiting for file changes to restart..."
                    }
                    break
                }
            }
            
            if ($global:restartRequested) {
                Write-Info "Restarting dev server..."
                
                try {
                    if (-not $process.HasExited) {
                        $process.Kill()
                        $process.WaitForExit(5000)
                    }
                } catch {
                    Write-Debug "Error stopping process: $_"
                }
                
                $global:restartRequested = $false
                
                if (Test-NeedsInstall $false) {
                    if (-not (Install-Dependencies $PackageManager)) {
                        Write-Err "Failed to install dependencies. Exiting watch mode."
                        break
                    }
                }
                
                continue
            } else {
                break
            }
        }
    } finally {
        $handlers | ForEach-Object { Unregister-Event $_.Name -ErrorAction SilentlyContinue }
        $watcher.Dispose()
        
        if ($process -and -not $process.HasExited) {
            $process.Kill()
        }
    }
}

# -------------------------
# Static Server Functions
# -------------------------

function Start-StaticServer {
    Write-Banner "STATIC FILE SERVER"
    Write-Info "No package.json found - serving static files"
    
    # Try npx serve first
    Write-Info "Attempting to use 'npx serve .'"
    & npx --yes serve . 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "'npx serve' failed, trying global 'serve'"
        
        if (-not (Test-Command "serve")) {
            Write-Info "Installing 'serve' globally..."
            & npm install -g serve
            
            if ($LASTEXITCODE -ne 0) {
                Write-Err "Failed to install 'serve'"
                return $LASTEXITCODE
            }
        }
        
        & serve .
        return $LASTEXITCODE
    }
    
    return 0
}

# -------------------------
# Main Execution
# -------------------------

function Main {
    # Clear screen for cleaner output
    Clear-Host
    
    # Display banner
    Write-Banner "🚀 SPMS Frontend Development Server"
    
    $projectName = Get-ProjectName
    Write-Info "Project: $projectName"
    Write-Info "Directory: $(Get-Location)"
    Write-Host ""
    
    # Change to script directory
    $scriptDir = Split-Path -Parent $MyInvocation.ScriptName
    if ($scriptDir) {
        Set-Location $scriptDir
        Write-Debug "Changed to script directory: $scriptDir"
    }
    
    # Check backend health if requested
    if ($CheckBackend) {
        $backendHealthy = Test-BackendHealth $BackendUrl
        Write-Host ""
        
        if (-not $backendHealthy) {
            Write-Warn "Backend is not responding. Continue anyway? (Y/N)"
            $response = Read-Host
            if ($response -ne "Y" -and $response -ne "y") {
                Write-Info "Exiting..."
                exit 0
            }
        }
    }
    
    # Check for package.json (framework project)
    if (Test-Path "package.json") {
        Write-Success "Framework-based project detected"
        
        # Detect package manager
        $packageManager = Get-PackageManager
        Write-Host ""
        
        # Install dependencies if needed
        if (Test-NeedsInstall $ForceInstall) {
            if (-not (Install-Dependencies $packageManager)) {
                Write-Err "Failed to install dependencies"
                exit 1
            }
        }
        Write-Host ""
        
        # Get dev script
        $scriptName = Get-DevScript $DevScript
        if (-not $scriptName) {
            Write-Err "No suitable dev script found in package.json"
            exit 2
        }
        Write-Host ""
        
        # Start server based on mode
        if ($Watch) {
            Start-WatchMode $packageManager $scriptName
        } else {
            $exitCode = Start-DevServer $packageManager $scriptName
            
            if ($exitCode -eq 0) {
                Write-Success "Dev server stopped gracefully"
            } else {
                Write-Err "Dev server exited with code $exitCode"
            }
            
            exit $exitCode
        }
    } else {
        # Static file server
        $exitCode = Start-StaticServer
        exit $exitCode
    }
}

# Run main function
try {
    Main
} catch {
    Write-Err "Unexpected error: $_"
    Write-Debug $_.ScriptStackTrace
    exit 1
} finally {
    Write-Host ""
    Write-Info "Cleanup complete"
}