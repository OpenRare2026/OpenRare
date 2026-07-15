# VEP Runner 安装说明

本模块通过 bioconda `ensembl-vep`（115.x，与 pixi 环境一致）运行 VEP，并加载 6 类扩展注释：

| 类型 | 名称 | 说明 |
|------|------|------|
| `--plugin` | CADD | SNV + indel 分数 |
| `--plugin` | SpliceAI | 剪接影响 |
| `--plugin` | AlphaMissense | missense 致病性 |
| `--plugin` | dbNSFP | SIFT/PolyPhen/REVEL/gnomAD 等 |
| `--plugin` | LoF (LoFTEE) | LoF 过滤 |
| `--custom` | ClinVar | 临床意义 overlay |

配置文件：[`config/vep_runner_config.json`](config/vep_runner_config.json)（路径使用 `${OPENRARE_DATA_ROOT}`）。

## 目录布局

默认由仓库根 `.env` 中的 `OPENRARE_DATA_ROOT` 指定（见 `.env.example`）：

```text
${OPENRARE_DATA_ROOT}/
├── vep_cache/                    # VEP offline cache + 插件 .pm
│   ├── homo_sapiens/             # vep_install 生成
│   └── Plugins/
│       ├── CADD.pm
│       ├── SpliceAI.pm
│       ├── AlphaMissense.pm
│       ├── dbNSFP.pm
│       └── loftee/               # LoFTEE（单独 git clone）
│           ├── LoF.pm
│           └── human_ancestor.fa.gz
├── vep_data/
│   ├── reference/GRCh38.p14.genome.fa
│   ├── CADD/
│   ├── SpliceAI/
│   ├── AlphaMissense/
│   ├── dbNSFP/
│   ├── ClinVar/
│   ├── GTEx/...
│   └── hpo_tpm/
└── tmp/
```

## 1. 安装 VEP 可执行文件（pixi）

```bash
cd /path/to/OpenRare/modules/pipeline
pixi install
pixi run vep --help    # 应显示 ensembl-vep 115.x
```

## 2. 安装 VEP cache（offline 注释必需）

```bash
export OPENRARE_DATA_ROOT=/path/to/your/data   # 或沿用 pixi 默认值

pixi run vep_install -a cf \
  -s homo_sapiens \
  -y GRCh38 \
  -c "${OPENRARE_DATA_ROOT}/vep_cache" \
  --CONVERT
```

或使用一键脚本（含 cache + 插件 .pm + LoFTEE）：

```bash
export OPENRARE_DATA_ROOT=/path/to/your/data
export OPENRARE_VEP_INSTALL_CACHE=yes
pixi run vep-setup-plugins
```

仅安装插件 Perl 模块（不下载 cache）：

```bash
pixi run vep-setup-plugins
```

脚本会：

