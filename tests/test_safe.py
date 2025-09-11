import pytest

from TKT.safe import Err, Ok


class TestResult:
    def test_bool_truthiness(self):
        """Ok should evaluate to True, Err should evaluate to False."""

    def test_and_operator(self):
        """Test short-circuit AND: Ok returns other, Err returns self."""

    def test_or_operator(self):
        """Test short-circuit OR: Ok returns self, Err returns other."""

    def test_unwrap_ok(self):
        """Unwrap should return the inner value of Ok."""

    def test_unwrap_err(self):
        """Unwrap should raise the contained error when called on Err."""

    def test_unwrap_or(self):
        """unwrap_or should return the value for Ok, or the default for Err."""

    def test_map(self):
        """map should apply a function to the value in Ok, leave Err unchanged."""

    def test_map_or(self):
        """map_or should apply a function for Ok, or return the default for Err."""

    def test_map_err(self):
        """map_err should transform the error in Err, leave Ok unchanged."""

    def test_properties(self):
        """Properties (is_ok, is_err, ok, err) should reflect the variant correctly."""
