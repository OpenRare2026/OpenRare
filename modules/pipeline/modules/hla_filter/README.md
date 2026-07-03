# HLA/MHC 区域行过滤模块

从 GENOS-VarRisk 宽表中删除 GRCh38 HLA/MHC 区域的变异行。对应主流程第 **07** 步（默认开启）。

## 过滤区间

```text
GRCh38 chr6:28477797-33448354
```

## 主流程

默认 `hla_filter=yes`，最终 CSV 为：

```text
<out-dir>/07_hla_filter/vep_output.no_hla.csv
```

跳过过滤：

```bash
bash scripts/run_full_pipeline.sh ... --hla-filter no
```

此时最终 CSV 为 `06_genos_evee_annotation/vep_output.with_genos_evee.csv`。

API 对应字段：`hla_filter`（`yes` / `no`）。

## 单独运行

```bash
python3 modules/hla_filter/scripts/filter_hla_region_csv.py \
  --input-csv /path/to/06_genos_evee_annotation/vep_output.with_genos_evee.csv \
  --output-csv /path/to/07_hla_filter/vep_output.no_hla.csv \
  --log-json /path/to/07_hla_filter/hla_filter.log.json
```

## 单测

```bash
pixi run hla-filter-test
```
