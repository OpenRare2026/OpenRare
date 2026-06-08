# Self-contained VEP runner

This directory is intended to be copied as one bundle. It contains the VEP
runtime, VEP offline cache, plugins, plugin data, GRCh38 FASTA, and a Python
wrapper that writes CSV output.

## Layout

- `bin/vep`: VEP launcher rooted inside this directory
- `bin/run_vep_to_csv.py`: Python wrapper, VCF in and CSV out
- `config/vep_runner_config.json`: wrapper config with `__VEP_RUNNER__` placeholders
- `envs/vep`: conda VEP environment
- `vep_cache`: VEP offline cache and plugin `.pm` files
- `vep_data`: CADD, SpliceAI, AlphaMissense, dbNSFP, ClinVar, and reference FASTA data
- `examples/example.vcf`: BRAF example input
- `output/`: example outputs
- `logs/`: example logs

The wrapper resolves paths from its own location, so it can be called from any
working directory after the whole `vep_runner` directory is copied.

## Basic Usage

```bash
python3 /path/to/vep_runner/bin/run_vep_to_csv.py \
  -i input.vcf \
  -o output.csv \
  --hgvs \
  --log /path/to/vep_runner/logs/run.log
```

The default input format is VCF. Use `--format` for other VEP-supported formats.

By default the wrapper now keeps all VEP transcript consequences, annotates
transcript quality fields, selects top transcripts per variant-gene, then ranks
only the selected rows. To bypass transcript selection and output all
transcript-level consequences:

```bash
python3 /path/to/vep_runner/bin/run_vep_to_csv.py \
  -i input.vcf \
  -o output.all_transcripts.csv \
  --no-transcript-selection
```

Phenotype-aware transcript selection can take HPO IDs directly. The wrapper maps
HPO terms to a GTEx tissue whitelist before scoring transcript expression:

```bash
envs/gtex_query/bin/python bin/run_vep_to_csv.py \
  -i input.vcf \
  -o output.selected_transcripts.csv \
  --hgvs \
  --hpo-id HP:0001250 \
  --hpo-id HP:0004322
```

Multiple HPO IDs can also be comma-separated. `--top-n-hpo-tissues` controls how
many coarse HPO-derived tissue groups are kept before expanding them to GTEx
tissue names:

```bash
envs/gtex_query/bin/python bin/run_vep_to_csv.py \
  -i input.vcf \
  -o output.hpo.csv \
  --hgvs \
  --hpo-id HP:0001250,HP:0000825,HP:0008066 \
  --top-n-hpo-tissues 3
```

For large VCF files, use VEP forks:

```bash
envs/gtex_query/bin/python bin/run_vep_to_csv.py \
  -i large.vcf.gz \
  -o large.vep.csv \
  --hgvs \
  --fork 8
```

## CSV Columns

CSV 输出下面这些核心列。缺失值统一写成 `-`，不会写空字符串。
如果输入格式是 VCF，wrapper 还会从原始 VCF header 读取 `##INFO`
定义，并把每个 INFO 字段作为动态列插入到 `alt` 后面，列名格式为
`vcf_info_<INFO_ID>`，例如 `vcf_info_AC`、`vcf_info_AF`、`vcf_info_DP`。
默认配置使用 Ensembl transcript ID，并通过 `--xref_refseq` 保留对应
RefSeq `NM_`/`NR_`。默认不使用 VEP `--pick`；VEP `PICK=1` 只作为
`vep_pick` 字段参与轻量 tie-break。

