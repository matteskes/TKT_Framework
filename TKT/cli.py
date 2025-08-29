# -*- coding: utf-8 -*-
"""
Created on 2025-08-14

@author: The Kernel Toolkit Project and contributors- (C) 2025.
All respective rights reserved.
@license: GNU General Public License v2-only (GPLv2)
@version: 0.3.0
@project: TKT Framework Project
@title: TKT Python Application
@contact: https://github.com/matteskes/TKT_Framework
@description: Python application for the TKT
"""

import importlib
import os
import platform
import sys
import tomllib
from types import ModuleType
from typing import Any, Dict, Final

import tomlkit
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.widgets import Input, Label

# Import distro_configs for package management
from TKT.distro_configs import get_distro_configs

SUPPORTED_DISTROS: Final[list[str]] = [
    "debian",
    "ubuntu",
    "fedora",
    "arch",
]


# Get distribution name using platform module
def get_distribution_name() -> str:
    if sys.platform != "linux":
        raise RuntimeError("Current operating system is not Linux")

    try:
        return platform.freedesktop_os_release()["ID"]
    except Exception:
        raise RuntimeError("Cannot get distribution name")


# Get supported distribution name or raise error if not supported
def get_supported_distribution_name() -> str:
    if sys.platform != "linux":
        raise RuntimeError("Current operating system is not Linux")

    try:
        info = platform.freedesktop_os_release()
        if info["ID"] in SUPPORTED_DISTROS:
            return info["ID"]
        elif info["ID_LIKE"] in SUPPORTED_DISTROS:
            return info["ID_LIKE"]
    except AttributeError:
        raise RuntimeError("Cannot get distribution name")
    except KeyError:
        raise RuntimeError(f"The distribution {info.get('ID')} is not supported")

    raise RuntimeError("Cannot get distribution name")


# Dynamically load the distribution-specific library
def load_library(lib_name: str) -> ModuleType | None:
    """Dynamically import a library by name, or return None if not found."""
    try:
        return importlib.import_module(lib_name)
    except ImportError:
        return None


# Enhanced backend chooser with distro config validation
def choose_backend(config: Dict[str, Any], config_path: str) -> tuple[str, bool]:
    """Ensure backend exists in config and validate distro support."""
    if "settings" not in config:
        config["settings"] = {}

    # Add default backend if missing
    if "backend" not in config["settings"]:
        distro = get_distribution_name()
        default_backend = f"kernel_lib_{distro}"
        config["settings"]["backend"] = default_backend

        # Persist the setting back to settings.toml
        with open(config_path, "w") as f:
            tomlkit.dump(config, f)

    backend = config["settings"]["backend"]

    # Check if distro is supported by distro_configs
    try:
        distro = get_distribution_name()
        get_distro_configs(distro)  # This will raise ValueError if unsupported
        distro_supported = True
    except ValueError:
        distro_supported = False

    return backend, distro_supported


class TKTSystemManager:
    """Manages system-level operations for TKT."""

    def __init__(self):
        self.distro = None
        self.distro_config = None
        self.distro_supported = False
        self._initialize_distro()

    def _initialize_distro(self):
        """Initialize distribution configuration."""
        try:
            self.distro = get_distribution_name()
            self.distro_config = get_distro_configs(self.distro)
            self.distro_supported = True
        except (ValueError, RuntimeError):
            # Reset all attributes when distribution is not supported
            self.distro = None
            self.distro_config = None
            self.distro_supported = False

    def install_dependencies(self) -> tuple[bool, str]:
        """
        Install required packages for kernel compilation.

        Returns:
            tuple[bool, str]: (success, message)
        """
        if not self.distro_supported or not self.distro_config:
            return (
                False,
                "Distribution not supported for automatic dependency installation",
            )

        try:
            self.distro_config.update_and_install()
            return True, "Dependencies installed successfully"
        except Exception as e:
            return False, f"Failed to install dependencies: {str(e)}"

    def prepare_kernel_source(self, kernel_version: str) -> tuple[bool, str]:
        """
        Prepare kernel source for compilation (placeholder for future implementation).

        Args:
            kernel_version: The kernel version to prepare

        Returns:
            tuple[bool, str]: (success, message)
        """
        # Placeholder for future kernel source setup logic
        return True, f"Kernel source preparation for {kernel_version} would go here"

    def configure_kernel(
        self, kernel_version: str, config_type: str = "default"
    ) -> tuple[bool, str]:
        """
        Configure kernel for compilation (placeholder for future implementation).

        Args:
            kernel_version: The kernel version to configure
            config_type: Type of configuration (default, custom, etc.)

        Returns:
            tuple[bool, str]: (success, message)
        """
        # Placeholder for future kernel configuration logic
        return (
            True,
            f"Kernel configuration for {kernel_version} ({config_type}) would go here",
        )


