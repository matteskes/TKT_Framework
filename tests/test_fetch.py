import pytest

from TKT.fetch import FileSize


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

    def test_post_init(self):
        """
        Test __post_init__ extracts distro, scheduler
        and compiler from name.
        """
