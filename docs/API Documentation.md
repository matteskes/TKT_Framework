# TKT API Documentation

This document provides detailed API documentation for The Kernel Toolkit (TKT) modules and classes.

## Table of Contents

- [CLI Module (`cli.py`)](#cli-module-clipy)
- [Distribution Configurations (`distro_configs.py`)](#distribution-configurations-distro_configspy)
- [Configuration Management](#configuration-management)
- [Error Handling](#error-handling)

## CLI Module (`cli.py`)

### Functions

#### `get_distribution_name() -> str`

Detects the current Linux distribution name.

**Returns:**
- `str`: The distribution ID (e.g., "ubuntu", "arch", "debian")

**Raises:**
- `RuntimeError`: If the operating system is not Linux or distribution cannot be detected

**Example:**
```python
try:
    distro = get_distribution_name()
    print(f"Detected distribution: {distro}")
except RuntimeError as e:
    print(f"Error: {e}")
```

#### `get_supported_distribution_name() -> str`

Gets the distribution name, ensuring it's supported by TKT.

**Returns:**
- `str`: Supported distribution name

**Raises:**
- `RuntimeError`: If OS is not Linux, distribution is unsupported, or cannot be detected

#### `load_library(lib_name: str) -> ModuleType | None`

Dynamically imports a library by name.

**Parameters:**
- `lib_name` (str): Name of the library to import

**Returns:**
- `ModuleType | None`: The imported module or None if import fails

**Example:**
```python
lib = load_library("kernel_lib_arch")
if lib:
    print("Library loaded successfully")
else:
    print("Library not found")
```

#### `choose_backend(config: Dict[str, Any], config_path: str) -> tuple[str, bool]`

Selects and validates the backend configuration.

**Parameters:**
- `config` (Dict[str, Any]): Configuration dictionary
- `config_path` (str): Path to configuration file

**Returns:**
- `tuple[str, bool]`: Backend name and whether distribution is supported

### Classes

#### `TKTSystemManager`

Manages system-level operations for TKT.

##### Methods

**`__init__()`**

Initializes the system manager and detects distribution configuration.

**`install_dependencies() -> tuple[bool, str]`**

Installs required packages for kernel compilation.

**Returns:**
- `tuple[bool, str]`: (success status, status message)

**Example:**
```python
manager = TKTSystemManager()
success, message = manager.install_dependencies()
if success:
    print("Dependencies installed successfully")
else:
    print(f"Installation failed: {message}")
```

**`prepare_kernel_source(kernel_version: str) -> tuple[bool, str]`**

Prepares kernel source for compilation (placeholder implementation).

**Parameters:**
- `kernel_version` (str): Target kernel version

**Returns:**
- `tuple[bool, str]`: (success status, status message)

**`configure_kernel(kernel_version: str, config_type: str = "default") -> tuple[bool, str]`**

Configures kernel for compilation (placeholder implementation).

**Parameters:**
- `kernel_version` (str): Target kernel version
- `config_type` (str, optional): Configuration type. Defaults to "default"

**Returns:**
- `tuple[bool, str]`: (success status, status message)

#### `KernelToolkitApp(App)`

Main Textual application class.

##### Attributes

- `title` (str): Application title displayed in terminal
- `BINDINGS` (list): Key binding definitions

##### Methods

**`__init__()`**

Initializes the application with system manager and configuration.

**`compose() -> ComposeResult`**

Creates the application UI layout.

**Returns:**
- `ComposeResult`: Textual compose result with UI widgets

**`update_status(message: str)`**

Updates the status message in the UI.

**Parameters:**
- `message` (str): Status message to display

**`handle_command(command: str) -> bool`**

Processes special commands entered by the user.

**Parameters:**
- `command` (str): Command string to process

**Returns:**
- `bool`: True if command was handled, False otherwise

**Supported Commands:**
- `deps`, `install-deps`: Install dependencies
- `config:TYPE`: Configure kernel (planned)
- `prepare:VERSION`: Prepare kernel source (planned)

**`action_install_deps()`**

Key binding action for installing dependencies (Ctrl+D).

**`on_input_submitted(event)`**

Handles user input submission from the input widget.

**`on_mount()`**

Called when the application is mounted. Focuses the input widget.

## Distribution Configurations (`distro_configs.py`)

### Abstract Base Classes

#### `DistroConfigs(ABC)`

Abstract base class for Linux distribution configuration.

##### Attributes

- `base_deps` (list): Common dependencies across all distributions

##### Abstract Methods

**`update_repos()`**

Updates package repositories for the distribution. Must be implemented by subclasses.

**Raises:**
- `NotImplementedError`: If not implemented by subclass

**`install_packages()`**

Installs required packages for the distribution. Must be implemented by subclasses.

**Raises:**
- `NotImplementedError`: If not implemented by subclass

##### Concrete Methods

**`update_and_install()`**

Default implementation that calls `update_repos()` then `install_packages()`. Can be overridden for specialized behavior.

### Concrete Implementations

#### `ArchConfigs(DistroConfigs)`

Package management configuration for Arch Linux.

##### Methods

**`update_and_install()`**

Runs `makepkg -si` for Arch Linux package management.

#### `DebianConfigs(DistroConfigs)`

Package management configuration for Debian GNU/Linux.

##### Attributes

- `deb_deps` (list): Debian-specific dependencies
- `packages` (list): Combined base and Debian dependencies

##### Methods

**`__init__()`**

Initializes with combined package list.

**`update_repos()`**

Runs `apt-get update -y`.

**`install_packages()`**

Runs `apt-get install -y` with package list.

#### `UbuntuConfigs(DebianConfigs)`

Package management configuration for Ubuntu. Inherits from `DebianConfigs`.

### Functions

#### `get_distro_configs(name: str) -> DistroConfigs`

Factory function that returns appropriate configuration class for a distribution.

**Parameters:**
- `name` (str): Linux distribution name

**Returns:**
- `DistroConfigs`: Configuration instance for the distribution

**Raises:**
- `ValueError`: If distribution is not supported

**Supported Distributions:**
- `"arch"` → `ArchConfigs`
- `"debian"` → `DebianConfigs` 
- `"ubuntu"` → `UbuntuConfigs`

**Example:**
```python
try:
    config = get_distro_configs("ubuntu")
    config.update_and_install()
except ValueError as e:
    print(f"Unsupported distribution: {e}")
```

## Configuration Management

### TOML Configuration Format

The application uses TOML format for configuration files:

```toml
[kernels]
available = ["6.16", "6.15.1"]

[settings]
backend = "kernel_lib_arch"
```

### Configuration Schema

#### `[kernels]` section
- `available` (list[str] or str): Available kernel versions for compilation

#### `[settings]` section  
- `backend` (str): Backend library name (auto-configured)

### Configuration Loading

Configuration is loaded in `KernelToolkitApp.__init__()` with fallback defaults:

```python
def _load_config(self) -> Dict[str, Any]:
    """Load TOML configuration with error handling and defaults."""
    try:
        with open(self.config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        # Create and return default configuration
        return self._create_default_config()
```

## Error Handling

### Exception Types

The application handles several exception types:

- `RuntimeError`: System-level errors (OS detection, unsupported distribution)
- `ValueError`: Invalid configuration values
- `ModuleNotFoundError`: Missing backend libraries
- `FileNotFoundError`: Missing configuration files
- `ImportError`: Failed module imports

### Error Patterns

#### Distribution Detection
```python
try:
    distro = get_distribution_name()
except RuntimeError:
    # Handle unsupported OS or detection failure
    pass
```

#### Configuration Loading
```python
try:
    config = load_config()
except FileNotFoundError:
    # Use default configuration
    config = create_default_config()
```

#### Package Installation
```python
success, message = manager.install_dependencies()
if not success:
    # Handle installation failure
    display_error(message)
```

### Best Practices

1. **Always handle exceptions** for system operations
2. **Provide meaningful error messages** to users
3. **Use fallback defaults** when possible
4. **Log errors** for debugging purposes
5. **Validate user input** before processing

## Extension Points

### Adding New Distributions

1. **Create configuration class:**
```python
class NewDistroConfigs(DistroConfigs):
    def update_repos(self):
        # Implementation for new distro
        pass
    
    def install_packages(self):
        # Implementation for new distro  
        pass
```

2. **Register in factory function:**
```python
def get_distro_configs(name: str) -> DistroConfigs:
    match name.lower():
        case "newdistro":
            return NewDistroConfigs()
        # ... existing cases
```

3. **Add to supported list:**
```python
SUPPORTED_DISTROS = [
    "debian", "ubuntu", "fedora", "arch", "newdistro"
]
```

### Adding New Commands

Add command handling in `KernelToolkitApp.handle_command()`:

```python
def handle_command(self, command: str) -> bool:
    if command_lower == "newcommand":
        # Handle new command
        return True
    # ... existing command handling
```

This API documentation provides the foundation for understanding and extending the TKT framework.