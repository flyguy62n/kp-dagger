# Installation

Dagger can be installed using pip or uv (recommended).

## Requirements

- Python 3.13 or higher
- DuckDB (bundled)
- Modern operating system (Windows, macOS, Linux)

## Using UV (Recommended)

UV is the fastest Python package manager and is recommended for Dagger.

### Install UV

```bash
# On Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dagger

```bash
# Install latest stable version
uv pip install Dagger

# Install with development dependencies
uv pip install Dagger[dev]

# Install with documentation dependencies
uv pip install Dagger[docs]
```

## Using Pip

```bash
# Install latest stable version
pip install Dagger

# Install with development dependencies
pip install Dagger[dev]

# Install with documentation dependencies
pip install Dagger[docs]
```

## Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/flyguy62n/Dagger.git
cd Dagger

# Install with UV
uv pip install -e .[dev,docs]

# Or with pip
pip install -e .[dev,docs]
```

## Verification

Verify your installation:

```bash
Dagger --version
Dagger --help
```

## Next Steps

- [Quick Start Guide](../getting-started/quickstart.md)
- [Configuration](../user-guide/configuration.md)
- [Your First Analysis](../getting-started/first-analysis.md)
