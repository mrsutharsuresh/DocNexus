# Makefile equivalent for Windows PowerShell
# Build and release automation for OmniDoc

param(
    [Parameter(Position = 0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
$ConfirmPreference = "None"

# Configuration
$ProjectRoot = $PSScriptRoot
$Version = (Get-Content "$ProjectRoot\VERSION").Trim()
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BuildVenv = "$ProjectRoot\build\venv"
$Python = "$BuildVenv\Scripts\python.exe"

function Show-Help {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  DocNexus v$Version - Build System  " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Python Environment:" -ForegroundColor Yellow
    if (Test-Path $Python) {
        $PythonVer = & $Python --version
        Write-Host "   Build Venv:     build\venv\" -ForegroundColor Gray
        Write-Host "   Python:         $PythonVer" -ForegroundColor Gray
    }
    else {
        Write-Host "   Build Venv:     Not created (run 'setup' first)" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Available Targets:" -ForegroundColor Yellow
    Write-Host "  make setup       - Setup build environment" -ForegroundColor Gray
    Write-Host "  make build       - Build executable binary" -ForegroundColor Gray
    Write-Host "  make release     - Create versioned release" -ForegroundColor Gray
    Write-Host "  make start       - Start latest release" -ForegroundColor Gray
    Write-Host "  make stop        - Stop running server" -ForegroundColor Gray
    Write-Host "  make clean       - Clean build outputs" -ForegroundColor Gray
    Write-Host "  make clean-all   - Clean everything" -ForegroundColor Gray
    Write-Host "  make test        - Run tests" -ForegroundColor Gray
    Write-Host "  make run         - Run from source (dev)" -ForegroundColor Gray
    Write-Host "  make help        - Show this help" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor Yellow
    Write-Host "   1. .\make.ps1 setup" -ForegroundColor Gray
    Write-Host "   2. .\make.ps1 release" -ForegroundColor Gray
    Write-Host "   3. .\make.ps1 start" -ForegroundColor Gray
    Write-Host ""
}

function Invoke-Setup {
    Write-Host "Setting up build environment..." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path $BuildVenv)) {
        Write-Host "Creating build venv at build\venv..." -ForegroundColor Gray
        python -m venv $BuildVenv
        Write-Host "Venv created" -ForegroundColor Green
    }
    else {
        Write-Host "Build venv already exists" -ForegroundColor Yellow
    }
    
    Write-Host "Installing dependencies..." -ForegroundColor Gray
    & "$BuildVenv\Scripts\pip.exe" install --upgrade pip setuptools wheel --quiet
    & "$BuildVenv\Scripts\pip.exe" install -r build\build-requirements.txt --quiet
    & "$BuildVenv\Scripts\pip.exe" install -r requirements.txt --quiet
    
    Write-Host "Build environment ready" -ForegroundColor Green
    Write-Host ""
    $PythonVer = & $Python --version
    Write-Host "Python version: $PythonVer" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-Build {
    Write-Host "Building executable..." -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path $Python)) {
        Write-Host "Build environment missing. Running setup..." -ForegroundColor Yellow
        Invoke-Setup
    }
    
    # Force reinstall dependencies to ensure latest versions
    Write-Host "Refreshing dependencies..." -ForegroundColor Gray
    & "$BuildVenv\Scripts\pip.exe" install -r requirements.txt --upgrade --quiet
    
    # Run PyInstaller build
    & "$ProjectRoot\build\build.ps1"
    
    # Post-build: Seed workspace with sample documents
    Write-Host "Seeding workspace with sample documents..." -ForegroundColor Gray
    $DocGallery = "$ProjectRoot\build\output\workspace"
    if (-not (Test-Path $DocGallery)) {
        New-Item -ItemType Directory -Path $DocGallery -Force | Out-Null
    }
    Copy-Item "$ProjectRoot\README.md" "$DocGallery\Welcome.md" -Force
    Copy-Item "$ProjectRoot\docs\USER_GUIDE.md" "$DocGallery\UserGuide.md" -Force
    # Copy examples if they exist
    if (Test-Path "$ProjectRoot\examples\*") {
        Copy-Item "$ProjectRoot\examples\*" "$DocGallery\" -Recurse -Force
    }
    Write-Host "Sample documents added: Welcome.md, UserGuide.md" -ForegroundColor Green
}

function Invoke-Release {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Creating Release v$Version" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Clean and build
    Invoke-Clean
    Invoke-Build
    
    # Create timestamped release directory
    $ArchiveDir = "$ProjectRoot\dist\archive\DocNexus_v$Version-$Timestamp"
    Write-Host "Creating timestamped release..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
    
    # Copy executable from build/output
    $ExePath = "$ProjectRoot\build\output\DocNexus_v$Version.exe"
    if (Test-Path $ExePath) {
        Copy-Item $ExePath $ArchiveDir\ -Force
    }
    else {
        Write-Host "ERROR: Executable not found at $ExePath" -ForegroundColor Red
        exit 1
    }
    
    # Copy documentation
    Copy-Item "$ProjectRoot\VERSION" $ArchiveDir\ -Force
    Copy-Item "$ProjectRoot\README.md" $ArchiveDir\ -Force
    Copy-Item "$ProjectRoot\RELEASE_NOTES_v$Version.md" $ArchiveDir\ -Force -ErrorAction SilentlyContinue
    Copy-Item -Recurse "$ProjectRoot\docs" $ArchiveDir\ -Force
    
    # Create workspace in release
    New-Item -ItemType Directory -Path "$ArchiveDir\workspace" -Force | Out-Null
    Copy-Item "$ProjectRoot\examples\*" "$ArchiveDir\workspace\" -Recurse -Force
    
    # Create release notes
    $PythonVer = & $Python --version
    $Platform = if ([Environment]::Is64BitOperatingSystem) { 'x64' }else { 'x86' }
    $ReleaseDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    
    "# DocNexus v$Version`n" | Out-File "$ArchiveDir\RELEASE.md" -Encoding UTF8
    "`nRelease Date: $ReleaseDate" | Add-Content "$ArchiveDir\RELEASE.md"
    "Platform: Windows-$Platform" | Add-Content "$ArchiveDir\RELEASE.md"
    "Python: Built with $PythonVer`n" | Add-Content "$ArchiveDir\RELEASE.md"
    "`n## Quick Start`n" | Add-Content "$ArchiveDir\RELEASE.md"
    ".\DocNexus_v$Version.exe`n" | Add-Content "$ArchiveDir\RELEASE.md"
    "Then open http://localhost:8000`n" | Add-Content "$ArchiveDir\RELEASE.md"
    
    # Create checksums
    $Hash = Get-FileHash "$ArchiveDir\DocNexus_v$Version.exe" -Algorithm SHA256
    "$($Hash.Algorithm): $($Hash.Hash)" | Out-File "$ArchiveDir\checksums.txt" -Encoding UTF8
    
    Write-Host "Release created: $ArchiveDir" -ForegroundColor Green
    Write-Host ""
    
    # Update latest junction (Windows symlink equivalent)
    $LatestLink = "$ProjectRoot\dist\latest"
    if (Test-Path $LatestLink) {
        # Use cmd to remove junction safely without deleting target contents or prompting
        cmd /c rmdir "$LatestLink"
    }
    
    cmd /c mklink /J "$LatestLink" "$ArchiveDir" 2>&1 | Out-Null
    Write-Host "Junction updated: dist\latest" -ForegroundColor Green
    Write-Host ""
    
    # Show release info
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Release Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Locations:" -ForegroundColor Yellow
    Write-Host "   Latest:  dist\latest\DocNexus_v$Version.exe" -ForegroundColor Cyan
    Write-Host "   Release: $ArchiveDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Release Contents:" -ForegroundColor Yellow
    Get-ChildItem $ArchiveDir | Format-Table Name, Length -AutoSize
    Write-Host ""
    Write-Host "Recent Releases:" -ForegroundColor Yellow
    Get-ChildItem "$ProjectRoot\dist\archive" -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name -AutoSize
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Start: .\make.ps1 start" -ForegroundColor Gray
    Write-Host "   2. Stop:  .\make.ps1 stop" -ForegroundColor Gray
    Write-Host ""
}

function Invoke-Start {
    # Auto-stop any running instances first
    Invoke-Stop

    Write-Host "Starting latest release..." -ForegroundColor Yellow
    Write-Host ""
    
    $LatestLink = "$ProjectRoot\dist\latest"
    $ExePath = ""

    if (Test-Path $LatestLink) {
        $ExePath = Get-ChildItem "$LatestLink\DocNexus_v*.exe" | Select-Object -ExpandProperty FullName -First 1
    }
    
    if (-not $ExePath) {
        # Fallback: Find latest in archive
        $LatestArchive = Get-ChildItem "$ProjectRoot\dist\archive" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($LatestArchive) {
            $ExePath = Get-ChildItem "$LatestArchive\DocNexus_v*.exe" | Select-Object -ExpandProperty FullName -First 1
        }
    }

    if ($ExePath -and (Test-Path $ExePath)) {
        Write-Host "Launching: $ExePath" -ForegroundColor Cyan
        Start-Process $ExePath
        Write-Host "Application started." -ForegroundColor Green
    }
    else {
        Write-Host "ERROR: No release executable found. Run '.\make.ps1 release' first." -ForegroundColor Red
        exit 1
    }
}

function Invoke-Stop {
    Write-Host "Stopping server..." -ForegroundColor Yellow
    Write-Host ""
    
    $Processes = Get-Process | Where-Object { $_.ProcessName -like "DocNexus_v*" }
    if ($Processes) {
        $Processes | Stop-Process -Force
        Write-Host "DocNexus processes stopped." -ForegroundColor Green
    }
    else {
        Write-Host "No running DocNexus processes found." -ForegroundColor Yellow
    }
}

function Invoke-Clean {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "$ProjectRoot\build\output" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$ProjectRoot\build\pyinstaller" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$ProjectRoot\dist\DocNexus_v$Version.exe" -ErrorAction SilentlyContinue
    Remove-Item "$ProjectRoot\*.spec" -ErrorAction SilentlyContinue
    Get-ChildItem -Path $ProjectRoot -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleaned (build\venv preserved)" -ForegroundColor Green
    Write-Host ""
}

function Invoke-CleanAll {
    Write-Host "Deep cleaning..." -ForegroundColor Yellow
    Invoke-Clean
    Remove-Item -Recurse -Force $BuildVenv -ErrorAction SilentlyContinue
    Write-Host "All cleaned - run '.\make.ps1 setup' to recreate venv" -ForegroundColor Green
    Write-Host ""
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path $Python) {
        if (Test-Path "$ProjectRoot\tests") {
            & $Python -m pytest tests\ -v
        }
        else {
            Write-Host "No tests directory found" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "ERROR: Build venv not found. Run '.\make.ps1 setup' first" -ForegroundColor Red
        exit 1
    }
}

function Invoke-Run {
    Write-Host "Starting development server..." -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path $Python) {
        & $Python run.py
    }
    else {
        Write-Host "ERROR: Build venv not found. Run '.\make.ps1 setup' first" -ForegroundColor Red
        exit 1
    }
}

# Execute target
switch ($Target.ToLower()) {
    "help" { Show-Help }
    "setup" { Invoke-Setup }
    "build" { Invoke-Build }
    "release" { Invoke-Release }
    "start" { Invoke-Start }
    "stop" { Invoke-Stop }
    "clean" { Invoke-Clean }
    "clean-all" { Invoke-CleanAll }
    "test" { Invoke-Test }
    "run" { Invoke-Run }
    default {
        Write-Host "ERROR: Unknown target '$Target'" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
