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


class TestDistroConfigsBase:
    """Test additional DistroConfigs base class behavior."""

    def test_run_command_check_true_failure(self, mocker):
        """Test _run_command raises RuntimeError when check=True and command fails."""
        from TKT.distro_configs import DistroConfigs

        class TestConfig(DistroConfigs):
            def update_repos(self):
                pass

            def install_packages(self):
                pass

        config = TestConfig()
        mock_run = mocker.patch(
            "subprocess.run",
            return_value=mocker.MagicMock(returncode=1, stderr="command not found"),
        )

        with pytest.raises(RuntimeError, match="Command failed"):
            config._run_command(["fake", "command"], check=True)

    def test_install_packages_not_implemented(self):
        """Test that base install_packages raises NotImplementedError."""
        from TKT.distro_configs import DistroConfigs

        class IncompleteConfig(DistroConfigs):
            def update_repos(self):
                pass

        config = IncompleteConfig()

        with pytest.raises(NotImplementedError, match="must implement 'install_packages'"):
            config.install_packages()

    def test_update_and_install_default(self, mocker):
        """Test default update_and_install calls update_repos then install_packages."""
        from TKT.distro_configs import DistroConfigs

        class TestConfig(DistroConfigs):
            def update_repos(self):
                pass

            def install_packages(self):
                pass

        config = TestConfig()
        mock_update = mocker.patch.object(config, "update_repos")
        mock_install = mocker.patch.object(config, "install_packages")

        config.update_and_install()

        mock_update.assert_called_once()
        mock_install.assert_called_once()
        # Verify order: update_repos called before install_packages
        assert mock_update.call_args_list[0].before(mock_install.call_args_list[0])


class TestArchConfigs:
    """Test Arch Linux-specific package management configuration."""

    def test_arch_configs_init(self):
        """Test ArchConfigs initialization includes all dependencies."""
        from TKT.distro_configs import ArchConfigs, DistroConfigs

        config = ArchConfigs()

        assert config.packages == DistroConfigs.base_deps + ArchConfigs.arch_deps
        assert "base-devel" in config.packages
        assert "linux-headers" in config.packages

    def test_arch_configs_update_and_install(self, mocker):
        """Test ArchConfigs update_and_install calls pacman."""
        from TKT.distro_configs import ArchConfigs

        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0)
        )

        config = ArchConfigs()
        config.update_and_install()

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "pacman"
        assert call_args[1] == "-Sy"
        assert call_args[2] == "--needed"
        assert len(call_args) > 3  # packages listed


class TestDebianConfigs:
    """Test Debian-specific package management configuration."""

    def test_debian_configs_init(self):
        """Test DebianConfigs initialization includes all dependencies."""
        from TKT.distro_configs import DebianConfigs, DistroConfigs

        config = DebianConfigs()

        assert config.packages == DistroConfigs.base_deps + DebianConfigs.deb_deps
        assert "build-essential" in config.packages
        assert "dpkg-dev" in config.packages

    def test_debian_configs_update_repos(self, mocker):
        """Test DebianConfigs update_repos calls apt-get update."""
        from TKT.distro_configs import DebianConfigs

        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0)
        )

        config = DebianConfigs()
        config.update_repos()

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "apt-get"
        assert call_args[1] == "update"
        assert call_args[2] == "-y"

    def test_debian_configs_install_packages(self, mocker):
        """Test DebianConfigs install_packages uses apt-get."""
        from TKT.distro_configs import DebianConfigs

        mock_run = mocker.patch(
            "subprocess.run", return_value=mocker.MagicMock(returncode=0)
        )

        config = DebianConfigs()
        config.install_packages()

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "apt-get"
        assert call_args[1] == "install"
        assert call_args[2] == "-y"
        assert len(call_args) > 3  # packages listed


class TestUbuntuConfigs:
    """Test Ubuntu-specific package management configuration."""

    def test_ubuntu_configs_init(self):
        """Test UbuntuConfigs replaces Debian deps with Ubuntu-specific ones."""
        from TKT.distro_configs import DistroConfigs, UbuntuConfigs

        config = UbuntuConfigs()

        # Should include base_deps + ubuntu_deps (NOT deb_deps)
        assert config.packages == DistroConfigs.base_deps + UbuntuConfigs.ubuntu_deps
        assert "libpython3-dev" in config.packages
        assert "python3-venv" in config.packages
        assert "python3-dev" in config.packages
        # Ensure Debian-specific deps are NOT in Ubuntu packages
        from TKT.distro_configs import DebianConfigs
        for dep in DebianConfigs.deb_deps:
            assert dep not in config.packages, f"{dep} should not be in Ubuntu packages"


class TestGetDistroConfigs:
    """Test get_distro_configs function for all supported distros."""

    def test_get_distro_configs_arch(self):
        """Test get_distro_configs returns ArchConfigs for 'arch'."""
        from TKT.distro_configs import ArchConfigs, get_distro_configs

        config = get_distro_configs("arch")
        assert isinstance(config, ArchConfigs)

    def test_get_distro_configs_debian(self):
        """Test get_distro_configs returns DebianConfigs for 'debian'."""
        from TKT.distro_configs import DebianConfigs, get_distro_configs

        config = get_distro_configs("debian")
        assert isinstance(config, DebianConfigs)

    def test_get_distro_configs_ubuntu(self):
        """Test get_distro_configs returns UbuntuConfigs for 'ubuntu'."""
        from TKT.distro_configs import UbuntuConfigs, get_distro_configs

        config = get_distro_configs("ubuntu")
        assert isinstance(config, UbuntuConfigs)

    def test_get_distro_configs_unsupported(self):
        """Test get_distro_configs raises ValueError for unsupported distro."""
        from TKT.distro_configs import get_distro_configs

        with pytest.raises(ValueError, match="Unsupported distribution"):
            get_distro_configs("unknown_distro_xyz")

    def test_get_distro_configs_case_insensitive_debian(self):
        """Test get_distro_configs handles case-insensitive names."""
        from TKT.distro_configs import DebianConfigs, get_distro_configs

        config = get_distro_configs("DEBIAN")
        assert isinstance(config, DebianConfigs)

        config = get_distro_configs("Debian")
        assert isinstance(config, DebianConfigs)
