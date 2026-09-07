import hashlib
from dataclasses import dataclass
from datetime import date, time

ELEMENTS = ["목", "화", "토", "금", "수"]
SLOTS = 8  # 사주 8자(년/월/일/시 각 2자) 개념을 흉내낸 슬롯 수


@dataclass
class AnalysisData:
    five_elements: dict[str, int]
    missing_elements: list[str]
    excess_elements: list[str]
    sinsal: list[str]


class SajuAdapter:
    """사주 분석 어댑터 인터페이스. 실제 벤더 API가 정해지면 이 클래스를 상속해 교체."""

    def analyze(self, birth_date: date, birth_time: time | None) -> AnalysisData:
        raise NotImplementedError


class MockSajuAdapter(SajuAdapter):
    """
    ponytail: 실제 만세력/60갑자 계산이 아니라 생년월일시 기반 결정론적 목업.
    같은 입력이면 항상 같은 결과. 벤더 API가 정해지면 이 클래스만 SajuAdapter의
    다른 구현체로 교체하면 되고, 호출부(라우터)는 바뀔 필요 없음.
    """

    def analyze(self, birth_date: date, birth_time: time | None) -> AnalysisData:
        five_elements = self._compute_five_elements(birth_date, birth_time)
        min_count = min(five_elements.values())
        max_count = max(five_elements.values())
        return AnalysisData(
            five_elements=five_elements,
            missing_elements=[e for e, c in five_elements.items() if c == min_count],
            excess_elements=[e for e, c in five_elements.items() if c == max_count],
            sinsal=[],
        )

    @staticmethod
    def _compute_five_elements(
        birth_date: date, birth_time: time | None
    ) -> dict[str, int]:
        key = birth_date.isoformat()
        if birth_time is not None:
            key += f"T{birth_time.hour:02d}:{birth_time.minute:02d}"

        counts = [0, 0, 0, 0, 0]
        for i in range(SLOTS):
            digest = hashlib.sha256(f"{key}-{i}".encode()).hexdigest()
            counts[int(digest, 16) % len(ELEMENTS)] += 1
        return dict(zip(ELEMENTS, counts))
