# 출근길 AI 브리핑 — 매일 실행 루틴

너는 매일 아침 팟캐스트 대본 한 편을 생성해 개인 GitHub 저장소에 push 한다.

## 순서
1. `state.json`을 읽는다. `date.today()`(KST)를 `today`로 둔다.
2. `python -m tools.state state.json <today>` 로 상태를 갱신하고, 갱신된 streak/episode 값을 확인한다.
3. 웹 리서치: 최근 24~48시간 **AI 동향**(새 모델·도구·논문·기업 발표)을 3건, 그리고 **시스템운영 관점**(DB/Oracle·보안 취약점·클라우드/인프라·IT운영) 1건을 선별한다. 신뢰할 만한 출처를 교차 확인한다.
4. `routine/script-template.md` 포맷 그대로 `scripts/<today>.md` 대본을 작성한다.
   - 프론트매터 date/streak/episode를 2번 값으로 채운다.
   - "(지난 회 요약)"에는 `scripts/`의 직전 회차 핵심을 1~2문장으로 넣는다.
   - 낭독 본문 700~900자.
   - **보안 절대 규칙**: 회사명·시스템명·고객·내부 수치·장애 상세를 절대 넣지 않는다. `config.yaml`의 `banned_terms` 단어를 쓰지 않는다.
5. `python -m tools.validate_script scripts/<today>.md` 로 자체 검증한다. 실패하면 대본을 고쳐 통과시킨다.
6. `scripts/<today>.md`와 `state.json`을 commit 하고 push 한다.

## 실패 폴백
- 리서치가 부실하면 "개념·트렌드 해설" 회차로 대체하되 분량·포맷은 유지한다.
- push 실패 시 재시도. 그래도 실패면 다음 실행에서 이어서 발행한다.
