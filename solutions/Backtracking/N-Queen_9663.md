# 백준 9663 👑 N-Queen 파이썬

## 느낀점
>
- 유명한 문제지만 처음 구현해보았다.
- 너무 어렵지만 배울 점 많은 문제다.
- 리스트, set 성능차이 조심하기

## 흐름

1. 퀸은 각 행에 정확히 하나씩 놓아야 하므로, 행을 0부터 N-1까지 순서대로 탐색
2. 각 행에서 열을 0~N-1까지 시도하며, 열/두 대각선 충돌 여부를 체크
3. 충돌이 없으면 해당 열과 대각선을 마킹하고 다음 행으로 재귀
4. N번째 행에 도달하면 유효한 배치이므로 카운트 증가
5. 재귀 복귀 시 마킹을 해제(백트래킹)

## 코드
```python
import sys
input = sys.stdin.readline
N = int(input())
visited = [False] * N
col_p = [False] * (2 * N)       # 행+열: 0 ~ 2N-2
col_m = [False] * (2 * N)       # 행-열: -(N-1) ~ N-1 → 오프셋 +N
answer = 0
def dfs(n):
    global answer
    if n == N:
        answer += 1
        return
    for cur in range(N):
        p = cur + n
        m = cur - n + N
        if not visited[cur] and not col_p[p] and not col_m[m]:
            visited[cur] = col_p[p] = col_m[m] = True
            dfs(n + 1)
            visited[cur] = col_p[p] = col_m[m] = False
dfs(0)
print(answer)
```

## 질문 & 실수 정리

### 새로 배운 것

#### 백트래킹에서 상태 표현 최적화
N-Queen처럼 "각 행에 하나씩" 놓는 제약이 있으면, 2D 배열 전체를 탐색할 필요 없이 행을 고정하고 열만 선택하는 1D 탐색으로 줄일 수 있다. 상태 공간을 줄이는 것이 백트래킹의 핵심.
- **핵심 원리**: 문제의 제약 조건을 활용해 탐색 차원을 줄인다
- **시간복잡도**: O(N!) (최악, 가지치기로 실제는 훨씬 적음)

#### 대각선 충돌 체크 기법
같은 `/` 대각선 위의 칸들은 `행+열` 값이 동일하고, 같은 `\` 대각선 위의 칸들은 `행-열` 값이 동일하다. 이 성질을 이용하면 O(1)에 대각선 충돌을 체크할 수 있다.
- **핵심 원리**: `행+열`, `행-열`을 인덱스로 사용하여 대각선을 식별
- **주의**: `행-열`은 음수가 될 수 있으므로 오프셋(+N)을 줘서 리스트 인덱스로 사용

#### set vs 리스트 성능 차이
파이썬에서 `set`의 `add`/`remove`/`in` 연산은 해싱 오버헤드가 있다. 인덱스 범위가 정해져 있을 때는 `bool` 리스트로 직접 인덱스 접근하는 것이 훨씬 빠르다.
- **핵심 원리**: 리스트 인덱스 접근은 O(1)이면서 상수 시간도 작다

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---|---|
| 2D visited + move 배열로 전체 탐색 | 행마다 하나씩 놓는 1D 백트래킹 |
| `abs(cur - n)`으로 대각선 체크 | `cur - n` 부호 유지해야 대각선 구분 가능 |
| 두 대각선을 같은 set에 저장 | `/`, `\` 대각선 별도 자료구조로 분리 |
| `visited[n]` (행 인덱스) 마킹 | `visited[cur]` (열 인덱스) 마킹 |
| `answer` 초기화 누락 | `answer = 0` 선언 필요 |
| base case에서 `return` 누락 | `answer += 1` 후 `return` 필수 |
| `set`으로 대각선 관리 → TLE | 리스트 인덱스 접근으로 최적화 |

## AI 코드 리뷰

### 개선할 점

1. **변수명 명확화**: `col_p`, `col_m` → `diag_plus`, `diag_minus`로 대각선 의미 전달. `n` → `row`, `cur` → `col`로 역할 명시.

## 수정된 코드
```python
import sys
input = sys.stdin.readline

N = int(input())
used_col = [False] * N
diag_plus = [False] * (2 * N)   # 행+열: 0 ~ 2N-2
diag_minus = [False] * (2 * N)  # 행-열+N: 1 ~ 2N-1
answer = 0

def dfs(row):
    global answer
    if row == N:
        answer += 1
        return
    for col in range(N):
        dp = col + row
        dm = col - row + N
        if not used_col[col] and not diag_plus[dp] and not diag_minus[dm]:
            used_col[col] = diag_plus[dp] = diag_minus[dm] = True
            dfs(row + 1)
            used_col[col] = diag_plus[dp] = diag_minus[dm] = False

dfs(0)
print(answer)
```
