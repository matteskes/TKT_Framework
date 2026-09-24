# TKT API Reference Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation & Import](#installation--import)
3. [Core API](#core-api)
4. [TKTSystemManager Additional Methods](#tktsystemmanager-additional-methods)
5. [Data Fetching API](#data-fetching-api)
6. [Safe Execution API](#safe-execution-api)
7. [Kernel Configuration API](#kernel-configuration-api)
8. [Distribution Support API](#distribution-support-api)
9. [Error Handling](#error-handling)
10. [Examples & Usage Patterns](#examples--usage-patterns)
11. [Type Definitions](#type-definitions)
12. [Extension Points](#extension-points)

## Overview

The Kernel Toolkit (TKT) provides both a command-line interface and a
programmatic API for kernel compilation and management across multiple
Linux distributions. This guide documents the public API for developers
who want to integrate TKT functionality into their own applications.

### API Design Principles

- _Type Safety_: All public functions include comprehensive type hints
- _Error Handling_: Consistent error reporting with structured exceptions
- _Cross-Platform_: Works across supported Linux distributions
- _Extensible_: Plugin architecture for adding new distributions
- _Async-Ready_: Compatible with async/await patterns where appropriate

## Installation & Import

```python
# For UI integration
from TKT.cli import KernelToolkitApp

# For distribution support
from TKT.cli import SUPPORTED_DISTROS, get_distribution_name, get_supported_distribution_name
```

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

#### SystemManager Class Definition

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

#### install_dependencies()

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

#### get_status()

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

#### on_input_submitted()

```python
def on_input_submitted(self, event) -> None:
    """Handle user input submission from the UI.

    Processes user input as either a kernel version or a special command.
    Validates kernel versions against the available list.

    Args:
        event: Textual Input submission event containing user input.
    """
```

#### handle_command(command: str) -> bool

```python
def handle_command(self, command: str) -> bool:
    """Handle special CLI commands.

    Processes special commands like 'deps', 'prepare', 'config'.
    Commands are recognized by their prefix (e.g., 'prepare:6.16').

    Args:
        command: The command string from user input.

    Returns:
        bool: True if command was handled, False otherwise.

    Supported Commands:
        - 'deps' / 'install-deps': Install kernel compilation dependencies
        - 'prepare:<version>': Prepare kernel source with full workflow
        - 'config:<type>': Configure kernel (placeholder for future use)

    Example:
        >>> app = KernelToolkitApp()
        >>> app.handle_command('prepare:6.16')  # Returns True
        >>> app.handle_command('unknown')        # Returns False
    """
```

#### update_status(message: str) -> None

```python
def update_status(self, message: str) -> None:
    """Update the status message displayed in the UI.

    Updates both the internal status_message attribute and the
    UI status label widget.

    Args:
        message: Status message to display.
    """
```

#### Abstract Methods

#### update_repos()

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

#### install_packages()

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

#### _run_command()

```python
def _run_command(self, cmd: list[str], description: str) -> tuple[bool, str]:
    """
    Execute system command with error handling.
    
    Args:
        cmd: Command and arguments as list
        description: Human-readable description for logging

    Returns:
        tuple[bool, str]: Result of command execution

    Example:
        >>> config = ArchConfigs()
        >>> success, msg = config._run_command(
        ...     ["sudo", "pacman", "-Sy"], 
        ...     "Updating repositories"
        ... )
        >>> print(f"Installation: {success}, {msg}")
    """
```

### get_available_kernel_releases()

```python
def get_available_kernel_releases(self) -> list[dict[str, Any]]:
    """Fetch available kernel releases from remote source.

    Retrieves the list of available kernel versions/releases that can
    be selected in the application.

    Returns:
        list[dict[str, Any]]: List of available kernel release data.

    Example:
        >>> releases = manager.get_available_kernel_releases()
        >>> for release in releases:
        ...     print(release['version'])
    """
```

---

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

### Configuration Management in Examples

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

### TKTSystemManager Additional Methods

#### prepare_kernel_source(kernel_version: str) -> tuple[bool, str]

```python
def prepare_kernel_source(self, kernel_version: str) -> tuple[bool, str]:
    """Prepare kernel source with configuration workflow.

    Downloads kernel source, validates it, applies configuration changes,
    resolves dependencies with make olddefconfig, and saves the final config.

    Args:
        kernel_version: Kernel version string (e.g., '6.16').

    Returns:
        tuple[bool, str]: (success_status, message) describing the result.

    Example:
        >>> manager = TKTSystemManager()
        >>> success, message = manager.prepare_kernel_source('6.16')
        >>> if success:
        ...     print(f'Config saved: {message}')
    """
```

#### configure_kernel(kernel_version: str, config_type: str = 'default') -> tuple[bool, str]

```python
def configure_kernel(
    self, kernel_version: str, config_type: str = 'default'
) -> tuple[bool, str]:
    """Configure kernel with specified settings.

    Placeholder method for future kernel configuration workflows.

    Args:
        kernel_version: Kernel version string.
        config_type: Configuration type ('default' or 'custom').

    Returns:
        tuple[bool, str]: (success_status, message).

    Example:
        >>> manager = TKTSystemManager()
        >>> success, message = manager.configure_kernel('6.16', 'custom')
    """
```

#### load_library_from_backend() -> ModuleType | None

```python
def load_library_from_backend(self) -> 'ModuleType | None':
    """Load the backend library module based on current backend.

    Dynamically imports the backend library module (e.g.,
    'kernel_lib_arch') based on the configured backend. Returns None
    if the library is not found.

    Returns:
        ModuleType | None: The imported module, or None if not found.

    Example:
        >>> manager = TKTSystemManager()
        >>> lib = manager.load_library_from_backend()
        >>> if lib:
        ...     print(f'Loaded backend: {lib.__name__}')
    """
```

---

## Data Fetching API

### Fetch Overview

The `TKT.fetch` module provides utilities for fetching data from
remote sources with caching support, downloading files with progress
reporting, and parsing GitHub release data. These utilities are
designed for lightweight, file-based caching without requiring
external databases.

### Fetch Import

```python
from TKT.fetch import (
    cached_fetch,
    download_file,
    get_files_from_releases,
    FileData,
    FileSize,
    filename_from_url,
)
```

### cached_fetch()

```python
def cached_fetch(url: str, name: str, ttl: int = 3600) -> Any:
    """Fetch JSON data from a URL with transparent caching.

    The response is stored locally under $XDG_STATE_HOME/TKT (or
    ~/.local/state/TKT if not set). Subsequent calls reuse the cached
    data until the specified time-to-live (TTL) expires (default: 1 hour).

    Args:
        url: The URL to fetch JSON data from.
        name: A unique identifier for the cached data (used as cache filename).
        ttl: Time-to-live in seconds before cache expires (default: 3600).

    Returns:
        Any: The parsed JSON data from the response. Returns cached data
        if the cache is still valid.

    Example:
        >>> releases = cached_fetch(
        ...     'https://api.github.com/repos/owner/repo/releases',
        ...     'kernel_releases'
        ... )
        >>> for release in releases.ok:
        ...     print(release['name'])
    """
```

### download_file()

```python
def download_file(
    url: str, output: 'str | None' = None, quiet: bool = False
) -> str:
    """Download a file from the given URL and save it to the current directory.

    The output filename is derived from the URL. By default, progress is
    shown in the terminal if the server provides a Content-Length header.
    If quiet is True, no progress is displayed. Existing files are never
    overwritten.

    Args:
        url: The URL to download the file from.
        output: Optional output filename. If None, derived from URL.
        quiet: If True, suppress progress output.

    Returns:
        str: The path to the downloaded file.

    Example:
        >>> path = download_file(
        ...     'https://example.com/kernel.tar.xz',
        ...     quiet=True
        ... )
        >>> print(f'Downloaded to: {path}')
    """
```

### get_files_from_releases()

```python
def get_files_from_releases(
    releases: list[dict[str, Any]]
) -> list[FileData]:
    """Parse data about releases fetched from the GitHub API.

    Extracts file information from GitHub release assets, parsing
    distribution, scheduler, and compiler information from filenames.

    Args:
        releases: List of release dictionaries from GitHub API.

    Returns:
        list[FileData]: Parsed file data objects with extracted metadata.

    Example:
        >>> raw_releases = cached_fetch(api_url, 'releases').ok
        >>> files = get_files_from_releases(raw_releases)
        >>> for f in files:
        ...     print(f'{f.distro}: {f.size} — {f.name}')
    """
```

### FileData

```python
@dataclass(frozen=True)
class FileData:
    """Immutable data class representing a release file.

    Attributes:
        name: The filename of the release asset.
        size: The file size as a FileSize object.
        updated_at: Last update timestamp.
        digest: SHA256 digest of the file.
        url: Download URL for the asset.
        version: Full release name/version string.
        tag: GitHub release tag name.
        distro: Parsed distribution name (from filename).
        scheduler: Parsed kernel scheduler (from filename).
        compiler: Parsed compiler name (from filename).

    Example:
        >>> file = FileData(
        ...     name='Arch-linux-6.16-bore-gcc.tar.gz',
        ...     size=FileSize(56245816),
        ...     updated_at=datetime.now(timezone.utc),
        ...     digest='sha256:abc123...',
        ...     url='https://example.com/file.tar.gz',
        ...     version='TKT v6.16-tkt',
        ...     tag='v6.16-tkt'
        ... )
        >>> print(f.distro)    # 'Arch'
        >>> print(f.scheduler) # 'bore'
        >>> print(f.compiler)  # 'gcc'
    """
```

## Safe Execution API

### Safe Overview

The `TKT.safe` module implements a Rust-style Result pattern for
error handling in Python. Functions decorated with `@safe` return a
`Result` object instead of raising exceptions, enabling explicit
error handling without try/except blocks. This pattern is inspired
by Rust's `Result<T, E>` type.

### Safe Import

```python
from TKT.safe import safe, Ok, Err, SafeFunction, Result
```

### safe Decorator

```python
def safe(func: Callable[P, T]) -> SafeFunction[P, T]:
    """Decorate a function to return a Result instead of raising exceptions.

    When applied, the decorated function will never raise exceptions.
    Instead, successful results are wrapped in Ok() and errors in Err().
    Set TKT_DEBUG=true environment variable to disable wrapping.

    Args:
        func: The function to wrap with safe error handling.

    Returns:
        SafeFunction: A wrapper that returns Result instead of raising.

    Example:
        >>> @safe
        ... def read_config(path: str) -> dict:
        ...     return json.loads(Path(path).read_text())

        >>> result = read_config('/etc/tkt/config.json')
        >>> if result.is_ok:
        ...     config = result.unwrap()
        >>> else:
        ...     print(f'Error: {result.err}')
    """
```

### Ok Class

```python
class Ok(BaseResult[T, Any]):
    """Successful Result variant.

    Wraps a successful return value. Evaluates to True in boolean contexts.

    Attributes:
        _value: The successful return value of the wrapped function.

    Methods:
        unwrap(): Returns the contained value.
        unwrap_or(default): Returns the value (ignores default).
        map(op): Applies a function to the value.
        is_ok: Always True.
        ok: Returns the value.

    Example:
        >>> result = Ok(42)
        >>> result.is_ok    # True
        >>> result.unwrap() # 42
        >>> result.ok       # 42
    """
```

### Err Class

```python
class Err(BaseResult[Never, E]):
    """Failed Result variant.

    Wraps an exception that was raised by the wrapped function.
    Evaluates to False in boolean contexts.

    Attributes:
        _error: The exception that was raised.

    Methods:
        unwrap(): Re-raises the contained error.
        unwrap_or(default): Returns the default value.
        map_err(op): Transforms the error.
        is_err: Always True.
        err: Returns the error.

    Example:
        >>> result = Err(RuntimeError('failed'))
        >>> result.is_err   # True
        >>> result.err      # RuntimeError('failed')
    """
```

### SafeFunction Class

```python
class SafeFunction(Generic[P, T]):
    """Wraps a function to return a Result instead of raising exceptions.

    This class creates a callable wrapper that executes the stored
    function and returns an Ok or Err instead of raising an exception.

    Attributes:
        _func: The original function to wrap.

    Example:
        >>> def divide(a, b):
        ...     return a / b

        >>> safe_divide = SafeFunction(divide)
        >>> safe_divide(10, 2)   # Ok(5.0)
        >>> safe_divide(10, 0)   # Err(ZeroDivisionError(...))
    """
```

### Result Type Alias

```python
Result: TypeAlias = 'Ok[Any] | Err[Any]'
```

---

## Kernel Configuration API

### Kernel Config Overview

The `TKT.kernel_config` module provides comprehensive kernel
configuration file management, including loading, modifying,
validating, and backing up `.config` files with automatic dependency
resolution using `make olddefconfig`.

### Kernel Config Import

```python
from TKT.kernel_config import KernelConfig, configure_kernel_with_changes
```

### KernelConfig Class

```python
class KernelConfig:
    """Manages kernel configuration files with automatic dependency resolution.

    The class follows this workflow:
    1. Load existing .config or generate with make defconfig if missing
    2. Apply user modifications to config entries
    3. Run make olddefconfig to resolve dependencies
    4. Provide status updates for integration with UI

    Attributes:
        kernel_source_dir: Path to the kernel source directory.
        kernel_version: Kernel version string (e.g., '6.16').
        config_path: Path to the .config file.
        backup_path: Path to the backup .config file.
        status_messages: List of status messages for UI integration.

    Example:
        >>> config = KernelConfig('/path/to/linux-6.16', '6.16')
        >>> changes = {'CONFIG_DEBUG_KERNEL': 'y', 'CONFIG_LOCALVERSION': '"-custom"'}
        >>> success, message = config.apply_config_changes(changes)
    """
```

#### Key Methods

#### __init__()

```python
def __init__(self, kernel_source_dir: str, kernel_version: str):
    """Initialize kernel configuration manager.

    Args:
        kernel_source_dir: Path to the kernel source directory.
        kernel_version: Kernel version string (e.g., '6.16').
    """
```

#### ensure_config_exists() -> bool

```python
def ensure_config_exists(self) -> bool:
    """Ensure .config exists, run make defconfig if missing.

    Checks if a .config file exists in the kernel source directory.
    If not, runs 'make defconfig' to generate a default configuration.

    Returns:
        bool: True if .config exists or was successfully generated.
    """
```

#### validate_kernel_source() -> bool

```python
def validate_kernel_source(self) -> bool:
    """Validate that the kernel source directory exists and is proper.

    Checks for key kernel files (Kconfig, Makefile, init/) to verify
    this is a valid kernel source directory.

    Returns:
        bool: True if the kernel source is valid.
    """
```

#### read_config() -> dict[str, str]

```python
def read_config(self) -> dict[str, str]:
    """Read and parse the .config file into a dictionary.

    Returns:
        dict[str, str]: Dictionary of config entries (key-value pairs).
    """
```

#### write_config(config: dict[str, str]) -> bool

```python
def write_config(self, config: dict[str, str]) -> bool:
    """Write a dictionary of config entries to the .config file.

    Args:
        config: Dictionary of config entries to write.

    Returns:
        bool: True if writing was successful.
    """
```

#### apply_config_changes(changes: dict[str, str]) -> tuple[bool, str]

```python
def apply_config_changes(
    self, changes: dict[str, str]
) -> tuple[bool, str]:
    """Apply and validate kernel configuration changes.

    Full workflow: validates source, ensures .config exists, applies
    changes, runs make olddefconfig, and validates the result.

    Args:
        changes: Dictionary of config changes to apply.

    Returns:
        tuple[bool, str]: (success, message) describing the result.

    Example:
        >>> changes = {
        ...     'CONFIG_DEBUG_KERNEL': 'y',
        ...     'CONFIG_LOCALVERSION': '"-custom"'
        ... }
        >>> success, message = config.apply_config_changes(changes)
    """
```

#### backup_config() -> bool

```python
def backup_config(self) -> bool:
    """Create a backup of the current .config file.

    Returns:
        bool: True if backup was successful.
    """
```

#### restore_config() -> bool

```python
def restore_config(self) -> bool:
    """Restore the .config file from backup.

    Returns:
        bool: True if restoration was successful.
    """
```

#### save_config_to_file(output_dir: str, distro: str = 'unknown') -> tuple[bool, str]

```python
def save_config_to_file(
    self, output_dir: str, distro: str = 'unknown'
) -> tuple[bool, str]:
    """Save the final resolved .config to a persistent location.

    Copies the kernel source's .config file to a distribution- and
    kernel-version-specific path under output_dir.

    Args:
        output_dir: Base directory where configs should be stored.
        distro: Distribution name for naming the saved file.

    Returns:
        tuple[bool, str]: (success, message) indicating the result.

    Example:
        >>> config.save_config_to_file('/tmp/configs', 'arch')
        (True, 'Config saved to /tmp/configs/arch-6.16.config')
    """
```

#### get_saved_config_path(output_dir: str, distro: str = 'unknown') -> str

```python
def get_saved_config_path(
    self, output_dir: str, distro: str = 'unknown'
) -> str:
    """Return the path where a saved config would be stored.

    Args:
        output_dir: Base directory where configs are stored.
        distro: Distribution name used for naming the saved file.

    Returns:
        str: Absolute path to the saved config file.

    Example:
        >>> config.get_saved_config_path('/tmp/configs', 'arch')
        '/tmp/configs/arch-6.16.config'
    """
```

#### get_status() / add_status()

```python
def get_status(self) -> str:
    """Get current status for UI display.

    Returns:
        str: Formatted status messages (last 5).
    """

def add_status(self, message: str) -> None:
    """Add a status message for UI integration.

    Args:
        message: Status message to add to the log.
    """
```

### configure_kernel_with_changes()

```python
def configure_kernel_with_changes(
    kernel_source_dir: str,
    kernel_version: str,
    config_changes: dict[str, str],
) -> tuple[bool, str]:
    """Helper function for easy integration with TKTSystemManager.

    Creates a KernelConfig instance and applies the given config changes.

    Args:
        kernel_source_dir: Path to kernel source directory.
        kernel_version: Kernel version string.
        config_changes: Dictionary of config changes to apply.

    Returns:
        Tuple[bool, str]: (success, message) indicating the result.

    Example:
        >>> success, message = configure_kernel_with_changes(
        ...     '/path/to/linux-6.16',
        ...     '6.16',
        ...     {'CONFIG_DEBUG_KERNEL': 'y'}
        ... )
    """
```

---

```python
Result: TypeAlias = 'Ok[Any] | Err[Any]'
```

### Usage Pattern

```python
# Basic usage with decorated function
from TKT.safe import safe

@safe
def fetch_kernel_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Handle result
result = fetch_kernel_data('https://api.example.com/releases')
if result.is_ok:
    data = result.unwrap()
    print(f'Found {len(data)} releases')
else:
    print(f'Fetch failed: {result.err}')

# Chaining with map
result = fetch_kernel_data(url).map(lambda d: d['assets'])

# Providing defaults
data = fetch_kernel_data(url).unwrap_or(default_data)

# Error transformation
safe_result = fetch_kernel_data(url).map_err(
    lambda e: RuntimeError(f'Network error: {e}')
)
```

---

### FileSize

```python
class FileSize(int):
    """A typed integer representing file sizes with human-readable formatting.

    Provides automatic conversion to human-readable units (B, KB, MB, GB, etc.)
    when converted to string.

    Attributes:
        _bytes: The underlying byte count as an integer.

    Example:
        >>> size = FileSize(1048576)
        >>> print(str(size))  # '1 MB'
        >>> print(repr(size)) # 'FileSize(1048576)'
        >>> int(size)         # 1048576
    """
```

### filename_from_url()

```python
def filename_from_url(url: str) -> str:
    """Extract filename from a URL.

    Args:
        url: The URL to extract a filename from.

    Returns:
        str: The filename component of the URL path.
            Returns 'downloaded.file' if no filename is present.

    Example:
        >>> filename_from_url('https://example.com/path/to/file.tar.gz')
        'file.tar.gz'
    """
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

- _Current Version_: 0.1.0
- _Python Compatibility_: 3.11+
- _API Stability_: Alpha (breaking changes possible)
- _Documentation Version_: 2024.09.01

## Support and Resources

- _GitHub Repository_: [TKT_Framework](https://github.com/matteskes/TKT_Framework)
- _Issue Tracking_: [GitHub Issues](https://github.com/matteskes/TKT_Framework/issues)
- _API Discussions_: [GitHub Discussions](https://github.com/matteskes/TKT_Framework/discussions)
- _Contributing Guide_: [CONTRIBUTING.md](CONTRIBUTING.md)
- _Developer Guide_: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

_This API reference is generated from the codebase and is updated
with each release. For the most current API information, please refer
to the inline documentation and type hints in the source code._
