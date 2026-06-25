请根据样本临床信息、HPO 表型和 Top 基因列表生成临床建议 JSON，字段：

- `immediate_recommendations`: 立即建议（字符串数组）
- `monitoring`: 动态监测（字符串数组）
- `communication_points`: 患者/家属沟通要点（字符串数组）
- `key_findings`: 关键发现提示（字符串数组），用于 §2.2

## key_findings 写作要求

- **逐基因**一条（每个 Top 基因至少一条），聚焦「基因关联疾病/表型」与「患者 clinical_info + hpo_terms」的匹配关系
- 优先引用 payload 中的 `open_targets_main_phenotype`；可用工具补充疾病背景，勿与预取字段矛盾
- 明确写出匹配判断：重叠较高 / 部分重叠 / 未见明显重叠 / 表型不支持
- 不要堆砌 ClinVar、VAF、CADD、排序分等宽表技术字段
- 匹配度低时说明为何不优先考虑该基因致病

不得编造宽表中的变异数值。
