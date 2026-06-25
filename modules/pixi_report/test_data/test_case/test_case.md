### 字段来源和含义

| 字段 | 含义 | 来源和生成方式 |
| --- | --- | --- |
| `chrom` | 染色体/contig 名称。 | 优先来自原始输入 VCF 的 `CHROM` 列。wrapper 会读取原始 VCF 坐标，避免 VEP 对 indel 做坐标规范化后丢失原始坐标。找不到原始映射时，从 VEP `Uploaded_variation` 解析。 |
| `pos` | 1-based 变异位置。 | 优先来自原始输入 VCF 的 `POS` 列；找不到时从 VEP `Uploaded_variation` 解析。 |
| `ref` | 参考等位基因。 | 优先来自原始输入 VCF 的 `REF` 列；找不到时从 VEP `Uploaded_variation` 解析。 |
| `alt` | 替代等位基因。 | 优先来自原始输入 VCF 的 `ALT` 列。多等位基因 VCF 会按每个 ALT 等位基因建立原始坐标映射；找不到时从 VEP `Uploaded_variation` 解析。 |
| `vcf_info_*` | 原始 VCF `INFO` 字段。 | 仅 VCF 输入时输出。wrapper 根据 `##INFO=<ID=...>` 动态生成列，位置在 `alt` 后面。`Number=A` 字段会按当前 ALT 等位基因取对应值，`Number=R` 字段会取当前 ALT 对应的非 REF 值，其他字段原样输出；flag 字段写为 `1`。 |
| `vcf_info_REG_CCRE_ID` | 命中的 ENCODE SCREEN cCRE ID。 | 来自 VEP 前置的 bundled regulatory 注释。多个 cCRE ID 用逗号分隔，未命中为 `-`。 |
| `vcf_info_REG_CCRE_CLASS` | 命中的 cCRE 类型。 | 来自 ENCODE SCREEN cCRE overlap，例如 `PLS`、`pELS`、`dELS`、`CA-CTCF`、`CA-TF`、`TF`。 |
| `vcf_info_REG_CCRE_COUNT` | 当前变异区间重叠到的 cCRE 区间数。 | 由 `bin/annotate_regulatory.py` 按 VCF `POS` 和 `REF` 长度计算区间后与 bundled BED overlap 得到。 |
| `vcf_info_REG_CCRE_SOURCE` | regulatory 注释来源标签。 | 默认 `ENCODE_SCREEN_v4_GRCh38`。 |
| `gene_symbol` | 当前输出行对应的基因符号。 | 依次取 VEP `SYMBOL`、`Extra.SYMBOL`、`Gene` 的第一个非空值。 |
| `all_genes` | 同一个 `Uploaded_variation` 在本次 VEP 输出中命中的所有基因符号。 | wrapper 汇总同一变异 ID 下所有非空 `gene_symbol`，排序后用逗号连接。没有可汇总基因时退回当前行 `gene_symbol`。 |
| `transcript_id` | 当前 consequence 使用的转录本 ID。 | 来自 VEP `Feature`。当前默认使用 Ensembl transcript ID，例如 `ENST...`，并保留版本号。 |
| `refseq_id` | VEP 交叉引用到的 RefSeq transcript ID。 | 来自 `--xref_refseq` 生成的 `RefSeq` 字段，可能包含多个 `NM_`/`NR_`/`XM_`/`XR_` ID，用逗号分隔。 |
| `biotype` | transcript biotype。 | 来自 VEP `BIOTYPE`，例如 `protein_coding`、`processed_transcript`、`nonsense_mediated_decay`。部分 biotype 会影响 `tx_eligibility`。 |
| `canonical` | 是否为 VEP canonical transcript。 | 来自 VEP `CANONICAL`，通常为 `YES` 或 `-`。 |
| `mane` | MANE 标记。 | 来自 VEP `MANE`，常见值包括 `MANE_Select`、`MANE_Plus_Clinical`。 |
| `mane_select` | MANE Select RefSeq ID。 | 来自 VEP `MANE_SELECT`。非空时该 transcript 会获得较高 `tx_confidence_score`，并可能被强制保留。 |
| `mane_plus_clinical` | MANE Plus Clinical RefSeq ID。 | 来自 VEP `MANE_PLUS_CLINICAL`。非空时该 transcript 会获得较高 `tx_confidence_score`，并可能被强制保留。 |
| `appris` | APPRIS principal/alternative 标记。 | 来自 VEP `APPRIS`，例如 `P1`、`P4`、`A1`。principal transcript 在 `tx_confidence_score` 中加分更多。 |
| `tsl` | Transcript Support Level。 | 来自 VEP `TSL`。`1`、`2`、`3` 会在 `tx_confidence_score` 中加分；无其他支持的 `TSL=5` transcript 可能被排除。 |
| `ccds` | CCDS ID。 | 来自 VEP `CCDS`。非空时提高 transcript 置信度。 |
| `vep_pick` | VEP `PICK` 标记。 | 来自 VEP `--flag_pick`。wrapper 默认不使用 VEP `--pick` 截断输出，只把 `PICK=1` 作为 tie-break 和强制保留依据。 |
| `transcript_flags` | VEP transcript flags。 | 来自 VEP `FLAGS`。`cds_start_NF`、`cds_end_NF` 等不完整 CDS 标记会影响 `tx_exclusion_reason`。 |
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
| `clinical_gtex_tissue_whitelist` | 临床/表型相关 GTEx tissue 白名单。 | 来自 `--clinical-tissue`、`--clinical-tissues-file` 或 HPO 映射后的 GTEx v11 tissue 列名。未提供时为 `-`。 |
| `clinical_best_tissue` | 白名单内 TPM 最高的 tissue。 | 在 GTEx transcript TPM parquet 中按当前 `transcript_id` 查询。没有白名单或 transcript 未命中时为 `-`。 |
| `clinical_transcript_tpm` | `clinical_best_tissue` 中的 transcript TPM。 | 来自 GTEx v11 transcript TPM，数值会压缩成较短浮点格式。 |
| `gtex_transcript_max_tissue` | 当前 transcript 全局 TPM 最高的 GTEx tissue。 | 来自 GTEx v11 transcript TPM。 |
| `gtex_transcript_max_tpm` | `gtex_transcript_max_tissue` 中的 TPM。 | 来自 GTEx v11 transcript TPM。 |
| `gtex_transcript_top5_tissues` | 当前 transcript TPM 最高的 5 个 tissue。 | 格式为 `tissue:TPM;tissue:TPM`。 |
| `gtex_max_tissue_in_clinical_whitelist` | 全局最高 TPM tissue 是否落在临床白名单内。 | 有临床白名单时输出 `YES` 或 `NO`；没有白名单时为 `-`。 |
| `clinical_vs_global_tpm_ratio` | 临床白名单内最高 TPM / 全局最高 TPM。 | 用于判断表型 tissue 表达相对全局峰值的比例。 |
| `gtex_lookup_status` | GTEx transcript TPM 查询状态。 | 常见值：`ok`、`not_found`、`gtex_file_missing`、`duckdb_unavailable`、`disabled`。 |
| `tx_consequence_score` | transcript 选择用 consequence 分数。 | 根据 VEP consequence 计算，高影响 LoF 最高，missense/protein_altering 次之。不同于最终 pathogenic ranking 的 `consequence_score`。 |
| `tx_confidence_score` | transcript 选择用证据/可信度分数。 | MANE、APPRIS、CCDS、canonical、TSL、curated RefSeq 和 VEP PICK 加分，最高截断到 35。 |
| `clinical_expression_score` | transcript 选择用表达分数。 | 白名单 tissue 表达使用满权重：TPM `>=10/5/1/0.1` 分别为 `20/16/10/4`；没有白名单时使用全局最高 TPM 的半权重。 |
| `tx_tie_breaker_score` | transcript 选择 tie-break 分数。 | VEP PICK、HGVS、蛋白位置和蛋白结构域等轻量信号加分，最高 5。 |
| `tx_selection_score` | transcript 选择总分。 | `tx_consequence_score + tx_confidence_score + clinical_expression_score + tx_tie_breaker_score`。 |
| `tx_rank_within_variant` | 当前 variant-gene 分组内 transcript 排名。 | 仅 rankable transcript 会编号。排序按 selection score、consequence、confidence、expression、tie-break 依次比较。 |
| `tx_eligibility` | transcript 选择状态。 | 常见值：`primary`、`selected`、`forced`、`rescued`、`excluded`。`--no-transcript-selection` 时所有输出行会保留。 |
| `tx_exclusion_reason` | transcript 被降级/排除的原因。 | 可能包括 `predicted_refseq`、`biotype:<name>`、`non_protein_coding:<name>`、`incomplete_cds`、`tsl5_no_support`。 |
| `tx_rescue_reason` | 被排除 transcript 重新进入候选的原因。 | 可能为 `unique_high_impact_consequence`、`high_expression_with_possible_effect`、`no_primary_transcript_available`。 |
| `tx_selected_reason` | 输出行被选中的原因。 | 常见值：`top_k`、`force:mane_select`、`force:mane_plus_clinical`、`force:vep_pick`、`force:max_consequence`。 |
| `pathogenic_rank` | 致病性规则分数排序名次。 | wrapper 先计算内部 `raw_pathogenic_score`，按分数降序稳定排序，再从 1 开始编号。分数相同时保持 VEP 输出的相对顺序。内部总分不作为单独列输出，可在 `evidence_summary` 中看到 `total=...`。 |
| `evidence_summary` | 排名原因/总分解释。 | wrapper 把非零评分组件串成可读文本，例如 `ClinVar=...; consequence=...; CADD=...; EAS_AF=...; frequency(...); total=+104`。这列用于解释 `pathogenic_rank`，不参与 VEP 注释本身。 |
| `is_pseudogene` | 当前 `chrom,pos` 是否落在假基因区间。 | 来自 bundled `bin/annotate_pseudogene.py`，按 1-based inclusive 坐标判断，值为 `Yes` 或 `No`。 |
| `pseudogene_name` | 命中的 HGNC 假基因 symbol。 | 使用 bundled `vep_data/pseudogene/` 中的 GENCODE v49、Pseudogene.org Human90 和 HGNC 映射；多个 symbol 用 `;` 分隔。 |
| `pseudogene_source` | 假基因区间来源。 | 取值为 `GENCODE.v49`、`Pseudogene.org` 或 `Pseudogene.org&GENCODE.v49`；未命中为空。 |
