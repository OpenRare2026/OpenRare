# Learnings

## 2026-05-29 Initial Analysis

- VEPCSVParser has 3 interrelated bugs in `_map_row()`:
  1. **Signature mismatch**: `parse()` passes 4 args but `_map_row()` accepts max 3+1 → TypeError
  2. **Type mismatch in get()**: `field_to_cols` is `Dict[str, List[str]]` but `get()` compares `mapped == field_name` (list vs string) → always False
  3. **get_with_extra() linear scan**: Uses global `EXTRA_KEY_ALIASES` instead of pre-built `extra_field_to_keys`
- Root cause: incomplete refactoring — `field_to_cols` was changed from `Dict[str,str]` to `Dict[str,List[str]]` but `_map_row()` wasn't updated
- 9/10 VEPCSVParser tests FAIL with TypeError
- `parse()` line 260 already passes correct args: `self._map_row(norm_row, field_to_cols, extra_field_to_keys, extra_fields)` — only `_map_row()` signature needs fixing
