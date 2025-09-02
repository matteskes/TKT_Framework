import pytest

from TKT.distro_configs import (
    DistroConfigs,
)


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
