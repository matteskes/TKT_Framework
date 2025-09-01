from unittest.mock import Mock

from TKT.cli import TKTSystemManager


class TestTKTSystemManager:
    def test_init_supported_distro(self, mocker):
        """Test initialization with supported distribution."""
        mock_distro_config = Mock()
        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        mocker.patch("TKT.cli.get_distro_configs", return_value=mock_distro_config)

        manager = TKTSystemManager()

        assert manager.distro == "debian"
        assert manager.distro_config is mock_distro_config
        assert manager.distro_supported is True

    def test_init_unsupported_distro_value_error(self, mocker):
        """Test initialization with unsupported distribution (ValueError)."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="gentoo")
        mocker.patch(
            "TKT.cli.get_distro_configs", side_effect=ValueError("Unsupported")
        )

        manager = TKTSystemManager()

        # When ValueError is caught in _initialize_distro, all attributes are reset
        # This matches the actual code behavior in the except block
        assert manager.distro is None
        assert manager.distro_config is None
        assert manager.distro_supported is False

    def test_init_runtime_error(self, mocker):
        """Test initialization with RuntimeError from get_distribution_name."""
        mocker.patch(
            "TKT.cli.get_distribution_name", side_effect=RuntimeError("No Linux")
        )

        manager = TKTSystemManager()

        assert manager.distro is None
        assert manager.distro_config is None
        assert manager.distro_supported is False

    def test_install_dependencies_success(self, mocker):
        """Test successful dependency installation."""
        mock_distro_config = Mock()
        mock_distro_config.update_and_install.return_value = None

        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs", return_value=mock_distro_config)

        manager = TKTSystemManager()
        success, message = manager.install_dependencies()

        assert success is True
        assert message == "Dependencies installed successfully"
        mock_distro_config.update_and_install.assert_called_once()

    def test_install_dependencies_unsupported_distro(self, mocker):
        """Test dependency installation with unsupported distribution."""
        mocker.patch(
            "TKT.cli.get_distribution_name", side_effect=ValueError("Unsupported")
        )

        manager = TKTSystemManager()
        success, message = manager.install_dependencies()

        assert success is False
        assert "Distribution not supported" in message

    def test_install_dependencies_no_distro_config(self, mocker):
        """Test dependency installation when distro_config is None."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs", side_effect=RuntimeError("Failed"))

        manager = TKTSystemManager()
        success, message = manager.install_dependencies()

        assert success is False
        assert "Distribution not supported" in message

    def test_install_dependencies_exception_during_install(self, mocker):
        """Test dependency installation when update_and_install raises exception."""
        mock_distro_config = Mock()
        mock_distro_config.update_and_install.side_effect = Exception(
            "Installation failed"
        )

        mocker.patch("TKT.cli.get_distribution_name", return_value="ubuntu")
        mocker.patch("TKT.cli.get_distro_configs", return_value=mock_distro_config)

        manager = TKTSystemManager()
        success, message = manager.install_dependencies()

        assert success is False
        assert "Failed to install dependencies: Installation failed" in message

    def test_prepare_kernel_source(self, mocker):
        """Test prepare_kernel_source placeholder method."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        mocker.patch("TKT.cli.get_distro_configs")

        manager = TKTSystemManager()
        success, message = manager.prepare_kernel_source("6.16")

        assert success is True
        assert "Kernel source preparation for 6.16 would go here" in message

    def test_configure_kernel_default(self, mocker):
        """Test configure_kernel with default config type."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        mocker.patch("TKT.cli.get_distro_configs")

        manager = TKTSystemManager()
        success, message = manager.configure_kernel("6.16")

        assert success is True
        assert "Kernel configuration for 6.16 (default) would go here" in message

    def test_configure_kernel_custom(self, mocker):
        """Test configure_kernel with custom config type."""
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")

        manager = TKTSystemManager()
        success, message = manager.configure_kernel("6.16", "custom")

        assert success is True
        assert "Kernel configuration for 6.16 (custom) would go here" in message
