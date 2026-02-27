param(
    [switch]$RunAsAdmin
)

# If not running as admin, request elevation
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    if ($RunAsAdmin) {
        Write-Host "[ERROR] Failed to gain administrator privileges"
        exit 1
    }
    
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "  JARVIS AI - Desktop App Builder"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "[*] Administrator privileges required"
    Write-Host ""
    Write-Host "A permission dialog will appear. Please click 'Yes' to continue."
    Write-Host ""
    
    # Wait a moment for user to read
    Start-Sleep -Seconds 2
    
    # Request admin elevation
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -RunAsAdmin" -Verb RunAs -Wait
    exit $LASTEXITCODE
}

# ============= RUNNING AS ADMIN FROM HERE =============

Write-Host ""
Write-Host "=========================================="
Write-Host "  JARVIS AI - Building Desktop Application"
Write-Host "=========================================="
Write-Host ""
Write-Host "[✓] Running with Administrator Privileges"
Write-Host ""

$buildDir = "e:\Bionic AI\Jarvis AI 3"

# Step 1: Clear electron-builder cache
Write-Host "[1/4] Clearing electron-builder cache..."
try {
    $cachePath = "$env:LOCALAPPDATA\electron-builder"
    if (Test-Path $cachePath) {
        Remove-Item -Path $cachePath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "      [✓] Cache cleared"
    }
} catch {
    Write-Host "      [!] Could not clear cache (non-critical)"
}

# Step 2: Clear npm cache
Write-Host "[2/4] Clearing npm cache..."
Push-Location $buildDir\frontend
npm cache clean --force *> $null
Write-Host "      [✓] npm cache cleared"

# Step 3: Set environment for optimal build
Write-Host "[3/4] Configuring build environment..."
$env:CSC_IDENTITY_AUTO_DISCOVERY = 'false'
$env:WIN_CSC_LINK = ''
$env:USE_HARD_LINKS = 'false'
$env:ELECTRON_BUILDER_CACHE = "$env:TEMP\electron-builder-cache"

# Try to enable symlink evaluation (Windows 10+)
Write-Host "[4/4] Building with electron-builder..."
Write-Host ""

# Run the actual build
npm run electron:build

$buildResult = $LASTEXITCODE
Pop-Location

Write-Host ""
if ($buildResult -eq 0) {
    Write-Host "=========================================="
    Write-Host "[✓] BUILD SUCCESSFUL!"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Desktop app created in: frontend\dist\"
    Write-Host ""
    Write-Host "Files available:"
    Write-Host "  - dist\JARVIS-AI-Setup.exe (recommended - with installer)"
    Write-Host "  - dist\JARVIS AI.exe (portable - run directly)"
    Write-Host ""
} else {
    Write-Host "=========================================="
    Write-Host "[✗] BUILD FAILED"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "If you see 'symbolic link' errors, enable Windows Developer Mode:"
    Write-Host ""
    Write-Host "Windows 11: Settings → System → For developers → Developer Mode"
    Write-Host "Windows 10: Settings → Update & Security → For developers → Developer mode"
    Write-Host ""
    Write-Host "Then restart your computer and try again."
    Write-Host ""
}

exit $buildResult
