# 示例用例（demo_case）

仓库内置的最小可跑样例，供 `scripts/generate_final_report.py` 快速验证流水线。

| 文件 | 说明 |
|------|------|
| `manifest.csv` | 一行样本：临床信息 + HPO + 宽表相对路径 |
| `wide_table.csv` | 4 个基因的 VEP 排序宽表片段（CNOT3、KANSL1、TNRC6B、SETD5） |

## 预生成报告（可直接查看）

| 目录 | 说明 |
|------|------|
| `output_agent/` | **默认**：含 LLM Agent 叙事与临床建议（`context.pre_agent.json` 可对比脚本层） |
| `output/` | 仅脚本预取 + 模板（`--no-agent`） |

## 重新生成

**完整报告（需 LLM + Open Targets MCP）：**

```bash
uv run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output_agent \
  --top-n 4
```

**仅脚本层（无需 LLM）：**

```bash
uv run python scripts/generate_final_report.py \
  --manifest examples/demo_case/manifest.csv \
  --output-dir examples/demo_case/output \
  --top-n 4 \
  --no-agent
```
