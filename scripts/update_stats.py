#!/usr/bin/env python3
from __future__ import annotations

"""
README 통계/다시풀기 목록 자동 업데이트 스크립트
solutions 폴더 내 파일 개수를 세고, README.md의 다시 풀 문제 목록을 갱신합니다.
"""

import html
import re
from pathlib import Path

# 프로젝트 루트 경로
ROOT_DIR = Path(__file__).parent.parent
SOLUTIONS_DIR = ROOT_DIR / "solutions"
README_PATH = ROOT_DIR / "README.md"
RETRY_SECTION_START = "<!-- retry-problems-start -->"
RETRY_SECTION_END = "<!-- retry-problems-end -->"

# 뱃지 라벨 → 폴더명 매핑
FOLDER_MAPPING = {
    "BFS/DFS": "BFS_DFS",
    "BFS%2FDFS": "BFS_DFS",  # URL 인코딩 버전
    "분할정복": "Divide_Conquer",
    "DP": "DP",
    "이분탐색": "Binary_Search",
    "그래프": "Graph",
    "스택/큐": "Stack_Queue",
    "스택%2F큐": "Stack_Queue",
    "트리": "Tree",
    "그리디": "Greedy",
    "백트래킹": "Backtracking",
    "브루트포스": "Brute_Force",
    "위상정렬": "Topological_Sort",
    "세그먼트트리": "Segment_Tree",
    "유니온파인드": "Union_Find",
    "비트마스킹": "Bitmask",
    "투포인터": "Two_Pointer",
    "슬라이딩윈도우": "Sliding_Window",
    "문자열": "String",
    "정렬": "Sorting",
    "수학": "Math",
    "구현": "Implementation",
    "최단경로": "Shortest_Path",
    "누적합": "Prefix_Sum",
    "기타": "Etc",
}

# 뱃지 색상 매핑 (원하는 대로 커스터마이즈)
BADGE_COLORS = {
    "BFS_DFS": "green",
    "Divide_Conquer": "orange",
    "DP": "red",
    "Binary_Search": "purple",
    "Graph": "blue",
    "Stack_Queue": "yellowgreen",
    "Tree": "brightgreen",
    "Greedy": "yellow",
    "Backtracking": "lightgrey",
    "Brute_Force": "blueviolet",
    "Topological_Sort": "ff69b4",
    "Segment_Tree": "00CED1",
    "Union_Find": "9cf",
    "Bitmask": "important",
    "Two_Pointer": "cyan",
    "Sliding_Window": "informational",
    "String": "success",
    "Sorting": "critical",
    "Math": "ff6347",
    "Implementation": "lightblue",
    "Shortest_Path": "gold",
    "Prefix_Sum": "9E9E9E",
    "Etc": "9E9E9E",
}


def count_problems(folder_path: Path) -> int:
    """폴더 내 문제 파일 개수를 셉니다 (.gitkeep 제외)"""
    if not folder_path.exists():
        return 0

    count = 0
    for item in folder_path.iterdir():
        if item.is_file() and item.name != ".gitkeep":
            count += 1
    return count


def get_all_stats() -> dict:
    """모든 폴더의 통계를 수집합니다"""
    stats = {}
    total = 0

    # 고유 폴더명들만 추출
    unique_folders = set(FOLDER_MAPPING.values())

    for folder_name in unique_folders:
        folder_path = SOLUTIONS_DIR / folder_name
        count = count_problems(folder_path)
        stats[folder_name] = count
        total += count

    stats["Total"] = total
    return stats


def update_badge(content: str, label: str, count: int, color: str = "blue") -> str:
    """README 내용에서 특정 뱃지의 숫자를 업데이트합니다"""

    # 배지 URL에서는 슬래시만 인코딩, 한글은 그대로 사용
    badge_label = label.replace("/", "%2F")

    # 패턴: ![Label](https://img.shields.io/badge/Label-숫자-color)
    pattern = rf'(\!\[{re.escape(label)}\]\(https://img\.shields\.io/badge/{re.escape(badge_label)})-(\d+)(-[^)]+\))'
    replacement = rf'\g<1>-{count}\g<3>'

    content = re.sub(pattern, replacement, content)
    return content


def update_total_badge(content: str, total: int) -> str:
    """Total 뱃지를 업데이트합니다"""
    pattern = rf'(\!\[Total\]\(https://img\.shields\.io/badge/Total)-(\d+)(%20problems-[^)]+\))'
    replacement = rf'\g<1>-{total}\g<3>'
    return re.sub(pattern, replacement, content)


