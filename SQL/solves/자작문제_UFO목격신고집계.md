# 자작문제 🛸 UFO 목격 신고 집계

## 문제 요약
> 각 UFO별로 목격 신고한 시민 수(중복 제거)와 사진 첨부된 신고 건수를 구하는 문제

### 문제링크
https://velog.io/@tesabel/SQL-자작문제-UFO-목격-신고-집계

## 느낀점
>
- DISTINCT 활용 문제
- 재밌게 잘 풀었다.

## 흐름
1. REPORT 테이블에서 UFO_ID별 고유 시민 수 집계 (COUNT DISTINCT)
2. REPORT 테이블에서 UFO_ID별 사진 첨부 건수 집계 (COUNT on PHOTO_URL)
3. UFO 테이블에 LEFT JOIN으로 결합하여 SHAPE 정보 포함
4. COALESCE로 NULL 방어 후 UFO_ID 오름차순 정렬

## 코드
```sql
WITH C_COUNT AS (
    SELECT UFO_ID, COUNT(DISTINCT CITIZEN_ID) AS CITIZEN_COUNT
    FROM REPORT
    GROUP BY UFO_ID
),
P_COUNT AS (
    SELECT UFO_ID, COUNT(PHOTO_URL) AS PHOTO_COUNT
    FROM REPORT
    GROUP BY UFO_ID
)
SELECT U.UFO_ID, U.SHAPE,
       COALESCE(C.CITIZEN_COUNT, 0) AS CITIZEN_COUNT,
       COALESCE(P.PHOTO_COUNT, 0) AS PHOTO_COUNT
FROM UFO U
LEFT JOIN C_COUNT C ON C.UFO_ID = U.UFO_ID
LEFT JOIN P_COUNT P ON U.UFO_ID = P.UFO_ID
ORDER BY UFO_ID
```

## 질문 & 실수 정리

### 새로 배운 것

#### COUNT(컬럼명) vs COUNT(*)
`COUNT(*)`는 NULL을 포함한 전체 행 수를 세지만, `COUNT(컬럼명)`은 해당 컬럼이 NULL이 아닌 행만 센다. 따라서 "사진이 첨부된 건수"처럼 NULL 여부로 필터링이 필요한 경우, `WHERE ... IS NOT NULL` 없이도 `COUNT(PHOTO_URL)`만으로 해결할 수 있다.
- **핵심 원리**: COUNT에 컬럼명을 넣으면 NULL 자동 제외 → 별도 WHERE 절 불필요

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---------|-----------|
| `COUNT(DISTINCT CITIZEN_ID)` — 사진을 첨부한 **시민 수** | `COUNT(PHOTO_URL)` — 사진이 첨부된 **신고 건수** |

"시민 수"와 "건수"는 다른 개념. 같은 시민이 같은 UFO에 사진 첨부 신고를 여러 번 하면 건수는 늘어나지만 DISTINCT 시민 수는 그대로.

## AI 코드 리뷰

### 개선할 점

1. **CTE 2개를 1개로 통합 가능**: C_COUNT와 P_COUNT 모두 REPORT를 GROUP BY UFO_ID로 집계하므로, 한 번의 집계로 두 값을 동시에 구할 수 있다. CTE를 분리하면 REPORT 테이블을 두 번 스캔하게 된다.

## 수정된 코드
```sql
SELECT U.UFO_ID, U.SHAPE,
       COALESCE(COUNT(DISTINCT R.CITIZEN_ID), 0) AS CITIZEN_COUNT,
       COALESCE(COUNT(R.PHOTO_URL), 0) AS PHOTO_COUNT
FROM UFO U
LEFT JOIN REPORT R ON U.UFO_ID = R.UFO_ID
GROUP BY U.UFO_ID, U.SHAPE
ORDER BY U.UFO_ID
```
