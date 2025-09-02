# TKT Developer Guide

This guide is for developers who want to contribute to The Kernel Toolkit (TKT) project or understand its internal architecture.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Architecture](#project-architecture)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Contributing](#contributing)
- [Adding New Features](#adding-new-features)
- [Distribution Support](#distribution-support)
- [Release Process](#release-process)

## Development Environment Setup

### Prerequisites

- **Python 3.10+** with pip
- **Git** for version control
- **Linux system** for testing (or VM)
- **Text editor/IDE** with Python support

### Setting Up the Environment

1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/TKT_Framework.git
cd TKT_Framework
```

2. **Create virtual environment:**
```bash
python -m venv tkt-dev
source tkt-dev/bin/activate  # Windows: tkt-dev\Scripts\activate
```

3. **Install development dependencies:**
```bash
# Runtime dependencies
pip install textual tomlkit

# Development dependencies  
pip install pytest pytest-cov black flake8 mypy pre-commit
pip install -e .
```

4. **Set up pre-commit hooks:**
```bash
pre-commit install
```

5. **Verify setup:**
```bash
python -m TKT  # Should launch the application
pytest         # Should run tests (if any exist)
```

## Project Architecture

### Overview

TKT follows a modular architecture with clear separation of concerns:

```
TKT/
├── __init__.py          # Package metadata and version
├── __main__.py          # Entry point and argument parsing  
├── cli.py              # Main application logic and UI
├── distro_configs.py   # Distribution-specific configurations
└── settings.toml       # Runtime configuration
```

### Core Components

#### 1. Application Layer (`cli.py`)

**`KernelToolkitApp`**: Main Textual application
- Handles UI rendering and user interaction
- Manages application state and configuration
- Coordinates between system manager and UI components

**`TKTSystemManager`**: System operations manager
- Abstracts system-level operations
- Handles distribution detection and validation
- Manages dependency installation and kernel operations

#### 2. Distribution Layer (`distro_configs.py`)

**`DistroConfigs`**: Abstract base class
- Defines common interface for package management
- Provides extensible architecture for new distributions
- Handles base dependency definitions

**Concrete implementations**: `ArchConfigs`, `DebianConfigs`, `UbuntuConfigs`
- Distribution-specific package management logic
- Custom dependency lists and installation procedures
- Error handling for platform-specific issues

#### 3. Configuration Layer

**TOML configuration**: `settings.toml`
- User-configurable kernel versions and settings
- Backend selection and validation
- Persistent storage for user preferences

### Design Patterns

#### Factory Pattern
```python
def get_distro_configs(name: str) -> DistroConfigs:
    """Factory function for distribution configurations."""
    match name.lower():
        case "arch": return ArchConfigs()
        case "debian": return DebianConfigs()
        # ...
```

#### Strategy Pattern
```python
class TKTSystemManager:
    def __init__(self):
        self.distro_config = get_distro_configs(self.distro)
        
    def install_dependencies(self):
        return self.distro_config.update_and_install()
```

#### Template Method Pattern
```python
class DistroConfigs(ABC):
    def update_and_install(self):
        """Template method - can be overridden."""
        self.update_repos()      # Abstract method
        self.install_packages()  # Abstract method
```

### Data Flow

1. **Application startup**: Detect distribution → Load configuration → Initialize UI
2. **User input**: UI → Command parsing → System manager → Distribution config
3. **System operations**: Distribution config → Subprocess calls → Status updates → UI

## Code Style and Standards

### Python Style Guide

TKT follows PEP 8 with some specific conventions:

#### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Any

# Third-party imports
import tomlkit
from textual.app import App

# Local imports
from TKT.distro_configs import get_distro_configs
```

#### Type Hints
All public functions must include type hints:
```python
def get_distribution_name() -> str:
    """Returns the distribution name."""
    
def choose_backend(config: Dict[str, Any], config_path: str) -> tuple[str, bool]:
    """Returns backend name and support status."""
```

#### Docstrings
Use Google-style docstrings:
```python
def install_dependencies(self) -> tuple[bool, str]:
    """
    Install required packages for kernel compilation.

    Returns:
        tuple[bool, str]: (success, message)
        
    Raises:
        RuntimeError: If distribution is not supported.
    """
```

#### Error Handling
Prefer specific exceptions with descriptive messages:
```python
# Good
if not self.distro_supported:
    raise RuntimeError("Distribution not supported for automatic dependency installation")

# Avoid
if not self.distro_supported:
    raise Exception("Error")
```

### Code Formatting

#### Black Configuration
Create `.pyproject.toml`:
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?
extend-exclude = '''
/(
  # Exclude specific directories
  build/
  | dist/
)/
'''
```

### Pre-commit Configuration

```yaml
repos:
  # Black for formatting
  - repo: https://github.com/psf/black
    rev: 24.4.2  # pin to latest stable
    hooks:
      - id: black

  # isort for import sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2 # pin to lastest stable
    hooks:
      - id: isort

  # Ruff for linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
      - id: ruff-format  # optional, if you want Ruff formatting checks too
```

### Testing Framework

TKT uses pytest for testing with the following structure:

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_cli.py             # CLI module tests
├── test_distro_configs.py  # Distribution config tests
├── integration/            # Integration tests
│   ├── test_full_flow.py
│   └── test_ui_interaction.py
└── fixtures/               # Test data
    ├── sample_configs/
    └── mock_responses/
```

