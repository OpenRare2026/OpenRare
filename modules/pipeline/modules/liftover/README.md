# 标准染色体过滤

在 phasing / VEP 等下游步骤之前，从 VCF 中**仅保留标准人类染色体**，并记录被忽略的非标准 contig 变异。

## 标准染色体定义

保留以下染色体（含 `chr` 前缀版本）：

- 常染色体 `1-22`
- 性染色体 `X`、`Y`
- 线粒体 `M` / `MT`

其他 contig（如 `chrUn_*`、`*_random`、`*_alt`、HLA scaffold、decoy）视为非标准，默认过滤并写入 ignored TSV。

## 主流程集成

由 `scripts/run_full_pipeline.sh` 在 **GRCh37 liftover（可选）之后、phasing 之前** 调用：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf sample.vcf.gz \
  --out-dir ./output \
  --liftover-filter-standard-chroms yes   # 默认 yes
```

关闭过滤：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf sample.vcf.gz \
  --out-dir ./output \
  --liftover-filter-standard-chroms no
```

## 脚本

| 文件 | 说明 |
|------|------|
| `scripts/filter_standard_chromosomes_vcf.py` | 过滤逻辑；读取 `.vcf` / `.vcf.gz`，输出未压缩 VCF |

单独运行示例：

```bash
python3 modules/liftover/scripts/filter_standard_chromosomes_vcf.py \
  --input-vcf input.vcf.gz \
  --output-vcf output.standard.vcf \
  --ignored-tsv ignored.tsv \
  --stats-tsv stats.tsv
```

## 输出（相对 `--out-dir`）

| 路径 | 说明 |
|------|------|
| `00_liftover_filter/input.standard_chromosomes.vcf.gz` | 过滤后的 VCF |
| `00_liftover_filter/input.ignored_nonstandard_chromosomes.tsv` | 被忽略的变异（`chrom pos id ref alt reason`） |
| `00_liftover_filter/input.standard_chromosome_filter.stats.tsv` | 过滤统计 |

`full_pipeline.outputs.tsv` 中会写入 `liftover_filter_standard_chroms`、`liftover_standard_vcf`、`liftover_ignored_nonstandard_tsv` 等字段。

## API

FastAPI 字段 `liftover_filter_standard_chroms`（默认 `"yes"`），对应 CLI `--liftover-filter-standard-chroms`。详见 [`complete_pipeline/README.md`](../../complete_pipeline/README.md)。
