"""Tests for TKT.cli module — TKTSystemManager and choose_backend edge cases."""

from unittest.mock import MagicMock

import pytest

from TKT.cli import TKTSystemManager, choose_backend


# =============================================================================
# choose_backend exception paths (lines 107, 118)
# =============================================================================


class TestChooseBackendExceptions:
    """Test exception paths in choose_backend not covered by existing tests."""

    def test_choose_backend_oserror_on_write(self, mocker):
        """Test OSError when writing config back to settings.toml fails."""
        config = {"settings": {}}
        config_path = "/fake/path/settings.toml"

        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        mocker.patch("TKT.cli.get_distro_configs")
        mocker.patch("TKT.cli.sys.platform", "linux")
        # Patch open to raise OSError
        mocker.patch("builtins.open", side_effect=OSError("permission denied"))
        mocker.patch("tomlkit.dump")

        backend, distro_supported = choose_backend(config, config_path)

        # OSError causes backend to be reset to empty string
        assert backend == ""
        assert distro_supported is True

    def test_choose_backend_runtime_error_on_get_supported_distro(self, mocker):
        """Test RuntimeError from get_distro_configs in choose_backend."""
        config = {"settings": {"backend": "kernel_lib_fedora"}}
        config_path = "/fake/path/settings.toml"

        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_fedora"
        assert distro_supported is False


class TestTKTSystemManagerInit:
    """Tests for TKTSystemManager.__init__."""

    def test_init_success(self, mocker):
        """Test successful initialization."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        mocker.patch("TKT.cli.get_distro_configs")

        manager = TKTSystemManager()

        assert manager.distro == "debian"
        assert manager.distro_supported is True

    def test_init_unsupported_distro(self, mocker):
        """Test ValueError when distro is not supported."""
        mocker.patch(
            "TKT.cli.get_distribution_name",
            side_effect=ValueError("not supported"),
        )

        manager = TKTSystemManager()
        assert manager.distro is None
        assert manager.distro_supported is False

    def test_init_not_linux(self, mocker):
        """Test RuntimeError when not running on Linux."""
        mocker.patch(
            "TKT.cli.get_distribution_name",
            side_effect=RuntimeError("not Linux"),
        )

        manager = TKTSystemManager()
        assert manager.distro is None
        assert manager.distro_supported is False


# =============================================================================
# TKTSystemManager — prepare_kernel_source
# =============================================================================


class TestTKTSystemManagerPrepare:
    """Tests for TKTSystemManager.prepare_kernel_source."""

    def test_prepare_kernel_source_full_workflow(self, mocker, tmp_path):
        """Test successful full workflow: config generation, save, path."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        # Mock KernelConfig with the actual methods called:
        # apply_config_changes, save_config_to_file, get_saved_config_path
        mock_kc = MagicMock()
        mock_kc.apply_config_changes.return_value = (True, "ok")
        mock_kc.save_config_to_file.return_value = (True, "saved")
        mock_kc.get_saved_config_path.return_value = "/path/to/config"
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is True
        assert "prepared" in message.lower() or "config" in message.lower()

    def test_prepare_kernel_source_apply_config_failure(self, mocker):
        """Test prepare_kernel_source when apply_config_changes fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_kc = MagicMock()
        mock_kc.apply_config_changes.return_value = (False, "error")
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is False
        assert "failed" in message.lower()

    def test_prepare_kernel_source_save_config_failure(self, mocker):
        """Test prepare_kernel_source when save_config_to_file fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_kc = MagicMock()
        mock_kc.apply_config_changes.return_value = (True, "ok")
        mock_kc.save_config_to_file.return_value = (False, "save error")
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is False
        assert "failed" in message.lower()


# =============================================================================
# TKTSystemManager — configure_kernel (placeholder)
# =============================================================================


class TestTKTSystemManagerConfigure:
    """Tests for TKTSystemManager.configure_kernel."""

    def test_configure_kernel_default(self, mocker):
        """Test configure_kernel with default config type (placeholder)."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        success, message = manager.configure_kernel("6.16")

        assert success is True
        assert "6.16" in message
        assert "default" in message

    def test_configure_kernel_custom(self, mocker):
        """Test configure_kernel with custom config type (placeholder)."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        success, message = manager.configure_kernel("6.16", config_type="custom")

        assert success is True
        assert "6.16" in message
        assert "custom" in message