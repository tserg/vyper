def test_values_should_be_increasing_ints(get_contract):
    code = """
enum Action:
    BUY
    SELL
    CANCEL

@external
@view
def buy() -> Action:
    return Action.BUY

@external
@view
def sell() -> Action:
    return Action.SELL

@external
@view
def cancel() -> Action:
    return Action.CANCEL
    """
    c = get_contract(code)
    assert c.buy() == 1
    assert c.sell() == 2
    assert c.cancel() == 4


def test_bitwise(get_contract, assert_tx_failed):
    code = """
enum Roles:
    USER
    STAFF
    ADMIN
    MANAGER
    CEO

@external
def bor() -> Roles:
    return Roles.USER | Roles.CEO

@external
def band() -> Roles:
    c: Roles = Roles.USER | Roles.CEO
    return c & Roles.USER

@external
def bor_arg(a: Roles, b: Roles) -> Roles:
    return a | b

@external
def band_arg(a: Roles, b: Roles) -> Roles:
    return a & b
    """
    c = get_contract(code)
    assert c.bor() == 17
    assert c.band() == 1

    assert c.bor_arg(1, 4) == 5
    # LHS: USER | ADMIN | CEO; RHS: USER | MANAGER | CEO
    assert c.band_arg(21, 25) == 17

    # LHS is out of bound
    assert_tx_failed(lambda: c.bor_arg(32, 3))
    assert_tx_failed(lambda: c.band_arg(32, 3))

    # RHS
    assert_tx_failed(lambda: c.bor_arg(3, 32))
    assert_tx_failed(lambda: c.band_arg(3, 32))


def test_for_in_enum(get_contract_with_gas_estimation):
    code = """
enum Roles:
    USER
    STAFF
    ADMIN
    MANAGER
    CEO

@external
def foo() -> bool:
    return Roles.USER in (Roles.USER | Roles.ADMIN)

@external
def bar(a: Roles) -> bool:
    return a in (Roles.USER | Roles.ADMIN)

@external
def baz(a: Roles) -> bool:
    x: Roles = Roles.USER | Roles.ADMIN | Roles.CEO
    y: Roles = Roles.USER | Roles.ADMIN | Roles.MANAGER
    return a in (x & y)
    """
    c = get_contract_with_gas_estimation(code)
    assert c.foo() is True

    assert c.bar(1) is True  # Roles.USER should pass
    assert c.bar(2) is False  # Roles.STAFF should fail

    assert c.baz(1) is True  # Roles.USER should pass
    assert c.baz(4) is True  # Roles.ADMIN should pass
    assert c.baz(8) is False  # Roles.MANAGER should fail
