# Velog 자작문제 🍷 SQL AI 자작문제 : 와이너리 빈티지 경매 투자 등급 분석

## 문제 요약
> 와인별 역대 최고 낙찰가와 최근 낙찰가의 비율로 투자 등급을 분류하고, PRIME 등급 와인을 2개 이상 보유한 와이너리의 모든 와인을 와이너리 내 순위와 함께 출력하라.
#### 문제링크
https://velog.io/@tesabel/SQL-AI-자작문제-와이너리-빈티지-경매-투자-등급-분석-91vbwmw0

## 느낀점
>
- 더럽게 어려웠다.
- 덕분에 많이 배웠다.
- 좋아하는 주제로 문제를 푸니 2시간 엉덩이 붙이기 가능했다.

## 흐름
1. `LATEST` CTE: 와인별 가장 최근 경매의 낙찰가 추출 — `(wine_id, auction_date)` 튜플 비교로 정확한 매칭
2. `HIGHEST` CTE: 와인별 역대 최고 낙찰가 추출 — `MAX(hammer_price)`
3. `I` CTE: 두 CTE를 JOIN하여 price_ratio 계산 + CASE WHEN으로 투자 등급 분류
4. `P_WINNER` CTE: wines, wineries 테이블과 JOIN하여 와이너리 정보 결합
5. `C` CTE: PRIME 등급 와인 2개 이상인 와이너리 필터링
6. `T` CTE: 필터링된 와이너리의 모든 와인에 `ROW_NUMBER() OVER(PARTITION BY winery_id)` 로 순위 부여
7. 최종 SELECT: `winery_name ASC, price_rank ASC` 정렬

## 코드
```sql
WITH LATEST AS (
    SELECT wine_id, hammer_price AS latest_price
    FROM auctions
    WHERE (wine_id, auction_date) IN (
        SELECT wine_id, MAX(auction_date)
        FROM auctions
        GROUP BY wine_id
    )
),HIGHEST AS (
    SELECT wine_id, MAX(hammer_price) AS all_time_high
    FROM auctions
    GROUP BY wine_id
), I AS (
    SELECT L.wine_id, H.all_time_high, L.latest_price, ROUND((L.latest_price / H.all_time_high)*100, 2) AS price_ratio,
    CASE
        WHEN ROUND((L.latest_price / H.all_time_high)*100, 2) >= 90 THEN 'PRIME'
        WHEN ROUND((L.latest_price / H.all_time_high)*100, 2) >= 70 THEN 'STANDARD'
        ELSE 'UNDERVALUED'
    END AS investment_grade
    FROM LATEST L
    JOIN HIGHEST H ON L.wine_id = H.wine_id
), P_WINNER AS (
    SELECT P.winery_id, P.winery_name, W.wine_name, W.vintage_year, I.latest_price, I.all_time_high, I.price_ratio, I.investment_grade
    FROM wines W
    JOIN I ON I.wine_id = W.wine_id
    JOIN wineries P ON P.winery_id = W.winery_id
), C AS (
    SELECT winery_id, COUNT(*) AS counter
    FROM P_WINNER
    WHERE investment_grade = 'PRIME'
    GROUP BY winery_id
), T AS(
    SELECT winery_name, wine_name, vintage_year, latest_price, all_time_high, price_ratio, investment_grade, ROW_NUMBER() OVER(PARTITION BY winery_id ORDER BY latest_price DESC) AS price_rank
    FROM P_WINNER R
    WHERE winery_id in (
        SELECT winery_id
        FROM C
        WHERE counter >= 2
    )
    ORDER BY latest_price DESC 
)
SELECT *
FROM T
ORDER BY winery_name, price_rank
```

## 질문 & 실수 정리

### 새로 배운 것

#### 튜플 비교 (Row Constructor Comparison)
`WHERE col IN (subquery)` 로 단일 컬럼만 비교하면, 다른 그룹의 값이 우연히 일치할 때 잘못된 행이 포함될 수 있다. `WHERE (col1, col2) IN (subquery)` 형태로 **여러 컬럼을 튜플로 묶어서** 비교하면, 두 컬럼이 동시에 일치하는 행만 정확히 필터링된다.
- **핵심 원리**: `(wine_id, auction_date) IN (...)` 은 wine_id와 auction_date가 **함께** 서브쿼리 결과와 매칭되는 행만 반환한다. 단일 컬럼 IN은 "그 와인의 최근 날짜"가 아닌 "아무 와인의 최근 날짜"와 매칭될 위험이 있다.

