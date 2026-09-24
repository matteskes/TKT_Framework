"""Extended tests for TKT.fetch — download_file, get_files_from_releases, FileData fallbacks."""

import datetime
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import requests

import TKT
from TKT.fetch import FileData, FileSize, filename_from_url, get_files_from_releases
from TKT.safe import Err, Ok

# =============================================================================
# FileData.__post_init__ fallback paths (lines 103-112)
# =============================================================================


class TestFileDataFallbacks:
    """Test FileData.__post_init__ fallback paths not covered by existing tests."""

    def test_filedata_3part_format(self):
        """Test 3-part name format: {distro}-{version}-{scheduler}."""
        file_data = FileData(
            name="Arch-6.16-bore",
            size=FileSize(1024),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            digest="sha256:abc123",
            url="https://example.com/file",
            version="TKT v6.16-tkt",
            tag="v6.16-tkt",
        )

        assert file_data.distro == "Arch"
        assert file_data.scheduler == "bore"
        assert file_data.compiler == "unknown"

    def test_filedata_empty_name(self):
        """Test empty name produces empty fallback fields."""
        file_data = FileData(
            name="",
            size=FileSize(0),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            digest="sha256:000",
            url="https://example.com/file",
            version="TKT",
            tag="v1",
        )

        assert file_data.distro == ""
        assert file_data.scheduler == ""
        assert file_data.compiler == ""

    def test_filedata_2part_name(self):
        """Test 2-part name format: {distro}-{version} (no scheduler)."""
        file_data = FileData(
            name="Arch-6.16",
            size=FileSize(1024),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            digest="sha256:abc123",
            url="https://example.com/file",
            version="TKT",
            tag="v1",
        )

        # 2 parts: ["Arch", "6.16"] falls into else branch (parts < 3)
        assert file_data.distro == ""
        assert file_data.scheduler == ""
        assert file_data.compiler == ""


# =============================================================================
# download_file (lines 150-184)
# =============================================================================


