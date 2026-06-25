# report.md 字段来源注释（26B01490717 · V3 宽表）

对应文件：[report.md](./report.md) · 结构化快照：[context.json](./context.json) · 宽表字段详解：[../../宽表字段说明.md](../../宽表字段说明.md)

**本报告输入**

| 项目 | 路径 / 值 |
|------|-----------|
| 样本 manifest | `test_v3_P001.csv` |
| 排序宽表 | `vep_output.sorted.csv`（OpenRare V3，**101 列**） |
| 样本 ID | `26B01490717` |
| Top 5 基因 | AURKAIP1, VWA1, ATAD3B, CCNL2, ENSG00000241860 |
| 生成日期 | 2026-06-15 |

**图例**

| 标记 | 含义 |
|------|------|
| 🟢 宽表 | `vep_output.sorted.csv` 经 `report/wide_table.py` 读取/聚合 |
| 🟡 静态 | Jinja 模板固定文案 |
| 🟣 工具 | 脚本调用的 MCP / 本地 DB / API（确定性） |
| 🔵 Agent | `build_report_gene_agent` / `build_report_clinical_agent`（LLM，受 prompt 约束） |
| 🟠 规则 | 脚本阈值、格式化、筛选、去重逻辑（非 LLM） |

**流水线顺序**

```text
test_v3_P001.csv → V3 宽表 → Reactome → Open Targets 表型
→ NCBI Gene 功能 → OMIM 遗传模式 → 严格用药筛选
→ Agent 叙事 → 模板渲染 → report.md
```

---

## 页眉

| 报告字段 | 来源 |
|----------|------|
| 报告版本 `v1.1` | 🟡 `ReportContext.report_version` 默认值 |
| 生成日期 | 🟠 `SampleMeta.report_date`（运行日） |
| 分析基础 / 宽表路径 | 🟢 manifest「宽表」→ `meta.wide_table_path` |

---

## §1 报告头部

| 报告字段 | 来源 |
|----------|------|
| 样本 ID | 🟢 manifest「样本编号」→ `meta.sample_id` |
| 家系类型 / 家系关系 | 🟢 manifest 首列「家系类型」、列「家系关系」 |
| 临床诊断 / 指征 | 🟢 manifest「临床信息」→ `meta.clinical_info` |
| HPO 表型 | 🟢 manifest「raghpo」→ `meta.hpo_raw`（**本例为 RAG job UUID，非 HPO ID**） |
| 报告受众 `clinician` | 🟡 `header.md.j2` 默认 |
| 分析目的 | 🟡 模板固定 |
| 排序宽表来源 | 🟢 `meta.wide_table_path` |
| VCF 来源 | 🟢 manifest「gz to vcf」→ `meta.vcf_path` |
| GRCh38 转换 | 🟢 manifest「37 to 38」→ `meta.liftover_path` |
| 分析日期 / 报告人 / 关键提示 | 🟡 模板 |

**说明**：manifest「raghpo-returns」JSON 中含真实 HPO（`HP:0000365` 听力障碍等），见 `meta.json` → `raghpo_returns`；当前 §1 未解析展示，Agent 主要依据 `clinical_info` 文本做表型匹配。

---

## §2.1 Top 基因快速列表

| 报告列 | 来源 |
|--------|------|
| 排名 | 🟠 `wide_table.py` 按基因内最小 `pathogenic_rank` 排序后的序号 |
| 基因 | 🟢 宽表 `gene_symbol` |
| 变异数 | 🟠 宽表按 `(chrom,pos,ref,alt)` 去重后组内计数（本例 Top5 合计 **215** 个位点） |
| 最高排序名次 | 🟢 宽表 `pathogenic_rank`（组内最小；如 AURKAIP1 **#16**） |
| ClinVar | 🟢 宽表 `clinvar_significance`（代表变异；本例 Top5 多为 `-`） |
| 主要关联表型 | 🟣 **Open Targets** `report/open_targets_lookup.lookup_main_associated_phenotype` |
| 主要关联通路 | 🟣 **Reactome Neo4j** `report/pathways.attach_reactome_pathways` → `main_pathway`；无命中为 `-` |

段落「Top 5 基因、215 个变异」：🟠 `summary` 与各卡 `variant_count` 求和。

---