```text
chrom,pos,ref,alt,[vcf_info_*],gene_symbol,all_genes,transcript_id,refseq_id,biotype,canonical,mane,mane_select,mane_plus_clinical,appris,tsl,ccds,vep_pick,transcript_flags,consequence,impact,hgvsc,hgvsp,cdna_position,cds_position,protein_position,amino_acids,codons,exon,intron,strand,protein_domains,revel_score,cadd_phred,gnomAD_popmax_AF,gnomAD_eas_AF,gnomAD_nhomalt,spliceAI_ds_max,spliceAI_type,loftee_lof_flag,loftee_lof_filter,clinvar_significance,clinvar_review_status,clinvar_star_rating,clinical_gtex_tissue_whitelist,clinical_best_tissue,clinical_transcript_tpm,gtex_transcript_max_tissue,gtex_transcript_max_tpm,gtex_transcript_top5_tissues,gtex_max_tissue_in_clinical_whitelist,clinical_vs_global_tpm_ratio,gtex_lookup_status,tx_consequence_score,tx_confidence_score,clinical_expression_score,tx_tie_breaker_score,tx_selection_score,tx_rank_within_variant,tx_eligibility,tx_exclusion_reason,tx_rescue_reason,tx_selected_reason,pathogenic_rank,evidence_summary
```

### 字段来源和含义

