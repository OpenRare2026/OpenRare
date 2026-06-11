# 字段词表（glossary）

写 narrative 那次模型调用读这份**蒸馏后的**词表来正确解读字段含义——不要把三份
原始 readme 整篇塞进上下文。原始 readme 是自由格式、由各模块协作者编写；本词表是
开发期人工/模型读一遍后提炼的稳定产物。字段变更时只需重新蒸馏本文件（可按 readme
哈希缓存，只在 readme 变动时重提）。

渲染层（build_context.py）**不读**本文件，也不读 readme——它只认 CSV 实际列名。
本词表只服务于"解读语义"，不参与任何数值渲染。

---

## 宽表（变异主线，VEP runner 输出）

每行一个变异。缺失值在源 CSV 中写作 `-`。

| 字段 | 含义 |
| --- | --- |
| `gene_symbol` / `all_genes` | 该行基因 / 该位点命中的全部基因（逗号分隔）。关联键。 |
| `consequence` / `impact` | VEP 后果术语 / 影响等级（HIGH/MODERATE/LOW/MODIFIER）。 |
| `hgvsc` / `hgvsp` | cDNA / 蛋白层 HGVS（已去转录本前缀，如 `c.1799T>A`、`p.Val600Glu`）。 |
| `revel_score` | REVEL 错义致病性预测，0–1，越高越倾向致病。 |
| `cadd_phred` | CADD PHRED，>20 约前 1% 有害、>30 约前 0.1%。 |
| `gnomAD_popmax_AF` / `gnomAD_eas_AF` | 人群最大 / 东亚等位基因频率。**频率越高越可能是常见多态、越不像罕见病致病变异。** |
| `gnomAD_nhomalt` | 纯合 alt 计数；罕见病致病变异通常很低。 |
| `spliceAI_ds_max` / `spliceAI_type` | SpliceAI 最大 delta 分及类型（acceptor/donor gain/loss），>=0.5 提示较强剪接影响。 |
| `loftee_lof_flag` | LOFTEE LoF 判定，`HC`=高置信、`LC`=低置信。 |
| `clinvar_significance` / `clinvar_star_rating` | ClinVar 临床意义 / 0–4 星证据等级（星越高越可信）。 |
| `pathogenic_rank` | 规则分排序名次，**越小越靠前**。本报告据此选基因和变异。规则分仅用于优先级排序，非临床结论。 |
| `evidence_summary` | `pathogenic_rank` 的可读理由（各组件加分 + `total=`）。 |

排序分（`pathogenic_rank` 背后，不单独成列）综合了 ClinVar、consequence/impact、
SpliceAI/LOFTEE、REVEL/CADD、频率、结构域。详细规则见宽表 README，解读时知道
"分高=多条证据共同支持优先级"即可，不要把它当致病性判定。

## 基因-表型评分（补充，按 `gene_symbol` 关联）

回答"该基因关联疾病的表型谱在多大程度上能解释患者 HPO"，**不是致病性判定**。

| 字段 | 含义 |
| --- | --- |
| `gene_score` | 表型匹配分，0–1，取该基因各关联疾病中最高的 disease score。 |
| `conclusion_code` | 表型匹配分层（见下）。只表示表型相似度。 |
| `best_disease_name` / `best_omim_id` / `best_orpha_id` / `best_mondo_id` | 最佳匹配疾病及其库 ID。 |
| `matched_hpo_count` / `unmatched_hpo_count` | 患者 HPO 与最佳疾病匹配 / 未匹配数。 |
| `best_term_evidence_summary` | 逐项 `患者HPO->疾病HPO:相似度`。 |
| `gene_rank` | 按 `gene_score` 的排名。 |

`conclusion_code`：`PHENOTYPE_MATCH_STRONG`(≥0.80) / `MODERATE`(0.50–0.80) /
`WEAK`(0.20–0.50) / `NONE`(<0.20 或无贡献)；`NO_GENE_DISEASE_MODEL`=库中无该基因
疾病模型；`NO_GENE_ANNOTATION`=位点无基因注释。

## PPI 双锚点评分（补充，按 `gene` 关联）

候选基因在 STRING 网络中相对"疾病锚点 D + 组织核心锚点 T"的网络优先级，**非致病性判定**。

| 字段 | 含义 |
| --- | --- |
| `ppi_final` | 综合分（可用轴重归一化后）。 |
| `disease_score` / `tissue_score` / `topology_score` | 疾病轴 / 组织轴 / 全局拓扑轴分。 |
| `score_mode` | 融合模式：`FULL_ANCHOR`(三轴) / `NO_D_REWEIGHTED` / `NO_T_REWEIGHTED` / `TOPOLOGY_ONLY` / `NOT_IN_STRING`。模式说明可解释强度。 |
| `gene_in_d` / `gene_in_t` | 候选基因本身是否进入 D / T 锚点集。 |
| `mapped_tissues_json` | 由患者 HPO 映射出的目标组织。 |
| `top_neighbors_json` | STRING 最强邻居及 `flag`（T=组织锚点，D=疾病锚点，none=都不是）。 |
| `note` | 边界标记，如 `EMPTY_D`、`NOT_IN_STRING`、`ISOLATED`。 |

D 轴权重 0.30、T 轴 0.45、拓扑 0.25；空轴不参与融合而非给 0 分——所以 `score_mode`
能提示"这条分是在几条证据轴上得出的"。组织轴权重最高，因为新致病基因常不在已知
疾病基因集 D 中，却可能与目标组织核心模块紧密互作。

---

### 解读语气约定

- 三类分都是**优先级/相似度**信号，不是诊断；narrative 要明确这一点。
- 该说弱就说弱：顶层变异多为非编码或 `MODIFIER`、表型 `WEAK/NONE`、
  `gnomAD` 频率偏高（可能常见多态）、PPI 为 `TOPOLOGY_ONLY` 或 `NOT_IN_STRING`，
  都要如实点出，不要拔高。
- 任何数字都以上方确定性表格为准，narrative 只引用、不新造。
