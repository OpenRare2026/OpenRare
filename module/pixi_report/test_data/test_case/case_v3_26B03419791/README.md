# 样例 26B03419791

## 文件

| 文件 | 说明 |
|------|------|
| `test_v3_26B03419791.csv` | 样本 manifest（临床信息 + HPO + 宽表路径） |
| `vep_output.with_info.ranked_large.top10000.csv` | 源宽表**前 10000 行**（1 行表头 + 9999 行数据，约 7MB） |
| `vep_output.with_info.ranked_large.header.csv` | 仅表头一行（便于查看列名） |

完整源宽表（约 5.9GB）：

`/mnt/workspace/hujie/workspace/test/26B03419791.final.vcf.gz.result/vep_output.with_info.ranked_large.csv`

## 生成报告

```bash
uv run python scripts/generate_final_report.py \
  --manifest test_data/test_case/case_v3_26B03419791/test_v3_26B03419791.csv \
  --output-dir test_data/test_case/case_v3_26B03419791 \
  --top-n 5
```

> 当前 manifest 指向 `top10000` 子集，便于本地快速跑通；全量宽表见上方源路径。

## HPO

`HP:0003510` `HP:0000887` `HP:0003551` `HP:0002148` `HP:0000767` `HP:0025802` `HP:5200134` `HP:0032066`

## 宽表与 V3 样例差异

本宽表在 V3 基础上末尾多 7 列评分分解：`clinvar_score`, `consequence_score`, `splice_lof_score`, `prediction_score`, `frequency_score`, `domain_score`, `raw_pathogenic_score`（`pathogenic_rank` / `evidence_summary` 仍保留）。报告脚本会忽略未映射列。
