请为给定基因生成叙事 JSON，字段：

- `gene_function`: 基因功能 2-3 句
- `inheritance_mode`: 遗传模式
- `phenotype_association`: 与临床信息 / HPO 的关联
- `pathway_summary`: 主要通路
- `clinical_note`: 1-2 句临床建议（不得新增 strict_drug_candidates 以外的药名）
- `therapeutic_implication`: 治疗意义/机制解读；仅基于 strict_drug_candidates
- `literature`: 数组，元素含 `pmid`, `title`, `authors_journal_year`, `summary`, `evidence_level`

不得编造宽表中的变异数值；不得编造 PMID 或药物名称。