## §2.2 关键发现提示

| 内容 | 来源 |
|------|------|
| 全文 bullet | 🔵 **临床建议 Agent** → `ClinicalAdvice.key_findings` |
| Agent 输入 | `clinical_info`、各基因宽表摘要（含 **vaf/read_support/sequencing_quality_note**）、`strict_drug_candidates`、Open Targets 预填表型 |
| Agent 工具 | `lookup_gene`、`get_gene_disease_associations`、可选 `paper_search_search_pubmed` |
| 第 4 条 reads/AF 不一致 | 🔵 Agent 引用宽表 **`sequencing_quality_note`** / **`genomic_context`**（🟠 `report/models.py` 规则生成） |
| 用药无候选 | 🔵 Agent 总结 + 🟠 各基因 `drug_recommendations=[]` |

---

## §2.3 排序得分白盒

| 内容 | 来源 |
|------|------|
| 示例基因 AURKAIP1 | 🟠 模板取 `gene_cards[0]` |
| 得分树 | 🟢 宽表 `evidence_summary` → 🟠 `render.parse_evidence_tree()` |
| 原始计分 | 宽表上游 OpenRare 06 模块（ClinVar/consequence/CADD/gnomAD 等） |

---

## §3 基因卡片 — 通用结构（5 张卡同逻辑）

以下以 **AURKAIP1 §3.1.3.1** 为例；VWA1 / ATAD3B / CCNL2 / ENSG00000241860 列名相同。

### §3.x.1 基因概述

| 报告字段 | 来源 |
|----------|------|
| 基因名 | 🟢 `gene_symbol` |
| 染色体位置 | 🟢 代表变异 `chrom` + `pos` |
| 主要转录本 | 🟢 `mane_select`；空则 `transcript_id` |
| 基因功能 | 🟣 **NCBI Gene (Entrez)** `report/gene_function_enrich.py` → `script_gene_function`；🔵 Agent **原样**写入 `narrative.gene_function` |
| 遗传模式 | 🟣 **OMIM SQLite** `report/omim_enrich.py` → `omim_inheritance_mode`；🔵 Agent 原样写入（本例 AURKAIP1 为 `-`） |
| 主要关联表型 | 🟣 Open Targets（同 §2.1） |
| 主要关联通路 | 🟣 Reactome |
| 致病性排名 | 🟢 `pathogenic_rank` |

### §3.x.2 变异列表

| 报告列 | 宽表字段 | 格式化 |
|--------|----------|--------|
| 变异标签 | `gene_symbol` + `hgvsp` 或坐标 | 🟠 `VariantRecord.variant_label` |
| 坐标 | `chrom`,`pos`,`ref`,`alt` | |
| 转录本 | `transcript_id` | 每变异经 🟠 转录本选择后 1 行 |
| 后果 | `consequence` | VEP |
| CADD | `cadd_phred` | |
| SpliceAI DS max | `spliceAI_ds_max` | |
| gnomAD AF | `gnomAD_eas_AF` | 🟠 `format_af` |
| ClinVar | `clinvar_significance` | |
| **测序比例** | **`vcf_info_VAF`** 优先，否则 **`vcf_info_AF`** | 🟠 `primary_vaf` → `format_vaf` |

**转录本去重规则**（🟠 `wide_table._transcript_score`）：`vep_pick=1` > `tx_rank_within_variant=1` > `mane_select` 非空 > `pathogenic_rank` 最小。

### §3.x.3.y.1 基因组与测序质量（V3 扩展）

| 报告字段 | 宽表 / 逻辑 | 展示条件 |
|----------|-------------|----------|
| 基因组坐标 | `chrom`,`pos`,`ref`,`alt` | 始终 |
| **测序等位基因比例** | **`vcf_info_VAF`**；无则 **`vcf_info_AF`** | 🟠 `primary_vaf`；标注「基于测序 reads」或「基于 GATK 基因型 AF」 |
| **Reads 支持** | **`vcf_info_REF_DP`**, **`vcf_info_ALT_DP`** | 两列均有值时 |
| **GATK 基因型 AF** | **`vcf_info_AF`** | 🟠 `show_gatk_af_row`：有 VAF 且 \|VAF−AF\|≥5% |
| 测序深度 | **`vcf_info_DP`** | 始终 |
| **碱基质量指标** | **`vcf_info_QD`**, **`vcf_info_FS`**, **`vcf_info_MQ`** | 至少一列非 `-` |
| **解读提示** | 🟠 `sequencing_quality_note` 规则（见下） | 有触发时 |
| 外显子 | `exon` | 始终 |