| 字段 | 含义 | 来源和生成方式 |
| --- | --- | --- |
| `chrom` | 染色体/contig 名称。 | 优先来自原始输入 VCF 的 `CHROM` 列。wrapper 会读取原始 VCF 坐标，避免 VEP 对 indel 做坐标规范化后丢失原始坐标。找不到原始映射时，从 VEP `Uploaded_variation` 解析。 |
| `pos` | 1-based 变异位置。 | 优先来自原始输入 VCF 的 `POS` 列；找不到时从 VEP `Uploaded_variation` 解析。 |
| `ref` | 参考等位基因。 | 优先来自原始输入 VCF 的 `REF` 列；找不到时从 VEP `Uploaded_variation` 解析。 |
| `alt` | 替代等位基因。 | 优先来自原始输入 VCF 的 `ALT` 列。多等位基因 VCF 会按每个 ALT 等位基因建立原始坐标映射；找不到时从 VEP `Uploaded_variation` 解析。 |
| `vcf_info_*` | 原始 VCF `INFO` 字段。 | 仅 VCF 输入时输出。wrapper 根据 `##INFO=<ID=...>` 动态生成列，位置在 `alt` 后面。`Number=A` 字段会按当前 ALT 等位基因取对应值，`Number=R` 字段会取当前 ALT 对应的非 REF 值，其他字段原样输出；flag 字段写为 `1`。 |
| `gene_symbol` | 当前输出行对应的基因符号。 | 依次取 VEP `SYMBOL`、`Extra.SYMBOL`、`Gene` 的第一个非空值。 |
| `all_genes` | 同一个 `Uploaded_variation` 在本次 VEP 输出中命中的所有基因符号。 | wrapper 汇总同一变异 ID 下所有非空 `gene_symbol`，排序后用逗号连接。没有可汇总基因时退回当前行 `gene_symbol`。 |
| `transcript_id` | 当前 consequence 使用的转录本 ID。 | 来自 VEP `Feature`。默认 `--refseq` 时通常为 RefSeq `NM_`/`NR_`；如果使用非 RefSeq cache，则可能是 Ensembl `ENST`。 |
| `consequence` | VEP consequence 术语。 | 来自 VEP `Consequence`，例如 `missense_variant`、`splice_donor_variant`、`intron_variant`。 |
| `impact` | VEP consequence 影响等级。 | 来自 VEP `IMPACT` 或 `Extra.IMPACT`，取值通常为 `HIGH`、`MODERATE`、`LOW`、`MODIFIER`。 |
| `hgvsc` | cDNA 层面的 HGVS 改变。 | 来自 VEP `HGVSc` 或 `Extra.HGVSc`。wrapper 会 URL decode，并去掉转录本前缀，只保留冒号后的部分，例如 `NM_004333.6:c.1799T>A` 输出为 `c.1799T>A`。需要 `--hgvs` 和配置中的 FASTA。 |
| `hgvsp` | 蛋白层面的 HGVS 改变。 | 来自 VEP `HGVSp` 或 `Extra.HGVSp`。wrapper 会 URL decode，并去掉蛋白/转录本前缀，只保留冒号后的部分，例如输出 `p.Val600Glu`。同义突变会显示 `p.Ser290=`，不是 URL 编码的 `%3D`。 |
| `cdna_position` | cDNA 位置。 | 来自 VEP `cDNA_position`。 |
| `cds_position` | CDS 编码区位置。 | 来自 VEP `CDS_position`。 |
| `protein_position` | 蛋白氨基酸位置。 | 来自 VEP `Protein_position`。 |
| `amino_acids` | 氨基酸变化。 | 来自 VEP `Amino_acids`，例如 `R/C`、`V/E`。 |
| `codons` | 密码子变化。 | 来自 VEP `Codons`，例如 `Cgt/Tgt`。 |
| `exon` | 外显子编号。 | 来自 VEP `EXON` 或 `Extra.EXON`，常见格式为 `6/27`。 |
| `intron` | 内含子编号。 | 来自 VEP `INTRON` 或 `Extra.INTRON`，常见格式为 `2/15`。 |
| `strand` | 转录本链方向。 | 来自 VEP `STRAND` 或 `Extra.STRAND`。`1` 表示正链，`-1` 表示负链。 |
| `protein_domains` | 蛋白结构域注释。 | 来自 VEP `DOMAINS` 或 `Extra.DOMAINS`，由 VEP `--domains` 产生。 |
| `revel_score` | REVEL missense pathogenicity score。 | 来自 dbNSFP 插件字段 `REVEL_score`。没有 dbNSFP 命中或该变异不适用时为 `-`。 |
| `cadd_phred` | CADD PHRED score。 | 依次取 dbNSFP 风格字段 `CADD_phred`、`Extra.CADD_phred`、CADD 插件风格字段 `CADD_PHRED`、`Extra.CADD_PHRED` 的第一个非空值。 |
| `gnomAD_popmax_AF` | gnomAD population maximum allele frequency。 | 优先来自 dbNSFP `gnomAD4.1_joint_POPMAX_AF`。如果缺失，wrapper 从 VEP cache 的 gnomAD exome/genome population AF 字段中取最大值；如果 population AF 都缺失，再退回 `max(gnomADe_AF, gnomADg_AF)`。 |
| `gnomAD_eas_AF` | gnomAD East Asian allele frequency。 | 优先来自 dbNSFP `gnomAD4.1_joint_EAS_AF`。如果缺失，退回 VEP cache 字段 `max(gnomADe_EAS_AF, gnomADg_EAS_AF)`。 |
| `gnomAD_nhomalt` | gnomAD homozygous alternate count。 | 来自 dbNSFP `gnomAD4.1_joint_nhomalt` 或 `Extra.gnomAD4.1_joint_nhomalt`。VEP cache 的 gnomAD AF 不提供 homozygote alternate count，所以没有 dbNSFP 命中时通常为 `-`。 |
| `spliceAI_ds_max` | SpliceAI 四类 delta score 的最大值。 | 来自 SpliceAI 插件 `SpliceAI_pred`。wrapper 解析 `DS_AG`、`DS_AL`、`DS_DG`、`DS_DL`，取最大分数。 |
| `spliceAI_type` | `spliceAI_ds_max` 对应的剪接影响类型。 | 由 SpliceAI 最大分数对应的字段决定：`DS_AG` -> `acceptor_gain`，`DS_AL` -> `acceptor_loss`，`DS_DG` -> `donor_gain`，`DS_DL` -> `donor_loss`。如果最大分数不存在或 <= 0，则为 `-`。 |
| `loftee_lof_flag` | LOFTEE LoF 判断。 | 来自 LOFTEE 插件 `LoF` 或 `Extra.LoF`，常见值包括 `HC`、`LC`。 |
| `loftee_lof_filter` | LOFTEE 过滤原因。 | 来自 LOFTEE 插件 `LoF_filter` 或 `Extra.LoF_filter`。非空通常表示该 LoF 判断被某些规则过滤或降级。 |
| `clinvar_significance` | ClinVar 临床意义。 | 来自自定义 ClinVar VCF 注释字段 `ClinVar_CLNSIG` 或 `Extra.ClinVar_CLNSIG`，下划线会转为空格。缺失为 `-`。 |
| `clinvar_review_status` | ClinVar review status。 | 来自自定义 ClinVar VCF 注释字段 `ClinVar_CLNREVSTAT` 或 `Extra.ClinVar_CLNREVSTAT`，下划线会转为空格。缺失为 `-`。 |
| `clinvar_star_rating` | ClinVar 证据星级，0-4。 | wrapper 根据原始 `CLNREVSTAT` 计算：`practice_guideline` -> 4；`reviewed_by_expert_panel` -> 3；`criteria_provided,_multiple_submitters,_no_conflicts` -> 2；`criteria_provided,_single_submitter` 或 conflicting criteria -> 1；其他或缺失 -> 0。 |
| `pathogenic_rank` | 致病性规则分数排序名次。 | wrapper 先计算内部 `raw_pathogenic_score`，按分数降序稳定排序，再从 1 开始编号。分数相同时保持 VEP 输出的相对顺序。内部总分不作为单独列输出，可在 `evidence_summary` 中看到 `total=...`。 |
| `evidence_summary` | 排名原因/总分解释。 | wrapper 把非零评分组件串成可读文本，例如 `ClinVar=...; consequence=...; CADD=...; EAS_AF=...; frequency(...); total=+104`。这列用于解释 `pathogenic_rank`，不参与 VEP 注释本身。 |