1. 从 [Ensembl/VEP_plugins `release/115`](https://github.com/Ensembl/VEP_plugins/tree/release/115) 下载 `CADD.pm`、`SpliceAI.pm`、`AlphaMissense.pm`、`dbNSFP.pm`
2. `git clone` [LoFTEE](https://github.com/konradjk/loftee) 到 `vep_cache/Plugins/loftee`

**注意**：VEP 版本须与 cache、插件 release 分支一致（当前 pin `ensembl-vep 115.*`）。

## 3. 参考 FASTA（`--hgvs` 必需）

```bash
DATA="${OPENRARE_DATA_ROOT}/vep_data/reference"
mkdir -p "$DATA"
# 示例：从已有安装复制，或从 Ensembl/GENCODE 下载 GRCh38 参考序列
cp /path/to/GRCh38.p14.genome.fa "$DATA/"
pixi run samtools faidx "$DATA/GRCh38.p14.genome.fa"
```

## 4. 插件注释数据库（大文件，需手动下载）

下载后放到 `${OPENRARE_DATA_ROOT}/vep_data/`，并用 `pixi run bgzip` + `pixi run tabix` 建索引。

### CADD

| 文件 | 配置路径 |
|------|----------|
| `whole_genome_SNVs.tsv.gz` | `vep_data/CADD/whole_genome_SNVs.tsv.gz` |
| `gnomad.genomes.r4.0.indel.tsv.gz` | `vep_data/CADD/gnomad.genomes.r4.0.indel.tsv.gz` |

来源：https://cadd.gs.washington.edu/download

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/CADD"
cd "${OPENRARE_DATA_ROOT}/vep_data/CADD"
# 下载后：
pixi run tabix -s 1 -b 2 -e 2 whole_genome_SNVs.tsv.gz
pixi run tabix -s 1 -b 2 -e 2 gnomad.genomes.r4.0.indel.tsv.gz
```

### SpliceAI

| 文件 | 说明 |
|------|------|
| `spliceai_scores.masked.snv.ensembl_mane_v1.4.grch38.vcf.gz` | SNV |
| `spliceai_scores.empty.indel.grch38.vcf.gz` | indel（可为空占位 VCF） |

来源：Illumina / SpliceAI 发布资源（Basespace 或项目内镜像）。

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/SpliceAI"
pixi run tabix -p vcf spliceai_scores.masked.snv.ensembl_mane_v1.4.grch38.vcf.gz
pixi run tabix -p vcf spliceai_scores.empty.indel.grch38.vcf.gz
```

### AlphaMissense

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/AlphaMissense"
# AlphaMissense_hg38.tsv.gz — https://github.com/google-deepmind/alphamissense
pixi run tabix -s 1 -b 2 -e 2 AlphaMissense_hg38.tsv.gz
```

### dbNSFP

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/dbNSFP"
# dbNSFP5.3.1a_grch38.gz — https://sites.google.com/site/jpopgen/dbNSFP
# 按 dbNSFP 文档生成 GRCh38 合并文件后：
pixi run tabix -s 1 -b 2 -e 2 dbNSFP5.3.1a_grch38.gz
```

### LoFTEE human ancestor

```bash
# 应在 loftee 目录内：
# ${OPENRARE_DATA_ROOT}/vep_cache/Plugins/loftee/human_ancestor.fa.gz
# 来源见 LoFTEE README；可从已有工作站安装复制。
```

### ClinVar（custom annotation）

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/ClinVar"
cd "${OPENRARE_DATA_ROOT}/vep_data/ClinVar"
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
mv clinvar.vcf.gz clinvar_20260523.vcf.gz   # 或更新 config 中的文件名
pixi run tabix -p vcf clinvar_20260523.vcf.gz
```

### 转录本选择（非 VEP 插件，但 04 步需要）

| 资源 | 路径 |
|------|------|
| GTEx v11 transcript TPM parquet | `vep_data/GTEx/v11/expression/gtex_v11_transcript_tpm.parquet`（由 [`gtex_preprocess`](../../resource_mock/gtex_preprocess/README.md) 从官网数据预计算） |
| HPO→tissue 映射 | `vep_data/hpo_tpm/` |

## 5. 校验安装

```bash
pixi run vep-verify-plugins
```

或手动 dry-run（打印完整 VEP 命令，不执行）：

```bash
pixi run vep-dry-run
```

## 6. 从已有工作站复制（最快）

若本机已有完整 `vep_runner` 树，只需设置环境变量，无需重新下载：

```bash
export OPENRARE_DATA_ROOT=/path/to/vep_runner
pixi run vep-verify-plugins
```

## 常见问题

**VEP 版本与 cache 不匹配**

确保 `pixi.toml` 中 `ensembl-vep = "115.*"` 与 `vep_cache` 的 release 一致；必要时重新 `vep_install`。

**插件 .pm 找不到**

运行 `pixi run vep-setup-plugins`，或确认 `--dir_plugins` 指向 `${OPENRARE_DATA_ROOT}/vep_cache/Plugins`。

**LoFTEE 报错**

确认 `loftee/LoF.pm` 与 `human_ancestor.fa.gz` 存在；LoFTEE 需额外 `--dir_plugins` 指向 `loftee` 子目录（`run_vep_to_csv.py` 已自动处理）。

**禁用单个插件**

```bash
pixi run python modules/vep_runner/scripts/run_vep_to_csv.py \
  ... --disable-plugin cadd --disable-plugin spliceai
```

可选值：`cadd`、`spliceai`、`alphamissense`、`dbnsfp`、`loftee`、`clinvar`。
