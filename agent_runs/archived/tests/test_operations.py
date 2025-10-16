import pytest
from math_utils import operations

def test_add():
    assert operations.add(2, 3) == 5
    assert operations.add(-1, 1) == 0

def test_subtract():
    assert operations.subtract(5, 3) == 2
    assert operations.subtract(0, 4) == -4

def test_multiply():
    assert operations.multiply(2, 3) == 6
    assert operations.multiply(-1, 5) == -5

def test_divide():
    assert operations.divide(6, 3) == 2
    assert operations.divide(5, 2) == 2.5
    with pytest.raises(ValueError):
        operations.divide(1, 0)