### 转录本选择和强制保留

默认输出不是 VEP 原始全量 transcript consequence。wrapper 会先保留 VEP
输出的 transcript-level consequence，补充 MANE、APPRIS、TSL、CCDS、RefSeq、
GTEx 表达等字段，再按每个 `chrom,pos,ref,alt,gene_symbol` 分组选出
`--top-k-transcripts` 条主转录本，默认 `5` 条。

除 top-k 外，下面这些 transcript 会被强制保留，避免临床或高影响转录本被
top-k 截掉：

- `MANE Select`
- `MANE Plus Clinical`
- `VEP PICK`
- 最高 `tx_consequence_score` 的最佳 transcript

这些保留原因写在 `tx_selected_reason` 中，例如 `top_k`、
`force:mane_select`、`force:mane_plus_clinical`、`force:vep_pick` 或
`force:max_consequence`。如果 transcript 已经在 top-k 中，原因通常显示
为 `top_k`。使用 `--no-transcript-selection` 可跳过选择并输出全量
transcript consequence。

### 排名分数规则

`pathogenic_rank` 使用下面的规则分数。该规则用于候选变异优先级排序，
不是临床诊断结论。

1. `clinvar_score`
   ClinVar significance 先给基础分：
   `pathogenic=40`，`likely_pathogenic=30`，
   `pathogenic/likely_pathogenic=35`，`uncertain_significance=3`，
   `conflicting_interpretations=0`，`likely_benign=-25`，
   `benign=-35`，`benign/likely_benign=-30`。
   非零基础分再乘以星级因子和 review 因子：
   star 4/3/2/1/0 分别为 `1.20/1.15/1.10/1.00/1.00`；
   `practice_guideline` 和 `reviewed_by_expert_panel` 为 `1.15`，
   `criteria_provided_multiple_submitters_no_conflicts` 为 `1.10`。
   良性项额外乘以调整因子：
   `benign=0.95`，`likely_benign=0.90`，
   `benign/likely_benign=0.925`。
   最终 ClinVar 分数为 `round(base * star_factor * review_factor * benign_adjust_factor)`。