class TestDownloadFile:
    """Tests for download_file function."""

    def _make_mock_response(self, content=b"test content", content_length=None, status_code=200):
        """Create a mock requests.Response for download_file."""
        response = MagicMock(spec=requests.Response)
        response.status_code = status_code
        response.headers = {}
        if content_length is not None:
            response.headers["Content-Length"] = str(content_length)

        mock_iter = iter([content])
        response.iter_content = MagicMock(return_value=mock_iter)
        response.__enter__ = MagicMock(return_value=response)
        response.__exit__ = MagicMock(return_value=False)
        return response

    def test_download_file_success(self, mocker):
        """Test successful file download."""
        content = b"hello world"
        mock_response = self._make_mock_response(content, content_length=len(content))
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_file"
            result_path = TKT.fetch.download_file(
                "https://example.com/test_file",
                output=str(output_path),
                quiet=True,
            )

            assert isinstance(result_path, Ok)
            assert Path(result_path.ok) == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == content

    def test_download_file_quiet_mode(self, mocker):
        """Test download_file with quiet=True (no progress output)."""
        content = b"quiet content"
        mock_response = self._make_mock_response(content, content_length=len(content))
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "quiet_file"

            # Capture stdout to verify no progress output
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                TKT.fetch.download_file(
                    "https://example.com/quiet_file",
                    output=str(output_path),
                    quiet=True,
                )

            stdout = f.getvalue()
            assert stdout == ""  # No progress output in quiet mode

    def test_download_file_no_content_length(self, mocker):
        """Test download_file when Content-Length header is missing."""
        content = b"no length header"
        mock_response = self._make_mock_response(content, content_length=None)
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "no_length"

            result = TKT.fetch.download_file(
                "https://example.com/no_length",
                output=str(output_path),
                quiet=True,
            )

            assert isinstance(result, Ok)
            assert Path(result.ok) == output_path
            assert output_path.exists()
            assert output_path.read_bytes() == content

    def test_download_file_http_error(self, mocker):
        """Test download_file when server returns HTTP error (404)."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(side_effect=requests.HTTPError("404"))
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        result = TKT.fetch.download_file("https://example.com/notfound")

        assert isinstance(result, Err)
        assert result.err is not None

    def test_download_file_file_exists(self, mocker):
        """Test download_file when output file already exists (FileExistsError)."""
        content = b"new content"
        mock_response = self._make_mock_response(content, content_length=len(content))
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "existing"
            # Pre-create the file
            output_path.write_bytes(b"existing")

            result = TKT.fetch.download_file(
                "https://example.com/existing",
                output=str(output_path),
                quiet=True,
            )

            assert isinstance(result, Err)
            assert result.err is not None
            # Original file should be unchanged
            assert output_path.read_bytes() == b"existing"

    def test_download_file_default_output_name(self, mocker):
        """Test download_file derives output filename from URL when not specified."""
        content = b"url derived"
        mock_response = self._make_mock_response(content, content_length=len(content))
        mocker.patch("TKT.fetch.requests.get", return_value=mock_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            import os as os_mod
            original_cwd = os_mod.getcwd()
            try:
                os_mod.chdir(tmpdir)
                result_path = TKT.fetch.download_file(
                    "https://example.com/myfile.tar.gz",
                    quiet=True,
                )

                assert isinstance(result_path, Ok)
                assert Path(result_path.ok).name == "myfile.tar.gz"
                assert Path(result_path.ok).exists()
                assert Path(result_path.ok).read_bytes() == content
            finally:
                os_mod.chdir(original_cwd)


# =============================================================================
# get_files_from_releases (lines 187-205)
# =============================================================================


class TestGetFilesFromReleases:
    """Tests for get_files_from_releases function."""

    def test_get_files_from_releases_empty(self):
        """Test get_files_from_releases with empty releases list."""
        files = get_files_from_releases([])
        assert files == []

    def test_get_files_from_releases_single_release_single_asset(self):
        """Test get_files_from_releases with single release and asset."""
        releases = [
            {
                "tag_name": "v1.0",
                "name": "Release 1.0",
                "assets": [
                    {
                        "name": "Arch-6.16-bore-gcc.tar.gz",
                        "size": 1024,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:abc123",
                        "browser_download_url": "https://example.com/file",
                    },
                ],
            },
        ]

        files = get_files_from_releases(releases)

        assert len(files) == 1
        assert files[0].name == "Arch-6.16-bore-gcc.tar.gz"
        assert files[0].distro == "Arch"
        assert files[0].scheduler == "bore"
        assert files[0].compiler == "gcc"
        assert files[0].tag == "v1.0"

    def test_get_files_from_releases_multiple(self):
        """Test get_files_from_releases with multiple releases and assets."""
        releases = [
            {
                "tag_name": "v1.0",
                "name": "Release 1.0",
                "assets": [
                    {
                        "name": "Arch-6.16-bore-gcc.tar.gz",
                        "size": 1024,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:abc",
                        "browser_download_url": "https://example.com/arch",
                    },
                    {
                        "name": "Debian-6.16-bore-gcc.tar.gz",
                        "size": 2048,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:def",
                        "browser_download_url": "https://example.com/debian",
                    },
                ],
            },
            {
                "tag_name": "v2.0",
                "name": "Release 2.0",
                "assets": [
                    {
                        "name": "Fedora-6.16-bore-gcc.tar.gz",
                        "size": 3072,
                        "updated_at": "2025-02-01T00:00:00+00:00",
                        "digest": "sha256:ghi",
                        "browser_download_url": "https://example.com/fedora",
                    },
                ],
            },
        ]

        files = get_files_from_releases(releases)

        assert len(files) == 3
        assert files[0].name == "Arch-6.16-bore-gcc.tar.gz"
        assert files[1].name == "Debian-6.16-bore-gcc.tar.gz"
        assert files[2].name == "Fedora-6.16-bore-gcc.tar.gz"
        assert files[0].tag == "v1.0"
        assert files[2].tag == "v2.0"

    def test_get_files_from_releases_multiple_assets_per_release(self):
        """Test get_files_from_releases with multiple assets per release."""
        releases = [
            {
                "tag_name": "v1.0",
                "name": "Release 1.0",
                "assets": [
                    {
                        "name": "Arch-6.16-bore-gcc.tar.gz",
                        "size": 1024,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:abc",
                        "browser_download_url": "https://example.com/1",
                    },
                    {
                        "name": "Arch-6.16-bore-clang.tar.gz",
                        "size": 2048,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:def",
                        "browser_download_url": "https://example.com/2",
                    },
                    {
                        "name": "Debian-6.16-bore-gcc.tar.gz",
                        "size": 3072,
                        "updated_at": "2025-01-01T00:00:00+00:00",
                        "digest": "sha256:ghi",
                        "browser_download_url": "https://example.com/3",
                    },
                ],
            },
        ]

        files = get_files_from_releases(releases)

        assert len(files) == 3
        assert files[0].compiler == "gcc"
        assert files[1].compiler == "clang"
        assert files[2].distro == "Debian"


# =============================================================================
# filename_from_url
# =============================================================================


class TestFilenameFromUrl:
    """Tests for filename_from_url function."""

    def test_filename_from_url_normal(self):
        """Test filename_from_url with normal URL."""
        name = filename_from_url("https://example.com/path/to/file.tar.gz")
        assert name == "file.tar.gz"

    def test_filename_from_url_no_filename(self):
        """Test filename_from_url when URL has no path."""
        name = filename_from_url("https://example.com")
        assert name == "downloaded.file"

    def test_filename_from_url_trailing_slash(self):
        """Test filename_from_url with trailing slash."""
        name = filename_from_url("https://example.com/path/")
        assert name == "downloaded.file"