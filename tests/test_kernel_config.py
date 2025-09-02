import shutil
import subprocess as sp
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from TKT.kernel_config import KernelConfig, configure_kernel_with_changes


class TestKernelConfig:
    """Test suite for KernelConfig class."""

    @pytest.fixture
    def temp_kernel_dir(self):
        """Create a temporary directory that mimics a kernel source tree."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kernel_dir = Path(temp_dir) / "linux-6.16"
            kernel_dir.mkdir()

            # Create essential kernel source files
            (kernel_dir / "Kconfig").write_text("# Kernel configuration")
            (kernel_dir / "Makefile").write_text("# Kernel Makefile")
            (kernel_dir / "init").mkdir()

            yield kernel_dir

    @pytest.fixture
    def kernel_config(self, temp_kernel_dir):
        """Create KernelConfig instance with temp directory."""
        return KernelConfig(str(temp_kernel_dir), "6.16")

    def test_init(self, temp_kernel_dir):
        """Test KernelConfig initialization."""
        config = KernelConfig(str(temp_kernel_dir), "6.16")

        assert config.kernel_source_dir == temp_kernel_dir
        assert config.kernel_version == "6.16"
        assert config.config_path == temp_kernel_dir / ".config"
        assert config.backup_path == temp_kernel_dir / ".config.backup"
        assert config.status_messages == []

    def test_add_status(self, kernel_config):
        """Test status message management."""
        kernel_config.add_status("First message")
        kernel_config.add_status("Second message")

        assert len(kernel_config.status_messages) == 2
        assert kernel_config.status_messages == ["First message", "Second message"]

    def test_add_status_max_messages(self, kernel_config):
        """Test status message limit enforcement."""
        # Add more than 10 messages
        for i in range(15):
            kernel_config.add_status(f"Message {i}")

        # Should keep only 10 most recent
        assert len(kernel_config.status_messages) == 10
        assert kernel_config.status_messages[0] == "Message 5"
        assert kernel_config.status_messages[-1] == "Message 14"

    def test_get_status(self, kernel_config):
        """Test status retrieval for UI display."""
        messages = ["Msg1", "Msg2", "Msg3", "Msg4", "Msg5", "Msg6", "Msg7"]
        for msg in messages:
            kernel_config.add_status(msg)

        status = kernel_config.get_status()
        # Should return last 5 messages joined with newlines
        expected = "Msg3\nMsg4\nMsg5\nMsg6\nMsg7"
        assert status == expected

    def test_validate_kernel_source_valid(self, kernel_config):
        """Test kernel source validation with valid directory."""
        result = kernel_config.validate_kernel_source()

        assert result is True
        assert any(
            "Valid kernel source" in msg for msg in kernel_config.status_messages
        )

    def test_validate_kernel_source_missing_directory(self, temp_kernel_dir):
        """Test kernel source validation with missing directory."""
        # Remove the directory
        shutil.rmtree(temp_kernel_dir)

        config = KernelConfig(str(temp_kernel_dir), "6.16")
        result = config.validate_kernel_source()

        assert result is False
        assert any("not found" in msg for msg in config.status_messages)

    def test_validate_kernel_source_invalid_directory(self, temp_kernel_dir):
        """Test kernel source validation with directory lacking kernel files."""
        # Remove kernel-specific files
        (temp_kernel_dir / "Kconfig").unlink()
        (temp_kernel_dir / "Makefile").unlink()
        shutil.rmtree(temp_kernel_dir / "init")

        config = KernelConfig(str(temp_kernel_dir), "6.16")
        result = config.validate_kernel_source()

        assert result is False
        assert any(
            "does not appear to contain kernel source" in msg
            for msg in config.status_messages
        )

    def test_ensure_config_exists_with_existing_config(self, kernel_config):
        """Test ensure_config_exists when .config already exists."""
        # Create existing config file
        kernel_config.config_path.write_text("CONFIG_DUMMY=y\n")

        result = kernel_config.ensure_config_exists()

        assert result is True
        assert any(
            "Found existing .config" in msg for msg in kernel_config.status_messages
        )

    @patch("subprocess.run")
    def test_ensure_config_exists_make_defconfig_success(self, mock_run, kernel_config):
        """Test ensure_config_exists when make defconfig succeeds."""
        mock_run.return_value.returncode = 0

        result = kernel_config.ensure_config_exists()

        assert result is True
        mock_run.assert_called_once_with(
            ["make", "defconfig"],
            cwd=kernel_config.kernel_source_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert any(
            "Successfully generated default config" in msg
            for msg in kernel_config.status_messages
        )

    @patch("subprocess.run")
    def test_ensure_config_exists_make_defconfig_failure(self, mock_run, kernel_config):
        """Test ensure_config_exists when make defconfig fails."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "make: *** [defconfig] Error 1"

        result = kernel_config.ensure_config_exists()

        assert result is False
        assert any(
            "make defconfig failed" in msg for msg in kernel_config.status_messages
        )

    @patch("subprocess.run")
    def test_ensure_config_exists_timeout(self, mock_run, kernel_config):
        """Test ensure_config_exists when make defconfig times out."""
        mock_run.side_effect = sp.TimeoutExpired("make", 300)

        result = kernel_config.ensure_config_exists()

        assert result is False
        assert any("timed out" in msg for msg in kernel_config.status_messages)

    @patch("subprocess.run")
    def test_ensure_config_exists_exception(self, mock_run, kernel_config):
        """Test ensure_config_exists when subprocess raises exception."""
        mock_run.side_effect = OSError("Command not found")

        result = kernel_config.ensure_config_exists()

        assert result is False
        assert any(
            "Error running make defconfig" in msg
            for msg in kernel_config.status_messages
        )

    def test_backup_config_success(self, kernel_config):
        """Test successful config backup."""
        # Create config file to backup
        kernel_config.config_path.write_text("CONFIG_TEST=y\n")

        result = kernel_config.backup_config()

        assert result is True
        assert kernel_config.backup_path.exists()
        assert kernel_config.backup_path.read_text() == "CONFIG_TEST=y\n"
        assert any("Created backup" in msg for msg in kernel_config.status_messages)

    def test_backup_config_no_config(self, kernel_config):
        """Test backup when no config file exists."""
        result = kernel_config.backup_config()

        assert result is False
        assert not kernel_config.backup_path.exists()

    def test_backup_config_exception(self, kernel_config, mocker):
        """Test backup when shutil.copy2 raises exception."""
        kernel_config.config_path.write_text("CONFIG_TEST=y\n")
        mocker.patch("shutil.copy2", side_effect=OSError("Permission denied"))

        result = kernel_config.backup_config()

        assert result is False
        assert any(
            "Failed to backup config" in msg for msg in kernel_config.status_messages
        )

    def test_restore_config_success(self, kernel_config):
        """Test successful config restoration."""
        # Create backup file
        kernel_config.backup_path.write_text("CONFIG_BACKUP=y\n")

        result = kernel_config.restore_config()

        assert result is True
        assert kernel_config.config_path.exists()
        assert kernel_config.config_path.read_text() == "CONFIG_BACKUP=y\n"
        assert any(
            "Restored .config from backup" in msg
            for msg in kernel_config.status_messages
        )

    def test_restore_config_no_backup(self, kernel_config):
        """Test restore when no backup exists."""
        result = kernel_config.restore_config()

        assert result is False

    def test_restore_config_exception(self, kernel_config, mocker):
        """Test restore when shutil.copy2 raises exception."""
        kernel_config.backup_path.write_text("CONFIG_BACKUP=y\n")
        mocker.patch("shutil.copy2", side_effect=OSError("Permission denied"))

        result = kernel_config.restore_config()

        assert result is False
        assert any(
            "Failed to restore config" in msg for msg in kernel_config.status_messages
        )

    def test_read_config_success(self, kernel_config):
        """Test reading valid config file."""
        config_content = """# Linux kernel configuration
CONFIG_64BIT=y
CONFIG_X86_64=y
CONFIG_LOCALVERSION="-custom"
# CONFIG_DEBUG_KERNEL is not set
CONFIG_MODULES=y

# End of configuration
"""
        kernel_config.config_path.write_text(config_content)

        result = kernel_config.read_config()

        expected = {
            "CONFIG_64BIT": "y",
            "CONFIG_X86_64": "y",
            "CONFIG_LOCALVERSION": '"-custom"',
            "CONFIG_MODULES": "y",
        }
        assert result == expected
        assert any(
            "Read 4 config options" in msg for msg in kernel_config.status_messages
        )

    def test_read_config_missing_file(self, kernel_config):
        """Test reading non-existent config file."""
        result = kernel_config.read_config()

        assert result == {}

    def test_read_config_exception(self, kernel_config, mocker):
        """Test reading config file when exception occurs."""
        kernel_config.config_path.write_text("CONFIG_TEST=y\n")
        mocker.patch("builtins.open", side_effect=OSError("Permission denied"))

        result = kernel_config.read_config()

        assert result == {}
        assert any(
            "Error reading config" in msg for msg in kernel_config.status_messages
        )

    def test_write_config_success(self, kernel_config):
        """Test writing config file successfully."""
        config_dict = {
            "CONFIG_64BIT": "y",
            "CONFIG_MODULES": "y",
            "CONFIG_LOCALVERSION": '"-test"',
        }

        result = kernel_config.write_config(config_dict)

        assert result is True
        content = kernel_config.config_path.read_text()

        # Check header
        assert "Automatically generated file" in content
        assert "Kernel configuration" in content

        # Check config entries (should be sorted)
        assert "CONFIG_64BIT=y" in content
        assert 'CONFIG_LOCALVERSION="-test"' in content
        assert "CONFIG_MODULES=y" in content

        assert any(
            "Successfully wrote 3 config options" in msg
            for msg in kernel_config.status_messages
        )

    def test_write_config_exception(self, kernel_config, mocker):
        """Test writing config file when exception occurs."""
        config_dict = {"CONFIG_TEST": "y"}
        mocker.patch("builtins.open", side_effect=OSError("Permission denied"))

        result = kernel_config.write_config(config_dict)

        assert result is False
        assert any(
            "Error writing config" in msg for msg in kernel_config.status_messages
        )

    def test_modify_config_success(self, kernel_config):
        """Test modifying existing config."""
        # Create initial config
        initial_config = "CONFIG_64BIT=y\nCONFIG_MODULES=y\n"
        kernel_config.config_path.write_text(initial_config)

        changes = {
            "CONFIG_MODULES": "n",  # Change existing
            "CONFIG_DEBUG": "y",  # Add new
        }

        result = kernel_config.modify_config(changes)

        assert result is True
        content = kernel_config.config_path.read_text()
        assert "CONFIG_MODULES=n" in content
        assert "CONFIG_DEBUG=y" in content
        assert "CONFIG_64BIT=y" in content  # Unchanged option should remain

    def test_modify_config_no_existing_file(self, kernel_config):
        """Test modifying config when no file exists."""
        changes = {"CONFIG_TEST": "y"}

        result = kernel_config.modify_config(changes)

        assert result is False
        assert any(
            "No config file to modify" in msg for msg in kernel_config.status_messages
        )

    @patch("subprocess.run")
    def test_run_olddefconfig_success(self, mock_run, kernel_config):
        """Test successful olddefconfig execution."""
        mock_run.return_value.returncode = 0

        success, message = kernel_config.run_olddefconfig()

        assert success is True
        assert "Successfully resolved config dependencies" in message
        mock_run.assert_called_once_with(
            ["make", "olddefconfig"],
            cwd=kernel_config.kernel_source_dir,
            capture_output=True,
            text=True,
            timeout=180,
        )

    @patch("subprocess.run")
    def test_run_olddefconfig_failure(self, mock_run, kernel_config):
        """Test failed olddefconfig execution."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Configuration error"

        success, message = kernel_config.run_olddefconfig()

        assert success is False
        assert "make olddefconfig failed: Configuration error" in message

    @patch("subprocess.run")
    def test_run_olddefconfig_timeout(self, mock_run, kernel_config):
        """Test olddefconfig timeout."""
        mock_run.side_effect = sp.TimeoutExpired("make", 180)

        success, message = kernel_config.run_olddefconfig()

        assert success is False
        assert "timed out after 3 minutes" in message

    @patch("subprocess.run")
    def test_run_olddefconfig_exception(self, mock_run, kernel_config):
        """Test olddefconfig when subprocess raises exception."""
        mock_run.side_effect = OSError("Command not found")

        success, message = kernel_config.run_olddefconfig()

        assert success is False
        assert "Error running make olddefconfig: Command not found" in message

    @patch("subprocess.run")
    def test_apply_config_changes_full_success(self, mock_run, kernel_config):
        """Test complete successful workflow of apply_config_changes."""
        # Mock make commands to succeed
        mock_run.return_value.returncode = 0

        # Create initial config
        kernel_config.config_path.write_text("CONFIG_64BIT=y\n")

        changes = {"CONFIG_DEBUG_KERNEL": "y", "CONFIG_LOCALVERSION": '"-custom"'}

        success, message = kernel_config.apply_config_changes(changes)

        assert success is True
        assert "Successfully applied and validated config changes" in message

        # Verify backup was created
        assert kernel_config.backup_path.exists()

        # Verify changes were applied
        content = kernel_config.config_path.read_text()
        assert "CONFIG_DEBUG_KERNEL=y" in content
        assert 'CONFIG_LOCALVERSION="-custom"' in content

    def test_apply_config_changes_invalid_kernel_source(self, temp_kernel_dir):
        """Test apply_config_changes with invalid kernel source."""
        # Remove kernel files to make directory invalid
        shutil.rmtree(temp_kernel_dir)

        config = KernelConfig(str(temp_kernel_dir), "6.16")
        changes = {"CONFIG_TEST": "y"}

        success, message = config.apply_config_changes(changes)

        assert success is False
        assert "Invalid kernel source directory" in message

    @patch("subprocess.run")
    def test_apply_config_changes_config_creation_failure(
        self, mock_run, kernel_config
    ):
        """Test apply_config_changes when config creation fails."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "make failed"

        changes = {"CONFIG_TEST": "y"}

        success, message = kernel_config.apply_config_changes(changes)

        assert success is False
        assert "Failed to create initial config" in message

    @patch("subprocess.run")
    def test_apply_config_changes_olddefconfig_failure_with_restore(
        self, mock_run, kernel_config
    ):
        """Test apply_config_changes when olddefconfig fails and config is restored."""

        # Mock make defconfig to succeed, olddefconfig to fail
        def mock_run_side_effect(*args, **kwargs):
            command = args[0]
            if command == ["make", "defconfig"]:
                mock_result = Mock()
                mock_result.returncode = 0
                return mock_result
            elif command == ["make", "olddefconfig"]:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stderr = "Config validation failed"
                return mock_result

        mock_run.side_effect = mock_run_side_effect

        # Create initial config to enable backup
        kernel_config.config_path.write_text("CONFIG_ORIGINAL=y\n")

        changes = {"CONFIG_TEST": "y"}

        success, message = kernel_config.apply_config_changes(changes)

        assert success is False
        assert "Config validation failed" in message

        # Verify config was restored to original state
        content = kernel_config.config_path.read_text()
        assert "CONFIG_ORIGINAL=y" in content
        assert "CONFIG_TEST=y" not in content


