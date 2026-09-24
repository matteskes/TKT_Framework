import pytest

from TKT.distro_configs import DistroConfigs


class TestDistroConfigs:
    """Test the abstract base class behavior."""

    def test_base_deps_defined(self):
        """Test that base dependencies are properly defined."""
        expected_deps = [
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
        assert DistroConfigs.base_deps == expected_deps

    def test_update_repos_not_implemented(self):
        """Test that abstract methods raise NotImplementedError."""

        class IncompleteConfig(DistroConfigs):
            pass

        config = IncompleteConfig()

        with pytest.raises(NotImplementedError, match="must implement 'update_repos'"):
            config.update_repos()


class TestFedoraConfigs:
    """Test Fedora-specific package management configuration."""

    def test_fedora_init(self):
        """Test FedoraConfigs initialization includes all dependencies."""
        from TKT.distro_configs import FedoraConfigs

        config = FedoraConfigs()

        # Should include base deps + fedora-specific deps
        assert len(config.packages) > len(DistroConfigs.base_deps)
        assert (
            config.packages[: len(DistroConfigs.base_deps)] == DistroConfigs.base_deps
        )

    def test_fedora_deps_defined(self):
        """Test that Fedora-specific dependencies are properly defined."""
        from TKT.distro_configs import FedoraConfigs

        expected_fedora_deps = [
            "binutils",
            "bison",
            "bc",
            "cscope",
            "ctags",
            "device-tree-compiler",
            "elfutils-libelf-devel",
            "flex",
            "gcc",
            "gcc-c++",
            "make",
            "ncurses-devel",
            "numactl-devel",
            "openssl-devel",
            "perl-Data-Dumper",
            "patchutils",
            "python3-setuptools",
            "rpm-build",
            "zstd-devel",
            "qt5-qtbase-devel",
            "kernel-devel",
        ]
        assert FedoraConfigs.fedora_deps == expected_fedora_deps

    def test_fedora_update_repos(self, mocker):
        """Test that Fedora update_repos calls dnf makecache."""
        from TKT.distro_configs import FedoraConfigs

        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0)
        )

        config = FedoraConfigs()
        config.update_repos()

        mock_run.assert_called_once_with(
            ["dnf", "makecache"], capture_output=True, text=True, check=False
        )

    def test_fedora_install_packages(self, mocker):
        """Test that Fedora install_packages uses dnf."""
        from TKT.distro_configs import FedoraConfigs

        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0)
        )

        config = FedoraConfigs()
        config.install_packages()

        # Verify dnf install is called with all packages
        call_args = mock_run.call_args[0]
        command = call_args[0]
        assert command[0] == "dnf"
        assert command[1] == "install"
        assert command[2] == "-y"
        # Remaining args are the packages
        assert len(command) > 3

    def test_fedora_get_distro_configs(self):
        """Test that get_distro_configs returns FedoraConfigs for 'fedora'."""
        from TKT.distro_configs import FedoraConfigs, get_distro_configs

        config = get_distro_configs("fedora")
        assert isinstance(config, FedoraConfigs)

    def test_fedora_get_distro_configs_case_insensitive(self):
        """Test that get_distro_configs handles case-insensitive names."""
        from TKT.distro_configs import FedoraConfigs, get_distro_configs

        config = get_distro_configs("FEDORA")
        assert isinstance(config, FedoraConfigs)

        config = get_distro_configs("Fedora")
        assert isinstance(config, FedoraConfigs)
