# Phase 1 결제 기능 설계 — 리드/회원 식별, 매직링크 인증, 결제 목업, 큐레이션 게이팅

- 상태: 승인됨 (2026-09-08 대화에서 확정)
- 관련 문서: `ohang_fit_prd.md` 5.5/5.6/6, `docs/superpowers/specs/2026-09-07-phase1-architecture-design.md` (섹션 2/3에서 이미 사용자 식별 모델 방향은 잡혀 있었음 — 이 문서가 그걸 실제 구현 가능한 수준으로 구체화)
- 범위: 온보딩 → 분석 → 큐레이션까지 완성된 상태에서, 이메일 리드 캡처 → 회원가입 → 결제 → 큐레이션 잠금 해제로 이어지는 전체 흐름

## 1. 배경 및 핵심 설계 원칙

**인증 토큰은 "이메일/비밀번호 → 내 profile_id 찾기" 용도로만 쓴다.** 그 이후의 모든 데이터 접근(온보딩/분석/큐레이션)은 지금까지와 동일하게 `profile_id` 기반 패턴을 유지한다. 이렇게 하면 기존 라우터들(`/profiles`, `/profiles/{id}/analysis`, `/profiles/{id}/curation`)에 인증 헤더 파싱 로직을 넣을 필요가 없다. 인증 로직은 `POST /leads`, `POST /signup`, `POST /login`, `GET /leads/by-token/{token}` 네 엔드포인트에만 존재하고, 이들의 역할은 전부 "이 이메일(+비번/토큰)을 가진 사람의 `profile_id`가 무엇인지 알려주는 것"으로 한정된다.

## 2. 전체 흐름

```
온보딩 → 분석 완료 (기존과 동일, 무인증, profile_id로 접근)
  → 큐레이션 화면 진입 시 이메일 입력 요구 (이메일 게이트)
    → POST /leads {profile_id, email} → Account(role=lead) 생성/재사용, profiles.account_id 연결
    → 매직링크 이메일 "발송" (MockEmailAdapter, 실제 전송 없음)
    → 큐레이션 재조회 시 "잠긴 미리보기" 노출 (컬러/아이템 내용은 숨김, locked=true)
  → "결제하기" 클릭 → 회원가입 폼(이메일 재사용 권장, 비밀번호 입력)
    → POST /signup {email, password} → 기존 리드 Account를 role=member로 전환
    → POST /profiles/{id}/payment → MockPaymentAdapter 항상 성공 → Payment(status=success)
    → 큐레이션 재조회 시 잠금 해제, 전체 노출
```

**재방문** (다른 기기 등): 이메일 매직링크 클릭(`GET /leads/by-token/{token}`) 또는 이메일+비밀번호 로그인(`POST /login`) → 둘 다 `profile_id`를 반환 → 프론트가 기존 `/onboarding/[id]` 페이지로 리다이렉트. 별도 마이페이지 화면은 만들지 않는다.

**이메일 게이트 범위**: 온보딩/분석 조회(`GET /profiles/{id}`, `GET /profiles/{id}/analysis`)는 지금처럼 계속 무인증 접근 가능 — PRD의 "부족한 오행 요소, 간단한 한 줄 요약까지는 무료 미리보기"와 이미 일치한다. 이메일 게이트는 **큐레이션(`GET /profiles/{id}/curation`)에만** 건다.

## 3. 스키마

### `accounts` (신규)

| 컬럼 | 타입 | 제약 |
|---|---|---|
| id | UUID (PK) | server 생성 |
| email | VARCHAR | not null, unique |
| role | VARCHAR (enum: lead/member) | not null, default 'lead' |
| password_hash | VARCHAR | nullable (리드는 없음) |
| access_token | VARCHAR | nullable, unique — 매직링크·로그인 세션 공용, 재발급 시 덮어써서 이전 토큰 자동 무효화 |
| token_created_at | TIMESTAMPTZ | nullable |
| converted_to_member_at | TIMESTAMPTZ | nullable — 리드→회원 전환 시각 (Phase 3 퍼널 추적용, PRD 5.6) |
| created_at | TIMESTAMPTZ | not null, default now() |

### `payments` (신규)

| 컬럼 | 타입 | 제약 |
|---|---|---|
| id | UUID (PK) | server 생성 |
| account_id | UUID (FK → accounts.id) | not null |
| profile_id | UUID (FK → profiles.id) | not null |
| amount | INTEGER | not null — Phase 1은 9900(원) 하드코딩. 가격 정책은 PRD상 TBD, 나중에 설정값으로 분리 |
| status | VARCHAR (enum: pending/success/failed) | not null |
| paid_at | TIMESTAMPTZ | nullable |
| created_at | TIMESTAMPTZ | not null, default now() |

### `profiles` 테이블 변경

