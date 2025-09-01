import tempfile
from pathlib import Path
from unittest.mock import mock_open

import pytest
import tomlkit

from TKT.cli import choose_backend


class TestChooseBackend:
    def test_config_with_existing_backend_supported_distro(self, mocker):
        """Test when config has backend and distro is supported."""
        config = {"settings": {"backend": "kernel_lib_debian"}}
        config_path = "/fake/path/settings.toml"

        # Mock get_distribution_name to return supported distro
        mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
        # Mock get_distro_configs to not raise exception (supported)
        mocker.patch("TKT.cli.get_distro_configs")

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_debian"
        assert distro_supported is True

    def test_config_with_existing_backend_unsupported_distro(self, mocker):
        """Test when config has backend but distro is unsupported."""
        config = {"settings": {"backend": "kernel_lib_gentoo"}}
        config_path = "/fake/path/settings.toml"

        # Mock get_distribution_name to return distro name
        mocker.patch("TKT.cli.get_distribution_name", return_value="gentoo")
        # Mock get_distro_configs to raise ValueError (unsupported)
        mocker.patch(
            "TKT.cli.get_distro_configs", side_effect=ValueError("Unsupported")
        )

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_gentoo"
        assert distro_supported is False

    def test_config_missing_settings_section(self, mocker):
        """Test when config is missing settings section."""
        config = {}
        config_path = "/fake/path/settings.toml"

        # Mock file operations
        mock_file = mock_open()
        mocker.patch("builtins.open", mock_file)
        mocker.patch("TKT.cli.get_distribution_name", return_value="arch")
        mocker.patch("TKT.cli.get_distro_configs")
        mocker.patch("tomlkit.dump")

        backend, distro_supported = choose_backend(config, config_path)

        # Should add settings section
        assert "settings" in config
        assert backend == "kernel_lib_arch"
        assert distro_supported is True

        # Should have written to file
        mock_file.assert_called_once_with(config_path, "w")

    def test_config_missing_backend_key(self, mocker):
        """Test when config has settings but missing backend key."""
        config = {"settings": {"other_setting": "value"}}
        config_path = "/fake/path/settings.toml"

        # Mock file operations
        mock_file = mock_open()
        mocker.patch("builtins.open", mock_file)
        mocker.patch("TKT.cli.get_distribution_name", return_value="ubuntu")
        mocker.patch("TKT.cli.get_distro_configs")
        mocker.patch("tomlkit.dump")

        backend, distro_supported = choose_backend(config, config_path)

        # Should add backend key
        assert config["settings"]["backend"] == "kernel_lib_ubuntu"
        assert backend == "kernel_lib_ubuntu"
        assert distro_supported is True

        # Should have written to file
        mock_file.assert_called_once_with(config_path, "w")

    def test_config_get_distro_configs_failure(self, mocker):
        """Test when get_distro_configs raises ValueError during distro check."""
        config = {"settings": {"backend": "kernel_lib_fedora"}}
        config_path = "/fake/path/settings.toml"

        # Mock get_distribution_name to succeed
        mocker.patch("TKT.cli.get_distribution_name", return_value="fedora")
        # Mock get_distro_configs to raise ValueError (unsupported distro)
        mocker.patch(
            "TKT.cli.get_distro_configs", side_effect=ValueError("Unsupported distro")
        )

        backend, distro_supported = choose_backend(config, config_path)

        assert backend == "kernel_lib_fedora"
        assert distro_supported is False

    def test_config_get_distribution_name_runtime_error(self, mocker):
        """Test when get_distribution_name raises RuntimeError during distro check."""
        config = {"settings": {"backend": "kernel_lib_fedora"}}
        config_path = "/fake/path/settings.toml"

        # Mock get_distribution_name to raise RuntimeError
        mocker.patch(
            "TKT.cli.get_distribution_name", side_effect=RuntimeError("No distro")
        )

        # The RuntimeError should propagate and not be caught by choose_backend
        with pytest.raises(RuntimeError, match="No distro"):
            choose_backend(config, config_path)

    def test_config_missing_backend_key_with_distro_failure(self, mocker):
        """Test when config has settings but missing backend key and distro detection fails."""
        config = {"settings": {"other_setting": "value"}}
        config_path = "/fake/path/settings.toml"

        # Mock get_distribution_name to fail when trying to add default backend
        mocker.patch(
            "TKT.cli.get_distribution_name", side_effect=RuntimeError("No distro")
        )

        # The RuntimeError should propagate when trying to get default backend
        with pytest.raises(RuntimeError, match="No distro"):
            choose_backend(config, config_path)
        """Test actual file writing when backend is added."""
        config = {}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            config_path = f.name

        try:
            mocker.patch("TKT.cli.get_distribution_name", return_value="debian")
            mocker.patch("TKT.cli.get_distro_configs")

            backend, distro_supported = choose_backend(config, config_path)

            assert backend == "kernel_lib_debian"
            assert distro_supported is True
            assert "settings" in config
            assert config["settings"]["backend"] == "kernel_lib_debian"

            # Verify file was written
            assert Path(config_path).exists()
            with open(config_path, "rb") as f:
                written_config = tomlkit.load(f)
                assert written_config["settings"]["backend"] == "kernel_lib_debian"

        finally:
            if Path(config_path).exists():
                Path(config_path).unlink()