#### PARTITION BY의 역할 (윈도우 함수 그룹 범위 지정)
`ROW_NUMBER() OVER(ORDER BY col DESC)` 는 전체 결과셋에서 1부터 순위를 매긴다. `PARTITION BY` 를 추가하면 **지정한 그룹별로 순위가 1부터 다시 시작**된다. 마치 `GROUP BY`가 집계 함수의 그룹을 정하듯, `PARTITION BY`는 윈도우 함수의 계산 범위(파티션)를 정한다.
- **핵심 원리**: `PARTITION BY winery_id ORDER BY latest_price DESC` → 와이너리별로 독립적인 순위가 매겨짐. PARTITION BY 없으면 전체가 하나의 파티션으로 취급되어 1~N까지 하나의 순위 체계.

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---------|-----------|
| `WHERE auction_date IN (SELECT MAX(auction_date) ...)` — 단일 컬럼 비교로 다른 와인의 날짜와 매칭 위험 | `WHERE (wine_id, auction_date) IN (...)` — 튜플 비교로 정확한 매칭 |
| `L.wine_id = L.wine_id` — 양쪽 다 같은 테이블 별칭 (항상 TRUE) | `L.wine_id = H.wine_id` — 올바른 JOIN 조건 |
| `I.wine_id = W.winery_id` — wine_id와 winery_id 비교 (타입은 같지만 의미 다름) | `I.wine_id = W.wine_id` — 같은 의미의 컬럼 비교 |
| P_WINNER SELECT에 `winery_id` 누락 → 이후 CTE에서 참조 불가 | SELECT 목록에 `P.winery_id` 포함 |
| `ROW_NUMBER() OVER(ORDER BY ...)` — PARTITION BY 없이 전체 순위 | `ROW_NUMBER() OVER(PARTITION BY winery_id ORDER BY ...)` — 와이너리별 순위 |

## AI 코드 리뷰

### 개선할 점

1. **CTE 이름 가독성**: `I`, `C`, `T` 같은 단일 문자 이름은 쿼리가 길어질수록 어떤 역할인지 파악하기 어렵다. `wine_metrics`, `prime_wineries` 등 역할을 설명하는 이름이 좋다.
2. **ROUND 반복 제거**: `I` CTE에서 `ROUND(...)` 를 3번 반복하고 있다. price_ratio를 먼저 계산하는 CTE를 분리하면 다음 CTE에서 별칭으로 CASE WHEN을 작성할 수 있다.
3. **불필요한 ORDER BY 제거**: `T` CTE 안의 `ORDER BY latest_price DESC`는 최종 SELECT에서 다시 정렬하므로 의미 없다. CTE 내부의 ORDER BY는 결과 순서를 보장하지 않는다.
4. **C CTE 통합 가능**: 별도 CTE 대신 WHERE 절에서 서브쿼리 + HAVING으로 한 번에 처리할 수 있다.

## 수정된 코드
```sql
WITH latest_prices AS (
    SELECT wine_id, hammer_price AS latest_price
    FROM auctions
    WHERE (wine_id, auction_date) IN (
        SELECT wine_id, MAX(auction_date)
        FROM auctions
        GROUP BY wine_id
    )
),
all_time_highs AS (
    SELECT wine_id, MAX(hammer_price) AS all_time_high
    FROM auctions
    GROUP BY wine_id
),
wine_metrics AS (
    SELECT
        L.wine_id,
        L.latest_price,
        H.all_time_high,
        ROUND(L.latest_price / H.all_time_high * 100, 2) AS price_ratio
    FROM latest_prices L
    JOIN all_time_highs H ON L.wine_id = H.wine_id
),
wine_grades AS (
    SELECT
        P.winery_id,
        P.winery_name,
        W.wine_name,
        W.vintage_year,
        M.latest_price,
        M.all_time_high,
        M.price_ratio,
        CASE
            WHEN M.price_ratio >= 90 THEN 'PRIME'
            WHEN M.price_ratio >= 70 THEN 'STANDARD'
            ELSE 'UNDERVALUED'
        END AS investment_grade
    FROM wines W
    JOIN wine_metrics M ON M.wine_id = W.wine_id
    JOIN wineries P ON P.winery_id = W.winery_id
)
SELECT
    winery_name,
    wine_name,
    vintage_year,
    latest_price,
    all_time_high,
    price_ratio,
    investment_grade,
    ROW_NUMBER() OVER (PARTITION BY winery_id ORDER BY latest_price DESC) AS price_rank
FROM wine_grades
WHERE winery_id IN (
    SELECT winery_id
    FROM wine_grades
    WHERE investment_grade = 'PRIME'
    GROUP BY winery_id
    HAVING COUNT(*) >= 2
)
ORDER BY winery_name, price_rank;
```
