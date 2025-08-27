# -*- coding: utf-8 -*-
"""
Created on 2025-08-14

@author: The Kernel Toolkit Project and contributors- (C) 2025.
All respective rights reserved.
@license: GNU General Public License v2-only (GPLv2)
@version: 0.1.0
@project: TKT Framework Project
@title: TKT Python Application
@contact: https://github.com/matteskes/TKT_Framework
@description: Python application for the TKT
"""

import configparser
import importlib
import os
import platform
import sys
from types import ModuleType
from typing import Final

from textual.app import App, ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Input, Label

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


# Ensure backend is set in config, defaulting to distro-specific if missing
def choose_backend(config: configparser.ConfigParser, config_path: str) -> str:
    """Ensure [settings] backend exists in config, defaulting to distro."""
    if not config.has_section("settings"):
        config.add_section("settings")

    # Add default backend if missing
    if not config.has_option("settings", "backend"):
        distro = get_distribution_name()
        default_backend = f"kernel_lib_{distro}"
        config.set("settings", "backend", default_backend)

        # Persist the setting back to settings.config
        with open(config_path, "w") as f:
            config.write(f)

    # Return the backend value
    return config.get("settings", "backend")


# Main application class using Textual
class KernelToolkitApp(App):
    title = "Kernel Toolkit"

    # CSS path for styling
    def compose(self) -> ComposeResult:

        # Welcome block (centered with title + subtext)
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

        # Distribution block
        distro = get_distribution_name()
        with Vertical(id="distro_block"):
            yield Label(f"Detected distribution: {distro}")

        # Backend / library resolution block
        config_path = os.path.join(os.path.dirname(__file__), "settings.config")
        config = configparser.ConfigParser()
        config.read(config_path)

        # Always resolve backend from settings.config (auto-populate if missing)
        backend = choose_backend(config, config_path)
        lib_module = load_library(backend)

        with Vertical(id="backend_block"):
            if lib_module:
                yield Label(f"Loaded library for {backend}")
            else:
                yield Label(f"No library found for '{backend}'")

        # Kernel list block
        kernels = []
        try:
            available_kernels_str = config.get("kernels", "available")
            kernels = [k.strip() for k in available_kernels_str.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError):
            with Vertical(id="kernels_block"):
                yield Label("No available kernels found in settings.config")
        else:
            with Vertical(id="kernels_block"):
                yield Label("Available kernels to build:")
                for kernel in kernels:
                    yield Label(f"- {kernel}")

        # Input block (always shown, disabled if no kernels available)
        with Vertical(id="input_block"):
            yield Label("Please enter the kernel version you want to build:")
            yield Input(
                placeholder=(
                    "Enter the kernel version to build"
                    if kernels
                    else "No kernels available. Please check settings.config or Press CTRL+Q to exit."
                ),
                id="kernel_version_input",
                name="kernel_version_input",
                disabled=not kernels,
            )

    # Handle input submission
    def on_input_submitted(self, event) -> None:
        kernel_version = event.input.value.strip()
        input_widget = self.query_one("#kernel_version_input", Input)

        # Validate input
        if not kernel_version:
            input_widget.placeholder = "Please enter a valid kernel version."
            return

        # Mock build feedback - use a single placeholder update
        input_widget.placeholder = f"Kernel version {kernel_version} selected."
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
