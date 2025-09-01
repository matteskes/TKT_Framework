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

#### Flake8 Configuration
Create `.flake8`:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist
```

### Pre-commit Configuration

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Testing

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

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import patch, MagicMock
from TKT.cli import TKTSystemManager, get_distribution_name

class TestTKTSystemManager:
    def test_init_supported_distro(self):
        """Test initialization with supported distribution."""
        with patch('TKT.cli.get_distribution_name', return_value='ubuntu'):
            manager = TKTSystemManager()
            assert manager.distro == 'ubuntu'
            assert manager.distro_supported is True

    def test_install_dependencies_success(self):
        """Test successful dependency installation."""
        manager = TKTSystemManager()
        manager.distro_supported = True
        manager.distro_config = MagicMock()
        manager.distro_config.update_and_install.return_value = None
        
        success, message = manager.install_dependencies()
        assert success is True
        assert "successfully" in message.lower()

    def test_install_dependencies_unsupported_distro(self):
        """Test dependency installation on unsupported distribution."""
        manager = TKTSystemManager()
        manager.distro_supported = False
        
        success, message = manager.install_dependencies()
        assert success is False
        assert "not supported" in message.lower()
```

#### Integration Tests
```python
import tempfile
import os
from TKT.cli import KernelToolkitApp

class TestApplicationIntegration:
    def test_config_creation_and_loading(self):
        """Test configuration file creation and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "settings.toml")
            
            # Initialize app (should create default config)
            app = KernelToolkitApp()
            app.config_path = config_path
            config = app._load_config()
            
            assert "kernels" in config
            assert "settings" in config
            assert os.path.exists(config_path)
```

#### Mock Testing for UI
```python
from textual.testing import AppTester
from TKT.cli import KernelToolkitApp

def test_dependency_installation_ui():
    """Test dependency installation through UI."""
    app = KernelToolkitApp()
    
    with AppTester(app) as pilot:
        # Simulate Ctrl+D keypress
        pilot.press("ctrl+d")
        
        # Check status update
        status_label = app.query_one("#status_label")
        assert "Installing dependencies" in status_label.renderable
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --cov=TKT
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    ui: marks tests that test UI components
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=TKT --cov-report=html

# Run specific test categories
pytest -m "not slow"              # Skip slow tests
pytest tests/test_cli.py          # Run specific module
pytest -k "test_install"          # Run tests matching pattern

# Run integration tests
pytest tests/integration/
```

## Contributing

### Contribution Workflow

1. **Create an issue** describing the bug/feature
2. **Fork the repository** and create a feature branch
3. **Make changes** following code standards
4. **Write tests** for new functionality
5. **Run the test suite** and ensure all tests pass
6. **Submit a pull request** with clear description

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes  
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(distro): add fedora support for package management

- Implement FedoraConfigs class with dnf commands
- Add fedora to supported distributions list
- Update documentation

Closes #123
```

```
fix(ui): resolve status message display issue

The status label was not updating correctly after
dependency installation due to widget not being mounted.

Fixes #456
```

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested on target distributions

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No unnecessary dependencies added
```

## Adding New Features

### Feature Development Process

1. **Design phase**: Create issue with detailed specification
2. **Architecture review**: Discuss integration approach
3. **Implementation**: Follow TDD (Test-Driven Development)
4. **Testing**: Unit tests, integration tests, manual testing
5. **Documentation**: Update all relevant documentation
6. **Review**: Code review and feedback incorporation

### Example: Adding Kernel Configuration Feature

#### 1. Define Interface
```python
# In TKTSystemManager
def configure_kernel(
    self, 
    kernel_version: str, 
    config_type: str = "default"
) -> tuple[bool, str]:
    """
    Configure kernel for compilation.
    
    Args:
        kernel_version: Target kernel version
        config_type: Configuration type (default, custom, minimal)
        
    Returns:
        tuple[bool, str]: (success, message)
    """
```

#### 2. Implement Core Logic
```python
def configure_kernel(self, kernel_version: str, config_type: str = "default") -> tuple[bool, str]:
    if not self.distro_supported:
        return False, "Distribution not supported for kernel configuration"
    
    try:
        # Implement kernel configuration logic
        config_path = self._get_kernel_config_path(kernel_version)
        
        if config_type == "default":
            success = self._apply_default_config(config_path)
        elif config_type == "custom":
            success = self._run_menuconfig(config_path)
        else:
            return False, f"Unknown configuration type: {config_type}"
            
        if success:
            return True, f"Kernel {kernel_version} configured successfully"
        else:
            return False, "Kernel configuration failed"
            
    except Exception as e:
        return False, f"Configuration error: {str(e)}"
```