2. `consequence_score`
   先从 `consequence` 中选择分数最高的术语，再叠加 `impact` 分。
   consequence 基础分：
   `transcript_ablation=30`，`splice_acceptor_variant=28`，
   `splice_donor_variant=28`，`stop_gained=28`，
   `frameshift_variant=28`，`stop_lost=24`，`start_lost=22`，
   `missense_variant=12`，`protein_altering_variant=12`，
   `inframe_insertion=10`，`inframe_deletion=10`，
   `splice_region_variant=6`，`synonymous_variant=2`，
   `intron_variant=0`，`upstream_gene_variant=-3`，
   `downstream_gene_variant=-3`，`intergenic_variant=-5`。
   impact 分：
   `HIGH=5`，`MODERATE=3`，`LOW=0`，`MODIFIER=-3`。

3. `splice_lof_score`
   SpliceAI 最大分数 `spliceAI_ds_max`：
   `>=0.8` 加 20，`>=0.5` 加 15，`>=0.2` 加 8，
   `>=0.1` 加 3；如果 `>=0.2` 且 `spliceAI_type` 非空，再加 2。
   对 LoF consequence，LOFTEE 也参与该项：
   `loftee_lof_filter` 非空记 `-8`；`loftee_lof_flag=HC` 加 15；
   `LC` 加 5；其他非空 flag 记 `-3`。

4. `prediction_score`
   只对 `missense_variant` 或 `protein_altering_variant` 使用 REVEL。
   REVEL：`>=0.9` 加 15，`>=0.75` 加 12，
   `>=0.5` 加 8，`>=0.25` 加 3。
   CADD：`>=30` 加 12，`>=25` 加 9，
   `>=20` 加 6，`>=10` 加 2。

5. `frequency_score`
   如果有 `gnomAD_eas_AF`，优先使用 EAS AF：
   `<0.0001` 加 10，`<0.001` 加 8，`<0.01` 加 3，
   `<=0.05` 记 `-10`，`>0.05` 记 `-25`。
   同时如果 `gnomAD_popmax_AF > 0.05`，额外 `-10`；
   如果 `gnomAD_popmax_AF > 0.01`，额外 `-5`。
   如果没有 EAS AF，则使用 popmax AF：
   `<0.0001` 加 8，`<0.001` 加 6，`<0.01` 加 2，
   `<=0.05` 记 `-8`，`>0.05` 记 `-20`。
   `gnomAD_nhomalt` 也会扣分：`1-5` 记 `-3`，
   `6-20` 记 `-8`，`>20` 记 `-15`。

6. `domain_score`
   `protein_domains` 非空时加 3，否则为 0。

最终：

```text
raw_pathogenic_score =
  clinvar_score
  + consequence_score
  + splice_lof_score
  + prediction_score
  + frequency_score
  + domain_score
```

CSV 不输出这些中间 score 列，只输出排序后的 `pathogenic_rank` 和用于解释
总分的 `evidence_summary`。

## Plugins Enabled By Default

- CADD
- SpliceAI
- AlphaMissense
- dbNSFP
- LOFTEE
- ClinVar custom VCF annotation

dbNSFP uses a practical default field set:
`SIFT_score`, `SIFT_pred`, `Polyphen2_HDIV_score`, `Polyphen2_HDIV_pred`,
`REVEL_score`, `CADD_phred`, and gnomAD 4.1 joint fields for
`gnomAD_popmax_AF`, `gnomAD_eas_AF`, and `gnomAD_nhomalt`.
For broader AF coverage, the wrapper also enables VEP cache gnomAD v4.1 with
`--af_gnomade` and `--af_gnomadg`; if dbNSFP has no AF for a variant,
`gnomAD_popmax_AF` and `gnomAD_eas_AF` fall back to those VEP cache values.
`gnomAD_nhomalt` is still dbNSFP-only because the VEP cache AF fields do not
include homozygote counts.

## gnomAD Field Strategy

The output gnomAD columns are built from two sources:

```text
1. dbNSFP gnomAD 4.1 joint fields
2. VEP offline cache gnomAD v4.1 fields
```

