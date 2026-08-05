# Algorithm Solution Workflow

이 저장소에서 사용자가 문제 풀이용 Markdown 표 행을 보내면 아래 절차를 따른다.

예시:

```md
| 구현 | Lv.1 | <a href="https://school.programmers.co.kr/learn/courses/30/lessons/468371?language=python3" target="_blank">🚦 노란불 신호등</a> | Prog | <a href="./solutions/Implementation/노란불신호등_468371.md">풀&#8288;이</a> | 2026&#8209;07&#8209;23 |  |  |
```

## 필수 작업 순서

1. 다른 파일을 확인하거나 수정하기 전에 저장소 루트에서 `git pull --rebase origin main`을 먼저 실행한다.
2. 표 행의 풀이 링크에서 저장 경로와 파일명을 추출한다.
   - 저장소 루트: `/Users/woochan0408/Desktop/algorithm-solutions`
   - 다운로드 폴더: `/Users/woochan0408/Downloads`
3. 다운로드 폴더에서 풀이 링크의 파일명과 정확히 일치하는 `.md` 파일을 찾는다.
4. 대상 디렉터리가 없으면 생성하고, 다운로드한 파일을 표에 적힌 저장소 경로로 이동한다.
   - 기존 대상 파일을 확인 없이 덮어쓰지 않는다.
   - 정확히 일치하는 파일이 없거나 후보가 여러 개라 판단하기 어려우면 임의 선택하지 않고 사용자에게 알린다.
5. 사용자가 보낸 표 행을 `README.md`의 `## 📝 문제 풀이 목록` 표에서 헤더와 정렬 행 바로 다음, 즉 데이터 행의 맨 위에 삽입한다.
   - 행의 링크, 이모지, 날짜, HTML 엔티티를 임의로 바꾸지 않는다.
   - 같은 문제 행이 이미 있으면 중복 추가하지 않는다.
6. 다음 항목을 검증한다.
   - 풀이 파일이 표의 링크 경로에 존재한다.
   - 새 행이 문제 풀이 목록의 첫 번째 데이터 행이다.
   - `git diff --check`가 통과한다.
   - `git status --short`로 의도한 파일만 변경되었는지 확인한다.

## 작업 완료 후 명령어

- 커밋이나 푸시는 사용자가 명시적으로 요청한 경우에만 직접 실행한다.
- 직접 실행하지 않은 경우, 답변 마지막에 사용자가 실행할 수 있는 한 줄 명령어를 반드시 제공한다.
- 모든 저장소 및 파일 위치는 절대경로로 적는다.
- `git add`에는 `README.md`와 새 풀이 Markdown 파일 두 개를 이어서 명시한다.
- 형식:

```bash
git -C "/Users/woochan0408/Desktop/algorithm-solutions" add "/Users/woochan0408/Desktop/algorithm-solutions/README.md" "/Users/woochan0408/Desktop/algorithm-solutions/<풀이 파일 경로>" && git -C "/Users/woochan0408/Desktop/algorithm-solutions" commit -m "docs: <문제명> 풀이 추가" && git -C "/Users/woochan0408/Desktop/algorithm-solutions" push origin main
```

## 푸시 요청을 받은 경우

1. 변경 범위와 현재 브랜치 상태를 확인한다.
2. 원격 변경이 있으면 로컬 변경을 보존하면서 `git pull --rebase origin main`으로 정리한다.
3. 의도한 파일만 스테이징하고 커밋한다.
4. `git push origin main`을 실행한다.
5. 마지막으로 로컬 `main`과 `origin/main`이 동기화되었는지 확인한다.
