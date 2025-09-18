import datetime

import pytest

from TKT.fetch import FileData, FileSize, filename_from_url


class TestFileSize:
    def test_init(self):
        """Test FileSize initialization and non-negative validation."""
        assert FileSize(0) == 0
        assert FileSize(1024) == 1024
        assert FileSize(200.5) == 200  # convert float into int

    def test_init_negative(self):
        """Test FileSize with negative input"""
        with pytest.raises(ValueError):
            FileSize(-500)

    def test_index(self):
        """
        Test __index__ returns the correct integer for
        indexing contexts.
        """
        size = FileSize(2)
        assert size.__index__() is size._bytes

    def test_int(self):
        """Test __int__ conversion returns the underlying byte value."""
        size = FileSize(200)
        assert int(size) is size._bytes

    def test_repr(self):
        """
        Test __repr__ produces the correct unambiguous
        representation.
        """
        assert repr(FileSize(10)) == "FileSize(10)"
        assert repr(FileSize(1024)) == "FileSize(1024)"
        assert repr(FileSize(1024**2)) == "FileSize(1048576)"

    def test_str(self):
        """Test __str__ formats file size into human-readable units."""
        assert str(FileSize(10)) == "10 B"
        assert str(FileSize(1024)) == "1 KB"
        assert str(FileSize(1024**2)) == "1 MB"

    def test_iadd(self):
        """Test in-place addition (__iadd__) updates the byte count."""
        size = FileSize(512)
        size += 512
        assert size == 1024

    def test_eq(self):
        """Test equality of FileSize objects."""
        size = FileSize(2048)
        assert size == 2048


class TestFileData:
    def test_init(self):
        """Test FileData initialization with expected attributes."""
        name = "Arch-linux-bore-gcc.tar.gz"
        size = FileSize(56245816)  # 53.64 MB
        updated_at = datetime.datetime(2025, 8, 21, 20, 0, 38, tzinfo=datetime.timezone.utc)
        digest = "sha256:20f5dfedc4b2f989ad022ba7aa697f5986c28841a44068ab76a2cacd1d06fe83"
        url = f"https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/{name}"
        version = "TKT v6.16-tkt — GHCI Prebuilt Diet Kernel"
        tag = "v6.16-tkt"

        file_data = FileData(
            name=name,
            size=size,
            updated_at=updated_at,
            digest=digest,
            url=url,
            version=version,
            tag=tag,
        )

        assert file_data.name == name
        assert file_data.size == size
        assert file_data.updated_at == updated_at
        assert file_data.digest == digest
        assert file_data.url == url
        assert file_data.version == version
        assert file_data.tag == tag

    def test_post_init(self):
        """
        Test __post_init__ extracts distro, scheduler
        and compiler from name.
        """

        name = "Debian-linux-diet-eevdf-gcc.tar.gz"
        size = FileSize(564559951)
        updated_at = datetime.datetime(2025, 8, 21, 20, 1, tzinfo=datetime.timezone.utc)
        digest = "sha256:5434fd4289962cfbab5bcee6074c5514e82ea6c94d878d6e5aa71605128dd23d"
        url = f"https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/{name}"
        version = "TKT v6.16-tkt — GHCI Prebuilt Diet Kernel"
        tag = "v6.16-tkt"

        file_data = FileData(
            name=name,
            size=size,
            updated_at=updated_at,
            digest=digest,
            url=url,
            version=version,
            tag=tag,
        )

        assert file_data.distro == "Debian"
        assert file_data.scheduler == "eevdf"
        assert file_data.compiler == "gcc"

        name = "Debian-linux.tar.gz"
        with pytest.raises(ValueError, match="^Unexpected file name format"):
            file_data = FileData(
                name=name,
                size=size,
                updated_at=updated_at,
                digest=digest,
                url=url,
                version=version,
                tag=tag,
            )


class TestFunctions:
    def test_filename_from_url(self):
        name = "Arch-linux-bore-gcc.tar.gz"
        url = f"https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/{name}"
        result = filename_from_url(url)
        assert result == name

        # test with id
        name = "Debian-linux-diet-eevdf-gcc.tar.gz"
        url = f"https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/{name}#releases"
        result = filename_from_url(url)
        assert result == name

        # test with query parameters
        name = "Fedora-linux-diet-eevdf-gcc.tar.gz"
        url = f"https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/{name}?distro=fedora"
        result = filename_from_url(url)
        assert result == name

        # test with empty path
        url = "https://github.com/The-Kernel-Toolkit/TKT/releases/download/v6.16-tkt/"
        result = filename_from_url(url)
        assert result == "downloaded.file"
