import pytest

from souriva.tools import calculator


def test_calculator_supports_arithmetic():
    assert calculator("(40 * 3) / 2") == 60
    assert calculator("2 ** 3") == 8


def test_calculator_rejects_code_execution():
    with pytest.raises(ValueError, match="numeric arithmetic"):
        calculator("__import__('os').getcwd()")
