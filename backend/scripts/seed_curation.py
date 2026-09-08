"""오행 컬러 매핑 + 큐레이션 아이템 시딩.

실행: cd backend && .venv/bin/python -m scripts.seed_curation (docker db가 떠 있어야 함)

- color_mappings: 전통 오행-색상 대응 (실제 이론, 목업 아님)
- curation_items: ponytail: 실제 카탈로그/이미지가 없어 오행당 2개씩 placeholder
  아이템만 넣어둠. 실제 아이템 풀이 생기면 이 스크립트 대신 진짜 데이터로 교체.
"""

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models.color_mapping import ColorMapping
from app.models.curation_item import CurationItem

COLOR_MAPPINGS = [
    ("목", "초록", "#2E8B57"),
    ("목", "청색", "#1E90FF"),
    ("화", "빨강", "#DC143C"),
    ("토", "노랑", "#FFD700"),
    ("토", "갈색", "#8B4513"),
    ("금", "흰색", "#FFFFFF"),
    ("금", "은색", "#C0C0C0"),
    ("수", "검정", "#000000"),
    ("수", "남색", "#000080"),
]

CURATION_ITEMS = [
    ("목", "초록 니트", "아우터", "https://placehold.co/400x400?text=green-knit"),
    ("목", "청색 셔츠", "이너", "https://placehold.co/400x400?text=blue-shirt"),
    ("화", "빨강 스카프", "액세서리", "https://placehold.co/400x400?text=red-scarf"),
    ("화", "빨강 스니커즈", "신발", "https://placehold.co/400x400?text=red-sneakers"),
    ("토", "노랑 가디건", "아우터", "https://placehold.co/400x400?text=yellow-cardigan"),
    ("토", "갈색 벨트", "액세서리", "https://placehold.co/400x400?text=brown-belt"),
    ("금", "화이트 셔츠", "이너", "https://placehold.co/400x400?text=white-shirt"),
    ("금", "은색 목걸이", "액세서리", "https://placehold.co/400x400?text=silver-necklace"),
    ("수", "검정 코트", "아우터", "https://placehold.co/400x400?text=black-coat"),
    ("수", "남색 니트", "이너", "https://placehold.co/400x400?text=navy-knit"),
]


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(select(func.count()).select_from(ColorMapping)).scalar_one()
        if existing > 0:
            print("color_mappings에 이미 데이터가 있어 시딩을 건너뜁니다.")
            return

        db.add_all(
            ColorMapping(element=element, color_name=color_name, hex_code=hex_code)
            for element, color_name, hex_code in COLOR_MAPPINGS
        )
        db.add_all(
            CurationItem(element=element, name=name, category=category, image_url=image_url)
            for element, name, category, image_url in CURATION_ITEMS
        )
        db.commit()
        print(
            f"시딩 완료: color_mappings {len(COLOR_MAPPINGS)}개, "
            f"curation_items {len(CURATION_ITEMS)}개"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
