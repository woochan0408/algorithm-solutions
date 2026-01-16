# Add New Category Guide

When adding a new algorithm category, complete ALL the following steps:

## Checklist

### 1. Create Folder
```bash
mkdir -p solutions/{Category_Name}
touch solutions/{Category_Name}/.gitkeep
```

### 2. Update README.md
- [ ] Add badge in header section:
```markdown
![카테고리명](https://img.shields.io/badge/카테고리명-0-COLOR?style=flat-square)
```
- [ ] Add link in category table (choose appropriate column: 탐색/그래프/자료구조/최적화/기법)

### 3. Update `scripts/update_stats.py`
- [ ] Add to `FOLDER_MAPPING`:
```python
"카테고리명": "Category_Name",
```
- [ ] Add to `BADGE_COLORS`:
```python
"Category_Name": "HEX_COLOR",
```

## Color Reference
Common badge colors:
- `00C853` (green), `7C4DFF` (purple), `FF5252` (red)
- `00BCD4` (cyan), `FFCA28` (yellow), `FF69B4` (pink)
- `9E9E9E` (gray - for 0 problems)

## Naming Convention
- Folder: `Snake_Case` (e.g., `Prefix_Sum`, `Binary_Search`)
- Badge label: Korean (e.g., `누적합`, `이분탐색`)