def normalize_text(text: str) -> str:
    """불필요한 공백과 HTML 엔티티를 정리합니다."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split()).strip()


def extract_link(cell: str) -> tuple[str | None, str]:
    """HTML/Markdown 링크에서 URL과 텍스트를 추출합니다."""
    cell = cell.strip()

    html_link = re.search(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', cell)
    if html_link:
        return html_link.group(1).strip(), normalize_text(html_link.group(2))

    markdown_link = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if markdown_link:
        return markdown_link.group(2).strip(), normalize_text(markdown_link.group(1))

    return None, normalize_text(cell)


def extract_retry_problems(content: str) -> list[dict]:
    """README 표에서 다시 풀기 체크된 문제를 추출합니다."""
    retry_problems = []
    in_problem_table = False

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("| 유형 |") and "RE?" in stripped:
            in_problem_table = True
            continue

        if not in_problem_table:
            continue

        if not stripped.startswith("|"):
            break

        if stripped.startswith("|:---"):
            continue

        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 8:
            continue

        retry_flag = parts[-1]
        if "✅" not in retry_flag:
            continue

        category = parts[0]
        problem_cell = parts[2]
        solution_cell = parts[4]
        solved_date = parts[5]

        problem_url, problem_label = extract_link(problem_cell)
        solution_url, _ = extract_link(solution_cell)

        retry_problems.append(
            {
                "category": category,
                "problem_label": problem_label or "문제 링크",
                "problem_url": problem_url,
                "solution_url": solution_url,
                "date": solved_date,
            }
        )

    return retry_problems


def build_retry_section(retry_problems: list[dict]) -> str:
    """다시 풀 문제 섹션 Markdown을 생성합니다."""
    if not retry_problems:
        return "> 다시 풀 문제가 없습니다."

    lines = [
        "<details>",
        f"<summary><strong>총 {len(retry_problems)}문제</strong></summary>",
        "",
    ]

    for problem in retry_problems:
        if problem["problem_url"]:
            problem_link = f"[{problem['problem_label']}]({problem['problem_url']})"
        else:
            problem_link = problem["problem_label"]

        solution_part = f" · [풀이]({problem['solution_url']})" if problem["solution_url"] else ""
        category_part = f" · `{problem['category']}`" if problem["category"] else ""
        lines.append(f"- `{problem['date']}` {problem_link}{solution_part}{category_part}")

    lines.extend(["", "</details>"])
    return "\n".join(lines)


def replace_section(content: str, start_marker: str, end_marker: str, replacement: str) -> tuple[str, bool]:
    """마커 사이 구간을 교체합니다."""
    if start_marker not in content or end_marker not in content:
        return content, False

    prefix, remainder = content.split(start_marker, 1)
    _, suffix = remainder.split(end_marker, 1)
    updated_content = f"{prefix}{start_marker}\n{replacement}\n{end_marker}{suffix}"
    return updated_content, True


def update_readme(stats: dict) -> bool:
    """README.md 파일을 업데이트합니다"""

    if not README_PATH.exists():
        print(f"❌ README.md not found at {README_PATH}")
        return False

    content = README_PATH.read_text(encoding="utf-8")
    original_content = content

    # Total 뱃지 업데이트 (별도 함수 사용)
    content = update_total_badge(content, stats["Total"])

    # 각 카테고리 뱃지 업데이트
    for label, folder_name in FOLDER_MAPPING.items():
        if "%" in label:  # URL 인코딩된 버전은 스킵 (원본만 처리)
            continue

        count = stats.get(folder_name, 0)
        if count > 0:  # 0인 경우는 뱃지 유지 또는 업데이트 선택
            color = BADGE_COLORS.get(folder_name, "blue")
            content = update_badge(content, label, count, color)

    retry_problems = extract_retry_problems(content)
    retry_section = build_retry_section(retry_problems)
    content, updated_retry_section = replace_section(
        content,
        RETRY_SECTION_START,
        RETRY_SECTION_END,
        retry_section,
    )
    if not updated_retry_section:
        print("⚠️ Retry problem section markers not found. Skipping retry section update.")

    # 변경사항이 있으면 저장
    if content != original_content:
        README_PATH.write_text(content, encoding="utf-8")
        print("✅ README.md updated successfully!")
        return True
    else:
        print("ℹ️ No changes needed")
        return False


def print_stats(stats: dict):
    """통계를 출력합니다"""
    print("\n📊 Problem Statistics:")
    print("-" * 30)

    for folder, count in sorted(stats.items()):
        if folder != "Total" and count > 0:
            print(f"  {folder}: {count}")

    print("-" * 30)
    print(f"  Total: {stats['Total']}")
    print()


def main():
    print("🔍 Scanning solutions folder...")

    stats = get_all_stats()
    print_stats(stats)

    print("📝 Updating README.md...")
    update_readme(stats)


if __name__ == "__main__":
    main()
