# 오행핏(Ohang Fit) 프로젝트 가이드

이 문서는 프로젝트 루트에 두고 Claude Code가 세션 시작 시 자동으로 참고하는 파일임.

## 참고 문서 (자동 임포트)

@ohang_fit_prd.md
@GIT_WORKFLOW.md

## ⚠️ 필수: 이 문서 업데이트 규칙

- **새 기능을 개발하거나 기존 기능/구조를 변경할 때마다 작업 마무리 단계에서 이 CLAUDE.md도 함께 업데이트할 것.** 코드만 바꾸고 문서는 그대로 두지 말 것.
- 업데이트 대상 예시:
  - 디렉토리 구조가 바뀌면 → "디렉토리 구조" 섹션 갱신
  - 새 실행 명령/환경변수/시딩 방법이 생기면 → "개발 환경" 섹션 갱신
  - 새로운 코딩 컨벤션이나 결정사항이 생기면 → "컨벤션 및 결정사항" 섹션에 추가
  - Phase가 바뀌거나 기능이 완성되면 → "진행 상황" 섹션 갱신
- 어댑터로 목업 처리해둔 부분(사주 API, PG, 커머스 등)의 실제 벤더가 정해지면 → 해당 섹션에 실제 연동 정보로 교체

## 프로젝트 개요

- 사주 오행 이론 기반 개인화 패션 "추천 아이템" 큐레이션 서비스
- 핵심 기능: 온보딩(사주 데이터 입력) → 분석(오행/신살) → 큐레이션(컬러/소재/아이템) → 결제(일회성) → 공유(SNS 카드)
- 자세한 배경/페르소나/카피 원칙은 `@ohang_fit_prd.md` 참고

## 디렉토리 구조

```
/frontend   → Next.js (App Router, TypeScript, Tailwind), 모바일 우선 반응형
  /src/app
    /onboarding        → 온보딩 입력 화면 (생성)
    /onboarding/[id]   → 저장된 온보딩 결과 조회/수정 화면
  /src/components      → 재사용 컴포넌트 (OnboardingForm 등)
  /src/lib/api.ts       → 백엔드 API 클라이언트 (fetch 래퍼, 타입)
/backend    → Python FastAPI
  /app
    main.py   → FastAPI 앱, 라우터 등록
    config.py → 환경변수 설정 (pydantic-settings)
    db.py     → SQLAlchemy 엔진/세션/Base
    /models   → SQLAlchemy 모델 (Profile, AnalysisResult 등)
    /schemas  → Pydantic 스키마 (요청/응답 검증)
    /routers  → API 라우터 (/profiles, /profiles/{id}/analysis, /profiles/{id}/curation 등)
    /adapters → 외부 연동 어댑터 인터페이스 (SajuAdapter 등). 벤더 미정인 동안은
                Mock*Adapter 구현체로 채워두고, 벤더 정해지면 같은 인터페이스의
                새 구현체로 교체 (호출부는 안 바뀜)
  /alembic    → DB 마이그레이션
  /scripts    → 시딩 등 관리 스크립트 (seed_curation.py 등). 실행: `cd backend && .venv/bin/python -m scripts.<파일명>`
  /tests      → pytest (모델/스키마/API 단위·통합 테스트)
  conftest.py → pytest 루트 설정 (sys.path + DB 세션/TestClient fixture)
  requirements.txt
  Dockerfile
docker-compose.yml → PostgreSQL(db) + backend 컨테이너 (frontend는 미포함, 로컬 npm run dev)
docs/superpowers/  → 기능별 설계 문서(specs)/구현 계획(plans)
ohang_fit_prd.md   → PRD 전체 문서
CLAUDE.md   → 이 문서
```

## 개발 환경

- 로컬 실행: `docker compose up` 으로 PostgreSQL(호스트 5433→컨테이너 5432) + backend(8000, FastAPI/uvicorn --reload) 실행
  - db 호스트 포트가 5433인 이유: 로컬 macOS에 이미 네이티브 Postgres가 5432를 점유하는 경우가 있어 충돌 회피용. 컨테이너 간 통신(backend→db)은 내부 5432 그대로라 영향 없음
