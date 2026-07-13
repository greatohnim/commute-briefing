# 출근길 AI 브리핑 팟캐스트

매일 아침 AI 중심 기술 브리핑을 음성으로 만들어 개인 팟캐스트 피드로 발행하고, 아이폰에서 CarPlay로 듣는 프로젝트입니다.

## 구성 (전액 무료 스택)
- **두뇌**: 회사 Claude Code 예약 루틴(schedule) → 매일 06:00 KST에 대본(.md) 생성 → 이 저장소에 push
- **손발**: GitHub Actions → edge-tts로 음성 변환 → RSS 피드 갱신 → GitHub Pages로 발행
- **청취**: 아이폰 Apple 팟캐스트 앱 + CarPlay ("시리야, 최신 에피소드 재생")

비용이 드는 구성 요소는 없습니다. GitHub 개인 계정(무료), GitHub Actions(공개 저장소 무료), GitHub Pages(무료), edge-tts(무료 TTS)만 사용합니다.

---

## 설정 절차 (비개발자용, 순서대로 진행)

### 1단계. 개인 GitHub 계정 준비 및 저장소 생성
1. 개인 GitHub 계정이 없다면 https://github.com 에서 무료로 가입합니다. (회사 계정이 아닌 **개인** 계정이어야 합니다.)
2. 로그인 후 우측 상단 `+` → **New repository** 클릭.
3. Repository name에 `commute-briefing` 입력, **Public**으로 설정(무료 Pages/Actions 사용을 위해 공개 저장소 권장), README/gitignore 등 초기 파일은 추가하지 않고 **빈 저장소**로 생성합니다.

### 2단계. 로컬 저장소를 방금 만든 GitHub 저장소에 연결
터미널(또는 Git Bash)에서 이 프로젝트 폴더(`commute-briefing`)로 이동한 뒤:

```bash
git remote add origin https://github.com/<본인계정>/commute-briefing.git
git branch -M main
git push -u origin main
```

`<본인계정>`은 실제 본인의 GitHub 아이디로 바꿔서 입력합니다. push 시 GitHub 로그인 인증을 요구하면 안내에 따라 진행합니다.

### 3단계. `config.yaml`의 `base_url`을 실제 주소로 교체
현재 `config.yaml`의 `base_url` 값은 아래처럼 `CHANGEME` 자리표시자(placeholder)로 되어 있습니다.

```yaml
base_url: "https://CHANGEME.github.io/commute-briefing"
```

이 값을 본인 계정 기준 실제 주소로 바꿉니다.

```yaml
base_url: "https://<본인계정>.github.io/commute-briefing"
```

수정 후 커밋·푸시합니다.

```bash
git add config.yaml
git commit -m "config: base_url 실제 계정 반영"
git push
```

### 4단계. GitHub Pages 활성화
1. GitHub 저장소 페이지 → **Settings** → 좌측 메뉴 **Pages**.
2. **Source**를 `Deploy from a branch`로 선택.
3. **Branch**는 `main`, 폴더는 `/docs`로 선택 → **Save**.
4. 1~2분 뒤 `https://<본인계정>.github.io/commute-briefing/` 접속이 되는지 확인합니다.

### 5단계. 두뇌(예약 루틴) 등록 — 사용자 직접 수행
> 이 단계는 Claude Code의 **schedule** 기능으로 사용자가 직접 등록해야 합니다(개인 GitHub 계정·PAT이 필요하므로 자동화 불가).

1. `routine/briefing-routine.md`의 내용을 예약 프롬프트로 등록합니다.
2. 실행 주기: **매일 06:00 KST**.
3. 작업 디렉터리: 이 저장소(`commute-briefing`) 로컬 경로.
4. push 인증용으로 **최소 권한 PAT**(Personal Access Token, `contents: write` 권한만)을 발급해 자격증명으로 등록합니다. PAT은 저장소 코드에 절대 커밋하지 않습니다.

### 6단계. 첫 회차 수동 발행 트리거
루틴을 1회 수동으로 실행하거나, 직접 `scripts/<오늘날짜>.md`를 템플릿(`routine/script-template.md`) 형식대로 작성해 push 합니다. 이후 GitHub 저장소의 **Actions** 탭에서 `build-and-publish` 워크플로가 성공(초록 체크)했는지 확인합니다.

### 7단계. 피드 접근 확인
아래 URL이 정상 응답하는지 확인합니다.

```
https://<본인계정>.github.io/commute-briefing/feed.xml
```

- HTTP 상태 200, Content-Type이 XML 계열이어야 합니다.
- 브라우저나 `curl -sI <위 주소>`로 확인 가능합니다.

### 8단계. 아이폰에서 구독 + CarPlay 확인
1. 아이폰 **Apple 팟캐스트** 앱 실행 → **라이브러리** 탭.
2. 우측 상단 `…` → **"URL로 팟캐스트 추가"** 선택.
3. `https://<본인계정>.github.io/commute-briefing/feed.xml` 주소 입력 후 추가.
4. 해당 팟캐스트 상세 화면에서 **자동 다운로드**를 켭니다(ON).
5. 차량에 아이폰을 연결해 CarPlay 진입 후 **"시리야, 최신 에피소드 재생"** 이라고 말해 hands-free로 재생되는지 확인합니다.

---

## 보안 주의사항
이 팟캐스트 피드는 **공개(public)** 로 발행됩니다. 대본에는 회사명, 시스템명, 고객 정보, 내부 수치, 장애 상세 등을 **절대 포함하지 않습니다**. `config.yaml`의 `script.banned_terms`에 등록된 금지어가 포함된 대본은 `tools/validate_script`가 검증에서 실패시켜 발행을 막습니다. 예약 루틴 실행 시에도 이 규칙은 그대로 적용됩니다.

## 로컬 개발 / 테스트
```bash
.venv/Scripts/python.exe -m pytest -v
```

## 폴더 구조 참고
- `routine/` — 매일 실행되는 예약 루틴 프롬프트 및 대본 템플릿
- `scripts/` — 날짜별 생성된 대본(.md)
- `docs/` — GitHub Pages로 발행되는 정적 파일(피드, 오디오, 커버 이미지)
- `tools/` — 상태 관리·대본 검증 스크립트
- `.github/workflows/` — TTS 변환·RSS 갱신·배포 자동화(Actions)
