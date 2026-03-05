# Claude자작 🎮 버그 헌터

## 문제 요약
> 온라인 게임 아이템 획득 로그(`ITEM_LOG`)에서, **같은 유저가 같은 아이템을 2번 이상 획득한 경우**(버그 의심 건)를 찾아 해당 유저ID, 아이템명, 획득 횟수를 출력한다. 획득 횟수 내림차순 정렬.

### 테이블 구조

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| LOG_ID | INT | 로그 고유 ID (PK) |
| USER_ID | INT | 유저 ID |
| ITEM_NAME | VARCHAR | 아이템 이름 |
| GRADE | CHAR(1) | 등급 (S, A, B) |
| ACQUIRED_AT | DATETIME | 획득 시각 |

### 예시 데이터

| LOG_ID | USER_ID | ITEM_NAME | GRADE | ACQUIRED_AT |
|--------|---------|-----------|-------|-------------|
| 1 | 1001 | 불꽃의 검 | S | 2025-03-01 10:00:00 |
| 2 | 1001 | 불꽃의 검 | S | 2025-03-01 10:00:01 |
| 3 | 1002 | 얼음 방패 | A | 2025-03-01 11:00:00 |
| 4 | 1003 | 불꽃의 검 | S | 2025-03-02 09:00:00 |
| 5 | 1001 | 바람의 망토 | A | 2025-03-02 14:00:00 |
| 6 | 1002 | 불꽃의 검 | S | 2025-03-03 08:00:00 |
| 7 | 1002 | 얼음 방패 | A | 2025-03-03 08:30:00 |
| 8 | 1004 | 바람의 망토 | A | 2025-03-03 12:00:00 |
| 9 | 1001 | 불꽃의 검 | S | 2025-03-03 15:00:00 |
| 10 | 1005 | 대지의 반지 | B | 2025-03-04 10:00:00 |

### 기대 출력

| USER_ID | ITEM_NAME | CNT |
|---------|-----------|-----|
| 1001 | 불꽃의 검 | 3 |
| 1002 | 얼음 방패 | 2 |

## 느낀점
>
- 

## 흐름
1. CTE로 (USER_ID, ITEM_NAME) 그룹핑하여 COUNT >= 2인 조합 추출
2. 원본 테이블과 LEFT JOIN 후 매칭되는 행만 필터
3. DISTINCT로 중복 제거 후 CNT 내림차순 정렬

## 코드
```sql
WITH L AS (
    SELECT USER_ID, ITEM_NAME, COUNT(*) AS CNT
    FROM ITEM_LOG
    GROUP BY USER_ID, ITEM_NAME
    HAVING CNT >= 2
)
SELECT DISTINCT I.USER_ID, I.ITEM_NAME, L.CNT
FROM ITEM_LOG I
LEFT JOIN L ON L.USER_ID = I.USER_ID AND L.ITEM_NAME = I.ITEM_NAME
WHERE L.CNT IS NOT NULL
ORDER BY CNT DESC
```

## 질문 & 실수 정리

### 새로 배운 것

#### LEFT JOIN + WHERE IS NOT NULL = INNER JOIN
LEFT JOIN 후 `WHERE 오른쪽테이블.컬럼 IS NOT NULL`로 필터하면, NULL인 행(=매칭 안 된 행)을 전부 제거하므로 결과적으로 INNER JOIN과 동일하다. 의도가 "매칭되는 것만"이라면 처음부터 INNER JOIN을 쓰는 게 의미가 명확하다.
- **핵심 원리**: LEFT JOIN의 존재 이유는 매칭 안 되는 행도 살리기 위함. WHERE로 그걸 다시 제거하면 LEFT의 의미가 사라짐.

#### 불필요한 CTE + JOIN 패턴 인식
GROUP BY + HAVING으로 이미 원하는 결과가 완성되는 경우, 원본 테이블로 다시 JOIN할 필요가 없다. CTE 결과 자체가 곧 최종 결과일 수 있는지 항상 먼저 확인해야 한다.
- **핵심 원리**: "이 중간 결과에서 추가로 필요한 컬럼이 있는가?"를 자문. 없으면 JOIN 없이 바로 출력.

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---------|-----------|
| `ITEM_NAME COUNT(*)` — 쉼표 누락 | `ITEM_NAME, COUNT(*)` |
| JOIN 조건에 `USER_ID`만 사용 → 다른 아이템끼리도 매칭됨 | `ON L.USER_ID = I.USER_ID AND L.ITEM_NAME = I.ITEM_NAME` 두 컬럼 모두 매칭 |

## AI 코드 리뷰

### 개선할 점

1. **CTE + JOIN이 불필요**: CTE 안의 SELECT 결과가 이미 USER_ID, ITEM_NAME, CNT를 다 갖고 있다. 원본 테이블로 다시 JOIN해서 DISTINCT를 걸 이유가 없음.

2. **LEFT JOIN → INNER JOIN**: `WHERE L.CNT IS NOT NULL`로 NULL을 제거하고 있으므로 LEFT JOIN 대신 INNER JOIN이 의도에 맞음. 다만 개선 코드에서는 JOIN 자체가 사라지므로 해당 없음.

3. **DISTINCT 불필요**: GROUP BY가 이미 유니크한 조합을 만들기 때문에 DISTINCT를 추가할 필요 없음.

## 수정된 코드
```sql
SELECT USER_ID, ITEM_NAME, COUNT(*) AS CNT
FROM ITEM_LOG
GROUP BY USER_ID, ITEM_NAME
HAVING CNT >= 2
ORDER BY CNT DESC
```
