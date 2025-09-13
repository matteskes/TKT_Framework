class TestFileSize:
    def test_init(self):
        """Test FileSize initialization and non-negative validation."""

    def test_index(self):
        """
        Test __index__ returns the correct integer for
        indexing contexts.
        """

    def test_int(self):
        """Test __int__ conversion returns the underlying byte value."""

    def test_repr(self):
        """
        Test __repr__ produces the correct unambiguous
        representation.
        """

    def test_str(self):
        """Test __str__ formats file size into human-readable units."""

    def test_iadd(self):
        """Test in-place addition (__iadd__) updates the byte count."""

    def test_match(self):
        """Test structural pattern matching works with FileSize."""


class TestFileData:
    def test_init(self):
        """Test FileData initialization with expected attributes."""

    def test_post_init(self):
        """
        Test __post_init__ extracts distro, scheduler
        and compiler from name.
        """
