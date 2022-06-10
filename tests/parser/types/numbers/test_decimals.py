from decimal import Decimal, getcontext

import pytest

from vyper.exceptions import DecimalOverrideException, InvalidOperation, OverflowException


def test_decimal_override():
    # consumers of vyper, even as a library, are not allowed to override Decimal precision
    with pytest.raises(DecimalOverrideException):
        getcontext().prec = 100


def test_decimal_test(get_contract_with_gas_estimation):
    decimal_test = """
@external
def foo() -> int256:
    return(floor(999.0))

@external
def fop() -> int256:
    return(floor(333.0 + 666.0))

@external
def foq() -> int256:
    return(floor(1332.1 - 333.1))

@external
def bar() -> int256:
    return(floor(27.0 * 37.0))

@external
def baz() -> int256:
    x: decimal = 27.0
    return(floor(x * 37.0))

@external
def mok() -> int256:
    return(floor(999999.0 / 7.0 / 11.0 / 13.0))

@external
def mol() -> int256:
    return(floor(499.5 / 0.5))

@external
def mom() -> int256:
    return(floor(1498.5 / 1.5))

@external
def moo() -> int256:
    return(floor(2997.0 / 3.0))

@external
def foom() -> int256:
    return(floor(1999.0 % 1000.0))

@external
def foop() -> int256:
    return(floor(1999.0 % 1000.0))
    """

    c = get_contract_with_gas_estimation(decimal_test)

    assert c.foo() == 999
    assert c.fop() == 999
    assert c.foq() == 999
    assert c.bar() == 999
    assert c.baz() == 999
    assert c.mok() == 999
    assert c.mol() == 999
    assert c.mom() == 999
    assert c.moo() == 999
    assert c.foom() == 999
    assert c.foop() == 999

    print("Passed basic addition, subtraction and multiplication tests")


def test_harder_decimal_test(get_contract_with_gas_estimation):
    harder_decimal_test = """
@external
def phooey(inp: decimal) -> decimal:
    x: decimal = 10000.0
    for i in range(4):
        x = x * inp
    return x

@external
def arg(inp: decimal) -> decimal:
    return inp

@external
def garg() -> decimal:
    x: decimal = 4.5
    x *= 1.5
    return x

@external
def harg() -> decimal:
    x: decimal = 4.5
    x *= 2.0
    return x

@external
def iarg() -> uint256:
    x: uint256 = as_wei_value(7, "wei")
    x *= 2
    return x
    """

    c = get_contract_with_gas_estimation(harder_decimal_test)
    assert c.phooey(Decimal("1.2")) == Decimal("20736.0")
    assert c.phooey(Decimal("-1.2")) == Decimal("20736.0")
    assert c.arg(Decimal("-3.7")) == Decimal("-3.7")
    assert c.arg(Decimal("3.7")) == Decimal("3.7")
    assert c.garg() == Decimal("6.75")
    assert c.harg() == Decimal("9.0")
    assert c.iarg() == Decimal("14")

    print("Passed fractional multiplication test")


def test_mul_overflow(assert_tx_failed, get_contract_with_gas_estimation):
    mul_code = """

@external
def _num_mul(x: decimal, y: decimal) -> decimal:
    return x * y

    """

    c = get_contract_with_gas_estimation(mul_code)

    NUM_1 = Decimal("85070591730234615865843651857942052864")
    NUM_2 = Decimal("136112946768375385385349842973")

    assert_tx_failed(lambda: c._num_mul(NUM_1, NUM_2))


def test_decimal_min_max_literals(assert_tx_failed, get_contract_with_gas_estimation):
    code = """
@external
def maximum():
    a: decimal = 18707220957835557353007165858768422651595.9365500927
@external
def minimum():
    a: decimal = -18707220957835557353007165858768422651595.9365500928
    """
    c = get_contract_with_gas_estimation(code)

    assert c.maximum() == []
    assert c.minimum() == []


def test_scientific_notation(get_contract_with_gas_estimation):
    code = """
@external
def foo() -> decimal:
    return 1e-10

@external
def bar(num: decimal) -> decimal:
    return num + -1e38
    """
    c = get_contract_with_gas_estimation(code)

    assert c.foo() == Decimal("1e-10")  # Smallest possible decimal
    assert c.bar(Decimal("1e37")) == Decimal("-9e37")  # Math lines up


bad_code = [
    (
        """
@external
def foo() -> decimal:
    return 2.2 ** 2.0
    """,
        InvalidOperation,
    ),
    (
        """
@external
def foo() -> decimal:
    return 18707220957835557353007165858768422651595.9365500928
    """,
        OverflowException,
    ),
    (
        """
@external
def foo() -> decimal:
    return -18707220957835557353007165858768422651595.9365500929
    """,
        OverflowException,
    ),
]


@pytest.mark.parametrize("bad_code,expected", bad_code)
def test_invalid_code(get_contract, assert_compile_failed, bad_code, expected):
    assert_compile_failed(lambda: get_contract(bad_code), expected)
