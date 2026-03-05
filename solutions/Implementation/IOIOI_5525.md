# 백준 5525 🔤 IOIOI 파이썬

## 느낀점
>
- 다 풀고 마지막에 실수를 했다.
(머리를 다 썼다..)
- 문제 자체는 쉬웠다.

## 흐름

1. 문자열을 처음부터 순회하면서 `I`로 시작하는 교대 패턴(IOIOI...)을 찾는다
2. 교대 패턴의 길이 `j`를 측정한 뒤 `result` 리스트에 저장한다
3. P_N의 길이 `t = 2N+1`과 각 패턴 길이 `c`를 비교하여, `c >= t`이면 `(c - t) // 2 + 1`개의 P_N이 포함된다

## 코드
```python
import sys
import math

input = sys.stdin.readline
N = int(input())
M = int(input())
arr = input().strip()
dic = {0 : 'I', 1 : 'O'}
result = []

i = 0
while i < M:
    j = 1
    if(arr[i] == 'I'):
        while True:
            cur = i + j
            if(cur < M and arr[cur] != arr[cur-1]):
                j += 1
            else:
                break
        result.append(j)
    i += j

t = 2*N+1
ans = 0
for c in result:
    if(t <= c):
        ans += (c - t)//2 + 1
print(ans)
```

## 질문 & 실수 정리

### 새로 배운 것

#### 교대 패턴 그룹화 후 개수 계산
연속된 교대 문자열(IOIOI...)을 하나의 그룹으로 묶고, 그 그룹 길이 `c` 안에 길이 `t`짜리 부분 패턴이 몇 개 들어가는지를 수식으로 바로 구할 수 있다. 슬라이딩 윈도우처럼 2칸씩 이동하므로 `(c - t) // 2 + 1`이 된다.
- **핵심 원리**: 그룹 길이에서 목표 길이를 빼고 2로 나눈 뒤 1을 더하면 포함 횟수

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---|---|
| `if(t < c)` — 길이가 정확히 같을 때 누락 | `if(t <= c)` — 같을 때도 1개 포함 |

## AI 코드 리뷰

### 개선할 점

1. **미사용 코드 제거**: `dic`, `math` import는 실제로 사용되지 않거나 대체 가능하므로 제거
2. **result 리스트 제거**: 패턴 길이를 리스트에 저장할 필요 없이 발견 즉시 `ans`에 누적하면 메모리 절약
3. **정수 나눗셈 사용**: `math.ceil((c - t)/2)`는 `c`와 `t`가 모두 홀수여서 차이가 항상 짝수이므로 `(c - t) // 2`로 충분

## 수정된 코드
```python
import sys

input = sys.stdin.readline
N = int(input())
M = int(input())
S = input().strip()

target_len = 2 * N + 1
ans = 0
i = 0

while i < M:
    if S[i] == 'I':
        # 교대 패턴 길이 측정
        j = 1
        while i + j < M and S[i + j] != S[i + j - 1]:
            j += 1
        # P_N 포함 횟수 누적
        if j >= target_len:
            ans += (j - target_len) // 2 + 1
        i += j
    else:
        i += 1

print(ans)
```
