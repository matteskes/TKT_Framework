# The Kernel Toolkit (TKT)

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-green.svg)](https://www.kernel.org/)

A modern, user-friendly terminal application for compiling and managing custom Linux kernels across multiple distributions.

## Features

- **Multi-Distribution Support**: Automated package management for Arch Linux, Debian, Ubuntu, and Fedora
- **Interactive Terminal UI**: Clean, modern interface built with Textual
- **Automated Dependency Installation**: One-command setup for kernel compilation dependencies
- **Configuration Management**: TOML-based configuration for kernel versions and settings
- **Extensible Architecture**: Plugin-style backend system for different distributions
- **Kernel Source Fetching**: Automated downloading and management of kernel source code via HTTP

## Requirements

- **Python 3.11+** (installed system-wide)
- **Make** (standard on most Unix-like systems)
- Linux operating system (supported: Arch, Debian, Ubuntu, Fedora)
- Terminal with TTY support

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

- **`make install`**
  Creates a virtual environment in `.venv/` and installs dependencies from `requirements.txt`.

### Development

- **`make test`**
  Runs the test suite with `pytest`. You can choose specific test files by
  using the `PYTEST_FILES` macro.

- **`make coverage`**
  Run tests with coverage reporting. Set `COV_REPORT=html` to generate HTML reports and start a local server to view them.

- **`make coverage test`**
  Run unit and coverage tests at the same time.

- **`make typecheck`**
  Performs static type checking using `mypy`.

- **`make lint`**
  Runs `ruff` to check code style and linting issues.

- **`make format`**
  Formats the code with `black` and `isort`.

- **`make force-fix`**
  Runs `ruff` with automatic fixes (including unsafe ones).

- **`make check`**
  Runs type checking, linting, and formatting in one step.

### Execution

- **`make run`**
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
|:-------------|:----------------|:-------|
| Arch Linux | pacman/makepkg | Supported |
| Debian | apt | Supported |
| Ubuntu | apt | Supported |
| Fedora | dnf | Planned |
| Linux Mint | apt | Planned |
| Open SuSE | zypper | Planned |
| Pop_OS! | apt | Planned |

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

```text
TKT/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point
├── cli.py               # Main application and UI logic
├── distro_configs.py    # Distribution-specific configurations
├── fetch.py             # Kernel source fetching utilities
├── kernel_config.py     # Kernel configuration management
├── safe.py              # Safe execution utilities
└── settings.toml        # Configuration file
```

## Dependencies

### Runtime Dependencies

- `textual==6.1.0` - Terminal UI framework
- `tomlkit>=0.12.0` - TOML configuration handling
- `requests==2.33.0` - HTTP requests for kernel fetching
- Standard library modules: `importlib`, `platform`, `subprocess`, `sys`, `os`

### System Dependencies (Auto-installed)

The application automatically installs kernel compilation dependencies including:

- Build tools (gcc, make, cmake)
- Kernel-specific tools (bc, bison, flex, kmod)
- Development libraries (libssl-dev, libelf-dev, ncurses-dev)
- Utilities (git, wget, rsync, tar)

### CLI Entry Point

The package can also be invoked via the `tkt` command after installation:

```bash
tkt
```

### Documentation

Additional documentation is available in the `docs/` directory:

- **[API Documentation](docs/API%20Documentation.md)** — Detailed API reference
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** — In-depth contribution and development guide

## Interactive Commands

### Available Commands

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

## Development Workflow

### Code Quality Tools

This project uses several code quality tools configured in `pyproject.toml`:

- **mypy** — Static type checking
- **ruff** — Linting and style checks
- **black** — Code formatting
- **isort** — Import sorting
- **pytest** — Testing with coverage reporting

Run all checks at once with `make check`. See the [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed contribution guidelines.

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

- **Solution**: Ensure you have Python 3.11+ and all dependencies installed. Run `make install` to set up the environment properly.

### Logging

TKT creates log files in `~/.local/share/tkt/logs/` for debugging purposes.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution

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

### CI/CD

This project uses GitHub Actions for continuous integration. The lint workflow (`.github/workflows/lint.yml`) runs automatically on pull requests to ensure code quality standards are met.

---

**Note**: This project is in active development. Some features mentioned in the documentation may not be fully implemented yet. Check the [project roadmap](https://github.com/matteskes/TKT_Framework/projects) for current status.