class TestConfigureKernelWithChanges:
    """Test the helper function for TKTSystemManager integration."""

    @pytest.fixture
    def temp_kernel_dir(self):
        """Create a temporary directory that mimics a kernel source tree."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kernel_dir = Path(temp_dir) / "linux-6.16"
            kernel_dir.mkdir()

            # Create essential kernel source files
            (kernel_dir / "Kconfig").write_text("# Kernel configuration")
            (kernel_dir / "Makefile").write_text("# Kernel Makefile")
            (kernel_dir / "init").mkdir()

            yield kernel_dir

    @patch("TKT.kernel_config.KernelConfig")
    def test_configure_kernel_with_changes_success(
        self, mock_kernel_config_class, temp_kernel_dir
    ):
        """Test successful configuration through helper function."""
        mock_config_instance = Mock()
        mock_config_instance.apply_config_changes.return_value = (True, "Success")
        mock_kernel_config_class.return_value = mock_config_instance

        changes = {"CONFIG_DEBUG": "y"}

        success, message = configure_kernel_with_changes(
            str(temp_kernel_dir), "6.16", changes
        )

        assert success is True
        assert message == "Success"

        mock_kernel_config_class.assert_called_once_with(str(temp_kernel_dir), "6.16")
        mock_config_instance.apply_config_changes.assert_called_once_with(changes)

    @patch("TKT.kernel_config.KernelConfig")
    def test_configure_kernel_with_changes_failure(
        self, mock_kernel_config_class, temp_kernel_dir
    ):
        """Test failed configuration through helper function."""
        mock_config_instance = Mock()
        mock_config_instance.apply_config_changes.return_value = (False, "Failed")
        mock_kernel_config_class.return_value = mock_config_instance

        changes = {"CONFIG_DEBUG": "y"}

        success, message = configure_kernel_with_changes(
            str(temp_kernel_dir), "6.16", changes
        )

        assert success is False
        assert message == "Failed"


class TestKernelConfigEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.fixture
    def temp_kernel_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            kernel_dir = Path(temp_dir) / "linux-6.16"
            kernel_dir.mkdir()
            (kernel_dir / "Kconfig").write_text("# Kernel configuration")
            (kernel_dir / "Makefile").write_text("# Kernel Makefile")
            (kernel_dir / "init").mkdir()
            yield kernel_dir

    def test_config_parsing_malformed_lines(self, temp_kernel_dir):
        """Test parsing config with malformed lines."""
        config = KernelConfig(str(temp_kernel_dir), "6.16")

        malformed_content = """# Valid comment
