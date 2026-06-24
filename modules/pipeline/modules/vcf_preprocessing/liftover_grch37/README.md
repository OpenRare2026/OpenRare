# GRCh37/hg19 → GRCh38 liftover

本步骤在 **phasing 之前** 将 GRCh37/hg19 VCF 转为 GRCh38，供后续 Beagle phasing、VEP（GRCh38）使用。

实现为调用外部 JAR：`liftover-runner.jar`（Picard LiftoverVcf + bcftools norm），不内嵌 reference/chain。

## 依赖

- `java`（`JAVA_BIN`）
- JAR：`LIFTOVER_JAR`
- TOML：`LIFTOVER_CONFIG`（chain、GRCh38 FASTA、picard/bcftools 路径）
- 外部工具由 TOML 配置：`picard`、`bcftools`、`samtools`、`tabix`、`bgzip`

参考项目：

```text
/mnt/workspace/changan/grch37_to_grch38_liftover/
```

## 环境变量（`modules/pipeline/.env`）

| 变量 | 说明 |
|------|------|
| `LIFTOVER_JAR` | `liftover-runner.jar` 路径 |
| `LIFTOVER_CONFIG` | `liftover_config.toml` 路径 |

## 全流程触发

`run_full_pipeline.sh` 支持：

```bash
--input-assembly auto    # 默认：读 VCF `##reference=` 判断
--input-assembly GRCh37  # 强制 liftover
--input-assembly GRCh38  # 跳过 liftover
```

检测到 GRCh37 时输出目录：`--out-dir/00_liftover/`，下游使用：

```text
00_liftover/output/output.grch38.norm.vcf.gz
```

## 单独运行

```bash
cd modules/pipeline
pixi run python modules/vcf_preprocessing/liftover_grch37/scripts/run_liftover_vcf.py \
  --input /path/to/grch37.vcf.gz \
  --out-dir /path/to/00_liftover \
  --normalize true \
  --force true
```

仅检测 assembly：

```bash
pixi run python modules/vcf_preprocessing/liftover_grch37/scripts/run_liftover_vcf.py \
  --input /path/to/sample.vcf.gz \
  --detect-only
```

## JAR 输出结构

```text
<out-dir>/
├── output/output.grch38.norm.vcf.gz   # 下游输入（normalize=true）
├── rejected/rejected.vcf.gz
├── logs/
└── summary/summary.json
```
