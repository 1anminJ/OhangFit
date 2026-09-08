class PaymentAdapter:
    """결제 어댑터 인터페이스. 실제 PG 벤더가 정해지면 이 클래스를 상속해 교체."""

    def charge(self, amount: int) -> bool:
        raise NotImplementedError


class MockPaymentAdapter(PaymentAdapter):
    """ponytail: 실제 PG 연동 없이 항상 성공 처리하는 목업. 벤더 정해지면 교체."""

    def charge(self, amount: int) -> bool:
        return True
