# The Kernel Toolkit (TKT)

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-green.svg)](https://www.kernel.org/)

A modern, user-friendly terminal application for compiling and managing custom Linux kernels across multiple distributions.

## Features

- **Multi-Distribution Support**: Automated package management for Arch Linux, Debian, Ubuntu, and Fedora
- **Interactive Terminal UI**: Clean, modern interface built with Textual
- **Automated Dependency Installation**: One-command setup for kernel compilation dependencies
- **Configuration Management**: TOML-based configuration for kernel versions and settings
- **Extensible Architecture**: Plugin-style backend system for different distributions

## Requirements

* **Python 3.10+** (installed system-wide)
* **Make** (standard on most Unix-like systems)
* Linux operating system (supported: Arch, Debian, Ubuntu, Fedora)
* Terminal with TTY support

The project uses a local virtual environment (`.venv/`) for dependencies.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/matteskes/TKT_Framework.git
cd TKT_Framework

# Install dependencies using Make
make install

# Or manually with pip
pip install -r requirements.txt
```

### Basic Usage

By default, running `make` (with no arguments) will execute the application:

```bash
make
```

or explicitly:

```bash
make run
```

You can also run directly with Python:

```bash
python -m TKT
```

## Available Make Commands

### Setup

* **`make install`**
  Creates a virtual environment in `.venv/` and installs dependencies from `requirements.txt`.

### Development

* **`make test`**
  Runs the test suite with `pytest`.

* **`make coverage`**
  Run coverage tests. Regular test results will not show up.

* **`make typecheck`**
  Performs static type checking using `mypy`.

* **`make lint`**
  Runs `ruff` to check code style and linting issues.

* **`make format`**
  Formats the code with `black` and `isort`.

* **`make force-fix`**
  Runs `ruff` with automatic fixes (including unsafe ones).

* **`make check`**
  Runs type checking, linting, and formatting in one step.

### Execution

* **`make run`**
  Runs the application (`python -m TKT`). Equivalent to just `make`.

## Application Usage

1. **Start the application**:
   ```bash
   make run
   # or
   python -m TKT
   ```

2. **Install kernel compilation dependencies**:
   - Press `Ctrl+D` or type `deps` in the input field

3. **Select a kernel version**:
   - Enter a kernel version (e.g., `6.16`) in the input field
   - Available versions are defined in `settings.toml`

4. **Exit the application**:
   - Press `Ctrl+Q`

## Supported Distributions

| Distribution | Package Manager | Status |
|-------------|----------------|--------|
| Arch Linux | pacman/makepkg | Partially Supported |
| Debian | apt-get | Partially Supported |
| Ubuntu | apt-get | Partially Supported |
| Fedora | dnf | ⚠️ Planned |

## Configuration

The application uses `settings.toml` for configuration:

```toml
# TKT Framework Configuration

[kernels]
available = ["6.16", "6.15.1", "5.19.12"]

[settings]
backend = "kernel_lib_arch"  # Auto-detected based on distribution
```

### Configuration Options

- **`kernels.available`**: List of kernel versions available for compilation
- **`settings.backend`**: Backend library to use (auto-configured)

## Project Structure

```
TKT/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point
├── cli.py              # Main application and UI logic
├── distro_configs.py   # Distribution-specific configurations
└── settings.toml       # Configuration file
```

## Dependencies

### Runtime Dependencies
- `textual` - Terminal UI framework
- `tomlkit` - TOML configuration handling
- Standard library modules: `importlib`, `platform`, `subprocess`

### System Dependencies (Auto-installed)
The application automatically installs kernel compilation dependencies including:
- Build tools (gcc, make, cmake)
- Kernel-specific tools (bc, bison, flex, kmod)
- Development libraries (libssl-dev, libelf-dev, ncurses-dev)
- Utilities (git, wget, rsync, tar)

## Commands

### Interactive Commands
- **Enter kernel version**: Select a kernel version for compilation (e.g., `6.16`)
- **`deps` or `install-deps`**: Install kernel compilation dependencies
- **`config:TYPE`**: Configure kernel (planned feature)
- **`prepare:VERSION`**: Prepare kernel source (planned feature)

### Keyboard Shortcuts
- **`Ctrl+D`**: Install dependencies
- **`Ctrl+Q`**: Quit application

## Architecture

### Core Components

1. **TKTSystemManager**: Handles system-level operations like dependency installation
2. **KernelToolkitApp**: Textual-based user interface
3. **DistroConfigs**: Abstract base class for distribution-specific package management
4. **Backend System**: Pluggable architecture for different kernel compilation backends

### Distribution Support

The application uses a plugin-style architecture where each Linux distribution has its own configuration class:

```python
class DebianConfigs(DistroConfigs):
    """Package management for Debian-based systems."""
    
    def update_repos(self):
        sp.run(["apt-get", "update", "-y"])
    
    def install_packages(self):
        sp.run(["apt-get", "install", "-y", *self.packages])
```

## Development

### Setting up Development Environment

```bash
# Clone and enter directory
git clone https://github.com/matteskes/TKT_Framework.git
cd TKT_Framework

# Install dependencies and set up environment
make install

# Or manually create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Development Workflow

```bash
# Run tests
make test

# Run with coverage
make coverage

# Type checking
make typecheck

# Linting
make lint

# Format code
make format

# Run all checks at once
make check

# Auto-fix linting issues (including unsafe fixes)
make force-fix
```

### Adding Distribution Support

1. Create a new class inheriting from `DistroConfigs`
2. Implement `update_repos()` and `install_packages()` methods
3. Add the distribution to `get_distro_configs()` function
4. Update `SUPPORTED_DISTROS` list in `cli.py`

## Troubleshooting

### Common Issues

**Issue**: "Current operating system is not Linux"
- **Solution**: TKT only supports Linux distributions. Ensure you're running on a supported Linux system.

**Issue**: "Distribution not supported"
- **Solution**: Check if your distribution is in the supported list. Consider adding support or using a compatible distribution.

**Issue**: "No library found for backend"
- **Solution**: The backend library is not implemented yet. This is expected for distributions under development.

**Issue**: Application fails to start
- **Solution**: Ensure you have Python 3.10+ and all dependencies installed. Run `make install` to set up the environment properly.

### Logging

TKT creates log files in `~/.local/share/tkt/logs/` for debugging purposes.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Areas for Contribution
- Complete Fedora support implementation
- Add more distribution support
- Implement kernel configuration features
- Add kernel source preparation logic
- Improve error handling and user feedback
- Write additional tests

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Authors and Contributors

- **The Kernel Toolkit Project and contributors** - Initial work and ongoing development

## Acknowledgments

- [Textual](https://github.com/Textualize/textual) for the excellent TUI framework
- The Linux kernel community for making custom kernel compilation accessible
- All contributors who help improve this project

## Support

- **Issues**: [GitHub Issues](https://github.com/matteskes/TKT_Framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matteskes/TKT_Framework/discussions)
- **Documentation**: [Project Wiki](https://github.com/matteskes/TKT_Framework/wiki)

---

**Note**: This project is in active development. Some features mentioned in the documentation may not be fully implemented yet. Check the [project roadmap](https://github.com/matteskes/TKT_Framework/projects) for current status.
