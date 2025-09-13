import pytest

from TKT.safe import Err, Ok


@pytest.mark.parametrize("Result", [Ok, Err])
class TestResult:
    def test_bool_truthiness(self, Result):
        """Ok should evaluate to True, Err should evaluate to False."""
        result = Result(object())
        match result:
            case Ok(_):
                assert result
            case Err(_):
                assert not result

    def test_and_operator(self, Result):
        """Test short-circuit AND: Ok returns other, Err returns self."""
        result = Result(object())
        other = object()
        match result:
            case Ok(_):
                assert (result & other) is other
            case Err(_):
                assert (result & other) is result

    def test_or_operator(self, Result):
        """Test short-circuit OR: Ok returns self, Err returns other."""
        result = Result(object())
        other = object()
        match result:
            case Ok(_):
                assert (result | other) is result
            case Err(_):
                assert (result | other) is other

    def test_eq_operator(self, Result):
        """Test two distinct Result objects for equality."""
        if Result is Ok:
            res1 = Ok(7)
            res2 = Ok(10)
            res3 = Err(Exception("error"))
            assert res1 == Ok(7)
            assert res1 != res2
            assert res1 != res3
        elif Result is Err:
            error = Exception("some error")
            res1  = Err(error)
            res2  = Err(RuntimeError("another error"))
            res3  = Ok(7)
            assert res1 == Err(error)
            assert res1 != res2
            assert res1 != res3

    def test_string_representation(self, Result):
        """Should return 'Ok(value)' or 'Err(error)'."""
        if Result is Ok:
            value  = "some value"
            result = Ok(value)
            assert repr(result) == f"Ok({value!r})"
        elif Result is Err:
            error  = Exception("some error")
            result = Err(error)
            assert repr(result) == f"Err({error!r})"

    def test_unwrap(self, Result):
        """
        unwrap should return the inner value of Ok or raise
        the contained error when called on Err.
        """
        if Result is Ok:
            value = object()
            result = Ok(value)
            assert result.unwrap() is value
        elif Result is Err:
            error = Exception("It can be any error")
            result = Err(error)
            with pytest.raises(Exception, check=(lambda err: err is error)):
                result.unwrap()

    def test_unwrap_or(self, Result):
        """unwrap_or should return the value for Ok, or the default for Err."""
        value = object()
        default = object()
        result = Result(value)
        match result:
            case Ok(inner_value):
                assert result.unwrap_or(default) is inner_value
            case Err(_):
                assert result.unwrap_or(default) is default

    def test_map(self, Result):
        """
        map should apply a function to the value in Ok
        and leave Err unchanged.
        """
        if Result is Ok:
            value = 5
            result = Ok(value)
            new_result = result.map(lambda x: x + 2)
            assert new_result.ok == 7
        elif Result is Err:
            error = Exception("Some error")
            result = Err(error)
            new_result = result.map(lambda x: x + 2)
            assert new_result.err is error

    def test_map_or(self, Result):
        """
        map_or should apply a function for Ok, or return
        the default for Err.
        """
        value      = object()
        default    = object()
        result     = Result(value)
        new_result = result.map_or({"result": Ok(0)}, lambda x: {"result": Ok(x)})
        match result:
            case Ok(inner_value):
                assert new_result == {"result": Ok(inner_value)}
            case Err(_):
                assert new_result == {"result": Ok(0)}

    def test_map_err(self, Result):
        """
        map_err should transform the error in Err
        and leave Ok unchanged.
        """
        def wrap_error(err: Exception) -> RuntimeError:
            new_err = RuntimeError("A new error")
            new_err.__cause__ = err
            return new_err

        value = object()
        error = Exception("It is an error")
        if Result is Ok:
            result     = Ok(value)
            new_result = result.map_err(wrap_error)
            assert new_result == result
        elif Result is Err:
            result     = Err(error)
            new_result = result.map_err(wrap_error)
            with pytest.raises(RuntimeError, check=wrap_error):
                new_result.unwrap()

    def test_is_ok(self, Result):
        """Should return True if Result is Ok and False otherwise."""
        if Result is Ok:
            value  = object()
            result = Ok(value)
            assert result.is_ok
        elif Result is Err:
            error  = Exception("error")
            result = Err(error)
            assert not result.is_ok

    def test_is_err(self, Result):
        """Should return True if Result is Err and False otherwise."""
        if Result is Ok:
            value  = object()
            result = Ok(value)
            assert not result.is_err
        elif Result is Err:
            error  = Exception("error")
            result = Err(error)
            assert result.is_err

    def test_ok(self, Result):
        """Should return the inner value if Ok or None otherwise."""
        if Result is Ok:
            value  = object()
            result = Ok(value)
            assert result.ok is value
        elif Result is Err:
            error  = Exception("error")
            result = Err(error)
            assert result.ok is None

    def test_err(self, Result):
        """Should return the wrapped error if Err or None otherwise."""
        if Result is Ok:
            value  = object()
            result = Ok(value)
            assert result.err is None
        elif Result is Err:
            error  = Exception("error")
            result = Err(error)
            assert result.err is error
