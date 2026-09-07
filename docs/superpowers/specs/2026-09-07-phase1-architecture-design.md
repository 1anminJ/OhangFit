# Phase 1 아키텍처 설계 — 사용자 식별 모델 + 온보딩 상세 스펙

- 상태: 승인됨 (2026-09-07 대화에서 확정)
- 관련 문서: `ohang_fit_prd.md` (5.5, 5.6, 6, 7, 9 섹션에 이번 결정 반영 완료), `ohang_fit_claude_code_prompts.md`
- 범위: Phase 1 전체 엔티티 관계의 큰 그림 + 오늘 구현하는 **온보딩** 기능의 상세 스펙

## 1. 배경 및 목표

Phase 1(MVP)을 시작하기 전, `ohang_fit_claude_code_prompts.md`의 지시대로 전체 DB 스키마와 API 엔드포인트 설계안을 먼저 확정한다. PRD에는 명시되지 않았던 "사용자를 어떻게 식별할 것인가"가 이번 설계의 핵심 결정 사항이었고, 그 결과를 `ohang_fit_prd.md`에도 반영했다.

개발은 기능 단위(온보딩 → 분석 → 큐레이션 → 결제 → 공유) 순서로 진행하며, 각 기능 차례에 해당 DB 테이블을 Alembic 마이그레이션으로 추가한다 — 이 문서의 전체 스키마는 "최종 그림"이지, 오늘 한 번에 다 만드는 것이 아니다.

## 2. 사용자 식별 모델 (Lead / Member)

- **리드(비회원)**: 온보딩+분석이 끝난 뒤 무료 미리보기를 보려면 이메일만 입력(비밀번호 없음). 결과 조회 링크를 이메일로 발송 — 링크는 `secrets.token_urlsafe()`로 발급한 랜덤 토큰을 DB에 저장해두고 대조하는 방식(=매직링크). 재방문 시 이 링크로 이메일 재입력 없이 결과에 복귀.
- **회원**: 결제하려는 사용자만 회원가입(이메일+비밀번호)으로 전환. 가입 폼에서 리드 단계에 쓴 이메일 재사용을 권장 — 동일 이메일로 가입하면 기존 리드 레코드(온보딩 데이터+분석 결과)를 그대로 이어받는다. 이 매칭으로 "무료 미리보기 → 회원가입" 퍼널을 추적한다(관리자 대시보드는 Phase 3 범위, PRD 7 참고).
- **결과 노출 수준은 결제 여부로만 갈린다** (회원가입 자체는 콘텐츠 등급에 영향 없음):
  - 결제 전(리드 or 미결제 회원): 무료 미리보기 수준(부족한 오행 + 한 줄 요약)만 노출
  - 결제 완료: 상세 큐레이션(컬러/소재/아이템) + 공유 카드 잠금 해제
  - 미결제 회원은 마이페이지에서도 무료 미리보기와 동일한 수준만 봄 — 마이페이지의 가치는 "재조회 가능"이지 "콘텐츠 업그레이드"가 아님
- 로그인 회원 대상 추가 알림/혜택은 카피 방향만 잡아두고 구체 시스템은 Phase 2 win-back 알림과 함께 설계 (액션 아이템)

## 3. Phase 1 전체 엔티티 관계 (개요)

```
Profile (온보딩)  ──1:1──  AnalysisResult (분석)
   │
   └──nullable FK (결제 기능 차례에 추가)──  Account (lead/member)
                                                  │
                                                  ├── Payment (결제)
                                                  └── access_token 기반 매직링크 인증

ColorMapping / CurationItem (큐레이션, 시딩 데이터로 채움)
ShareCard (공유, Profile에 연결)
```

