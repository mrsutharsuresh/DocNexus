# DocNexus - Project Structure

This document describes the standard Python project structure for DocNexus.

## Directory Layout

```
DocNexus/
├── docnexus/                 # Main application package
│   ├── __init__.py            # Package initialization & version
│   ├── version_info.py        # Single Source of Truth for Version
│   ├── app.py                 # Flask application setup
│   ├── cli.py                 # Command-line interface
│   ├── core/                  # Core functionality
│   │   └── renderer.py        # Markdown rendering engine
│   ├── features/              # Feature modules
│   │   ├── registry.py        # Feature registration
│   │   ├── standard.py        # Standard features (TOC, etc.)
│   │   └── smart_convert.py  # Experimental features
│   └── templates/             # HTML templates
│       ├── components/        # Reusable UI components (header_brand, settings)
│       ├── index.html         # File browser
│       ├── view.html          # Document viewer
│       └── docs.html          # Documentation viewer
│
├── docs/                      # Project documentation
│   ├── README.md              # Documentation index
│   ├── USER_GUIDE.md          # User manual
│   ├── BUILD.md               # Build instructions
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── PRODUCTION_SUMMARY.md
│   ├── RELEASE_NOTES_v1.0.0.md
│   ├── CHANGELOG.md           # Version history
│   ├── VERSION.md             # Version tracking
│   └── VIBRANT_UPDATE.md      # UI updates
│
├── examples/                  # Sample markdown files
│   ├── sample.md
│   ├── 45CPS_EXECUTIVE_BRIEFING.md
│   └── [more samples...]
│
├── releases/                  # Distribution packages
│   ├── v1.0.0/               # Version-specific build
│   │   ├── DocNexus.exe    # Standalone executable
│   │   ├── README.md
│   │   └── examples/         # Samples
│   ├── DocNexus-v1.0.0-Windows-x64.zip
│   ├── CHECKSUMS.txt         # SHA256 verification
│   └── README.md             # Release notes
│
├── build/                     # Build artifacts (gitignored)
├── dist/                      # PyInstaller output (gitignored)
├── .venv/                     # Virtual environment (gitignored)
│
├── README.md                  # Project overview
├── LICENSE                    # MIT License
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern packaging (PEP 518)
├── setup.py                   # Legacy setuptools
├── MANIFEST.in               # Package data rules
├── run.py                     # Development server
├── start.bat                  # Windows launcher
├── DocNexus.spec           # PyInstaller config
└── .gitignore                # Git exclusions

```

## Key Files

### Packaging Configuration

- **pyproject.toml** - Modern Python packaging standard (PEP 518)
  - Build system configuration
  - Project metadata
  - Dependencies
  - Entry points
  - Tool configurations (black, pytest)

- **setup.py** - Legacy setuptools configuration
  - Backward compatibility
  - Dynamic version reading
  - Package discovery

- **MANIFEST.in** - Package data inclusion rules
  - Templates, documentation, samples
  - Excluded files (build artifacts)

- **requirements.txt** - Runtime dependencies
  - Flask, markdown, Pygments, pymdown-extensions

### Application Entry Points

- **run.py** - Development server
  - Direct Flask execution
  - Debug mode enabled
  - Auto-reload on changes

- **docnexus/cli.py** - Command-line interface
  - Production entry point
  - Command-line argument parsing
  - Installed as `docnexus` command

### Build Configuration

- **DocPresent.spec** - PyInstaller specification
  - Single-file executable configuration
  - Data file collection
  - Hidden imports for Flask/markdown
  - UPX compression settings

## Installation Methods

### 1. End Users (Pre-built Executable)
```bash
# Download from releases/
unzip DocNexus-v1.1.2-Windows-x64.zip
cd v1.1.2
./DocNexus.exe
```

### 2. Developers (Source Installation)
```bash
# Clone and install
git clone [repository]
cd DocPresent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### 3. Package Installation (pip)
```bash
# Install from source
pip install -e .

# Or from PyPI (if published)
pip install docnexus

# Run installed command
docnexus
```

## Build Process

### Development Build
```bash
python run.py
```

### Production Executable
```bash
pip install pyinstaller
pyinstaller DocPresent.spec --clean
# Output: dist/DocPresent.exe
```

### Python Package
```bash
# Build wheel
python -m build

# Output: dist/docpresent-1.0.0-py3-none-any.whl
```

### Create Release
```bash
# Build executable
pyinstaller DocPresent.spec --clean

# Create release structure
mkdir releases/v1.0.0
cp dist/DocPresent.exe releases/v1.0.0/
cp README.md releases/v1.0.0/
cp -r doc releases/v1.0.0/
cp -r workspace releases/v1.0.0/

# Create archive
cd releases
zip -r DocPresent-v1.0.0-Windows-x64.zip v1.0.0/

# Generate checksum
sha256sum DocPresent-v1.0.0-Windows-x64.zip > CHECKSUMS.txt
```

## Git Workflow

### Ignored Files (.gitignore)
- Build artifacts: `build/`, `dist/`, `*.egg-info/`
- Virtual environments: `.venv/`, `venv/`
- Python cache: `__pycache__/`, `*.pyc`
- Releases: `releases/`
- IDE configs: `.vscode/`, `.idea/`

### Tracked Files
- Source code: `doc_viewer/`
- Documentation: `docs/`, `README.md`
- Samples: `examples/`
- Configuration: `pyproject.toml`, `setup.py`, `requirements.txt`
- Build specs: `DocPresent.spec`, `MANIFEST.in`

## Standards Compliance

This project follows Python packaging best practices:

- ✅ **PEP 518** - pyproject.toml for build system
- ✅ **PEP 621** - Project metadata in pyproject.toml
- ✅ **PEP 517** - Build backend specification
- ✅ **PEP 440** - Version numbering (1.0.0)
- ✅ **Setuptools** - Package discovery and data files
- ✅ **Entry Points** - Console scripts registration
- ✅ **MANIFEST.in** - Explicit data file inclusion
- ✅ **Semantic Versioning** - Major.Minor.Patch

## Distribution Channels

### GitHub Releases
- Release archive: `DocPresent-v1.0.0-Windows-x64.zip`
- SHA256 checksums for verification
- Release notes and documentation

### PyPI (Future)
- Python wheel: `docpresent-1.0.0-py3-none-any.whl`
- Source distribution: `docpresent-1.0.0.tar.gz`
- Install via: `pip install docpresent`

### Standalone Executable
- Windows: `DocPresent.exe` (15 MB)
- No Python installation required
- All dependencies bundled

---

**Last Updated:** December 16, 2025  
**Version:** 1.1.2  
**Structure:** Standard Python Package