- frontend는 컨테이너화하지 않고 `cd frontend && npm run dev`로 로컬 실행(3000), backend 컨테이너의 API(localhost:8000)를 바라봄
- backend 헬스체크: `GET /health` (앱 기동 확인), `GET /health/db` (DB 커넥션 확인)
- backend 환경변수: `backend/.env.example` 참고 (`DATABASE_URL`, `CORS_ORIGINS`). 로컬에서 docker 없이 backend만 띄울 때는 `backend/.env` 생성 후 사용 (기본값은 `localhost:5433` 기준)
- frontend 환경변수: `frontend/.env.example` 참고 (`NEXT_PUBLIC_API_URL`, 백엔드 API 주소). Next.js는 `NEXT_PUBLIC_*` 변수를 런타임이 아니라 **빌드 타임**에 JS 번들에 박아넣으므로, 배포 시 `npm run build` 실행 전에 반드시 올바른 값을 설정해야 함 (빠뜨리면 번들이 조용히 `localhost:8000`을 가리키게 되고 서버 에러도 없이 전체 방문자에게 깨진 상태로 배포됨)
- backend를 docker 없이 로컬로 띄우려면: `cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --reload`
- DB 마이그레이션: Alembic 사용, `backend/` 에서 실행
  - 모델 추가 후 `alembic/env.py`에 `from app.models import <module>` 등록 필요 (target_metadata가 `app.db.Base.metadata`를 봄)
  - **새 모델을 만들면 pytest보다 마이그레이션을 먼저 생성할 것.** `conftest.py`의 `create_all()` 세이프티넷 때문에, 모델을 만든 뒤 마이그레이션 생성 전에 pytest를 먼저 돌리면 테이블이 create_all로 먼저 생겨버려서 `alembic revision --autogenerate`가 빈 마이그레이션(`pass`)을 만들어냄 (alembic 기록과 실제 스키마는 여기서도 어긋남 — 실제로 한 번 겪은 버그, `alembic stamp <revision>`으로 수동 동기화해서 복구했음). 순서: 모델 작성 → 마이그레이션 생성·적용 → 그 다음에 pytest
  - 새 마이그레이션 생성: `.venv/bin/alembic revision --autogenerate -m "설명"`
  - 적용: `.venv/bin/alembic upgrade head` (docker db가 떠 있어야 함, `docker compose up -d db`)
  - 시딩: `cd backend && .venv/bin/python -m scripts.seed_curation` (docker db가 떠 있어야 함). `color_mappings`에 이미 데이터가 있으면 건너뜀(재실행해도 중복 안 됨)
- 백엔드 테스트: `cd backend && .venv/bin/pytest -v` (docker db가 떠 있어야 함, `docker compose up -d db`). `conftest.py`의 세션 fixture는 `Base.metadata.create_all()`만 하고 **drop은 하지 않음** — dev DB가 pytest·docker가 공유하는 동일 DB라서, 세션 종료 시 테이블을 drop하면 alembic 기록과 실제 스키마가 어긋나며 다른 실행 중인 backend가 깨짐 (실제로 한 번 겪은 버그). 테스트 데이터 격리는 `db_session` fixture의 트랜잭션 롤백으로 충분히 되므로 스키마 drop은 앞으로도 추가하지 말 것

## 개발 순서 원칙

- 기능 단위(온보딩 → 분석 → 큐레이션 → 결제 → 공유)로 진행하며, 한 기능마다 아래 순서를 지킬 것:
  1. 백엔드(DB 스키마 + API) 구현
  2. 대응하는 프론트 화면 구현
  3. 실제 API와 연동해서 테스트까지 완료
  4. 위 3단계가 끝나야 다음 기능으로 이동
- 프론트를 여러 기능 몰아서 한 번에 만들지 않기

## 컨벤션 및 결정사항

- 사주/오행 계산, 결제(PG), 제휴 커머스는 벤더 미정 상태 → 모두 어댑터 패턴으로 인터페이스 분리, 우선 목업으로 구현
- 모노레포 구조 사용 (frontend/backend 레포 분리 안 함)
- 사용자 식별 모델(리드/회원, 결제 여부에 따른 노출 수준)은 `docs/superpowers/specs/2026-09-07-phase1-architecture-design.md` 및 PRD 5.6 참고
- 계정(Account) 시스템이 붙기 전까지, 온보딩처럼 완전 익명인 리소스는 서버가 발급한 UUID 자체를 조회/수정 키로 사용 (URL에 노출돼도 추측 불가하므로 안전). Account가 생기면 그쪽 인증으로 전환
- (TBD: 코드 스타일/린트 규칙, 커밋 컨벤션, 테스트 전략 — 정해지는 대로 추가)

## UX/카피 원칙

- "패션 추천"이 아니라 **"추천 아이템"** 이라는 표현 사용
- "오늘 뭐 입지" 대신 **"오늘 뭘 입으면 나에게 도움이 될까"** 톤
- UI 라벨은 "오늘의 컬러", "오늘의 추천 아이템"처럼 데일리 콘텐츠 느낌으로 노출하되, 실제 값은 결제 시점 기준 고정값 (일회성 결제 모델)

## 진행 상황 (Progress Log)

- [ ] Phase 1 (MVP) — 진행 중 (온보딩·분석·큐레이션 완료. 온보딩: `POST/GET/PATCH /profiles` + 입력/조회/수정 화면. 분석: `POST/GET /profiles/{id}/analysis`(MockSajuAdapter, 결정론적 목업) + 오행 분포/부족/과다 표시, 온보딩 저장 시 자동 실행. 큐레이션: `GET /profiles/{id}/curation`(부족 오행 → 컬러 매핑 + 자체 아이템, 시딩 데이터) + "오늘의 컬러"/"오늘의 추천 아이템" 표시, 분석 완료 시 자동 실행. 셋 다 실제 연동 테스트 완료. 결제/공유 남음)
- [ ] Phase 2 — 시작 전
- [ ] Phase 3 — 시작 전

> 기능 완성될 때마다 위 체크리스트와 각 섹션을 업데이트할 것