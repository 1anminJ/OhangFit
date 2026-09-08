class EmailAdapter:
    """이메일 발송 어댑터 인터페이스. 실제 벤더 API가 정해지면 이 클래스를 상속해 교체."""

    def send_magic_link(self, email: str, token: str) -> None:
        raise NotImplementedError


class MockEmailAdapter(EmailAdapter):
    """
    ponytail: 실제 이메일 전송 없이 로그만 남기는 목업. 개발 편의를 위해 실제 링크는
    /leads 응답의 magic_link_url로 그대로 노출한다(라우터 쪽 책임). 벤더 정해지면
    이 클래스만 교체하면 됨.
    """

    def send_magic_link(self, email: str, token: str) -> None:
        print(f"[MockEmailAdapter] {email}에게 매직링크 발송 (토큰: {token})")
