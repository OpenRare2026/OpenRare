# 致病性排序模块（可选）

对宽表 CSV 按 OpenRare 致病性评分规则排序。排序逻辑沿用原 `run_vep_to_csv.py` 中的规则：ClinVar、后果类型、剪接/LoF、预测分数、群体频率和蛋白结构域等证据共同计算 `_raw_pathogenic_score`，按分数从高到低排序，并写入 `pathogenic_rank` 与 `evidence_summary`。

## 与主流程的关系

当前 `scripts/run_full_pipeline.sh` **默认不调用**本模块。主流程在 06 GENOS-VarRisk 注释之后，由 07 HLA 过滤产出最终宽表：

```text
05 vcf_info_to_csv → 06 genos_evee_annotation → 07 hla_filter（默认最终 CSV）
```

如需致病性排序，请在主流程完成后**单独运行**本脚本，或自行取消 `run_full_pipeline.sh` 末尾的排序步骤注释。

## 输入

- `--input-csv`：带 `vcf_info_*`（及可选 `GENOS-VarRisk`）列的宽表，通常来自 `05_vcf_info_to_csv/` 或 `06_genos_evee_annotation/`。
- `--output-csv`：排序后的 CSV。

## 单独运行示例

```bash
python3 modules/result_sorting/scripts/sort_vep_csv.py \
  --input-csv /path/to/output/06_genos_evee_annotation/vep_output.with_genos_evee.csv \
  --output-csv /path/to/output/optional_sorting/vep_output.sorted.csv \
  --log-json /path/to/output/optional_sorting/result_sorting.log.json
```
