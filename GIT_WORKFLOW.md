# Git 형상관리 가이드 (오행핏)

혼자 진행하는 프로젝트 + Claude Code로 기능 단위 개발하는 흐름에 맞춘 가벼운 규칙.

## 브랜치 전략

- `main`: 항상 실행 가능한 상태 유지 (깨진 상태로 두지 않기)
- 기능 개발은 브랜치 분리: `feature/<phase>-<기능명>`
  - 예: `feature/phase1-onboarding`, `feature/phase1-analysis`, `feature/phase2-material-curation`
- 급한 버그 수정: `fix/<설명>`
- 기능 단위(온보딩/분석/큐레이션/결제/공유 등) 시작할 때마다 새 브랜치를 파고, 해당 기능의 백엔드+프론트+연동테스트까지 끝나면 `main`으로 머지

## 커밋 컨벤션

- [Conventional Commits](https://www.conventionalcommits.org/) 스타일 사용
  - `feat: 온보딩 입력 폼 구현`
  - `fix: 오행 계산 API 응답 오류 수정`
  - `refactor: 사주 분석 어댑터 인터페이스 정리`
  - `docs: PRD/CLAUDE.md 업데이트`
  - `chore: docker-compose 설정 추가`
  - `test: 결제 목업 플로우 테스트 추가`
- 커밋 단위는 의미 있는 작업 단위로 (한 기능을 통째로 몰아서 커밋 X, 그렇다고 너무 잘게 쪼개지도 않기)
- 백엔드 구현 → 프론트 구현 → 연동 테스트, 이 세 단계를 각각 커밋으로 나눠도 좋음

## 머지 전략

- 리뷰어 없는 1인 프로젝트이므로 PR 없이 로컬에서 브랜치 완성 후 `main`으로 머지
- 머지는 **squash merge** 권장 (기능 브랜치의 잡다한 커밋을 하나로 정리해서 `main` 히스토리를 깔끔하게 유지)
- 머지 전 체크: 연동 테스트 통과 여부, `CLAUDE.md`/`ohang_fit_prd.md` 반영 여부
- **머지는 반드시 사용자 승인 후 진행.** Claude Code는 머지 준비가 끝나면 먼저 사용자에게 알리고 승인받은 다음에 머지할 것 (임의로 먼저 머지하지 않기)

## Commit 규칙

- **Commit은 사용자가 직접 진행함. Claude Code는 commit하지 않는다.**
- 커밋할 시점(의미 있는 작업 단위가 끝났을 때)이 되면, 사용자가 그대로 실행할 수 있도록 어떤 명령어로 커밋하면 되는지 알려줄 것
  - 예: `git add .` + `git commit -m "feat: 온보딩 입력 폼 구현"` 처럼 add/commit 명령어와 커밋 메시지(위 커밋 컨벤션 기준)까지 함께 안내

## Push 규칙

- **Push도 사용자가 직접 진행함. Claude Code는 push하지 않는다.**
- 커밋이 끝나면, 사용자가 그대로 실행할 수 있도록 어떤 명령어로 push하면 되는지 알려줄 것
  - 예: `git push origin feature/phase1-onboarding`, `git push origin main` 등 브랜치명 포함해서 정확한 명령어 안내

## 태깅

- Phase 완료 시점마다 태그: `v0.1.0-phase1`, `v0.2.0-phase2`, `v0.3.0-phase3`
- 정식 시맨틱 버저닝은 서비스 출시 이후부터 적용 고려

## .gitignore 필수 항목

```
# frontend
node_modules/
.next/

# backend
__pycache__/
*.pyc
.venv/

# 환경변수/시크릿
.env
.env.local
.env.*.local

# OS/에디터
.DS_Store
.vscode/

# docker
docker-compose.override.yml
```

## 환경변수/시크릿 관리

- 실제 값이 든 `.env`는 **절대 커밋하지 않음**
- 대신 `.env.example` 파일에 필요한 키 이름만 공유 (사주 API 키, PG 키, DB 접속 정보 등)
- 사주 API / PG / 커머스 벤더가 정해지는 대로 `.env.example`에 필요한 키 추가

## Claude Code 작업 규칙

- 새 기능 작업 시작 전: `feature/<phase>-<기능명>` 브랜치 생성
- 의미 있는 작업 단위가 끝날 때마다: 직접 commit하지 말고 사용자에게 commit 명령어(메시지 포함) 안내
- 기능의 백엔드 → 프론트 → 연동 테스트가 모두 끝나면: 사용자에게 머지해도 되는지 확인받고, 승인 후에 `main`에 머지
- 머지 시점에 `CLAUDE.md`의 "진행 상황" 체크리스트도 함께 업데이트
- commit과 push는 직접 하지 말고, 각 시점마다 사용자가 실행할 명령어만 안내할 것