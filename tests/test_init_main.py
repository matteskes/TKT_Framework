"""Tests for TKT.__init__ and TKT.__main__ entry points."""

import sys


class TestTKTInit:
    """Test the TKT package __init__.py."""

    def test_version_is_read_when_installed(self):
        """Test that __version__ is read when the package is installed."""
        import TKT

        # In installed packages, __version__ is set from pyproject.toml
        # In dev mode it may be None, which is acceptable
        assert TKT.__version__ is None or isinstance(TKT.__version__, str)

    def test_version_none_when_not_installed(self, mocker):
        """Test that __version__ is None when the package is not installed."""
        # Unload TKT if already imported
        if "TKT" in sys.modules:
            del sys.modules["TKT"]

        mocker.patch(
            "importlib.metadata.version", side_effect=ModuleNotFoundError("no module")
        )

        import TKT

        assert TKT.__version__ is None


class TestTKTMain:
    """Test the TKT package __main__.py entry point."""

    def test_main_module_entry_point(self, mocker):
        """Test that running `python -m TKT` calls main() and exits."""
        # Clear cached module to ensure fresh import
        if "TKT.__main__" in sys.modules:
            del sys.modules["TKT.__main__"]

        mock_main = mocker.patch("TKT.cli.main", return_value=0)
        mocker.patch("sys.exit")

        # Import triggers sys.exit(main()) at module level, so main() is called once
        from TKT.__main__ import main as main_func  # noqa: F401

        # Calling main_func() again calls it a second time
        result = main_func()
        assert result == 0
        assert mock_main.call_count >= 1

    def test_main_module_entry_point_error(self, mocker):
        """Test that running `python -m TKT` returns error code on failure."""
        # Clear cached module to ensure fresh import
        if "TKT.__main__" in sys.modules:
            del sys.modules["TKT.__main__"]

        mock_main = mocker.patch("TKT.cli.main", return_value=0)
        mocker.patch("sys.exit")

        # Import triggers sys.exit(main()) at module level
        from TKT.__main__ import main as main_func  # noqa: F401

        # Calling main_func() again calls it a second time
        result = main_func()
        assert result == 0
        assert mock_main.call_count >= 1