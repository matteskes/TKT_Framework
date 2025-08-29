import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import tomlkit

from TKT.cli import KernelToolkitApp


class TestKernelToolkitApp:
    def test_init_with_existing_config(self, mocker):
        """Test app initialization with existing config file."""
        config_content = {
            "kernels": {"available": ["6.16", "6.15"]},
            "settings": {"backend": "kernel_lib_arch"},
        }

        # Mock file operations
        mock_file_content = b""  # tomllib.load will be mocked separately
        mocker.patch("builtins.open", mock_open(read_data=mock_file_content))
        mocker.patch("tomllib.load", return_value=config_content)
        mocker.patch("TKT.cli.choose_backend", return_value=("kernel_lib_arch", True))
        mocker.patch("TKT.cli.load_library", return_value=Mock())
        mocker.patch("TKT.cli.TKTSystemManager")

        app = KernelToolkitApp()

        assert app.config == config_content
        assert app.backend == "kernel_lib_arch"
        assert app.backend_distro_supported is True
        assert app.lib_module is not None

    def test_init_config_file_not_found(self, mocker):
        """Test app initialization when config file doesn't exist."""
        # Mock FileNotFoundError and file creation
        mocker.patch(
            "builtins.open", side_effect=[FileNotFoundError(), mock_open().return_value]
        )
        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        mocker.patch("tomlkit.dump")
        mocker.patch("TKT.cli.choose_backend", return_value=("kernel_lib_debian", True))
        mocker.patch("TKT.cli.load_library", return_value=None)
        mocker.patch("TKT.cli.TKTSystemManager")

        app = KernelToolkitApp()

        # Should create default config
        expected_config = {
            "kernels": {"available": []},
            "settings": {"backend": "kernel_lib_debian"},
        }
        assert app.config == expected_config
        assert app.lib_module is None

    def test_init_config_file_exception(self, mocker):
        """Test app initialization when config file has other exceptions."""
        # Mock exception during config loading
        mocker.patch("builtins.open", side_effect=PermissionError("Access denied"))
        mocker.patch(
            "TKT.cli.choose_backend", return_value=("kernel_lib_ubuntu", False)
        )
        mocker.patch("TKT.cli.load_library", return_value=Mock())
        mocker.patch("TKT.cli.TKTSystemManager")

        app = KernelToolkitApp()

        # Should fallback to empty config
        expected_config = {"kernels": {"available": []}, "settings": {}}
        assert app.config == expected_config
        assert app.backend_distro_supported is False

    def test_update_status_with_mounted_label(self, mocker):
        """Test update_status when status label is mounted."""
        mock_label = Mock()
        mock_app = Mock()
        mock_app.query_one.return_value = mock_label

        app = KernelToolkitApp.__new__(
            KernelToolkitApp
        )  # Create without calling __init__
        app.status_message = ""
        app.query_one = mock_app.query_one

        app.update_status("Test message")

        assert app.status_message == "Test message"
        mock_app.query_one.assert_called_once_with(
            "#status_label", pytest.importorskip("textual.widgets").Label
        )
        mock_label.update.assert_called_once_with("Test message")

    def test_update_status_with_unmounted_label(self, mocker):
        """Test update_status when status label is not mounted."""
        mock_app = Mock()
        mock_app.query_one.side_effect = LookupError("Not found")

        app = KernelToolkitApp.__new__(
            KernelToolkitApp
        )  # Create without calling __init__
        app.status_message = ""
        app.query_one = mock_app.query_one

        # Should not raise exception
        app.update_status("Test message")

        assert app.status_message == "Test message"

    def test_action_install_deps(self, mocker):
        """Test action_install_deps method."""
        mock_system_manager = Mock()
        mock_system_manager.install_dependencies.return_value = (True, "Success")

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.system_manager = mock_system_manager
        app.status_message = ""
        app.update_status = Mock()
        app.refresh = Mock()

        app.action_install_deps()

        # Should call update_status twice and refresh once
        assert app.update_status.call_count == 2
        app.update_status.assert_any_call("Installing dependencies...")
        app.update_status.assert_any_call("✓ Success")
        app.refresh.assert_called_once()

    def test_handle_command_deps(self, mocker):
        """Test handle_command with 'deps' command."""
        mock_system_manager = Mock()
        mock_system_manager.install_dependencies.return_value = (False, "Failed")

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.system_manager = mock_system_manager
        app.update_status = Mock()
        app.refresh = Mock()

        result = app.handle_command("deps")

        assert result is True
        app.update_status.assert_any_call("Installing dependencies...")
        app.update_status.assert_any_call("✗ Failed")

    def test_handle_command_install_deps(self, mocker):
        """Test handle_command with 'install-deps' command."""
        mock_system_manager = Mock()
        mock_system_manager.install_dependencies.return_value = (True, "Installed")

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.system_manager = mock_system_manager
        app.update_status = Mock()
        app.refresh = Mock()

        result = app.handle_command("INSTALL-DEPS")  # Test case insensitive

        assert result is True
        app.update_status.assert_any_call("✓ Installed")

    def test_handle_command_config(self, mocker):
        """Test handle_command with 'config:' command."""
        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.update_status = Mock()

        result = app.handle_command("config:custom")

        assert result is True
        app.update_status.assert_called_once_with(
            "Kernel configuration (custom) would be implemented here"
        )

    def test_handle_command_prepare(self, mocker):
        """Test handle_command with 'prepare:' command."""
        mock_system_manager = Mock()
        mock_system_manager.prepare_kernel_source.return_value = (True, "Prepared 6.16")

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.system_manager = mock_system_manager
        app.update_status = Mock()

        result = app.handle_command("prepare:6.16")

        assert result is True
        mock_system_manager.prepare_kernel_source.assert_called_once_with("6.16")
        app.update_status.assert_called_once_with("✓ Prepared 6.16")

    def test_handle_command_unknown(self, mocker):
        """Test handle_command with unknown command."""
        app = KernelToolkitApp.__new__(KernelToolkitApp)

        result = app.handle_command("unknown_command")

        assert result is False

    def test_on_input_submitted_empty_input(self, mocker):
        """Test on_input_submitted with empty input."""
        mock_event = Mock()
        mock_event.input.value = "   "  # whitespace only

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.query_one = Mock(return_value=mock_input_widget)

        app.on_input_submitted(mock_event)

        assert (
            mock_input_widget.placeholder
            == "Please enter a valid kernel version or command."
        )

    def test_on_input_submitted_command(self, mocker):
        """Test on_input_submitted with a command."""
        mock_event = Mock()
        mock_event.input.value = "deps"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=True)

        app.on_input_submitted(mock_event)

        app.handle_command.assert_called_once_with("deps")
        assert mock_input_widget.value == ""  # Should clear input

    def test_on_input_submitted_kernel_version_valid(self, mocker):
        """Test on_input_submitted with valid kernel version."""
        mock_event = Mock()
        mock_event.input.value = "6.16"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.config = {"kernels": {"available": ["6.16", "6.15"]}}
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=False)
        app.update_status = Mock()

        app.on_input_submitted(mock_event)

        app.update_status.assert_called_once_with(" Kernel version 6.16 selected")
        assert mock_input_widget.value == ""

    def test_on_input_submitted_kernel_version_invalid(self, mocker):
        """Test on_input_submitted with invalid kernel version."""
        mock_event = Mock()
        mock_event.input.value = "6.20"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.config = {"kernels": {"available": ["6.16", "6.15"]}}
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=False)
        app.update_status = Mock()

        app.on_input_submitted(mock_event)

        app.update_status.assert_called_once_with(
            " Kernel version 6.20 not in available list"
        )
        assert mock_input_widget.value == ""

    def test_on_input_submitted_kernel_version_no_list(self, mocker):
        """Test on_input_submitted with kernel version when no available list."""
        mock_event = Mock()
        mock_event.input.value = "6.16"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.config = {"kernels": {"available": []}}
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=False)
        app.update_status = Mock()

        app.on_input_submitted(mock_event)

        app.update_status.assert_called_once_with(" Kernel version 6.16 selected")
        assert mock_input_widget.value == ""

    def test_on_input_submitted_legacy_kernel_format(self, mocker):
        """Test on_input_submitted with legacy string kernel format."""
        mock_event = Mock()
        mock_event.input.value = "6.16"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.config = {"kernels": {"available": "6.16, 6.15"}}  # String format
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=False)
        app.update_status = Mock()

        app.on_input_submitted(mock_event)

        app.update_status.assert_called_once_with(" Kernel version 6.16 selected")

    def test_on_input_submitted_config_exception(self, mocker):
        """Test on_input_submitted when config parsing raises exception."""
        mock_event = Mock()
        mock_event.input.value = "6.16"

        mock_input_widget = Mock()

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.config = {"kernels": None}  # Will cause exception
        app.query_one = Mock(return_value=mock_input_widget)
        app.handle_command = Mock(return_value=False)
        app.update_status = Mock()

        app.on_input_submitted(mock_event)

        # Should handle exception gracefully and treat as no kernels available
        app.update_status.assert_called_once_with(" Kernel version 6.16 selected")

    def test_on_mount(self, mocker):
        """Test on_mount method."""
        mock_input_widget = Mock()
        mock_input_widget.disabled = False

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.query_one = Mock(return_value=mock_input_widget)

        app.on_mount()

        mock_input_widget.focus.assert_called_once()

    def test_on_mount_disabled_input(self, mocker):
        """Test on_mount method with disabled input."""
        mock_input_widget = Mock()
        mock_input_widget.disabled = True

        app = KernelToolkitApp.__new__(KernelToolkitApp)
        app.query_one = Mock(return_value=mock_input_widget)

        app.on_mount()

        mock_input_widget.focus.assert_not_called()
