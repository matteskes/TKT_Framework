"""
Kernel configuration management module.

This module provides functionality to manage Linux kernel configuration files,
including loading, modifying, and validating .config files with proper
dependency resolution using make olddefconfig.

Usage:
    The main entrypoint is the `KernelConfig` class, which handles the full
    workflow of ensuring a config exists, applying user changes, and validating
    dependencies.

Design:
    - The `KernelConfig` class follows a similar pattern to `DistroConfigs`
    - Provides status feedback compatible with the Textual UI
    - Includes proper error handling and backup/restore functionality
    - Designed for easy integration with the existing TKTSystemManager
"""

import shutil
import subprocess as sp
from pathlib import Path
from typing import Dict, List, Tuple


class KernelConfig:
    """
    Manages kernel configuration files with automatic dependency resolution.

    The class follows this workflow:
    1. Load existing .config or generate with make defconfig if missing
    2. Apply user modifications to config entries
    3. Run make olddefconfig to resolve dependencies
    4. Provide status updates for integration with UI

    Example:
        >>> config = KernelConfig("/path/to/linux-6.16", "6.16")
        >>> changes = {"CONFIG_DEBUG_KERNEL": "y", "CONFIG_LOCALVERSION": '"-custom"'}
        >>> success, message = config.apply_config_changes(changes)
    """

    def __init__(self, kernel_source_dir: str, kernel_version: str):
        self.kernel_source_dir = Path(kernel_source_dir)
        self.kernel_version = kernel_version
        self.config_path = self.kernel_source_dir / ".config"
        self.backup_path = self.kernel_source_dir / ".config.backup"
        self.status_messages: List[str] = []

    def add_status(self, message: str) -> None:
        """
        Add a status message for UI integration.

        Parameters
        ----------
        message : str
            Status message to add to the log
        """
        self.status_messages.append(message)
        # Keep only the most recent messages
        if len(self.status_messages) > 10:
            self.status_messages.pop(0)

    def get_status(self) -> str:
        """
        Get current status for UI display.

        Returns
        -------
        str
            Formatted status messages
        """
        return "\n".join(self.status_messages[-5:])

    def validate_kernel_source(self) -> bool:
        """
        Validate that the kernel source directory exists and is proper.

        Returns
        -------
        bool
            True if kernel source is valid, False otherwise
        """
        if not self.kernel_source_dir.exists():
            self.add_status(
                f"Error: Kernel source directory not found: {self.kernel_source_dir}"
            )
            return False

        # Check for key kernel files to validate this is a kernel source
        required_files = ["Kconfig", "Makefile", "init"]
        if not any((self.kernel_source_dir / f).exists() for f in required_files):
            self.add_status("Error: Directory does not appear to contain kernel source")
            return False

        self.add_status(f"Valid kernel source: {self.kernel_source_dir}")
        return True

    def ensure_config_exists(self) -> bool:
        """
        Ensure .config exists, run make defconfig if missing.

        Returns
        -------
        bool
            True if config exists or was created successfully
        """
        if self.config_path.exists():
            self.add_status("Found existing .config file")
            return True

        self.add_status("No .config found, running 'make defconfig'...")

        try:
            result = sp.run(
                ["make", "defconfig"],
                cwd=self.kernel_source_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                self.add_status("Successfully generated default config")
                return True
            else:
                self.add_status(f"make defconfig failed: {result.stderr}")
                return False

        except sp.TimeoutExpired:
            self.add_status("make defconfig timed out after 5 minutes")
            return False
        except Exception as e:
            self.add_status(f"Error running make defconfig: {str(e)}")
            return False

    def backup_config(self) -> bool:
        """
        Create a backup of the current config file.

        Returns
        -------
        bool
            True if backup was successful
        """
        try:
            if self.config_path.exists():
                shutil.copy2(self.config_path, self.backup_path)
                self.add_status("Created backup of .config")
                return True
            return False
        except Exception as e:
            self.add_status(f"Failed to backup config: {str(e)}")
            return False

    def restore_config(self) -> bool:
        """
        Restore config from backup.

        Returns
        -------
        bool
            True if restore was successful
        """
        try:
            if self.backup_path.exists():
                shutil.copy2(self.backup_path, self.config_path)
                self.add_status("Restored .config from backup")
                return True
            return False
        except Exception as e:
            self.add_status(f"Failed to restore config: {str(e)}")
            return False

    def read_config(self) -> Dict[str, str]:
        """
        Read the current .config file into a dictionary.

        Returns
        -------
        Dict[str, str]
            Dictionary of config options and their values
        """
        config_dict: Dict[str, str] = {}

        if not self.config_path.exists():
            return config_dict

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#") or line.startswith("//"):
                        continue

                    # Parse CONFIG_OPTION=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config_dict[key.strip()] = value.strip()

            self.add_status(f"Read {len(config_dict)} config options")
            return config_dict

        except Exception as e:
            self.add_status(f"Error reading config: {str(e)}")
            return {}

    def write_config(self, config_dict: Dict[str, str]) -> bool:
        """
        Write configuration dictionary to .config file.

        Parameters
        ----------
        config_dict : Dict[str, str]
            Dictionary of config options to write

        Returns
        -------
        bool
            True if write was successful
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                # Write header
                f.write("#\n# Automatically generated file; DO NOT EDIT.\n#\n")
                f.write("# Kernel configuration\n#\n\n")

                # Write config entries in sorted order for consistency
                for key in sorted(config_dict.keys()):
                    f.write(f"{key}={config_dict[key]}\n")

            self.add_status(f"Successfully wrote {len(config_dict)} config options")
            return True

        except Exception as e:
            self.add_status(f"Error writing config: {str(e)}")
            return False

    def modify_config(self, changes: Dict[str, str]) -> bool:
        """
        Modify specific config options.

        Parameters
        ----------
        changes : Dict[str, str]
            Dictionary of config changes to apply

        Returns
        -------
        bool
            True if modifications were successful
        """
        if not self.config_path.exists():
            self.add_status("No config file to modify")
            return False

        # Read current config
        config_dict = self.read_config()

        # Apply changes
        for key, value in changes.items():
            config_dict[key] = value
            self.add_status(f"Set {key}={value}")

        # Write modified config
        return self.write_config(config_dict)

    def run_olddefconfig(self) -> Tuple[bool, str]:
        """
        Run make olddefconfig to resolve dependencies.

        Returns
        -------
        Tuple[bool, str]
            (success, message) indicating the result
        """
        self.add_status("Running 'make olddefconfig' to resolve dependencies...")

        try:
            result = sp.run(
                ["make", "olddefconfig"],
                cwd=self.kernel_source_dir,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
            )

            if result.returncode == 0:
                message = "Successfully resolved config dependencies"
                self.add_status(message)
                return True, message
            else:
                error_msg = f"make olddefconfig failed: {result.stderr}"
                self.add_status(error_msg)
                return False, error_msg

        except sp.TimeoutExpired:
            error_msg = "make olddefconfig timed out after 3 minutes"
            self.add_status(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running make olddefconfig: {str(e)}"
            self.add_status(error_msg)
            return False, error_msg

    def apply_config_changes(self, changes: Dict[str, str]) -> Tuple[bool, str]:
        """
        Main method to apply config changes with full workflow.

        Parameters
        ----------
        changes : Dict[str, str]
            Dictionary of config changes to apply

        Returns
        -------
        Tuple[bool, str]
            (success, message) indicating the result
        """
        self.add_status(f"Applying config changes for kernel {self.kernel_version}")

        # Step 1: Validate kernel source
        if not self.validate_kernel_source():
            return False, "Invalid kernel source directory"

        # Step 2: Ensure config exists
        if not self.ensure_config_exists():
            return False, "Failed to create initial config"

        # Step 3: Backup current config
        self.backup_config()

        # Step 4: Apply user changes
        if not self.modify_config(changes):
            self.restore_config()
            return False, "Failed to apply config changes"

        # Step 5: Run olddefconfig
        success, message = self.run_olddefconfig()

        if not success:
            self.restore_config()
            return False, f"Config validation failed: {message}"

        return True, "Successfully applied and validated config changes"


# Integration function for TKTSystemManager
def configure_kernel_with_changes(
    kernel_source_dir: str, kernel_version: str, config_changes: Dict[str, str]
) -> Tuple[bool, str]:
    """
    Helper function for easy integration with TKTSystemManager.

    Parameters
    ----------
    kernel_source_dir : str
        Path to kernel source directory
    kernel_version : str
        Kernel version string
    config_changes : Dict[str, str]
        Dictionary of config changes to apply

    Returns
    -------
    Tuple[bool, str]
        (success, message) indicating the result
    """
    config_manager = KernelConfig(kernel_source_dir, kernel_version)
    return config_manager.apply_config_changes(config_changes)
