# Installation

PyBastion can be installed using pip or uv (recommended).

## Requirements

- Python 3.13 or higher
- DuckDB (bundled)
- Modern operating system (Windows, macOS, Linux)

## Using UV (Recommended)

UV is the fastest Python package manager and is recommended for PyBastion.

### Install UV

```bash
# On Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install PyBastion

```bash
# Install latest stable version
uv pip install pybastion

# Install with development dependencies
uv pip install pybastion[dev]

# Install with documentation dependencies
uv pip install pybastion[docs]
```

## Using Pip

```bash
# Install latest stable version
pip install pybastion

# Install with development dependencies
pip install pybastion[dev]

# Install with documentation dependencies
pip install pybastion[docs]
```

## Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/flyguy62n/pybastion.git
cd pybastion

# Install with UV
uv pip install -e .[dev,docs]

# Or with pip
pip install -e .[dev,docs]
```

## Verification

Verify your installation:

```bash
pybastion --version
pybastion --help
```

## Next Steps

- [Quick Start Guide](../getting-started/quickstart.md)
- [Configuration](../user-guide/configuration.md)
- [Your First Analysis](../getting-started/first-analysis.md)
