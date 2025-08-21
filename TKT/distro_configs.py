"""
This module provides a common interface for handling distribution-
specific package management tasks such as updating repositories and
installing packages.

Usage:
    The main entrypoint is the `get_distro_configs` function, which
    takes the name of a Linux distribution (e.g., "arch", "debian",
    "ubuntu") and returns an appropriate configuration object. The
    configuration object provides methods for updating repositories and
    installing predefined packages.

Design:
    - The `DistroConfigs` abstract base class defines the interface and
      enforces that subclasses either implement both `update_repos` and
      `install_packages` or override `update_and_install` directly.
    - Subclasses should specify a list of `packages` and provide
      implementations appropriate for the target distribution.
    - This design allows new distributions to be supported by adding
      subclasses.

Example:
    >>> cfg = get_distro_configs("arch")
    >>> cfg.update_and_install()
"""

import subprocess as sp
from abc import ABC


class DistroConfigs(ABC):
    """
    Abstract base class for Linux distribution configuration.

    Subclasses must either:
    - Override both `update_repos` and `install_packages`, OR
    - Override `update_and_install` to handle everything themselves.
    """

    base_deps = [
        "bash",
        "bc",
        "bison",
        "ccache",
        "cmake",
        "cpio",
        "curl",
        "flex",
        "git",
        "kmod",
        "lz4",
        "make",
        "patchutils",
        "perl",
        "python3",
        "python3-pip",
        "rsync",
        "sudo",
        "tar",
        "time",
        "wget",
        "zstd",
    ]

    def update_repos(self):
        """
        Update the package repositories for the distribution.

        Subclasses must implement this method unless they override
        `update_and_install` directly.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} must implement 'update_repos' "
            "or override 'update_and_install'."
        )

    def install_packages(self):
        """
        Install the required packages for the distribution.

        Subclasses must implement this method unless they override
        `update_and_install` directly.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} must implement 'install_packages' "
            "or override 'update_and_install'."
        )

    def update_and_install(self):
        """
        Default implementation: update repositories, then install packages.

        Subclasses may override this entirely if they have a specialized
        process.
        """

        self.update_repos()
        self.install_packages()


class ArchConfigs(DistroConfigs):
    """Package management configuration for Arch Linux."""

    def update_and_install(self):
        sp.run(["makepkg", "-si"])


class DebianConfigs(DistroConfigs):
    """Package management configuration for Debian GNU/Linux."""

    deb_deps = [
        "binutils",
        "binutils-dev",
        "binutils-gold",
        "build-essential",
        "debhelper",
        "device-tree-compiler",
        "dpkg-dev",
        "dwarves",
        "fakeroot",
        "g++",
        "g++-multilib",
        "gcc",
        "gcc-multilib",
        "gnupg",
        "libc6-dev",
        "libc6-dev-i386",
        "libdw-dev",
        "libelf-dev",
        "libncurses-dev",
        "libnuma-dev",
        "libperl-dev",
        "libssl-dev",
        "libstdc++-14-dev",
        "libudev-dev",
        "ninja-build",
        "python3-setuptools",
        "qtbase5-dev",
        "schedtool",
        "xz-utils",
    ]

    # TODO: add logic for specific version number
    def __init__(self):
        self.packages = self.base_deps + self.deb_deps

    def update_repos(self):
        sp.run(["apt-get", "update", "-y"])

    def install_packages(self):
        sp.run(["apt-get", "install", "-y", *self.packages])


class UbuntuConfigs(DebianConfigs):
    """
    Package management configuration for Ubuntu.

    Inherits most behavior from Debian but adds extra packages.
    """


def get_distro_configs(name: str) -> DistroConfigs:
    """
    Return the configuration class associated with a given distribution
    name.

    Parameters
    ----------
    name: str
        The Linux distribution name (e.g., 'arch', 'debian', 'ubuntu').

    Returns
    -------
    DistroConfigs
        An instance of the appropriate configuration class for the given
        distro.

    Raises
    ------
    ValueError
        If the distribution is not recognized.
    """
    match name.lower():
        case "arch":
            return ArchConfigs()
        case "debian":
            return DebianConfigs()
        case "ubuntu":
            return UbuntuConfigs()
        case _:
            raise ValueError(f"Unsupported distribution: {name}")
