# `vep_output.sorted.csv` 表头字段说明

文件：`/mnt/workspace/wangzilu1/openrare_v3_api_service_test/output/P001_api_full/06_result_sorting/vep_output.sorted.csv`

本表是 OpenRare V3 全流程的最终排序结果。字段主要来自 4 类来源：

- 基础变异坐标：`chrom,pos,ref,alt`
- VCF INFO 回填：`vcf_info_*`，由 05 模块从进入 VEP 的 VCF 中展开得到
- VEP/插件注释：基因、转录本、后果、ClinVar、CADD、REVEL、SpliceAI、LoFTEE、gnomAD、GTEx 等
- OpenRare 排序与选择：`tx_*`、`pathogenic_rank`、`evidence_summary`

> 说明：`-` 通常表示当前记录无该项注释或该项不可用；`.` 多来自 VCF 原始缺失值。

## 字段总览

| 序号 | 字段名 | 含义 |
|---:|---|---|
| 1 | `chrom` | 染色体名称，来自 VCF/VEP 解析结果。 |
| 2 | `pos` | 变异位置。SNV 与 VCF POS 一致；indel 在 VEP 结果中可能使用 normalized 坐标，05 回填模块已兼容 VEP indel POS 比原始 VCF POS 多 1 的情况。 |
| 3 | `ref` | 参考等位基因。 |
| 4 | `alt` | 替代等位基因。 |
| 5 | `vcf_info_AC` | VCF INFO `AC`：该 ALT 等位基因的 allele count。多等位位点按 ALT 拆分匹配。 |
| 6 | `vcf_info_AF` | VCF INFO `AF`：该 ALT 等位基因频率。 |
| 7 | `vcf_info_AN` | VCF INFO `AN`：参与等位基因计数的总 allele number。 |
| 8 | `vcf_info_BaseQRankSum` | GATK 质量指标：REF 与 ALT reads 的 base quality RankSum 检验。 |
| 9 | `vcf_info_DP` | VCF INFO `DP`：总体测序深度或位点深度。 |
| 10 | `vcf_info_END` | VCF INFO `END`：区间型变异结束坐标。普通 SNV/小 indel 通常为空。 |
| 11 | `vcf_info_ExcessHet` | GATK 质量指标：过量杂合度统计值。 |
| 12 | `vcf_info_FS` | GATK FisherStrand：链偏倚 Fisher 精确检验 Phred 值。 |
| 13 | `vcf_info_InbreedingCoeff` | GATK 质量指标：近交系数估计。 |
| 14 | `vcf_info_MLEAC` | GATK 最大似然估计 ALT allele count。 |
| 15 | `vcf_info_MLEAF` | GATK 最大似然估计 ALT allele frequency。 |
| 16 | `vcf_info_MQ` | RMS mapping quality，reads 比对质量。 |
| 17 | `vcf_info_MQRankSum` | REF 与 ALT reads 的 mapping quality RankSum 检验。 |
| 18 | `vcf_info_QD` | Quality by Depth，QUAL/DP。 |
| 19 | `vcf_info_RAW_MQandDP` | GATK 原始 MQ 和 DP 中间统计值。 |
| 20 | `vcf_info_ReadPosRankSum` | REF 与 ALT reads 在 read 内位置分布的 RankSum 检验。 |
| 21 | `vcf_info_SOR` | Symmetric Odds Ratio，链偏倚相关指标。 |
| 22 | `vcf_info_BEAGLE_PHASED` | V3 phasing 模块写入：该位点是否经过 Beagle phasing 处理/标记。 |
| 23 | `vcf_info_CHN_REF_SUPPORT` | CHN 参考面板支持信息，来自 phasing/refsupport 模块。 |
| 24 | `vcf_info_CHN_ALT_CARRIER_COUNT` | CHN 参考面板中携带 ALT 的样本/个体数量。 |
| 25 | `vcf_info_CHN_ALT_AC` | CHN 参考面板中 ALT allele count。 |
| 26 | `vcf_info_PHASING_CONFIDENCE` | phasing/refsupport 模块给出的相位或参考支持置信度标记。 |
| 27 | `vcf_info_VAF` | 前置 VAF 模块计算的 variant allele fraction，通常为 ALT_DP / DP 或 ALT_DP / (REF_DP + ALT_DP)。 |
| 28 | `vcf_info_REF_DP` | 前置 VAF 模块计算/提取的 REF reads 深度。 |
| 29 | `vcf_info_ALT_DP` | 前置 VAF 模块计算/提取的 ALT reads 深度。 |
| 30 | `vcf_info_REG_CCRE_ID` | CRE 调控区注释：与变异重叠的 ENCODE SCREEN cCRE ID，多个以逗号合并。 |
| 31 | `vcf_info_REG_CCRE_CLASS` | CRE 调控区类别，例如 `PLS`、`pELS`、`dELS`、`CA-CTCF` 等。 |
| 32 | `vcf_info_REG_CCRE_COUNT` | 与该变异重叠的 cCRE 区间数量。 |
| 33 | `vcf_info_REG_CCRE_SOURCE` | CRE 数据源版本，当前为 ENCODE SCREEN / WengLab Registry GRCh38 资源。 |
| 34 | `vcf_info_NCRNA_GENE_ID` | ncRNA 注释：与变异重叠的 GENCODE 非编码 RNA gene ID。 |
| 35 | `vcf_info_NCRNA_GENE_NAME` | ncRNA 注释：重叠的 GENCODE 非编码 RNA gene name。 |
| 36 | `vcf_info_NCRNA_GENE_TYPE` | ncRNA 注释：重叠 gene 的类型，例如 lncRNA、miRNA、snRNA、snoRNA 等。 |
| 37 | `vcf_info_NCRNA_GENE_COUNT` | 与该变异重叠的 ncRNA gene 区间数量。 |
| 38 | `vcf_info_NCRNA_SOURCE` | ncRNA 数据源版本，当前来自 GENCODE v49 GRCh38 ncRNA BED。 |
| 39 | `vcf_info_is_pseudogene` | 假基因模块结果：`Yes` 表示命中假基因相关证据，`No` 表示未命中。 |
| 40 | `vcf_info_pseudogene_name` | 命中的假基因 HGNC symbol 列表；仅 reads 层面证据时可为 `-`；缺失时为 `.`。 |
| 41 | `vcf_info_pseudogene_source` | 假基因证据来源，例如 `GENCODE.v49`、`Pseudogene.org`、`Pseudogene.org&GENCODE.v49`、`Reads_mapped`。 |
| 42 | `gene_symbol` | VEP 注释到的基因 symbol。 |
| 43 | `all_genes` | 当前变异相关的所有基因 symbol 汇总。 |
| 44 | `transcript_id` | VEP 注释的转录本 ID，通常为 Ensembl transcript ID 或 RefSeq transcript ID。 |
| 45 | `refseq_id` | RefSeq 转录本 ID，若 VEP/xref 能匹配则填写。 |
| 46 | `biotype` | 转录本/基因生物类型，例如 `protein_coding`、`lncRNA` 等。 |
| 47 | `canonical` | 是否为 Ensembl canonical transcript。 |
| 48 | `mane` | MANE 相关标记汇总。 |
| 49 | `mane_select` | 是否为 MANE Select 转录本。 |
| 50 | `mane_plus_clinical` | 是否为 MANE Plus Clinical 转录本。 |
| 51 | `appris` | APPRIS 主转录本/功能证据等级。 |
| 52 | `tsl` | Transcript Support Level，转录本支持等级。 |
| 53 | `ccds` | CCDS ID，若该转录本在 CCDS 中有对应记录。 |
| 54 | `vep_pick` | VEP `PICK` 标记，表示 VEP 默认挑选的代表 consequence。 |
| 55 | `transcript_flags` | 转录本相关 flags，例如 incomplete CDS、异常支持等标记。 |
| 56 | `consequence` | VEP consequence term，例如 missense_variant、frameshift_variant、splice_donor_variant 等。 |
| 57 | `impact` | VEP consequence impact 等级：HIGH、MODERATE、LOW、MODIFIER。 |
| 58 | `hgvsc` | HGVS cDNA 层面描述。 |
| 59 | `hgvsp` | HGVS protein 层面描述。 |
| 60 | `cdna_position` | 变异在 cDNA 中的位置。 |
| 61 | `cds_position` | 变异在 CDS 中的位置。 |
| 62 | `protein_position` | 变异在蛋白中的位置。 |
| 63 | `amino_acids` | 氨基酸变化，VEP `Amino_acids`。 |
| 64 | `codons` | 密码子变化，VEP `Codons`。 |
| 65 | `exon` | 外显子编号/总数。 |
| 66 | `intron` | 内含子编号/总数。 |
| 67 | `strand` | 转录本链方向，通常为 `1` 或 `-1`。 |
| 68 | `protein_domains` | 蛋白结构域注释，来自 VEP domains 相关输出。 |
| 69 | `revel_score` | REVEL missense 致病性预测分数；越高通常越支持有害。 |
| 70 | `cadd_phred` | CADD PHRED 分数；越高通常表示变异更可能有功能影响。 |
| 71 | `gnomAD_popmax_AF` | gnomAD 各群体中最大的 ALT allele frequency。 |
| 72 | `gnomAD_eas_AF` | gnomAD East Asian 群体 ALT allele frequency。 |
| 73 | `gnomAD_nhomalt` | gnomAD 中 homozygous ALT 个体数量。 |
| 74 | `spliceAI_ds_max` | SpliceAI 四类 DS 分数的最大值；越高越提示剪接影响。 |
| 75 | `spliceAI_type` | 产生最大 SpliceAI DS 的剪接类型，例如 acceptor_gain、acceptor_loss、donor_gain、donor_loss。 |
| 76 | `loftee_lof_flag` | LoFTEE LoF 标记，例如 HC/LC，用于判断 loss-of-function 可信度。 |
| 77 | `loftee_lof_filter` | LoFTEE filter；非空通常表示 LoF 结果存在过滤/降级原因。 |
| 78 | `clinvar_significance` | ClinVar 临床意义，例如 Pathogenic、Likely_pathogenic、Benign、VUS 等。 |
| 79 | `clinvar_review_status` | ClinVar review status，例如 criteria provided、reviewed by expert panel 等。 |
| 80 | `clinvar_star_rating` | 根据 ClinVar review status 转换的星级/证据强度。 |
| 81 | `clinical_gtex_tissue_whitelist` | HPO/临床相关 GTEx 组织白名单；未传 HPO 时通常为默认或 `-`。 |
| 82 | `clinical_best_tissue` | 在临床相关组织白名单中表达最高的组织。 |
| 83 | `clinical_transcript_tpm` | `clinical_best_tissue` 中该转录本 TPM。 |
| 84 | `gtex_transcript_max_tissue` | GTEx 全组织中该转录本表达最高的组织。 |
| 85 | `gtex_transcript_max_tpm` | GTEx 全组织中该转录本最高 TPM。 |
| 86 | `gtex_transcript_top5_tissues` | GTEx 中该转录本表达最高的前 5 个组织及 TPM。 |
| 87 | `gtex_max_tissue_in_clinical_whitelist` | 全局最高表达组织是否落在临床组织白名单内，通常为 `YES`/`NO`。 |
| 88 | `clinical_vs_global_tpm_ratio` | 临床相关组织最高 TPM / 全局最高 TPM，用于衡量表达是否集中在相关组织。 |
| 89 | `gtex_lookup_status` | GTEx 表达查找状态，例如命中、未命中或无表达数据。 |
| 90 | `tx_consequence_score` | OpenRare 转录本选择分：按 consequence 严重程度给分。 |
| 91 | `tx_confidence_score` | OpenRare 转录本选择分：按 canonical、MANE、APPRIS、TSL、CCDS、VEP PICK 等转录本可信度给分。 |
| 92 | `clinical_expression_score` | OpenRare 转录本选择分：按 GTEx/HPO 相关组织表达量给分。 |
| 93 | `tx_tie_breaker_score` | OpenRare 转录本选择分：用于同分时打破平局的辅助分。 |
| 94 | `tx_selection_score` | 转录本选择总分，等于 `tx_consequence_score + tx_confidence_score + clinical_expression_score + tx_tie_breaker_score`。 |
| 95 | `tx_rank_within_variant` | 同一变异/基因下转录本排序名次；数值越小越优先。 |
| 96 | `tx_eligibility` | 转录本是否参与优先选择，例如 `primary` 或 `excluded`。 |
| 97 | `tx_exclusion_reason` | 转录本被排除的原因，例如 predicted RefSeq、非 protein coding、TSL5 且无支持等。 |
| 98 | `tx_rescue_reason` | 被排除转录本重新纳入候选的原因；无则为 `-`。 |
| 99 | `tx_selected_reason` | 当前转录本被选为代表转录本的原因说明。 |
| 100 | `pathogenic_rank` | 最终排序名次。06 模块按 OpenRare `_raw_pathogenic_score` 从高到低排序后生成，`1` 表示当前 CSV 中最高优先级。 |
| 101 | `evidence_summary` | 最终排序证据摘要，汇总 ClinVar、consequence、SpliceAI/LoFTEE、REVEL、CADD、gnomAD 频率、protein domain 等得分依据和总分。 |

