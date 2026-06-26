# 示例用例（demo_case）

`demo_case` 是仓库内置的最小可跑样例，包含新格式宽表、PPI 得分与 HPO 输入，供 `scripts/generate_final_report.py` 与 API 快速验证流水线。

| 文件 | 说明 |
|------|------|
| `manifest.csv` | 一行样本：临床信息 + HPO + 宽表 / PPI 相对路径 |
| `wide_table.csv` | 新格式排序宽表（含 `pathogenic_rank_1`、`ppi_final`、`evolve_score` 等 120 列）；本例为 Top 5 基因各 1 行 |
| `ppi_score.csv` | 基因级 PPI 得分（`gene` + `ppi_final`），对应宽表中的 5 个基因 |
| `gene_phenotype_score.csv` | 基因-表型匹配得分（参考数据，报告流水线暂不读取） |
| `hpo_terms.txt` | HPO 术语列表 |

**示例 Top 5 基因**（按 `pathogenic_rank_1`）：HLA-DPA1、CXCL17、PCDHGC4、DDI2、BMP8B

## 预生成报告（可直接查看）

| 目录 | 说明 |
|------|------|
| `output_agent/` | **默认**：含 LLM Agent 叙事与临床建议（`context.pre_agent.json` 可对比脚本层） |
| `output/` | 仅脚本预取 + 模板（`--no-agent`） |

## 重新生成

**完整报告（需 LLM + Open Targets MCP）：**

```bash
pixi run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output_agent \
  --top-n 5
```

**仅脚本层（无需 LLM）：**

```bash
pixi run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output \
  --top-n 5 \
  --no-agent
```

**API 请求示例：**

```bash
curl -N -X POST http://127.0.0.1:8800/report/stream \
  -H 'Content-Type: application/json' \
  -d '{
    "wide_path": "examples/demo_case/wide_table.csv",
    "phenotype_path": "fixtures/phenotype.csv",
    "hpo_path": "examples/demo_case/hpo_terms.txt",
    "ppi_path": "examples/demo_case/ppi_score.csv",
    "top_n": 5
  }'
```