The wrapper uses dbNSFP first when available:

```text
gnomAD4.1_joint_POPMAX_AF  -> gnomAD_popmax_AF
gnomAD4.1_joint_EAS_AF     -> gnomAD_eas_AF
gnomAD4.1_joint_nhomalt    -> gnomAD_nhomalt
```

If dbNSFP has no AF for a variant, the wrapper falls back to VEP cache values:

```text
gnomAD_popmax_AF = max(
  gnomADe_AFR_AF, gnomADe_AMR_AF, gnomADe_ASJ_AF, gnomADe_EAS_AF,
  gnomADe_FIN_AF, gnomADe_MID_AF, gnomADe_NFE_AF,
  gnomADe_REMAINING_AF, gnomADe_SAS_AF,
  gnomADg_AFR_AF, gnomADg_AMI_AF, gnomADg_AMR_AF, gnomADg_ASJ_AF,
  gnomADg_EAS_AF, gnomADg_FIN_AF, gnomADg_MID_AF, gnomADg_NFE_AF,
  gnomADg_REMAINING_AF, gnomADg_SAS_AF
)

gnomAD_eas_AF = max(gnomADe_EAS_AF, gnomADg_EAS_AF)
```

If all population AF values are missing, `gnomAD_popmax_AF` falls back to
`max(gnomADe_AF, gnomADg_AF)`.

Current limitation:

```text
gnomAD_nhomalt is only populated from dbNSFP.
```

The VEP cache exposes gnomAD allele frequencies but not homozygote alternate
counts, so `gnomAD_nhomalt` may be empty even when `gnomAD_popmax_AF` and
`gnomAD_eas_AF` are populated from the VEP cache.

Empirical check on `P001.genotyper1000.vcf`:

```text
dbNSFP-only gnomAD AF coverage:       1 / 1000 variants
dbNSFP + VEP cache fallback coverage: 959 / 1000 variants
gnomAD_nhomalt coverage:              1 / 1000 variants
```

LOFTEE is configured from the bundled `vep_cache/Plugins/loftee` directory with
GERP/PhyloCSF conservation inputs disabled. The CSV exposes `LoF` as
`loftee_lof_flag` and `LoF_filter` as `loftee_lof_filter`.

ClinVar is configured from the bundled
`vep_data/ClinVar/clinvar_20260523.vcf.gz` file and its `.tbi` index. The CSV
exposes `CLNSIG` as `clinvar_significance`, `CLNREVSTAT` as
`clinvar_review_status`, and a calculated 0-4 `clinvar_star_rating`.
Missing ClinVar significance and review status values are written as `-`.

You can disable one plugin if needed:

```bash
--disable-plugin dbnsfp
--disable-plugin clinvar
```

## HGVS

`--hgvs` is ready to use. The bundle includes:

- `vep_data/reference/GRCh38.p14.genome.fa`
- `vep_data/reference/GRCh38.p14.genome.fa.fai`

## Test Command

```bash
python3 /path/to/vep_runner/bin/run_vep_to_csv.py \
  -i /path/to/vep_runner/examples/example.vcf \
  -o /path/to/vep_runner/output/example.test.csv \
  --hgvs
```

Expected result includes `consequence=missense_variant`, `gene_symbol=BRAF`,
`transcript_id=NM_004333.6`, `hgvsc=c.1799T>A`, and
`hgvsp=p.Val600Glu`.

## HPO Tissue TPM Export

This bundle also includes a standalone HPO-to-expression helper:

- `bin/export_hpo_tissue_tpm.py`: maps HPO IDs to coarse tissues, then exports
  GTEx/HPA expression evidence as `TPM.csv`
- `vep_data/hpo_tpm/`: bundled HPO, UBERON, HGNC, BioMart, GTEx v10, and HPA
  data used by the exporter
- `requirements-hpo-tpm.txt`: Python dependencies for this helper

Install the helper dependencies:

```bash
python3 -m pip install --user -r /path/to/vep_runner/requirements-hpo-tpm.txt
```

The bundled `envs/gtex_query/bin/python` environment already includes these
dependencies in this copy.

Run with HPO IDs from a file:

```bash
python3 /path/to/vep_runner/bin/export_hpo_tissue_tpm.py \
  --hpo-file /path/to/hpo_ids.txt \
  --output-csv /path/to/TPM.csv \
  --audit-json /path/to/tpm_audit.json
```

The default GTEx input is
`GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz` from
`vep_data/hpo_tpm/`. Override the data directory with `HPO_TPM_DATA_DIR` or
`--data-dir`, and override individual inputs with flags such as `--gtex-file`,
`--hpa-rna-file`, `--hpo-obo`, and `--uberon-obo`.

## FastAPI Service

Install the API-only Python dependencies:

```bash
python3 -m pip install --user -r /path/to/vep_runner/requirements-api.txt
```

Start the service:

```bash
/path/to/vep_runner/bin/serve_api.sh
```

By default it listens on `0.0.0.0:8000`. Override with `VEP_API_HOST` and
`VEP_API_PORT` if needed. The OpenAPI UI is available at `/docs`.

Submit a VCF:

```bash
curl -s -X POST http://127.0.0.1:8000/runs \
  -F file=@/path/to/vep_runner/examples/example.vcf \
  -F hgvs=true \
  -F fork=8
```

Submit a VCF with multiple HPO IDs:

```bash
curl -s -X POST http://127.0.0.1:8000/runs \
  -F file=@/path/to/input.vcf \
  -F hgvs=true \
  -F fork=8 \
  -F hpo_id="HP:0001250,HP:0000825,HP:0008066" \
  -F top_n_hpo_tissues=3
```

The response includes a `job_id` and a stable `result_url`. You can poll that
same `result_url`: while VEP is still running it returns JSON with HTTP 202;
after VEP succeeds, it returns the CSV file directly. API JSON responses expose
these public `status` values:

```text
queuing    waiting or still running
completion finished successfully
failure    failed
```

```bash
curl -s http://127.0.0.1:8000/runs/JOB_ID
curl -L -o result.csv http://127.0.0.1:8000/runs/JOB_ID/result
```

Example polling loop:

```bash
RESULT_URL="http://127.0.0.1:8000/runs/JOB_ID/result"
while true; do
  code=$(curl -sS -w "%{http_code}" -o result.csv "$RESULT_URL")
  if [ "$code" = "200" ]; then
    echo "result.csv is ready"
    break
  fi
  cat result.csv
  sleep 10
done
```

Useful form fields for `POST /runs`:

- `hgvs`: `true` or `false`, default `true`
- `no_pick`: legacy flag; transcript selection now keeps VEP consequences before wrapper selection
- `no_transcript_selection`: `true` outputs all transcript-level consequences after annotation
- `top_k_transcripts`: number of primary transcripts selected per variant-gene, default `5`
- `clinical_tissue`: comma-separated GTEx tissue names for phenotype-aware expression scoring
- `hpo_id`: comma-separated HPO IDs, for example `HP:0001250,HP:0000825`
- `top_n_hpo_tissues`: number of coarse HPO-derived tissue groups to keep, default `3`
- `format`: VEP input format, default `vcf`
- `fork`: VEP fork count, default `1`
- `disable_plugins`: comma-separated plugin names, for example `dbnsfp,loftee`
- `keep_raw_vep`: `true` keeps the raw VEP tab output in the job directory

VCF input through the API uses the same final CSV conversion as the CLI, so
dynamic `vcf_info_*` columns are included in downloaded results. HPO-aware runs
are reflected in `clinical_gtex_tissue_whitelist`, `clinical_best_tissue`,
`clinical_transcript_tpm`, `clinical_expression_score`, and
`tx_selection_score`.

Job files are written under `api_jobs/` by default. Override with
`VEP_API_JOB_DIR`.