CONFIG_VALID=y
MALFORMED_LINE_WITHOUT_EQUALS
CONFIG_EMPTY_VALUE=
CONFIG_SPACES = y
# Another comment
CONFIG_QUOTED="value with spaces"
"""
        config.config_path.write_text(malformed_content)

        result = config.read_config()

        expected = {
            "CONFIG_VALID": "y",
            "CONFIG_EMPTY_VALUE": "",
            "CONFIG_SPACES": "y",
            "CONFIG_QUOTED": '"value with spaces"',
        }
        assert result == expected

    def test_unicode_config_handling(self, temp_kernel_dir):
        """Test handling of unicode characters in config."""
        config = KernelConfig(str(temp_kernel_dir), "6.16")

        unicode_config = {"CONFIG_LOCALVERSION": '"-ñice"', "CONFIG_TEST": "y"}

        # Should handle unicode without issues
        result = config.write_config(unicode_config)
        assert result is True

        read_result = config.read_config()
        assert read_result == unicode_config

    def test_large_config_file(self, temp_kernel_dir):
        """Test handling of large configuration files."""
        config = KernelConfig(str(temp_kernel_dir), "6.16")

        # Create a large config dictionary
        large_config = {f"CONFIG_OPTION_{i}": "y" for i in range(1000)}

        result = config.write_config(large_config)
        assert result is True

        read_result = config.read_config()
        assert len(read_result) == 1000
        assert read_result == large_config