#### 3. Add UI Integration
```python
# In KernelToolkitApp.handle_command
elif command_lower.startswith("config:"):
    config_parts = command_lower.split(":", 2)
    if len(config_parts) >= 2:
        config_type = config_parts[1]
        kernel_version = config_parts[2] if len(config_parts) > 2 else self.selected_kernel
        
        if not kernel_version:
            self.update_status("No kernel version selected")
            return True
            
        self.update_status(f"Configuring kernel {kernel_version}...")
        self.refresh()
        
        success, message = self.system_manager.configure_kernel(kernel_version, config_type)
        self.update_status(f"{'✓' if success else '✗'} {message}")
        return True
```

#### 4. Add Tests
```python
class TestKernelConfiguration:
    def test_configure_kernel_default(self):
        """Test default kernel configuration."""
        manager = TKTSystemManager()
        manager.distro_supported = True
        
        with patch.object(manager, '_apply_default_config', return_value=True):
            success, message = manager.configure_kernel("6.16", "default")
            assert success is True
            assert "configured successfully" in message

    def test_configure_kernel_unsupported_distro(self):
        """Test kernel configuration on unsupported distribution."""
        manager = TKTSystemManager()
        manager.distro_supported = False
        
        success, message = manager.configure_kernel("6.16")
        assert success is False
        assert "not supported" in message
```

## Distribution Support

### Adding New Distribution Support

#### Step 1: Create Distribution Configuration Class

```python
# In distro_configs.py
class NewDistroConfigs(DistroConfigs):
    """Package management configuration for NewDistro."""
    
    # Distribution-specific dependencies
    new_distro_deps = [
        "kernel-headers",
        "build-tools",
        "dev-libs",
    ]
    
    def __init__(self):
        self.packages = self.base_deps + self.new_distro_deps
    
    def update_repos(self) -> bool:
        """Update package repositories."""
        return self._run_command(
            ["sudo", "newdistro-pkg", "update"],
            "Updating NewDistro repositories"
        )
    
    def install_packages(self) -> bool:
        """Install required packages."""
        return self._run_command(
            ["sudo", "newdistro-pkg", "install"] + self.packages,
            "Installing NewDistro packages"
        )
```

#### Step 2: Register in Factory Function

```python
def get_distro_configs(name: str) -> DistroConfigs:
    match name.lower():
        case "arch": return ArchConfigs()
        case "debian": return DebianConfigs()
        case "ubuntu": return UbuntuConfigs()
        case "newdistro": return NewDistroConfigs()  # Add this line
        case _: raise ValueError(f"Unsupported distribution: {name}")
```

#### Step 3: Update Supported Distributions List

```python
# In cli.py
SUPPORTED_DISTROS: Final[list[str]] = [
    "debian",
    "ubuntu", 
    "fedora",
    "arch",
    "newdistro",  # Add this line
]
```

#### Step 4: Add Tests

```python
class TestNewDistroConfigs:
    def test_new_distro_initialization(self):
        """Test NewDistro configuration initialization."""
        config = NewDistroConfigs()
        assert len(config.packages) > len(config.base_deps)
        assert "kernel-headers" in config.packages
    
    def test_get_distro_configs_new_distro(self):
        """Test factory function returns correct config."""
        config = get_distro_configs("newdistro")
        assert isinstance(config, NewDistroConfigs)
```

#### Step 5: Update Documentation

Update all relevant documentation:
- README.md supported distributions table
- User guide installation instructions
- API documentation with new class
- Add distribution-specific troubleshooting notes

### Distribution Testing

Test new distribution support thoroughly:

1. **Virtual machine testing**: Test on actual distribution
2. **Package installation**: Verify all dependencies install correctly
3. **Permission handling**: Test sudo requirements
4. **Error conditions**: Test network failures, permission errors
5. **Integration testing**: Test with main application

## Release Process

### Version Management

TKT uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

#### Pre-release
- [ ] All tests pass on CI/CD
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped in `__init__.py`
- [ ] Dependencies reviewed and updated

#### Release
- [ ] Create release branch: `release/vX.Y.Z`
- [ ] Final testing on supported distributions
- [ ] Create GitHub release with changelog
- [ ] Tag release: `git tag vX.Y.Z`
- [ ] Merge to main branch

#### Post-release
- [ ] Update development version
- [ ] Close milestone on GitHub
- [ ] Announce release in discussions
- [ ] Update documentation site

### Automated Testing

Set up GitHub Actions for automated testing:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
        
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov
        
    - name: Run tests
      run: pytest --cov=TKT --cov-report=xml
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

This developer guide provides the foundation for contributing to and extending the TKT project. For specific implementation questions, refer to the existing codebase and create GitHub discussions for architectural decisions.