# TKT API Reference Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation & Import](#installation--import)
3. [Core API](#core-api)
4. [Distribution Support API](#distribution-support-api)
5. [Configuration API](#configuration-api)
6. [Command Line Interface](#command-line-interface)
7. [Error Handling](#error-handling)
8. [Examples & Usage Patterns](#examples--usage-patterns)
9. [Type Definitions](#type-definitions)
10. [Extension Points](#extension-points)

## Overview

The Kernel Toolkit (TKT) provides both a command-line interface and a programmatic API for kernel compilation and management across multiple Linux distributions. This guide documents the public API for developers who want to integrate TKT functionality into their own applications.

### API Design Principles

- **Type Safety**: All public functions include comprehensive type hints
- **Error Handling**: Consistent error reporting with structured exceptions
- **Cross-Platform**: Works across supported Linux distributions
- **Extensible**: Plugin architecture for adding new distributions
- **Async-Ready**: Compatible with async/await patterns where appropriate

## Installation & Import

### Package Installation

```bash
# From PyPI (when released)
pip install the-kernel-toolkit

# From source
git clone https://github.com/matteskes/TKT_Framework.git
cd TKT_Framework
pip install -e .
```

### Basic Imports

```python
# Core functionality
from TKT.cli import TKTSystemManager, get_distribution_name
from TKT.distro_configs import get_distro_configs, DistroConfigs

# Configuration handling
from TKT.cli import load_kernel_config, get_available_kernels

# For UI integration
from TKT.cli import KernelToolkitApp
```

## Core API

### TKTSystemManager

Primary class for system-level kernel compilation operations.

#### Class Definition

```python
class TKTSystemManager:
    """
    Core system manager for kernel compilation operations.
    
    Handles distribution detection, dependency installation, and
    system configuration for kernel compilation workflows.
    
    Attributes:
        distro_supported (bool): Whether current distribution is supported
        distro_config (DistroConfigs | None): Distribution-specific configuration
        distro_name (str | None): Detected distribution name
    """
```

#### Constructor

```python
def __init__(self) -> None:
    """
    Initialize system manager with automatic distribution detection.
    
    Automatically detects the current Linux distribution and loads
    appropriate configuration. Sets distro_supported to False if
    distribution is not supported.
    
    Example:
        >>> manager = TKTSystemManager()
        >>> if manager.distro_supported:
        ...     print(f"Running on supported {manager.distro_name}")
        ... else:
        ...     print("Distribution not currently supported")
    """
```

#### Methods

##### install_dependencies()

```python
def install_dependencies(self) -> tuple[bool, str]:
    """
    Install kernel compilation dependencies for current distribution.
    
    Uses distribution-specific package manager to install all required
    packages for kernel compilation including build tools, libraries,
    and development packages.
    
    Returns:
        tuple[bool, str]: Success status and descriptive message
            - bool: True if installation succeeded, False otherwise  
            - str: Human-readable status message
            
    Raises:
        RuntimeError: If distribution is not supported
        
    Example:
        >>> manager = TKTSystemManager()
        >>> success, message = manager.install_dependencies()
        >>> if success:
        ...     print("Dependencies installed successfully")
        ... else:
        ...     print(f"Installation failed: {message}")
    """
```

##### get_status()

```python
def get_status(self) -> dict[str, any]:
    """
    Get current system status and configuration information.
    
    Returns:
        dict[str, any]: Status information including:
            - 'distribution': Detected distribution name
            - 'supported': Whether distribution is supported
            - 'dependencies_installed': Dependency installation status
            - 'available_kernels': List of available kernel versions
            
    Example:
        >>> manager = TKTSystemManager()
        >>> status = manager.get_status()
        >>> print(f"Distribution: {status['distribution']}")
        >>> print(f"Supported: {status['supported']}")
    """
```

### Distribution Detection

#### get_distribution_name()

```python
def get_distribution_name() -> str:
    """
    Detect current Linux distribution name.
    
    Uses multiple detection methods including /etc/os-release,
    platform.freedesktop_os_release(), and fallback methods.
    
    Returns:
        str: Lowercase distribution name (e.g., 'arch', 'ubuntu', 'debian')
        
    Raises:
        RuntimeError: If distribution cannot be determined or is not Linux
        
    Example:
        >>> distro = get_distribution_name()
        >>> print(f"Running on: {distro}")
        'Running on: arch'
    """
```

### Configuration Management

#### load_kernel_config()

```python
def load_kernel_config() -> dict[str, any]:
    """
    Load kernel configuration from settings.toml.
    
    Loads available kernel versions and backend configuration
    from the settings file, with fallback defaults if file
    is not found or invalid.
    
    Returns:
        dict[str, any]: Configuration dictionary with keys:
            - 'kernels': Dict with 'available' list of versions
            - 'settings': Dict with backend and other settings
            
    Raises:
        FileNotFoundError: If settings.toml is not found and no defaults
        toml.TomlDecodeError: If settings.toml is malformed
        
    Example:
        >>> config = load_kernel_config()
        >>> available = config['kernels']['available']
        >>> print(f"Available kernels: {available}")
        ['6.16', '6.15.1', '5.19.12']
    """
```

#### get_available_kernels()

```python
def get_available_kernels() -> list[str]:
    """
    Get list of available kernel versions from configuration.
    
    Convenience function that loads configuration and returns
    just the available kernel versions list.
    
    Returns:
        list[str]: Available kernel versions
        
    Example:
        >>> kernels = get_available_kernels()
        >>> for kernel in kernels:
        ...     print(f"Available: {kernel}")
    """
```

## Distribution Support API

### DistroConfigs Base Class

Abstract base class for distribution-specific package management.

#### Class Definition

```python
from abc import ABC, abstractmethod

class DistroConfigs(ABC):
    """
    Abstract base class for distribution-specific configurations.
    
    Provides common interface for package management operations
    across different Linux distributions. Subclasses implement
    distribution-specific package manager commands.
    
    Attributes:
        base_deps (list[str]): Common packages required across distributions
        packages (list[str]): Combined base and distribution-specific packages
    """
```

#### Base Dependencies

```python
base_deps = [
    # Build tools
    "git", "make", "gcc", "cmake", "ninja-build",
    
    # Kernel-specific tools  
    "bc", "bison", "flex", "kmod",
    
    # Development libraries
    "libssl-dev", "libelf-dev", "libncurses-dev",
    
    # Utilities
    "wget", "rsync", "tar", "curl"
]
```

#### Abstract Methods

##### update_repos()

```python
@abstractmethod
def update_repos(self) -> tuple[bool, str]:
    """
    Update package repositories.
    
    Updates the distribution's package repositories to ensure
    latest package information is available.
    
    Returns:
        tuple[bool, str]: Success status and message
        
    Note:
        Must be implemented by distribution-specific subclasses.
    """
```

##### install_packages()

```python
@abstractmethod  
def install_packages(self) -> tuple[bool, str]:
    """
    Install kernel compilation packages.
    
    Installs all packages required for kernel compilation
    using the distribution's package manager.
    
    Returns:
        tuple[bool, str]: Success status and message
        
    Note:
        Must be implemented by distribution-specific subclasses.
    """
```

#### Utility Methods

##### _run_command()

```python
def _run_command(self, cmd: list[str], description: str) -> tuple[bool, str]:
    """
    Execute system command with error handling.
    
    Args:
        cmd: Command and arguments as list
        description: Human-readable description for logging
        
    Returns:
        tuple[bool, str]: Success status and message
        
    Example:
        >>> config = ArchConfigs()
        >>> success, msg = config._run_command(
        ...     ["sudo", "pacman", "-Sy"], 
        ...     "Updating repositories"
        ... )
    """
```

### Distribution-Specific Classes

#### ArchConfigs

```python
class ArchConfigs(DistroConfigs):
    """
    Package management configuration for Arch Linux.
    
    Uses pacman for package management with makepkg for AUR packages.
    Includes Arch-specific packages like base-devel group.
    """
    
    arch_deps = [
        "base-devel",  # Meta-package with build tools
        "linux-headers",
        "xmlto", "docbook-xsl"
    ]
    
    def update_repos(self) -> tuple[bool, str]:
        """Update pacman repositories."""
        
    def install_packages(self) -> tuple[bool, str]:
        """Install packages using pacman."""
```

#### DebianConfigs

```python
class DebianConfigs(DistroConfigs):
    """
    Package management configuration for Debian and derivatives.
    
    Uses apt for package management. Includes Debian-specific
    package names and development packages.
    """
    
    debian_deps = [
        "build-essential",  # Meta-package with build tools
        "linux-headers-generic",
        "libncurses5-dev", "pkg-config"
    ]
    
    def update_repos(self) -> tuple[bool, str]:
        """Update apt repositories."""
        
    def install_packages(self) -> tuple[bool, str]:
        """Install packages using apt."""
```

#### UbuntuConfigs

```python
class UbuntuConfigs(DebianConfigs):
    """
    Package management configuration for Ubuntu.
    
    Inherits from DebianConfigs since Ubuntu uses apt,
    but may override specific packages or add Ubuntu-specific
    dependencies as needed.
    """
```

### Factory Function

#### get_distro_configs()

```python
def get_distro_configs(distro_name: str) -> DistroConfigs:
    """
    Factory function to get distribution-specific configuration.
    
    Returns appropriate DistroConfigs subclass instance based
    on the provided distribution name.
    
    Args:
        distro_name: Distribution name (e.g., 'arch', 'debian', 'ubuntu')
        
    Returns:
        DistroConfigs: Configuration instance for the distribution
        
    Raises:
        ValueError: If distribution is not supported
        
    Example:
        >>> config = get_distro_configs('arch')
        >>> success, msg = config.install_packages()
        >>> print(f"Installation: {success}, {msg}")
    """
```

## Configuration API

### Settings File Format

TKT uses TOML for configuration with the following structure:

```toml
# settings.toml
[kernels]
available = ["6.16", "6.15.1", "5.19.12"]

[settings]  
backend = "kernel_lib_arch"  # Auto-detected based on distribution
```

### Configuration Functions

#### validate_kernel_version()

```python
def validate_kernel_version(version: str) -> bool:
    """
    Validate kernel version format.
    
    Checks if provided version string matches expected
    kernel version patterns (e.g., "6.16", "5.19.12").
    
    Args:
        version: Kernel version string to validate
        
    Returns:
        bool: True if version format is valid
        
    Example:
        >>> validate_kernel_version("6.16")
        True
        >>> validate_kernel_version("invalid")
        False
    """
```

#### update_kernel_config()

```python
def update_kernel_config(new_kernels: list[str]) -> bool:
    """
    Update available kernels in configuration file.
    
    Args:
        new_kernels: List of kernel versions to set as available
        
    Returns:
        bool: True if configuration was updated successfully
        
    Example:
        >>> success = update_kernel_config(["6.16", "6.15.1"])
        >>> print(f"Config updated: {success}")
    """
```

## Command Line Interface

### KernelToolkitApp

Textual-based terminal UI application.

```python
class KernelToolkitApp(App):
    """
    Main Textual application for terminal UI.
    
    Provides interactive interface for kernel compilation
    operations with real-time status updates and command processing.
    """
    
    async def on_mount(self) -> None:
        """Initialize UI components and system manager."""
        
    async def handle_command(self, command: str) -> None:
        """Process user commands and update UI."""
        
    async def install_dependencies(self) -> None:
        """Handle dependency installation with UI updates."""
```

### CLI Entry Points

#### main()

```python
def main() -> None:
    """
    Main entry point for TKT command-line interface.
    
    Launches the Textual-based terminal application.
    Can be called directly or via CLI command 'tkt'.
    
    Example:
        >>> from TKT.cli import main
        >>> main()  # Launches interactive UI
    """
```

#### Command Registration

The package provides a CLI script entry point:

```toml
[project.scripts]
tkt = "TKT.cli:main"
```

## Error Handling

### Exception Types

TKT uses standard Python exceptions with descriptive messages:

#### RuntimeError
- Distribution not supported
- System configuration errors
- Package manager failures

#### ValueError  
- Invalid kernel version format
- Invalid configuration values

#### FileNotFoundError
- Missing configuration files
- Missing system dependencies

### Error Response Pattern

Most API functions return `tuple[bool, str]` for error handling:

```python
# Success case
success, message = manager.install_dependencies()
if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")
    
# Exception case  
try:
    config = get_distro_configs("unsupported")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Logging Integration

```python
import logging

# Configure logging for TKT operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TKT')

# TKT logs to ~/.local/share/tkt/logs/ by default
manager = TKTSystemManager()
success, message = manager.install_dependencies()
# Logs are automatically written during operations
```

## Examples & Usage Patterns

### Basic System Management

```python
from TKT.cli import TKTSystemManager

def setup_kernel_environment():
    """Set up environment for kernel compilation."""
    manager = TKTSystemManager()
    
    # Check if distribution is supported
    if not manager.distro_supported:
        print(f"Distribution {manager.distro_name} not supported")
        return False
    
    print(f"Setting up environment on {manager.distro_name}")
    
    # Install dependencies
    success, message = manager.install_dependencies()
    if not success:
        print(f"Failed to install dependencies: {message}")
        return False
    
    print("Environment setup complete")
    return True

if __name__ == "__main__":
    setup_kernel_environment()
```

### Configuration Management

```python
from TKT.cli import load_kernel_config, get_available_kernels

def list_available_kernels():
    """Display available kernel versions."""
    try:
        kernels = get_available_kernels()
        print("Available kernel versions:")
        for kernel in kernels:
            print(f"  - {kernel}")
    except FileNotFoundError:
        print("Configuration file not found")
    except Exception as e:
        print(f"Error loading configuration: {e}")

def add_kernel_version(version: str):
    """Add new kernel version to configuration."""
    config = load_kernel_config()
    current_kernels = config['kernels']['available']
    
    if version not in current_kernels:
        current_kernels.append(version)
        # Save updated configuration
        # (Implementation depends on your config saving mechanism)
        print(f"Added kernel version: {version}")
    else:
        print(f"Kernel version {version} already available")
```

### Custom Distribution Support

```python
from TKT.distro_configs import DistroConfigs

class CustomDistroConfigs(DistroConfigs):
    """Example custom distribution configuration."""
    
    custom_deps = [
        "custom-build-tools",
        "custom-kernel-dev",
        "custom-libraries"
    ]
    
    def __init__(self):
        self.packages = self.base_deps + self.custom_deps
    
    def update_repos(self) -> tuple[bool, str]:
        """Update repositories for custom distribution."""
        return self._run_command(
            ["sudo", "custompkg", "refresh"],
            "Updating custom distribution repositories"
        )
    
    def install_packages(self) -> tuple[bool, str]:
        """Install packages for custom distribution."""  
        return self._run_command(
            ["sudo", "custompkg", "install"] + self.packages,
            "Installing custom distribution packages"
        )

# Register custom distribution
def get_distro_configs_extended(distro_name: str):
    """Extended factory with custom distribution support."""
    from TKT.distro_configs import get_distro_configs
    
    if distro_name == "customdistro":
        return CustomDistroConfigs()
    else:
        return get_distro_configs(distro_name)
```

### Async Integration

```python
import asyncio
from TKT.cli import TKTSystemManager

async def async_dependency_installation():
    """Example of async integration with TKT."""
    manager = TKTSystemManager()
    
    # Run dependency installation in thread pool
    loop = asyncio.get_event_loop()
    success, message = await loop.run_in_executor(
        None, manager.install_dependencies
    )
    
    if success:
        print(f"Dependencies installed: {message}")
    else:
        print(f"Installation failed: {message}")

# Run async function
asyncio.run(async_dependency_installation())
```

### Integration with Other Tools

```python
from TKT.cli import TKTSystemManager, get_distribution_name
import subprocess

class KernelBuildPipeline:
    """Example integration class for kernel build pipelines."""
    
    def __init__(self):
        self.manager = TKTSystemManager()
        self.distro = get_distribution_name()
    
    def setup_environment(self) -> bool:
        """Set up complete kernel build environment."""
        if not self.manager.distro_supported:
            raise RuntimeError(f"Distribution {self.distro} not supported")
        
        # Install TKT dependencies
        success, message = self.manager.install_dependencies()
        if not success:
            raise RuntimeError(f"Failed to install dependencies: {message}")
        
        # Additional setup steps
        self._configure_build_environment()
        return True
    
    def _configure_build_environment(self):
        """Additional environment configuration."""
        # Custom build environment setup
        pass
    
    def build_kernel(self, version: str) -> bool:
        """Build specific kernel version."""
        # Kernel building logic
        print(f"Building kernel {version} on {self.distro}")
        return True
```

## Type Definitions

### Common Types

```python
from typing import TypeAlias, Tuple, Dict, List, Optional, Any

# Status tuple returned by most operations
StatusResult: TypeAlias = Tuple[bool, str]

# Configuration dictionary structure
ConfigDict: TypeAlias = Dict[str, Any]

# Kernel version list
KernelVersions: TypeAlias = List[str]

# System status information
SystemStatus: TypeAlias = Dict[str, Any]
```

### Protocol Definitions

```python
from typing import Protocol

class PackageManager(Protocol):
    """Protocol for package manager implementations."""
    
    def update_repos(self) -> StatusResult:
        """Update package repositories."""
        ...
    
    def install_packages(self) -> StatusResult:
        """Install required packages."""
        ...

class SystemManager(Protocol):
    """Protocol for system management implementations."""
    
    distro_supported: bool
    distro_name: Optional[str]
    
    def install_dependencies(self) -> StatusResult:
        """Install system dependencies."""
        ...
    
    def get_status(self) -> SystemStatus:
        """Get system status."""
        ...
```

## Extension Points

### Adding New Commands

The command handling system is extensible:

```python
class ExtendedKernelToolkitApp(KernelToolkitApp):
    """Extended app with custom commands."""
    
    async def handle_command(self, command: str) -> None:
        """Extended command handler."""
        
        # Handle custom commands
        if command.startswith("custom:"):
            await self.handle_custom_command(command[7:])
        
        # Fall back to parent handler
        else:
            await super().handle_command(command)
    
    async def handle_custom_command(self, cmd: str) -> None:
        """Handle custom command implementations."""
        if cmd == "status":
            await self.show_system_status()
        elif cmd == "cleanup":
            await self.cleanup_build_artifacts()
        # Add more custom commands as needed
```

### Plugin Architecture

```python
from abc import ABC, abstractmethod

class TKTPlugin(ABC):
    """Base class for TKT plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        pass
    
    @abstractmethod
    def initialize(self, manager: TKTSystemManager) -> bool:
        """Initialize plugin with system manager."""
        pass

class PluginManager:
    """Manages TKT plugins."""
    
    def __init__(self):
        self.plugins: List[TKTPlugin] = []
    
    def register_plugin(self, plugin: TKTPlugin) -> None:
        """Register a new plugin."""
        self.plugins.append(plugin)
    
    def initialize_plugins(self, manager: TKTSystemManager) -> None:
        """Initialize all registered plugins."""
        for plugin in self.plugins:
            plugin.initialize(manager)
```

### Custom Backend Integration

```python
from TKT.distro_configs import DistroConfigs

def register_custom_backend(name: str, config_class: type[DistroConfigs]) -> None:
    """Register custom distribution backend."""
    
    # Extend the factory function
    original_get_distro_configs = get_distro_configs
    
    def enhanced_get_distro_configs(distro_name: str) -> DistroConfigs:
        if distro_name == name:
            return config_class()
        return original_get_distro_configs(distro_name)
    
    # Replace factory function (in practice, you'd modify the original)
    globals()['get_distro_configs'] = enhanced_get_distro_configs

# Usage
register_custom_backend("nixos", NixOSConfigs)
```

---

## API Version Information

- **Current Version**: 0.1.0
- **Python Compatibility**: 3.11+
- **API Stability**: Alpha (breaking changes possible)
- **Documentation Version**: 2024.09.01

## Support and Resources

- **GitHub Repository**: [TKT_Framework](https://github.com/matteskes/TKT_Framework)
- **Issue Tracking**: [GitHub Issues](https://github.com/matteskes/TKT_Framework/issues)
- **API Discussions**: [GitHub Discussions](https://github.com/matteskes/TKT_Framework/discussions)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Developer Guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

*This API reference is generated from the codebase and is updated with each release. For the most current API information, please refer to the inline documentation and type hints in the source code.*
