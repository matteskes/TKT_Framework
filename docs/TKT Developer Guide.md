# TKT Developer Documentation Guide

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Environment](#development-environment)
4. [Code Standards & Quality](#code-standards--quality)
5. [Testing Strategy](#testing-strategy)
6. [Build System](#build-system)
7. [Distribution Support](#distribution-support)
8. [Contributing Workflow](#contributing-workflow)
9. [Release Process](#release-process)
10. [Debugging & Troubleshooting](#debugging--troubleshooting)

## Project Overview

The Kernel Toolkit (TKT) is a modern, cross-distribution Linux kernel compilation tool built with Python 3.11+. The project emphasizes:

- **User Experience**: Clean terminal UI with Textual framework
- **Cross-Platform**: Multi-distribution support with pluggable backends
- **Modern Python**: Type hints, async patterns, and modern tooling
- **Quality Assurance**: Comprehensive testing and automated checks

### Key Technologies

- **UI Framework**: Textual (terminal-based UI)
- **Configuration**: TOML with tomlkit
- **Build System**: Make with virtual environment management
- **Quality Tools**: Black, Ruff, MyPy, pytest
- **CI/CD**: GitHub Actions for automated testing

## Architecture

### Core Components

```
TKT/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── cli.py              # Main application logic & UI
├── distro_configs.py   # Distribution-specific backends
└── settings.toml       # Runtime configuration
```

### Component Responsibilities

#### `cli.py` - Application Core
- **TKTSystemManager**: System operations and dependency management
- **KernelToolkitApp**: Textual UI application
- **Distribution Detection**: Auto-detect Linux distribution
- **Command Routing**: Handle user input and commands

#### `distro_configs.py` - Backend System
- **DistroConfigs**: Abstract base class for package management
- **Distribution Classes**: Concrete implementations (Arch, Debian, Ubuntu, Fedora)
- **Package Management**: Repository updates and dependency installation

#### Configuration System
- **settings.toml**: Available kernel versions and backend selection
- **TOML Loading**: Dynamic configuration with fallback defaults

### Design Patterns

#### Plugin Architecture
Distribution support uses a factory pattern:

```python
def get_distro_configs(distro_name: str) -> DistroConfigs:
    """Factory function returning appropriate config class."""
    configs = {
        'arch': ArchConfigs,
        'debian': DebianConfigs,
        'ubuntu': UbuntuConfigs,
        # ... extensible for new distributions
    }
    return configs[distro_name]()
```

#### Command Pattern
User commands are processed through a centralized handler:

```python
async def handle_command(self, command: str) -> None:
    """Process user commands with validation and error handling."""
    if command in ['deps', 'install-deps']:
        await self.install_dependencies()
    elif self.is_kernel_version(command):
        await self.select_kernel(command)
    # ... extensible command system
```

## Development Environment

### Prerequisites

- **Python 3.11+** (system-wide installation)
- **Make** (for build automation)
- **Git** (version control)
- **Linux System** (for testing distribution-specific features)

### Environment Setup

```bash
# 1. Clone repository
git clone https://github.com/matteskes/TKT_Framework.git
cd TKT_Framework

# 2. Create virtual environment and install dependencies
make install

# 3. Verify setup
make check  # Run all quality checks
make test   # Run test suite
make run    # Launch application
```

### Virtual Environment Management

The project uses a local `.venv/` directory:

```makefile
# Virtual environment is created automatically
.venv/:
    python -m venv .venv
    .venv/bin/pip install -r requirements.txt
```

### Development Dependencies

```
# Runtime Dependencies
textual           # Terminal UI framework
tomlkit>=0.12.0  # TOML configuration handling

# Development Dependencies  
mypy             # Static type checking
pytest           # Testing framework
pytest-cov      # Coverage reporting
pytest-mock     # Mocking utilities
black           # Code formatting
isort           # Import sorting
ruff            # Fast Python linter

# Compatibility
tomli>=2.0.0    # Python <3.11 compatibility
```

## Code Standards & Quality

### Python Style Guide

**Formatting**: Black with 88-character line length
```toml
[tool.black]
line-length = 88
target-version = ["py311"]
skip-string-normalization = false
```

**Import Sorting**: isort with Black compatibility
```toml
[tool.isort]
profile = "black"
line_length = 88
```

**Linting**: Ruff with automatic fixes
```toml
[tool.ruff]
line-length = 88
target-version = "py311"
fix = true
select = ["E", "F", "I"]  # errors, formatting, imports
```

### Type Annotations

**Required for all public APIs**:

```python
def install_dependencies(self) -> tuple[bool, str]:
    """
    Install required packages for kernel compilation.
    
    Returns:
        tuple[bool, str]: Success status and descriptive message
    """
```

### Documentation Standards

**Google-style docstrings**:

```python
def get_distro_configs(distro_name: str) -> DistroConfigs:
    """
    Factory function to get distribution-specific configuration.

    Args:
        distro_name: Name of the Linux distribution (e.g., 'arch', 'debian')

    Returns:
        DistroConfigs: Configuration object for the specified distribution

    Raises:
        ValueError: If distribution is not supported
        
    Example:
        >>> config = get_distro_configs('arch')
        >>> success, msg = config.install_packages()
    """
```

### Error Handling Patterns

**Structured error handling**:

```python
# Good: Specific exceptions with context
try:
    config = get_distro_configs(distro_name)
    success, message = config.install_packages()
except ValueError as e:
    logger.error(f"Unsupported distribution: {distro_name}")
    return False, f"Distribution '{distro_name}' not supported"
except subprocess.CalledProcessError as e:
    logger.error(f"Package installation failed: {e}")
    return False, f"Failed to install packages: {e.stderr}"

# Avoid: Generic exception handling
try:
    # operations
except Exception:
    return False, "Something went wrong"
```

## Testing Strategy

### Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── fixtures/          # Test data and mocks
└── conftest.py       # Pytest configuration
```

### Testing Patterns

**Unit Testing Example**:

```python
import pytest
from unittest.mock import patch, MagicMock
from TKT.cli import TKTSystemManager

class TestTKTSystemManager:
    def test_install_dependencies_success(self):
        """Test successful dependency installation."""
        manager = TKTSystemManager()
        manager.distro_supported = True
        manager.distro_config = MagicMock()
        manager.distro_config.install_packages.return_value = (True, "Success")
        
        success, message = manager.install_dependencies()
        
        assert success is True
        assert "success" in message.lower()
        manager.distro_config.install_packages.assert_called_once()

    @patch('TKT.cli.get_distribution_name')
    def test_unsupported_distribution_handling(self, mock_get_distro):
        """Test graceful handling of unsupported distributions."""
        mock_get_distro.side_effect = ValueError("Unsupported distro")
        
        manager = TKTSystemManager()
        assert not manager.distro_supported
```

**Integration Testing Example**:

```python
@patch('subprocess.run')
def test_complete_dependency_installation(mock_subprocess):
    """Test full dependency installation workflow."""
    # Mock successful subprocess calls
    mock_subprocess.return_value.returncode = 0
    
    manager = TKTSystemManager()
    success, message = manager.install_dependencies()
    
    assert success is True
    assert mock_subprocess.called
```

### Coverage Requirements

- **Minimum coverage**: 80% overall
- **Critical paths**: 90%+ coverage for core functionality
- **New features**: Must include comprehensive tests

### Running Tests

```bash
# Run all tests
make test

# Run with coverage reporting
make coverage

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -k "test_install"     # Tests matching pattern
```

## Build System

### Makefile Structure

The project uses Make for build automation:

```makefile
# Primary targets
install: .venv/              # Set up development environment
run: .venv/                  # Launch application
test: .venv/                 # Run test suite
check: typecheck lint format # Run all quality checks

# Quality assurance
typecheck: .venv/            # Static type checking with MyPy
lint: .venv/                 # Code linting with Ruff
format: .venv/               # Code formatting with Black/isort
coverage: .venv/             # Coverage testing
force-fix: .venv/            # Automatic code fixes
```

### Key Build Patterns

**Virtual Environment Management**:
```makefile
.venv/:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

# All targets depend on .venv/ to ensure environment exists
run: .venv/
	.venv/bin/python -m TKT
```

**Quality Checks Integration**:
```makefile
check: typecheck lint format
	@echo "✅ All quality checks passed"

typecheck: .venv/
	.venv/bin/mypy TKT/

lint: .venv/ 
	.venv/bin/ruff check TKT/

format: .venv/
	.venv/bin/black TKT/
	.venv/bin/isort TKT/
```

### Development Workflow

```bash
# Daily development cycle
make install    # Initial setup (once)
make run        # Test application
make check      # Verify code quality
make test       # Run test suite
make coverage   # Check test coverage
```

## Distribution Support

### Adding New Distribution Support

The plugin architecture makes adding new distributions straightforward:

#### 1. Research Phase
- **Package Manager**: Identify distribution's package manager (apt, dnf, zypper, etc.)
- **Package Names**: Map kernel development packages to distribution-specific names
- **Commands**: Document update and installation command syntax

#### 2. Implementation Phase

**Create Distribution Config**:
```python
class NewDistroConfigs(DistroConfigs):
    """Package management for NewDistro Linux."""
    
    # Distribution-specific package names
    newdistro_deps = [
        "kernel-devel",
        "build-essential-equivalent", 
        "development-tools"
    ]
    
    def __init__(self):
        self.packages = self.base_deps + self.newdistro_deps
    
    def update_repos(self) -> tuple[bool, str]:
        """Update package repositories."""
        return self._run_command(
            ["sudo", "newpkg", "update"],
            "Updating NewDistro repositories"
        )
    
    def install_packages(self) -> tuple[bool, str]:
        """Install kernel compilation dependencies."""
        return self._run_command(
            ["sudo", "newpkg", "install", "-y"] + self.packages,
            "Installing NewDistro development packages"
        )
```

**Register in Factory**:
```python
def get_distro_configs(distro_name: str) -> DistroConfigs:
    configs = {
        'arch': ArchConfigs,
        'debian': DebianConfigs,
        'ubuntu': UbuntuConfigs,
        'newdistro': NewDistroConfigs,  # Add here
    }
    # ... rest of function
```

#### 3. Testing Phase
- **Virtual Machine Testing**: Test on actual distribution
- **Package Verification**: Ensure all dependencies install correctly
- **Error Scenarios**: Test failure handling and error messages
- **Integration Testing**: Verify with main application

#### 4. Documentation Phase
- **README Update**: Add to supported distributions table
- **Contributing Guide**: Add distribution-specific notes
- **Troubleshooting**: Document common issues and solutions

### Distribution Detection

The system automatically detects Linux distributions:

```python
def get_distribution_name() -> str:
    """
    Detect Linux distribution name.
    
    Returns:
        str: Lowercase distribution name
        
    Raises:
        RuntimeError: If distribution cannot be determined
    """
    try:
        import distro
        return distro.id().lower()
    except ImportError:
        # Fallback to /etc/os-release parsing
        return parse_os_release()
```

## Contributing Workflow

### Branch Strategy

```bash
# Feature development
git checkout -b feature/add-fedora-support
git checkout -b bugfix/fix-status-display
git checkout -b docs/update-user-guide

# Naming convention: type/description
```

### Pre-commit Workflow

**Set up pre-commit hooks** (optional but recommended):
```bash
pip install pre-commit
pre-commit install
```

**Manual quality checks**:
```bash
make check    # Run all quality checks
make test     # Run test suite
```

### Pull Request Process

1. **Create feature branch** from main
2. **Implement changes** following code standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run quality checks**: `make check`
6. **Submit pull request** with clear description

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Examples**:
```
feat(distro): add fedora support with dnf package management

- Implement FedoraConfigs class
- Add fedora to supported distributions  
- Update documentation with fedora notes

Closes #123

fix(ui): resolve status message not updating after dependency installation

The status widget was not refreshing due to async timing issues.
Added proper state management and UI update triggers.

Fixes #456
```

## Release Process

### Version Management

**Project versioning** in `pyproject.toml`:
```toml
[project]
name = "the-kernel-toolkit"
version = "0.1.0"  # Update for releases
```

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/lint.yml`):
```yaml
name: Lint & Format
on: [pull_request, push]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      # Quality checks
      - run: pip install black isort ruff
      - run: black --check .
      - run: ruff check .
      - run: isort --check-only .
```

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with new features and fixes
- [ ] Run full test suite: `make test coverage`
- [ ] Update documentation for any API changes
- [ ] Create release branch and submit PR
- [ ] Tag release after merge: `git tag v0.1.0`
- [ ] Create GitHub release with changelog

## Debugging & Troubleshooting

### Logging Strategy

**Application logs** stored in `~/.local/share/tkt/logs/`:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Dependency installation started")
logger.error(f"Failed to install package: {package_name}")
```

### Common Development Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
# Or use Make targets which handle this automatically
make run
```

**Test Failures**:
```bash
# Run with verbose output
pytest -v tests/

# Run specific failing test
pytest tests/unit/test_cli.py::TestTKTSystemManager::test_install_dependencies

# Run with debugging
pytest --pdb tests/
```

**Type Checking Issues**:
```bash
# Run MyPy with verbose output
make typecheck

# Check specific file
.venv/bin/mypy TKT/cli.py
```

### Performance Debugging

**Profile application startup**:
```python
import cProfile
import pstats

def profile_main():
    pr = cProfile.Profile()
    pr.enable()
    
    # Run application code
    from TKT.cli import main
    main()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative').print_stats(10)
```

**Memory usage monitoring**:
```python
import tracemalloc

tracemalloc.start()
# ... application code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
```

### Distribution-Specific Debugging

**Test distribution detection**:
```python
from TKT.cli import get_distribution_name
print(f"Detected distribution: {get_distribution_name()}")
```

**Test package manager commands**:
```bash
# Test in isolation
python -c "
from TKT.distro_configs import get_distro_configs
config = get_distro_configs('arch')  # or your distro
success, msg = config.update_repos()
print(f'Update repos: {success}, {msg}')
"
```

### UI Debugging

**Textual development tools**:
```python
# Enable Textual development mode
export TEXTUAL=devtools

# Run with debug logging
python -m TKT --dev
```

**Console debugging**:
```python
# Add to Textual app for live debugging
from textual import log
log("Debug message here")
```

---

## Contributing to This Guide

This developer documentation is maintained alongside the codebase. When contributing:

1. **Update relevant sections** when adding new features
2. **Add examples** for new architectural patterns  
3. **Document new tools** or development processes
4. **Keep examples current** with actual codebase

**Location**: This guide should be saved as `DEVELOPER_GUIDE.md` in the project root.

For questions about development practices or architecture decisions, please:
- Check existing [GitHub Issues](https://github.com/matteskes/TKT_Framework/issues)
- Start a [GitHub Discussion](https://github.com/matteskes/TKT_Framework/discussions)
- Reference this guide in code reviews and documentation updates
