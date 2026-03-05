# 자작문제 🎮 소환사 협곡 KDA 스냅샷 리포트

## 문제 요약
> 소환사별 최근 5경기를 필터링하고, 솔로/듀오 유형별 평균 KDA와 전체 평균 KDA를 구한 뒤 KDA 기준 랭킹을 매기는 문제

#### 문제링크
https://velog.io/@tesabel/소환사-협곡-KDA-스냅샷-리포트-문제

## 느낀점
>
- 어려웠다..
- CASE, ROUND, AVG 순서에 따라 결과는 완전히 다르다. 항상 고민하고 풀자
   - CASE문을 집계 내부에 쓸 경우 별칭 제거하기
- WITH절 하나 완성할때마다 디버깅하기

## 흐름
1. **RECENT_GAMES**: ROW_NUMBER()로 소환사별 최근 5경기 필터링 + KILLS, DEATHS, ASSISTS 포함
2. **GAME_KDA**: PLAY_TYPE 솔로/듀오 분류 + 개별 게임 KDA 계산 (DEATHS=0 분기 처리)
3. **TYPE_KDA**: 소환사 × 플레이 유형별 AVG(KDA)
4. **OVERALL_KDA**: 소환사별 전체 게임 AVG(KDA) — 개별 KDA에서 직접 평균
5. **최종 SELECT**: JOIN으로 합치고 RANK() OVER()로 순위 매기기

## 코드
```sql
WITH RECENT_GAMES AS (
    SELECT SUMMONER_ID, SUMMONER_NAME, MATCH_ID,
           DUO_PARTNER_ID, KILLS, DEATHS, ASSISTS
    FROM (
        SELECT 
            ROW_NUMBER() OVER(PARTITION BY S.SUMMONER_ID ORDER BY MS.PLAYED_AT DESC) AS RN,
            R.DUO_PARTNER_ID, R.KILLS, R.DEATHS, R.ASSISTS,
            S.SUMMONER_ID, S.SUMMONER_NAME, MS.MATCH_ID
        FROM SUMMONERS S
        JOIN MATCH_RECORDS R ON R.SUMMONER_ID = S.SUMMONER_ID
        JOIN MATCHES MS ON MS.MATCH_ID = R.MATCH_ID
    ) AS SUB
    WHERE RN <= 5
), GAME_KDA AS (
    SELECT *,
        CASE WHEN DUO_PARTNER_ID IS NULL THEN '솔로' ELSE '듀오' END AS PLAY_TYPE,
        CASE
            WHEN DEATHS = 0 THEN (KILLS + ASSISTS) * 1.0
            ELSE (KILLS + ASSISTS) * 1.0 / DEATHS
        END AS KDA
    FROM RECENT_GAMES
), TYPE_KDA AS (
    SELECT SUMMONER_ID, SUMMONER_NAME, PLAY_TYPE,
        ROUND(AVG(KDA), 2) AS TYPE_AVG_KDA
    FROM GAME_KDA
    GROUP BY SUMMONER_ID, SUMMONER_NAME, PLAY_TYPE
), OVERALL_KDA AS (
    SELECT SUMMONER_ID,
        ROUND(AVG(KDA), 2) AS OVERALL_AVG_KDA
    FROM GAME_KDA
    GROUP BY SUMMONER_ID
)
SELECT 
    T.SUMMONER_NAME,
    T.PLAY_TYPE,
    T.TYPE_AVG_KDA,
    O.OVERALL_AVG_KDA,
    RANK() OVER(ORDER BY O.OVERALL_AVG_KDA DESC) AS KDA_RANK
FROM TYPE_KDA T
JOIN OVERALL_KDA O ON T.SUMMONER_ID = O.SUMMONER_ID
ORDER BY KDA_RANK, T.SUMMONER_NAME, T.PLAY_TYPE;
```

## 질문 & 실수 정리

### 새로 배운 것

#### 그룹별 Top N은 ROW_NUMBER()
"소환사별 최근 5경기"처럼 **그룹별로 N개씩 자르기**는 `IN` + `LIMIT`이나 `EXISTS` + `LIMIT`로는 구조적으로 풀기 어렵다. MySQL에서 `IN` 서브쿼리 안에 `LIMIT`을 쓸 수 없고, 상관 서브쿼리 안의 파생 테이블에서 바깥 참조도 불가능하기 때문이다. `ROW_NUMBER() OVER(PARTITION BY ... ORDER BY ...)`로 그룹별 순번을 매기고, 바깥에서 `WHERE RN <= N`으로 필터링하는 패턴이 가장 깔끔하다.
- **핵심 원리**: PARTITION BY로 그룹을 나누고, ORDER BY로 순서를 정해 순번을 매긴 뒤, 파생 테이블로 감싸서 필터링

#### CTE 내부에서 자기 자신 참조 불가
CTE를 정의하는 도중에 그 CTE 자체를 참조할 수 없다. `WITH M5 AS (SELECT ... WHERE M5.col = ...)`처럼 아직 만들어지지 않은 CTE를 내부에서 쓰면 에러가 난다. 이미 FROM절에 정의된 테이블을 참조하는 상관 서브쿼리(`EXISTS`, `=` 등)와는 다른 상황이다.
- **핵심 원리**: 상관 서브쿼리는 "이미 존재하는" 바깥 테이블 참조 → 가능 / CTE 자기 자신 참조 → 불가능