**解读提示触发规则**（`report/models.py`）：

| 条件 | 提示 |
|------|------|
| `vcf_info_ALT_DP` < 3 | 支持变异的 reads 偏少，建议 Sanger 验证 |
| `vcf_info_DP` < 10 | 测序深度偏低，等位基因比例可信度有限 |
| \|VAF − AF\| ≥ 5% 且有 VAF | reads 比例与 GATK AF 不一致，优先参考 reads |
| `vcf_info_QD` < 2 | 位点质量指标 QD 偏低 |

**本例示例**（AURKAIP1 p.Ala122Glu）：VAF=20%，AF=50%，REF=8/ALT=2 → 三条提示均可能触发。

### §3.x.3.y.1b 基因组注释与人群上下文（V3 新增）

整节由 🟠 `VariantRecord.genomic_context_items` 驱动，**仅有解读价值时展示**。

| 报告维度 | 宽表字段 | 展示条件 |
|----------|----------|----------|
| **变异相位** | `vcf_info_PHASING_CONFIDENCE`, `vcf_info_BEAGLE_PHASED` | `HIGH` 且 `BEAGLE_PHASED=1` |
| **中国参考人群** | `vcf_info_CHN_ALT_CARRIER_COUNT`, `vcf_info_CHN_ALT_AC` | 携带者 >0 或 ALT AC >0 |
| **调控元件** | `vcf_info_REG_CCRE_CLASS`, `vcf_info_REG_CCRE_COUNT` | `REG_CCRE_CLASS` 非空 |
| **非编码 RNA** | `vcf_info_NCRNA_GENE_NAME`, `vcf_info_NCRNA_GENE_TYPE` | 基因名非空 |
| **假基因区域** | `vcf_info_is_pseudogene`, `vcf_info_pseudogene_name`, `vcf_info_pseudogene_source` | 仅 `Yes` |

**CRE 类型中文化**（🟠 `_CRE_CLASS_ZH`）：如 `pELS` → 近端增强子样元件 (pELS)。

**本例**：AURKAIP1 p.Ala122Glu 仅展示 **调控元件 pELS**；多数常见变异展示 **中国参考人群** 或 **相位**（v3 宽表 HIGH 较普遍）。

**解读提示列**：🟡 模板固定中文说明；🔵 Agent 叙事可引用 `genomic_context` JSON（见 `report/enrich.py` `_variant_payload`）。

### §3.x.3.y.2 转录本与功能影响

| 字段 | 宽表（VEP） |
|------|-------------|
| 转录本 / RefSeq | `transcript_id`, `refseq_id` |
| HGVSc / HGVSp | `hgvsc`, `hgvsp` |
| VEP 后果 / 影响 | `consequence`, `impact` |

### §3.x.3.y.3 预测工具评分

| 字段 | 宽表 | 解读列 |
|------|------|--------|
| CADD | `cadd_phred` | 🟠 模板 `>20` 规则 |
| SpliceAI | `spliceAI_ds_max`, `spliceAI_type` | 🟠 模板 |
| REVEL | `revel_score` | 🟠 模板 `≥0.5` |
| LOFTEE | `loftee_lof_flag` | 🟠 模板 |

### §3.x.3.y.4 人群频率与数据库

| 字段 | 宽表 |
|------|------|
| gnomAD EAS / Popmax | `gnomAD_eas_AF`, `gnomAD_popmax_AF` |
| gnomAD 纯合数 | `gnomAD_nhomalt` |
| ClinVar | `clinvar_significance`, `clinvar_review_status`, `clinvar_star_rating` |
| 临床相关表达 | `clinical_best_tissue`, `clinical_transcript_tpm`（GTEx + HPO tissue 白名单） |
| GTEx Top5 | `gtex_transcript_top5_tissues` |

### §3.x.3.y.5 蛋白结构域与功能影响

