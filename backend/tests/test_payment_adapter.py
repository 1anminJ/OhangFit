from app.adapters.payment import MockPaymentAdapter


def test_charge_always_succeeds():
    adapter = MockPaymentAdapter()
    assert adapter.charge(9900) is True


def test_charge_succeeds_for_any_amount():
    adapter = MockPaymentAdapter()
    assert adapter.charge(1) is True
    assert adapter.charge(1_000_000) is True
