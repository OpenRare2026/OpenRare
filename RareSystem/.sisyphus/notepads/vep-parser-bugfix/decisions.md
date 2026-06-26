# Decisions

## 2026-05-29

- Merged original Task 1 + Task 2 into single Task 1 (both modify same `_map_row()` function, can't parallelize)
- Performance optimization is a natural consequence of fixing the O(n) lookup bug — no separate optimization pass needed
- No streaming refactor (out of scope for bug fix)