| 字段 | 来源 |
|------|------|
| 蛋白结构域 | 🟢 `protein_domains` |
| 证据摘要 | 🟢 `evidence_summary` |
| 治疗意义 | 🔵 Agent `therapeutic_implication`；无 Agent 时用 🟠 `drug_recommendation_summary` |

### §3.x.3.y.6 文献证据

| 列 | 来源 |
|----|------|
| PMID / 标题 / 摘要 | 🔵 **基因叙事 Agent** + 🟣 **`paper_search_search_pubmed`** → `literature[]` |
| 约束 | prompt 禁止编造 PMID |

### §3.x.4 基因-表型-通路关联

| 维度 | 来源 |
|------|------|
| 关联表型 | 🔵 Agent `phenotype_association`；输入含 OT 预填 + **`get_gene_disease_associations`** + HPO/clinical |
| 关联通路 | 🔵 Agent `pathway_summary`；优先 🟣 Reactome `main_pathway` |
| 临床建议 | 🔵 Agent `clinical_note`；须结合宽表 HGVS/ClinVar/CADD/**测序比例**与 `clinical_info` |

### §3.x.5 严格筛选用药建议

| 内容 | 来源 |
|------|------|
| 段首说明 | 🟠 **`report/drug_recommendations.py`** → `drug_recommendation_summary` |
| 药物表 | 🟠 同上；**本样本全部 `drug_recommendations=[]`** → 占位行 |
| 筛选工具 | 🟣 `lookup_gene` + `get_gene_disease_associations` + **`get_gene_drug_details`**（Open Targets） |
| 筛选规则 | 🟠 匹配 `clinical_info`/HPO/`main_associated_phenotype` + ClinVar 可信 + 临床阶段阈值 |

### §3.x.6 中国临床试验团队

仅当 `drug_recommendations` 非空且 evidence 非 exploratory 时调用 🟣 `search_chinadrug_trials` / `search_chictr_trials`。**本样本无 §3.x.6**。

---

## 本报告 Top 5 基因要点

| 基因 | 宽表代表 | 脚本/工具预填 | Agent 叙事侧重 |
|------|----------|---------------|----------------|
| **AURKAIP1** | rank #16；错义 p.Ala122Glu；VAF 20%/AF 50%；CRE pELS | OT：neurodegenerative disease；Reactome：线粒体核糖体 QC | 证据有限；调控区；与听力/智力表型匹配弱 |
| **VWA1** | rank #27；frameshift c.961_967del；ClinVar `-` | OT：远端 HMN7 / 神经肌肉病 | 潜在 LoF；典型表型与患者神经发育/听力不完全一致 |
| **ATAD3B** | rank #33；78 个位点；高 CADD 错义 | OT：卵巢肿瘤、UC 等 | 与当前表型关联弱 |
| **CCNL2** | rank #44 | OT：infection / breast cancer | 辅助讨论 |
| **ENSG00000241860** | rank #53；64 位点 | OT：MDS | 非蛋白基因符号；谨慎解读 |

---

## §4 方法学与数据质量

| 内容 | 来源 |
|------|------|
| 流程 / 排序 bullet | 🟡 `methodology.md.j2` |
| 样本 / VCF / Liftover | 🟢 `meta` |
| 去重后 **10000** 变异 / **194** 基因 | 🟠 `wide_table.py` 统计 |
| 排序字段说明 | 🟡 模板 + 宽表 `pathogenic_rank` / `evidence_summary` |

---

## §5 免责声明 · §6 阴性结果

全部 🟡 模板；§6 数字来自 🟠 `summary.total_variants`（10000）、`summary.genes_outside_top_n`（189）。

---

## §7 临床建议摘要

| 小节 | 来源 |
|------|------|
| §7.1 立即建议 | 🔵 临床建议 Agent → `immediate_recommendations` |
| §7.2 动态监测 | 🔵 Agent → `monitoring` |
| §7.3 沟通要点 | 🔵 Agent → `communication_points` |
| Agent 依据 | 宽表（含 **VAF/reads 提示**）+ `clinical_info` + OT 疾病背景 + **`strict_drug_candidates` 全空** |
| §7.4 | 模板：仅 `drug_recommendations` 非空时显示；**本样本无 §7.4** |

---

## §8 ReportOutput JSON

| 字段 | 来源 |
|------|------|
| report_version / title / gene_count / variant_count / top_genes | 🟠 `build_report_output_json()` |
| output_path | 运行时路径 |
| literature_strategy / disclaimer_included | 🟠 脚本常量 |

---

## 快速查表：V3 宽表列 → 报告位置

### 测序与质量（V3 重点）

| 宽表列 | 报告位置 |
|--------|----------|
| `vcf_info_VAF` | §3.3.1 测序等位基因比例（**优先**） |
| `vcf_info_REF_DP`, `vcf_info_ALT_DP` | §3.3.1 Reads 支持 |
| `vcf_info_AF` | §3.3.1 GATK 基因型 AF（条件展示）或 fallback 测序比例 |
| `vcf_info_DP` | §3.3.1 测序深度 |
| `vcf_info_QD`, `vcf_info_FS`, `vcf_info_MQ` | §3.3.1 碱基质量指标 |
| （规则） | §3.3.1 解读提示 |

### 基因组上下文（V3 新增）

| 宽表列 | 报告位置 |
|--------|----------|
| `vcf_info_PHASING_CONFIDENCE`, `vcf_info_BEAGLE_PHASED` | §3.3.1b 变异相位（条件） |
| `vcf_info_CHN_ALT_CARRIER_COUNT`, `vcf_info_CHN_ALT_AC` | §3.3.1b 中国参考人群（条件） |
| `vcf_info_REG_CCRE_*` | §3.3.1b 调控元件（条件） |
| `vcf_info_NCRNA_*` | §3.3.1b 非编码 RNA（条件） |
| `vcf_info_is_pseudogene` 等 | §3.3.1b 假基因（仅 Yes） |

### 注释与排序（与旧版相同）

| 宽表列 | 报告位置 |
|--------|----------|
| `chrom,pos,ref,alt`, `gene_symbol` | §2、§3 坐标与分组 |
| `transcript_id`, `mane_select`, `refseq_id`, `hgvsc`, `hgvsp`, `consequence`, `impact`, `exon` | §3.3.1–3.3.2 |
| `cadd_phred`, `revel_score`, `spliceAI_*`, `loftee_lof_flag` | §3.3.3 |
| `gnomAD_*`, `clinvar_*`, `clinical_*`, `gtex_*` | §3.3.4 |
| `protein_domains`, `evidence_summary` | §3.3.5、§2.3 |
| `pathogenic_rank` | §2.1、§3.1 |
| `vep_pick`, `tx_rank_within_variant` | 🟠 转录本去重（不直接展示） |

---

## 快速查表：工具 → 报告位置

| 工具 / 模块 | 写入报告 |
|-------------|----------|
| NCBI Gene Entrez | §3.x.1 基因功能 |
| OMIM SQLite | §3.x.1 遗传模式 |
| Open Targets 表型查询 | §2.1 / §3.x.1 主要关联表型 |
| Open Targets `get_gene_disease_associations` | 🔵 Agent 表型/§7 |
| Open Targets `get_gene_drug_details` | §3.x.5 用药筛选（本样本无命中） |
| Reactome Neo4j | §2.1 / §3.x.1 主要关联通路 |
| PubMed `paper_search_search_pubmed` | §3.x.3.6 文献 |
| ChinaDrug / ChiCTR | §3.x.6（本样本无） |

---

## Agent 输入 JSON 中的宽表摘要（`_variant_payload`）

每个变异传给 Agent 的字段（`report/enrich.py`）：

| JSON 键 | 对应宽表 / 规则 |
|---------|-----------------|
| `coordinate`, `hgvsc`, `hgvsp`, `consequence` | 宽表直接 |
| `clinvar`, `cadd` | 宽表直接 |
| `vaf` | 🟠 `primary_vaf`（VAF 优先） |
| `gatk_af`, `read_vaf` | `vcf_info_AF`, `vcf_info_VAF` |
| `read_support` | REF_DP / ALT_DP 格式化 |
| `sequencing_quality_note` | 🟠 规则文案 |
| `genomic_context` | 🟠 `genomic_context_items` 列表 |
| `evidence_summary` | 宽表直接 |

---

*生成说明：与 [report.md](./report.md) 同目录；再运行 `generate_final_report.py` 会覆盖 report 与 context，本注释需随模板/字段逻辑变更同步更新。*
