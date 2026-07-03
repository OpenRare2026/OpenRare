# GENOS-VarRisk 疾病预测数据库注释模块

将疾病预测模型输出中的 `p_fusion` 按 CPRA 匹配到宽表，列名固定为 `GENOS-VarRisk`。对应主流程第 **06** 步。

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/build_genos_evee_db.py` | 将 prediction TSV shard 构建为 bgzip + tabix 数据库 |
| `scripts/add_genos_evee_to_csv.py` | 在 05 宽表中加入 `GENOS-VarRisk` 列 |

## 主流程

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output \
  --GENOS-VarRisk-db /path/to/genos_evee.cpra.tsv.gz
```

默认数据库路径由 `.env` 的 `FULL_PIPELINE_GENOS_EVEE_DB` 或 `config/path_utils.py` 解析。数据库不存在时流程仍可运行，该列全部填 `-`。

输出：`06_genos_evee_annotation/vep_output.with_genos_evee.csv`（默认还会继续进入 07 HLA 过滤）。

联调可使用 [`resource_mock/genos_evee/genos_evee.cpra.mock.tsv.gz`](../../resource_mock/README.md)。

## 单独注释

```bash
python3 modules/genos_evee_annotation/scripts/add_genos_evee_to_csv.py \
  --input-csv /path/to/05_vcf_info_to_csv/vep_output.with_info.csv \
  --database /path/to/genos_evee.cpra.tsv.gz \
  --output-csv /path/to/06_genos_evee_annotation/vep_output.with_genos_evee.csv \
  --log-json /path/to/06_genos_evee_annotation/genos_evee_annotation.log.json
```

未命中数据库的位点填 `-`，不删除行。

## 构建数据库

```bash
python3 modules/genos_evee_annotation/scripts/build_genos_evee_db.py \
  --input '/path/to/predictions.shard*.tsv' \
  --output /path/to/genos_evee.cpra.tsv.gz \
  --threads 8 \
  --log-json /path/to/build.log.json
```

prediction TSV 须含 `p_fusion`，坐标可为 `chrom pos ref alt` 或 `variant_id` / `CPRA` 等形式。
