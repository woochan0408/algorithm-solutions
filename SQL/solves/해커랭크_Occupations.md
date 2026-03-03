# 해커랭크 Occupations 🔄 Occupations

## 문제 요약
> OCCUPATIONS 테이블을 피벗하여 Doctor, Professor, Singer, Actor 4개 컬럼으로 변환하고, 각 직업별 이름을 알파벳순 정렬, 부족한 행은 NULL로 채우기

## 느낀점
>
- 정말 어렵고 중요한 문제.
- MAX는 큰 의미가 있는게 아니라 GROUP BY 오류 회피용이다.
    - (일치하는 갑은 하나지만 MYSQL은 비집계칼럼이 SELECT에 있으면 안 된다.)
    - 즉 MIN 써도 답 맞음
- 꼭 다시 풀어보기

## 흐름
1. CTE에서 ROW_NUMBER()로 각 직업별 알파벳순 순번(N) 부여
2. N을 기준으로 GROUP BY하여 같은 순번끼리 한 행으로 묶기
3. CASE WHEN으로 각 직업별 이름을 별도 컬럼으로 분리
4. MAX로 감싸서 그룹 내 NULL 아닌 값 추출

## 코드
```sql
WITH F AS 
( SELECT NAME, OCCUPATION,  
ROW_NUMBER() OVER(PARTITION BY OCCUPATION ORDER BY NAME) AS N 
FROM OCCUPATIONS 
    )
SELECT
MAX(CASE WHEN Occupation = 'Doctor' THEN Name END), 
MAX(CASE WHEN Occupation = 'Professor' THEN Name END), 
MAX(CASE WHEN Occupation = 'Singer' THEN Name END), 
MAX(CASE WHEN Occupation = 'Actor' THEN Name END) 
FROM F
GROUP BY N;
```

## 질문 & 실수 정리

### 새로 배운 것

#### 1. 피벗(Pivot) 패턴: `ROW_NUMBER()` + `GROUP BY` + `CASE WHEN`
행(row) 기반 데이터를 열(column) 기반으로 변환하는 대표적인 SQL 피벗 기법입니다. MySQL에는 PIVOT 키워드가 없기 때문에 이 세 가지 문법을 조합하여 사용합니다.

문법 사용법 및 핵심 원리:
- `ROW_NUMBER() OVER(PARTITION BY 카테고리 ORDER BY 정렬기준)`: 각 그룹(직업)별로 알파벳 순번을 매겨, 나중에 같은 가로줄에 배치될 기준점(`N`)을 만듭니다.
- `GROUP BY N`: 부여된 순번(`N`)을 기준으로 같은 순서인 데이터들을 하나의 행으로 합칩니다.
- `CASE WHEN 조건 THEN 결과 END`: 그룹화된 행 안에서 조건에 맞는 데이터만 해당 컬럼에 배치하고, 나머지는 NULL로 둡니다.

#### 2. 집계 함수를 "값 추출 용도"로 사용하기: `MAX()` / `MIN()`
`GROUP BY`를 사용하면 그룹 내 여러 행이 하나로 합쳐지므로, `SELECT`에 오는 컬럼은 반드시 집계 함수로 감싸야 하는 문법적 규칙이 있습니다.

문법 사용법 및 핵심 원리:
- `MAX(CASE WHEN ... END)`: 여기서 `MAX`나 `MIN`은 "최대/최소값을 구하겠다"는 본래 의미가 아닙니다. 해당 조건을 만족하는 데이터가 어차피 1개뿐이므로, "SQL 문법 오류를 피하면서, NULL을 무시하고 존재하는 유일한 값을 꺼내겠다"는 용도로 사용됩니다.

### 실수했던 부분

| 틀린 것 | 올바른 것 |
|---------|-----------|
| MAX를 쓰면 전체에서 1등만 뽑힌다고 오해 | MAX는 GROUP BY N별로 각각 동작하므로 모든 순번의 값이 추출됨 |
| 피벗에 재귀(recursion)가 필요하다고 생각 | ROW_NUMBER + GROUP BY + CASE WHEN 패턴으로 충분 |

## AI 코드 리뷰

### 개선할 점

1. **컬럼 별칭 추가**: 현재 출력에 컬럼명이 `MAX(CASE WHEN ...)`으로 표시되므로, 별칭을 붙이면 결과가 더 명확해진다
2. **들여쓰기 통일**: CTE 내부와 메인 쿼리의 들여쓰기를 일관되게 정리

## 수정된 코드
```sql
WITH F AS (
    SELECT 
        NAME, 
        OCCUPATION,
        ROW_NUMBER() OVER(PARTITION BY OCCUPATION ORDER BY NAME) AS N
    FROM OCCUPATIONS
)
SELECT
    MAX(CASE WHEN Occupation = 'Doctor' THEN Name END) AS Doctor,
    MAX(CASE WHEN Occupation = 'Professor' THEN Name END) AS Professor,
    MAX(CASE WHEN Occupation = 'Singer' THEN Name END) AS Singer,
    MAX(CASE WHEN Occupation = 'Actor' THEN Name END) AS Actor
FROM F
GROUP BY N;
```