- **Profile**: 사주 입력값. 계정 개념 없이 완전 익명으로 생성됨 (오늘 구현 대상)
- **Account**: `id, email(unique), role(lead/member), password_hash(nullable), access_token(nullable, unique), token_created_at, converted_to_member_at, created_at`. **결제 기능 차례**에 테이블 생성 + `profiles.account_id` nullable FK 추가
- **AnalysisResult**: `profile_id`(1:1 FK), 오행 분포(JSON), 부족/과다 오행, 신살(JSON, 확장 가능). **분석 기능 차례**에 생성. 계산 로직은 어댑터 패턴(`SajuAdapter` 인터페이스 + Mock 구현체)으로 분리
- **ColorMapping**: 오행 → 컬러 매핑 테이블. **큐레이션 기능 차례**
- **CurationItem**: 에디터가 시딩하는 자체 아이템 풀 (id, name, category, image_url, 연결 컬러/오행). **큐레이션 기능 차례**. 관리용 CRUD는 시딩 스크립트 수준으로 충분(전용 어드민 UI는 만들지 않음)
- **Payment**: `account_id, profile_id, amount, status(pending/success/failed), paid_at`. 목업 PG 어댑터로 처리. **결제 기능 차례**
- **ShareCard**: `profile_id`, 생성된 이미지 asset 참조. **공유 기능 차례**. 서버사이드 이미지 렌더링 구현 방식은 그 기능 차례에 리서치

## 4. 오늘 구현 범위: 온보딩

### 4.1 테이블: `profiles`

| 컬럼 | 타입 | 제약 |
|---|---|---|
| id | UUID (PK) | server 생성 (`uuid4`) |
| birth_date | DATE | not null |
| birth_time | TIME | nullable |
| birth_time_unknown | BOOLEAN | not null, default false |
| gender | VARCHAR (enum: male/female) | not null |
| birth_region | VARCHAR | not null |
| created_at | TIMESTAMPTZ | not null, default now() |
| updated_at | TIMESTAMPTZ | not null, default now() |

### 4.2 검증 규칙 (PRD 5.1)

- `birth_date`: `1900-01-01 <= birth_date <= 오늘`. 범위 밖이면 거부
- `birth_time_unknown=false`이면 `birth_time` 필수. `true`이면 `birth_time`은 저장하지 않음(요청에 값이 와도 무시하고 null 처리)
- `gender`: `male` | `female` 중 하나
- `birth_region`: 빈 문자열 불가, 자유 텍스트(지오코딩 없음 — MVP 단순화)

### 4.3 API

인증 시스템이 없는 단계이므로, 발급된 `id`(UUID, 추측 불가) 자체가 "이 온보딩을 조회/수정할 수 있는 키" 역할을 한다. 결제 기능이 붙으면 그때부터 Account 인증으로 넘어간다.

- `POST /profiles` — 생성. 검증 실패 시 `422` + 필드별 에러 메시지
- `GET /profiles/{id}` — 조회. 없는 id는 `404`
- `PATCH /profiles/{id}` — 부분 수정(재입력)

### 4.4 에러 처리

FastAPI/Pydantic 기본 `422` 응답 형식을 그대로 쓰고, 커스텀 검증(미래 날짜, 1900년 이전, birth_time_unknown 정합성)은 Pydantic validator에서 명확한 한국어 에러 메시지로 반환한다.

### 4.5 테스트

pytest + FastAPI `TestClient`. 검증 규칙별 케이스 위주:
- 정상 생성/조회/수정
- 미래 날짜 거부
- 1900년 이전 거부
- `birth_time_unknown=true`인데 `birth_time` 같이 온 경우 → 무시하고 저장 안 됨
- `birth_time_unknown=false`인데 `birth_time` 없는 경우 → 거부
- 잘못된 gender 값 거부
- 존재하지 않는 id 조회/수정 시 404

## 5. 보안/개인정보

생년월일시는 민감정보이지만, Phase 1은 **인프라 레벨 암호화**(배포 환경의 관리형 Postgres 디스크 암호화 + TLS 연결)로 대응하고 컬럼 단위 앱 레벨 암호화는 하지 않는다. 1인 프로젝트 규모에서 앱 레벨 암호화 키 관리 부담이 인프라 레벨 암호화보다 크다고 판단. 배포 시 사용할 Postgres가 저장 암호화를 지원하는지 확인 필요(액션 아이템, PRD 9 참고).

## 6. 다음 단계

이 스펙에서는 온보딩만 구현한다. 분석/큐레이션/결제/공유는 각 기능 차례가 됐을 때 이 문서의 3장 개요를 기준으로 상세 설계를 다시 확인한다(세부사항이 그 시점에 바뀔 수 있음 — 이 문서는 지금 시점의 최선의 그림).
