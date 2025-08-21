import json
import platform
import sys
from pathlib import Path

import pytest

from TKT.cli import (
    SUPPORTED_DISTROS,
    get_distribution_name,
    get_supported_distribution_name,
)

with Path("tests/distros.json").open() as file:
    distro_list = json.load(file)


def find(func, iterable):
    return next(filter(func, iterable), None)


def find_distro(name):
    return find(lambda distro: distro["ID"] == name, distro_list)


class TestGetDistributionName:
    """Test get_distribution_name function"""

    def test_non_linux_platform(self, mocker):
        mocker.patch.object(sys, "platform", "darwin")
        with pytest.raises(RuntimeError, match="not Linux"):
            get_distribution_name()

    def test_linux_with_valid_distribution(self, mocker):
        fake_release = find_distro("arch")
        mocker.patch.object(sys, "platform", "linux")
        mocker.patch.object(
            platform, "freedesktop_os_release", return_value=fake_release
        )
        assert get_distribution_name() == "arch"

    def test_linux_with_missing_id(self, mocker):
        fake_release = {}
        mocker.patch.object(sys, "platform", "linux")
        mocker.patch.object(
            platform, "freedesktop_os_release", return_value=fake_release
        )
        with pytest.raises(RuntimeError, match="Cannot get distribution name"):
            get_distribution_name()

    def test_linux_with_exception(self, mocker):
        mocker.patch.object(sys, "platform", "linux")
        mocker.patch.object(
            platform, "freedesktop_os_release", side_effect=OSError("boom")
        )
        with pytest.raises(RuntimeError, match="Cannot get distribution name"):
            get_distribution_name()


@pytest.mark.parametrize("distro", SUPPORTED_DISTROS)
class TestGetSupportedDistributionName:
    """Test get_supported_distribution_name function"""

    def test_supported_distro_id(self, distro, mocker):
        """Should return the distro name when ID is in SUPPORTED_DISTROS."""

        mocker.patch.object(
            platform, "freedesktop_os_release", return_value={"ID": distro}
        )
        assert get_supported_distribution_name() == distro

    def test_supported_distro_id_like(self, distro, mocker):
        """
        Should return the distro name when ID_LIKE is in
        SUPPORTED_DISTROS.
        """

        mocker.patch.object(
            platform,
            "freedesktop_os_release",
            return_value={"ID": "nonsense", "ID_LIKE": distro},
        )
        assert get_supported_distribution_name() == distro

    def test_unsupported_distro_keyerror(self, distro, mocker):
        """Should raise RuntimeError when distro ID is not supported."""

        mocker.patch.object(
            platform, "freedesktop_os_release", return_value={"ID": "nonsense"}
        )
        with pytest.raises(RuntimeError, match="not supported"):
            get_supported_distribution_name()

    def test_missing_fields_raises_runtimeerror(self, distro, mocker):
        """Should raise RuntimeError when required keys are missing."""

        mocker.patch.object(platform, "freedesktop_os_release", return_value={})
        with pytest.raises(
            RuntimeError, match="not supported|Cannot get distribution name"
        ):
            get_supported_distribution_name()

    def test_attribute_error_in_os_release(self, distro, mocker):
        """
        Should raise RuntimeError when freedesktop_os_release is
        missing attributes.
        """

        mocker.patch.object(
            platform, "freedesktop_os_release", side_effect=AttributeError
        )
        with pytest.raises(RuntimeError, match="Cannot get distribution name"):
            get_supported_distribution_name()

    def test_non_linux_platform(self, distro, mocker):
        """Should raise RuntimeError when not running on Linux."""

        mocker.patch.object(sys, "platform", "win32")
        with pytest.raises(RuntimeError, match="not Linux"):
            get_supported_distribution_name()
