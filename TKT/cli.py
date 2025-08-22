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
from textual.widgets import Input, Label
from textual.containers import Vertical

SUPPORTED_DISTROS: Final[list[str]] = [
    "debian",
    "ubuntu",
    "fedora",
    "arch",
]


def get_distribution_name() -> str:
    """Return the Linux distribution name using freedesktop_os_release()."""
    if sys.platform != "linux":
        raise RuntimeError("Current operating system is not Linux")

    try:
        return platform.freedesktop_os_release()["ID"]
    except Exception:
        raise RuntimeError("Cannot get distribution name")


def get_supported_distribution_name() -> str:
    """Return supported distribution name or raise if unsupported."""
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


def load_library(lib_name: str) -> ModuleType | None:
    """Dynamically import a library by name, or return None if not found."""
    try:
        return importlib.import_module(lib_name)
    except ImportError:
        return None


def choose_backend(config: configparser.ConfigParser, config_path: str) -> str:
    """Ensure [settings] backend exists in config, defaulting to distro."""
    if not config.has_section("settings"):
        config.add_section("settings")

    if not config.has_option("settings", "backend"):
        distro = get_distribution_name()
        default_backend = f"kernel_lib_{distro}"
        config.set("settings", "backend", default_backend)

        # Persist the setting back to settings.config
        with open(config_path, "w") as f:
            config.write(f)

    return config.get("settings", "backend")


class KernelToolkitApp(App):
    """Textual-based UI application for the Kernel Toolkit."""

    title = "Kernel Toolkit"

    # CSS styling for consistent margins, padding, and nested items
    CSS = """
    #welcome_block {
        width: 100%;
        align: center top;
        padding-bottom: 3;
    }

    .left-section {
        margin-left: 2;
    }

    .nested-item {
        margin-left: 4;
    }

    #kernels_title {
        padding-top: 1;
        text-style: bold;
    }

    #distro {
        padding-top: 1;
    }

    #backend_status {
        padding-top: 1;
    }

    #kernel_version_input {
        padding-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Build and yield the application layout."""

        # Welcome block (centered header with subtitle)
        yield Vertical(
            Label("Welcome to The Kernel Toolkit", id="welcome_title", classes="bold"),
            Label(
                "This program will help users compile and install your custom Linux kernel.",
                id="welcome_subtitle",
            ),
            id="welcome_block",
        )

        # Distro detection
        distro = get_distribution_name()
        yield Label(f"Detected distribution: {distro}", id="distro", classes="left-section")

        # Load settings.config
        config_path = os.path.join(os.path.dirname(__file__), "settings.config")
        config = configparser.ConfigParser()
        config.read(config_path)

        # Always resolve backend from settings.config (auto-populate if missing)
        backend = choose_backend(config, config_path)
        lib_module = load_library(backend)

        if lib_module:
            yield Label(f"Loaded library for {backend}", id="backend_status", classes="left-section")
        else:
            yield Label(f"No library found for '{backend}'", id="backend_status", classes="left-section")

        # Read available kernels from settings.config
        kernels = []
        try:
            available_kernels_str = config.get("kernels", "available")
            kernels = [k.strip() for k in available_kernels_str.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError):
            yield Label("No available kernels found in settings.config", classes="left-section")
        else:
            yield Label("Available kernels to build:", id="kernels_title", classes="left-section")
            for kernel in kernels:
                yield Label(f"• {kernel}", classes="nested-item")

        # Always create the input field, disable it if no kernels found
        yield Label("Please enter the kernel version you want to build:", classes="left-section")
        yield Input(
            placeholder=(
                "Enter the kernel version to build"
                if kernels
                else "No kernels available. Please check settings.config or Press CTRL+Q to exit."
            ),
            id="kernel_version_input",
            name="kernel_version_input",
            disabled=not kernels,
            classes="left-section",
        )

    def on_input_submitted(self, event) -> None:
        """Handle kernel version input submission events."""
        kernel_version = event.input.value.strip()
        if not kernel_version:
            self.query_one("#kernel_version_input", Input).placeholder = (
                "Please enter a valid kernel version."
            )
            return

        # Mock build feedback
        self.query_one("#kernel_version_input", Input).placeholder = (
            f"Selecting kernel version {kernel_version}..."
        )
        self.query_one("#kernel_version_input", Input).placeholder = (
            f"Kernel version {kernel_version} Selected."
        )

    def on_mount(self) -> None:
        """Focus the input field if kernels are available."""
        input_widget = self.query_one("#kernel_version_input", Input)
        if not input_widget.disabled:
            input_widget.focus()


def main():
    """Main entry point for launching the TUI."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Error: stdin and stdout must be a tty", file=sys.stderr)
        return 1

    app = KernelToolkitApp()
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