# Main application class using Textual
class KernelToolkitApp(App):
    title = "Kernel Toolkit"

    # Add key bindings for new functionality
    BINDINGS = [
        Binding("ctrl+d", "install_deps", "Install Dependencies"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.system_manager = TKTSystemManager()
        self.status_message = ""

        # Initialize TOML configuration
        self.config_path = os.path.join(os.path.dirname(__file__), "settings.toml")
        self.config = self._load_config()

        # Get backend info with distro validation
        self.backend, self.backend_distro_supported = choose_backend(
            self.config, self.config_path
        )
        self.lib_module = load_library(self.backend)

    def _load_config(self) -> Dict[str, Any]:
        """Load TOML configuration file."""
        try:
            with open(self.config_path, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            # Create default config if it doesn't exist
            default_config = {
                "kernels": {"available": []},
                "settings": {"backend": f"kernel_lib_{get_distribution_name()}"},
            }
            with open(self.config_path, "w") as f:
                tomlkit.dump(default_config, f)
            return default_config
        except Exception:
            # Fallback to empty config
            return {"kernels": {"available": []}, "settings": {}}

    def compose(self) -> ComposeResult:
        # Welcome block (centered with title + subtext) - UNCHANGED
        with Vertical(id="welcome_block"):
            yield Center(
                Label(
                    "Welcome to The Kernel Toolkit",
                    id="welcome_title",
                )
            )
            yield Center(
                Label(
                    "This program will help users compile and install your custom Linux kernel.",
                    id="welcome_subtext",
                )
            )

        # Distribution block - ENHANCED
        with Vertical(id="distro_block"):
            if self.system_manager.distro:
                yield Label(f"Detected distribution: {self.system_manager.distro}")
                if self.system_manager.distro_supported:
                    yield Label("Distribution supported for package management")
                else:
                    yield Label(
                        "Distribution not supported for automatic package management"
                    )
            else:
                yield Label("Could not detect distribution")

        # Backend / library resolution block
        with Vertical(id="backend_block"):
            if self.lib_module:
                yield Label(f"Loaded library for {self.backend}")
            else:
                yield Label(f"No library found for '{self.backend}'")

            if self.backend_distro_supported and self.system_manager.distro_supported:
                yield Label("Full system support available")
            else:
                yield Label("Limited functionality due to missing components")

        # Status block
        with Vertical(id="status_block"):
            yield Label(self.status_message, id="status_label")

        # Kernel list block
        kernels = []
        try:
            kernels = self.config.get("kernels", {}).get("available", [])
            if isinstance(kernels, str):  # Handle legacy format
                kernels = [k.strip() for k in kernels.split(",")]
        except Exception:
            pass

        if not kernels:
            with Vertical(id="kernels_block"):
                yield Label("No available kernels found in settings.toml")
        else:
            with Vertical(id="kernels_block"):
                yield Label("Available kernels to build:")
                for kernel in kernels:
                    yield Label(f"- {kernel}")

        # Enhanced help text
        with Vertical(id="help_block"):
            yield Label("Commands:")
            yield Label("• Enter kernel version to select for building")
            yield Label("• 'deps' or 'install-deps' - Install compilation dependencies")
            yield Label("• Ctrl+D - Install dependencies")
            yield Label("• Ctrl+Q - Quit")

        # Input block
        with Vertical(id="input_block"):
            yield Label(
                "Please enter the kernel version you want to build or a command:"
            )
            yield Input(
                placeholder=(
                    "Enter kernel version, 'deps', or command"
                    if kernels or self.system_manager.distro_supported
                    else "No kernels available and no package management support. Press CTRL+Q to exit."
                ),
                id="kernel_version_input",
                name="kernel_version_input",
                disabled=not (kernels or self.system_manager.distro_supported),
            )

    def update_status(self, message: str):
        """Update the status message display."""
        self.status_message = message
        try:
            status_label = self.query_one("#status_label", Label)
            status_label.update(message)
        except (AttributeError, LookupError):
            pass  # Status label might not be mounted yet

    def action_install_deps(self):
        """Install dependencies via key binding."""
        self.update_status("Installing dependencies...")
        self.refresh()

        success, message = self.system_manager.install_dependencies()
        self.update_status(f"{'✓' if success else '✗'} {message}")

    def handle_command(self, command: str) -> bool:
        """
        Handle special commands.

        Returns:
            bool: True if command was handled, False otherwise
        """
        command_lower = command.lower().strip()

        if command_lower in ["deps", "install-deps"]:
            self.update_status("Installing dependencies...")
            self.refresh()

            success, message = self.system_manager.install_dependencies()
            self.update_status(f"{'✓' if success else '✗'} {message}")
            return True

        # Future commands can be added here
        elif command_lower.startswith("config:"):
            # Example: config:default, config:custom
            config_type = command_lower[7:]  # Remove 'config:'
            self.update_status(
                f"Kernel configuration ({config_type}) would be implemented here"
            )
            return True

        elif command_lower.startswith("prepare:"):
            # Example: prepare:6.16
            kernel_version = command_lower[8:]  # Remove 'prepare:'
            success, message = self.system_manager.prepare_kernel_source(kernel_version)
            self.update_status(f"{'✓' if success else '✗'} {message}")
            return True

        return False

    # Handle input submission
    def on_input_submitted(self, event) -> None:
        user_input = event.input.value.strip()
        input_widget = self.query_one("#kernel_version_input", Input)

        # Validate input
        if not user_input:
            input_widget.placeholder = "Please enter a valid kernel version or command."
            return

        # Check if it's a command
        if self.handle_command(user_input):
            input_widget.value = ""  # Clear the input
            return

        # Handle as kernel version selection
        kernel_version = user_input

        # Get available kernels for validation
        kernels = []
        try:
            kernels = self.config.get("kernels", {}).get("available", [])
            if isinstance(kernels, str):  # Handle legacy format
                kernels = [k.strip() for k in kernels.split(",")]
        except Exception:
            kernels = []

        # Validate kernel version if kernels are defined
        if kernels and kernel_version not in kernels:
            self.update_status(
                f" Kernel version {kernel_version} not in available list"
            )
        else:
            self.update_status(f" Kernel version {kernel_version} selected")

        input_widget.value = ""  # Clear the input

    # Focus input again
    def on_mount(self) -> None:
        # Focus the input if it's enabled
        input_widget = self.query_one("#kernel_version_input", Input)
        if not input_widget.disabled:
            input_widget.focus()


# Main function to run the app
def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Error: stdin and stdout must be a tty", file=sys.stderr)
        return 1

    app = KernelToolkitApp()
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
