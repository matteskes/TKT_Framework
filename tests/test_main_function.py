import sys
from unittest.mock import Mock, patch

import pytest

from TKT.cli import main


class TestMainFunction:
    def test_main_not_tty_stdin(self, mocker):
        """Test main function when stdin is not a tty."""
        mocker.patch.object(sys.stdin, "isatty", return_value=False)
        mocker.patch.object(sys.stdout, "isatty", return_value=True)

        # Mock print to capture the error message since it goes to stderr via print()
        captured_output = []

        def mock_print(*args, **kwargs):
            if kwargs.get("file") == sys.stderr:
                captured_output.extend(args)

        mocker.patch("builtins.print", mock_print)

        result = main()

        assert result == 1
        # Check that error message was printed
        assert any(
            "stdin and stdout must be a tty" in str(arg) for arg in captured_output
        )

    def test_main_not_tty_stdout(self, mocker):
        """Test main function when stdout is not a tty."""
        mocker.patch.object(sys.stdin, "isatty", return_value=True)
        mocker.patch.object(sys.stdout, "isatty", return_value=False)

        # Mock print to capture the error message
        captured_output = []

        def mock_print(*args, **kwargs):
            if kwargs.get("file") == sys.stderr:
                captured_output.extend(args)

        mocker.patch("builtins.print", mock_print)

        result = main()

        assert result == 1
        # Check that error message was printed
        assert any(
            "stdin and stdout must be a tty" in str(arg) for arg in captured_output
        )

    def test_main_both_not_tty(self, mocker):
        """Test main function when both stdin and stdout are not tty."""
        mocker.patch.object(sys.stdin, "isatty", return_value=False)
        mocker.patch.object(sys.stdout, "isatty", return_value=False)

        # Mock print to capture the error message
        captured_output = []

        def mock_print(*args, **kwargs):
            if kwargs.get("file") == sys.stderr:
                captured_output.extend(args)

        mocker.patch("builtins.print", mock_print)

        result = main()

        assert result == 1

    def test_main_success(self, mocker):
        """Test main function with successful execution."""
        mocker.patch.object(sys.stdin, "isatty", return_value=True)
        mocker.patch.object(sys.stdout, "isatty", return_value=True)

        # Mock the KernelToolkitApp
        mock_app_instance = Mock()
        mock_app_class = Mock(return_value=mock_app_instance)
        mocker.patch("TKT.cli.KernelToolkitApp", mock_app_class)

        result = main()

        assert result == 0
        mock_app_class.assert_called_once()
        mock_app_instance.run.assert_called_once()

    def test_main_app_exception(self, mocker):
        """Test main function when app raises an exception."""
        mocker.patch.object(sys.stdin, "isatty", return_value=True)
        mocker.patch.object(sys.stdout, "isatty", return_value=True)

        # Mock the KernelToolkitApp to raise an exception
        mock_app_instance = Mock()
        mock_app_instance.run.side_effect = Exception("App crashed")
        mock_app_class = Mock(return_value=mock_app_instance)
        mocker.patch("TKT.cli.KernelToolkitApp", mock_app_class)

        # The exception should propagate (main doesn't handle it)
        with pytest.raises(Exception, match="App crashed"):
            main()

    def test_main_as_script(self, mocker):
        """Test the if __name__ == '__main__' block."""
        mocker.patch.object(sys.stdin, "isatty", return_value=True)
        mocker.patch.object(sys.stdout, "isatty", return_value=True)

        # Mock the KernelToolkitApp
        mock_app_instance = Mock()
        mock_app_class = Mock(return_value=mock_app_instance)
        mocker.patch("TKT.cli.KernelToolkitApp", mock_app_class)

        # Mock sys.exit to capture the exit code
        mock_exit = Mock()
        mocker.patch.object(sys, "exit", mock_exit)

        # This would normally be tested by running the script directly,
        # but we can test the logic by calling main() directly
        result = main()

        assert result == 0