## 关键字段补充说明

### `vcf_info_*`

`vcf_info_*` 字段不是 VEP 原生字段，而是 05 模块从 04 输入 VCF 的 INFO 中展开得到。字段名规则为：

```text
vcf_info_<原始 INFO ID>
```

例如 VCF 中 `REG_CCRE_CLASS=PLS` 会变成 CSV 中的 `vcf_info_REG_CCRE_CLASS`。

### 调控区与 ncRNA

- `REG_CCRE_*`：来自 ENCODE SCREEN / WengLab cCRE，表示变异是否直接重叠 promoter-like、enhancer-like、CTCF 等候选顺式调控元件。
- `NCRNA_*`：来自 GENCODE v49 ncRNA gene BED，表示变异是否重叠非编码 RNA 基因区间。

### 假基因

`is_pseudogene/pseudogene_name/pseudogene_source` 由 03 假基因模块写入 VCF INFO，然后由 05 模块回填到 CSV。坐标证据主要来自 GENCODE v49 pseudogene 和 Pseudogene.org，并结合 HGNC symbol 映射；数据库未命中时还可补充 reads 层面的判断。

### 转录本选择分数 `tx_*`

`tx_selection_score` 用于同一变异/基因下挑选更合适的转录本，包含：

```text
tx_selection_score = tx_consequence_score + tx_confidence_score + clinical_expression_score + tx_tie_breaker_score
```

其中：

- `tx_consequence_score`：后果越严重通常分数越高。
- `tx_confidence_score`：MANE、canonical、APPRIS、TSL、CCDS、VEP PICK 等证据越强分数越高。
- `clinical_expression_score`：在 HPO/临床相关组织中表达越支持，分数越高。
- `tx_tie_breaker_score`：用于稳定排序的辅助项。

### 最终排序 `pathogenic_rank`

06 模块根据 OpenRare 致病性打分排序。打分证据包括：

- ClinVar 临床意义和 review status
- VEP consequence 与 impact
- SpliceAI 剪接影响和 LoFTEE LoF 证据
- REVEL、CADD 预测分数
- gnomAD EAS/popmax AF 和 homozygous ALT 数量
- protein domain 命中情况

排序后 `pathogenic_rank=1` 表示当前结果表中最高优先级的候选记录。