#### AVG, ROUND, CASE의 순서가 결과를 바꾼다
`ROUND(AVG(CASE WHEN ... END), 2)` vs `AVG(ROUND(CASE WHEN ... END, 2))`는 결과가 다르다. 개별 값을 먼저 반올림하면 정보가 손실된 채로 평균이 계산되므로, **평균을 구한 뒤 마지막에 반올림**하는 것이 정확하다. 마찬가지로 `CASE`는 개별 행의 조건 분기이므로 `AVG()` 안쪽에, `ROUND()`는 `AVG()` 바깥에 위치해야 한다.
- **핵심 원리**: 안쪽부터 CASE(행별 분기) → AVG(집계) → ROUND(최종 반올림)

#### 전체 평균은 유형별 평균의 단순 평균이 아니다
솔로 3경기 평균 KDA와 듀오 2경기 평균 KDA를 더해서 2로 나누면, 게임 수 가중치가 무시된다. 전체 평균 KDA는 **개별 게임 KDA 5개에서 직접 AVG()**를 구해야 정확하다.
- **핵심 원리**: 가중 평균이 필요할 때 그룹 평균의 단순 평균은 오류 → 원본 데이터에서 직접 집계

#### 정수 나눗셈 주의
MySQL에서 `INT / INT`는 정수 나눗셈이 되어 소수점이 버려진다. `(KILLS + ASSISTS) * 1.0 / DEATHS`처럼 `* 1.0`을 곱하거나 `CAST(... AS DECIMAL)`로 형변환해야 소수점 결과를 얻을 수 있다.
- **핵심 원리**: 피연산자 중 하나라도 실수형이면 실수 나눗셈이 수행됨

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---------|-----------|
| CTE 내부에서 자기 자신(M5) 참조 | ROW_NUMBER()로 그룹별 순번 매기기 |
| M5에 KILLS, DEATHS, ASSISTS 미포함 → 재조인 필요 | 처음부터 필요한 컬럼을 모두 포함 |
| `SELECT *` + `GROUP BY` 사용 | GROUP BY 시 필요한 컬럼 명시적 나열 |
| `SUM(유형별 평균) / 2`로 전체 평균 계산 | 개별 게임 KDA에서 직접 AVG() |
| `AVG(ROUND(CASE ...))` 순서 | `ROUND(AVG(CASE ...), 2)` 순서 |
| 파생 테이블에 alias 누락 | `FROM (...) AS SUB` 필수 |

## AI 코드 리뷰

### 개선할 점

1. **CTE 네이밍**: `M5`, `M5TYPE` 같은 이름보다 `RECENT_GAMES`, `GAME_KDA`처럼 역할을 담은 이름이 가독성에 좋다
2. **ROW_NUMBER() alias 관례**: `COUNTER`보다 `RN`이 업계에서 널리 쓰이는 관례
3. **불필요한 컬럼 제거**: `RN`은 필터링에만 쓰이므로 바깥 SELECT에서 제외

## 수정된 코드
```sql
WITH RECENT_GAMES AS (
    SELECT SUMMONER_ID, SUMMONER_NAME, MATCH_ID,
           DUO_PARTNER_ID, KILLS, DEATHS, ASSISTS
    FROM (
        SELECT 
            ROW_NUMBER() OVER(PARTITION BY S.SUMMONER_ID ORDER BY MS.PLAYED_AT DESC) AS RN,
            R.DUO_PARTNER_ID, R.KILLS, R.DEATHS, R.ASSISTS,
            S.SUMMONER_ID, S.SUMMONER_NAME, MS.MATCH_ID
        FROM SUMMONERS S
        JOIN MATCH_RECORDS R ON R.SUMMONER_ID = S.SUMMONER_ID
        JOIN MATCHES MS ON MS.MATCH_ID = R.MATCH_ID
    ) AS SUB
    WHERE RN <= 5
), GAME_KDA AS (
    SELECT *,
        CASE WHEN DUO_PARTNER_ID IS NULL THEN '솔로' ELSE '듀오' END AS PLAY_TYPE,
        CASE
            WHEN DEATHS = 0 THEN (KILLS + ASSISTS) * 1.0
            ELSE (KILLS + ASSISTS) * 1.0 / DEATHS
        END AS KDA
    FROM RECENT_GAMES
), TYPE_KDA AS (
    SELECT SUMMONER_ID, SUMMONER_NAME, PLAY_TYPE,
        ROUND(AVG(KDA), 2) AS TYPE_AVG_KDA
    FROM GAME_KDA
    GROUP BY SUMMONER_ID, SUMMONER_NAME, PLAY_TYPE
), OVERALL_KDA AS (
    SELECT SUMMONER_ID,
        ROUND(AVG(KDA), 2) AS OVERALL_AVG_KDA
    FROM GAME_KDA
    GROUP BY SUMMONER_ID
)
SELECT 
    T.SUMMONER_NAME,
    T.PLAY_TYPE,
    T.TYPE_AVG_KDA,
    O.OVERALL_AVG_KDA,
    RANK() OVER(ORDER BY O.OVERALL_AVG_KDA DESC) AS KDA_RANK
FROM TYPE_KDA T
JOIN OVERALL_KDA O ON T.SUMMONER_ID = O.SUMMONER_ID
ORDER BY KDA_RANK, T.SUMMONER_NAME, T.PLAY_TYPE;
```
