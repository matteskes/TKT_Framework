# -*- coding: utf-8 -*-
"""
Created on 2025-08-14

@author: The Kernel Toolkit Project and contributors- (C) 2025. All respective rights reserved.
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

SUPPORTED_DISTROS: Final[list[str]] = [
    "debian",
    "ubuntu",
    "fedora",
    "arch",
]


def get_distribution_name() -> str:
    if sys.platform != "linux":
        raise RuntimeError("Current operating system is not Linux")

    try:
        return platform.freedesktop_os_release()["ID"]
    except Exception:
        raise RuntimeError("Cannot get distribution name")


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


# Main application class for the Kernel Toolkit
# This class is responsible for the main application logic, including UI composition and event handling.
# It uses Textual for the UI framework and provides a simple interface for users to select and build kernel versions.
class KernelToolkitApp(App):
    title = "Kernel Toolkit"

    def compose(self) -> ComposeResult:
        welcome_message = "Welcome to The Kernel Toolkit. This program will help users compile and install your custom Linux kernel."
        yield Label(welcome_message)

        distro = get_distribution_name()
        yield Label(f"Detected distribution: {distro}")

        # Try sourcing a distribution-specific library
        lib_module: ModuleType | None = None
        try:
            lib_module = importlib.import_module(f"TKT.kernel_lib_{distro}")
            yield Label(f"Sourced distribution-specific library for {distro}")
        except ImportError:
            yield Label(f"No distribution-specific library found for {distro}")

        # Read available kernels from settings.config
        config_path = os.path.join(os.path.dirname(__file__), "settings.config")
        config = configparser.ConfigParser()
        config.read(config_path)

        kernels = []
        try:
            available_kernels_str = config.get("kernels", "available")
            kernels = [k.strip() for k in available_kernels_str.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError):
            yield Label("No available kernels found in settings.config")
        else:
            yield Label("Available kernels to build. ")
            for kernel in kernels:
                yield Label(f"- {kernel}")

        # Always create the input field, disable it if no kernels found
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

        # Add a submit button for the input

    def on_input_submitted(self, event) -> None:
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
        # Focus the input if it’s enabled
        input_widget = self.query_one("#kernel_version_input", Input)
        if not input_widget.disabled:
            input_widget.focus()


def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Error: stdin and stdout must be a tty", file=sys.stderr)
        return 1

    app = KernelToolkitApp()
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
