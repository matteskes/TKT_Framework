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
        mocker.patch("TKT.cli.get_supported_distribution_name", return_value="debian")
        mocker.patch("TKT.cli.sys.platform", "linux")
        mock_platform = mocker.patch("TKT.cli.platform")
        mock_platform.freedesktop_os_release.return_value = {"ID": "debian"}
        # Patch open to raise OSError
        mocker.patch("builtins.open", side_effect=OSError("permission denied"))
        mocker.patch("tomlkit.dump")

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_debian"
        assert distro_supported is True
        # settings should have been set before the write failed
        assert config["settings"]["backend"] == "kernel_lib_debian"

    def test_choose_backend_runtime_error_on_get_supported_distro(self, mocker):
        """Test RuntimeError from get_supported_distribution_name in choose_backend."""
        config = {"settings": {"backend": "kernel_lib_fedora"}}
        config_path = "/fake/path/settings.toml"

        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("unsupported"))
        mocker.patch("TKT.cli.sys.platform", "linux")

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_fedora"
        assert distro_supported is False


# =============================================================================
# TKTSystemManager — constructor
# =============================================================================


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
        """Test successful full workflow: download, validate, generate, save."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_subprocess = mocker.patch("TKT.kernel_config.subprocess.run")
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Mock KernelConfig methods
        mock_kc = MagicMock()
        mock_kc.validate_kernel_source.return_value = True
        mock_kc.ensure_config_exists.return_value = True
        mock_kc.run_olddefconfig.return_value = (True, "ok")
        mock_kc.save_config_to_file.return_value = (True, "saved")
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is True
        assert "successfully" in message.lower() or "success" in message.lower()
        # Verify subprocess was called for source download
        assert mock_subprocess.called

    def test_prepare_kernel_source_download_failure(self, mocker):
        """Test prepare_kernel_source when source download fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_subprocess = mocker.patch("TKT.kernel_config.subprocess.run")
        mock_subprocess.return_value = MagicMock(returncode=1)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is False
        assert "failed" in message.lower() or "error" in message.lower()

    def test_prepare_kernel_source_validate_failure(self, mocker, tmp_path):
        """Test prepare_kernel_source when kernel source validation fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_subprocess = mocker.patch("TKT.kernel_config.subprocess.run")
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Mock KernelConfig.validate_kernel_source to return False
        mock_kc = MagicMock()
        mock_kc.validate_kernel_source.return_value = False
        mock_kc.ensure_config_exists.return_value = True
        mock_kc.run_olddefconfig.return_value = (True, "ok")
        mock_kc.save_config_to_file.return_value = (True, "saved")
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is False
        assert "invalid" in message.lower() or "not found" in message.lower()

    def test_prepare_kernel_source_defconfig_failure(self, mocker):
        """Test prepare_kernel_source when olddefconfig fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_subprocess = mocker.patch("TKT.kernel_config.subprocess.run")
        mock_subprocess.return_value = MagicMock(returncode=0)

        mock_kc = MagicMock()
        mock_kc.validate_kernel_source.return_value = True
        mock_kc.ensure_config_exists.return_value = True
        mock_kc.run_olddefconfig.return_value = (False, "olddefconfig failed")
        mock_kc.save_config_to_file.return_value = (True, "saved")
        mocker.patch("TKT.cli.KernelConfig", return_value=mock_kc)

        success, message = manager.prepare_kernel_source("6.16")

        assert success is False
        assert "failed" in message.lower()


# =============================================================================
# TKTSystemManager — configure_kernel
# =============================================================================


class TestTKTSystemManagerConfigure:
    """Tests for TKTSystemManager.configure_kernel."""

    @pytest.fixture
    def manager(self, mocker):
        """Create a TKTSystemManager with mocked dependencies."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        return TKTSystemManager()

    def test_configure_kernel_default(self, mocker):
        """Test configure_kernel with default config type."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_prepare = mocker.patch.object(
            manager, "prepare_kernel_source", return_value=(True, "ok")
        )

        success, message = manager.configure_kernel("6.16")

        assert success is True
        mock_prepare.assert_called_once_with("6.16", config_type="default")

    def test_configure_kernel_custom(self, mocker):
        """Test configure_kernel with custom config type."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mock_prepare = mocker.patch.object(
            manager, "prepare_kernel_source", return_value=(True, "ok")
        )

        success, message = manager.configure_kernel("6.16", config_type="custom")

        assert success is True
        mock_prepare.assert_called_once_with("6.16", config_type="custom")

    def test_configure_kernel_prep_failure(self, mocker):
        """Test configure_kernel when prepare_kernel_source fails."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        manager = TKTSystemManager()

        mocker.patch.object(
            manager, "prepare_kernel_source", return_value=(False, "failed")
        )

        success, message = manager.configure_kernel("6.16")

        assert success is False
        assert "failed" in message.lower()