- `account_id` 컬럼 추가: UUID (FK → accounts.id), nullable, unique (프로필 1개당 계정 1개)

## 4. 어댑터

- **EmailAdapter 인터페이스 + MockEmailAdapter**: `send_magic_link(email, token) -> None`. Mock은 실제 전송 없이 로그만 남기고, 개발 편의를 위해 `POST /leads` 응답에 `magic_link_url`을 그대로 포함한다 (실제 이메일 벤더 연동 시 이 필드는 응답에서 제거하고 어댑터만 교체).
- **PaymentAdapter 인터페이스 + MockPaymentAdapter**: `charge(amount) -> bool`. Mock은 항상 `True`(성공) 반환. 실패 케이스는 백엔드 단위 테스트에서 어댑터를 직접 실패하도록 스텁해서 커버.

## 5. API

- `POST /leads` — `{profile_id, email}` → 같은 이메일이 이미 있으면 기존 Account 재사용(멱등), 없으면 `role=lead`로 생성. 토큰 재발급, `profile.account_id` 연결(이미 다른 account에 연결돼 있었으면 새 account로 재바인딩 — 드문 edge case라 과설계하지 않음). 응답에 `magic_link_url` 포함
- `GET /leads/by-token/{token}` — 토큰으로 Account 조회 → 연결된 `profile_id` 반환. 토큰 없으면 404
- `POST /signup` — `{email, password}` → 같은 이메일의 Account가 있으면(리드) `role=member`로 전환 + `password_hash` 설정 + `converted_to_member_at` 기록, 없으면 새로 `role=member`로 생성. 이미 `role=member`인 이메일로 재요청하면 409("이미 가입된 이메일입니다")
- `POST /login` — `{email, password}` → bcrypt 검증 → 새 토큰 발급 → 연결된 `profile_id` 반환. 실패 시 401
- `POST /profiles/{id}/payment` — profile에 연결된 Account가 없으면 404("이메일을 먼저 입력해주세요"), `role`이 `member`가 아니면 403("회원가입이 필요합니다"), 맞으면 `PaymentAdapter.charge()` 호출 → `Payment(status=success)` 생성
- `GET /profiles/{id}/curation` 수정 — `profile.account_id` 없으면 403("이메일을 먼저 입력해주세요"). 있지만 해당 account에 성공한 Payment가 없으면 `{locked: true, missing_elements: [...], colors: [], items: []}` 반환(부족 오행 개수/목록은 계속 무료로 보여주되 내용은 숨김). 결제 완료면 `{locked: false, missing_elements, colors, items}` 전체 노출

## 6. 프론트

- `/onboarding/[id]` (기존 확장): 큐레이션 조회가 403이면 이메일 입력 폼, `locked:true`면 "결제하고 잠금 해제" 섹션(비밀번호 입력 + 결제하기 버튼 — 누르면 회원가입→결제 순차 호출), 결제 완료 후 재조회 시 잠금 해제된 화면
- `/magic-link/[token]` (신규): 로드 시 토큰으로 `profile_id` 조회해서 즉시 리다이렉트
- `/login` (신규, 최소 구성): 이메일+비밀번호 → `profile_id` 받아 리다이렉트

에러 처리는 기존 `handleResponse`(문자열/배열 detail 모두 처리)를 그대로 재사용.

## 7. 보안

- 비밀번호는 `bcrypt`로 해싱, 평문 저장 금지
- 매직링크 토큰은 `secrets.token_urlsafe()`로 발급 (온보딩 설계 때 이미 결정된 방식과 동일)
- 개발 편의상 `magic_link_url`을 API 응답에 노출하는 것은 Phase 1 한정 — 실제 이메일 벤더 연동 시 반드시 제거해야 함 (액션 아이템)

## 8. 테스트

- 백엔드: 모델 → 어댑터(Mock 성공/실패 케이스) → API 통합 테스트. 커버할 시나리오: 리드 생성/재사용, 회원 전환(리드→멤버), 이미 가입된 이메일 재가입 거부, 로그인 성공/실패, 결제(회원 아니면 거부 → 회원 전환 후 성공), 큐레이션 3단계 게이팅(계정 없음 403 / 미결제 잠금 / 결제 완료 전체 노출)
- 프론트: 테스트 프레임워크 없음(기존 결정 유지) — 빌드 클린 + 실제 브라우저로 전체 플로우(이메일 입력 → 회원가입 → 결제 → 잠금 해제, 매직링크 클릭 리다이렉트, 로그인 리다이렉트) 확인

## 9. 다음 단계

이 스펙은 "결제" 기능 전체를 다룬다. 구현은 writing-plans로 세부 태스크 계획을 만든 뒤 subagent-driven-development로 진행한다(스코프가 커서 온보딩 때와 같은 방식 채택).
