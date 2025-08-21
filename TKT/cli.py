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

from textual.app import App, ComposeResult
from textual.widgets import Input, Label


# These two functions retrieve the distribution ID and any like distributions
def get_like_distro():
    info = platform.freedesktop_os_release()
    ids = [info["ID"]]
    if "ID_LIKE" in info:
        ids.extend(info["ID_LIKE"].split())
    return ids


def get_distribution_name():
    return get_like_distro()[0]


def load_library(lib_name: str):
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
    title = "Kernel Toolkit"

    def compose(self) -> ComposeResult:
        welcome_message = (
            "Welcome to The Kernel Toolkit. This program will help users compile "
            "and install your custom Linux kernel."
        )
        yield Label(welcome_message)

        distro = get_distribution_name()
        yield Label(f"Detected distribution: {distro}")

        # Load settings.config
        config_path = os.path.join(os.path.dirname(__file__), "settings.config")
        config = configparser.ConfigParser()
        config.read(config_path)

        # Always resolve backend from settings.config (auto-populate if missing)
        backend = choose_backend(config, config_path)
        lib_module = load_library(backend)

        if lib_module:
            yield Label(f"Loaded library for {backend}")
        else:
            yield Label(f"No library found for '{backend}'")

        # Read available kernels from settings.config
        kernels = []
        try:
            available_kernels_str = config.get("kernels", "available")
            kernels = [k.strip() for k in available_kernels_str.split(",")]
        except (configparser.NoSectionError, configparser.NoOptionError):
            yield Label("No available kernels found in settings.config")
        else:
            yield Label("Available kernels to build:")
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
    app = KernelToolkitApp()
    app.run()


if __name__ == "__main__":
    main()
