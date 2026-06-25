# 06 VEP CSV 排序模块

功能：对 05 生成的 CSV 做最终致病性排序，输出完整流程的最终 CSV。

排序逻辑沿用原 `run_vep_to_csv.py` 中的 OpenRare 打分规则：ClinVar、后果类型、剪接/LoF、预测分数、群体频率和蛋白结构域等证据共同计算 `_raw_pathogenic_score`，按分数从高到低排序，并写入 `pathogenic_rank` 与 `evidence_summary`。

## 输入

- `--input-csv`：05 输出的带 `vcf_info_*` 列 CSV。
- `--output-csv`：最终排序 CSV。

## 单独运行示例

```bash
python3 modules/result_sorting/scripts/sort_vep_csv.py \
  --input-csv test/output/example/05_vcf_info_to_csv/vep_output.with_info.csv \
  --output-csv test/output/example/06_result_sorting/vep_output.sorted.csv \
  --log-json test/output/example/06_result_sorting/result_sorting.log.json
```
