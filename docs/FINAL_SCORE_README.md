# Clean-case 最终评分表说明

本文档专门解释 clean-case 流程生成的 `*_final_score.csv`。

每个样本会输出两张表：

```text
*_ppi_score.csv    纯 PPI 评分表；字段与主 README 中的 PPI 输出字段一致
*_final_score.csv  最终病例融合表；合并 phenotype、VEP 和 PPI 证据
```

如果只想查看 PPI 网络证据，用 `*_ppi_score.csv`。如果要看单个病例的最终候选基因排序，用 `*_final_score.csv`。

## 输入来源

最终表由三类输入合并得到：

| 输入 | 作用 |
| --- | --- |
| phenotype-gene CSV | 提供 `gene_score`、`gene_rank` 和疾病匹配信息 |
| VEP CSV | 提供变异层面的基因证据，并按基因汇总 |
| HPO 列表 | 构建疾病锚点 `D`、映射组织、构建组织锚点 `T`，并计算 PPI 分数 |

处理大 VEP 文件时，clean-case 流程只读取 VEP 中这几列：

```text
gene_symbol
pathogenic_rank
cadd_phred
```

候选基因集合默认取两部分并集：

```text
VEP 排名前 candidate_top_n 的基因
phenotype 排名前 candidate_top_n 的基因
```

默认 `candidate_top_n=30000`。如果设置 `candidate_top_n=0`，则使用所有基因。

## 排名规则

最终表会保留所有进入候选集合的基因，但只有能完成 phenotype + PPI 融合的基因才会有 `final_rank`。

```text
可融合基因 = gene_score 非空 且 in_network == true
combined_score = (gene_score + ppi_final) / 2
final_rank = 可融合基因按 combined_score 排序后的名次
```

所以 `final_rank` 不是文件行号，也不是所有输出基因的连续编号。

例如某个基因 PPI 分很高，但 phenotype 输入里的 `gene_score` 为空，那么它仍会保留在 `*_final_score.csv` 中，且会有 `ppi_final`、`ppi_rank` 等 PPI 信息；但它不能计算 `combined_score`，因此 `final_rank` 为空。

如果只想看 PPI 排序，请使用：

```text
*_ppi_score.csv
```

或在 `*_final_score.csv` 中查看：

```text
ppi_rank
```

## 字段说明

当 `output_all_ppi_fields=true` 时，`*_final_score.csv` 包含下表字段。如果 `include_evidence_json=false`，证据 JSON 字段可能不输出；如果 `include_neighbors=false`，邻居字段可能不输出。

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `final_rank` | 最终融合 | 最终综合排名；只给可融合基因编号 |
| `gene` | 候选基因集合 | HGNC gene symbol |
| `combined_score` | 最终融合 | 可融合基因的 `(gene_score + ppi_final) / 2` |
| `gene_score` | phenotype CSV | 表型-gene 分数；原始输入为空时这里也为空 |
| `ppi_final` | PPI 评分 | 最终 PPI 网络综合分数 |
| `in_network` | PPI 评分 | 该基因是否存在于 STRING 网络 |
| `disease_score` | PPI 评分 | 与疾病锚点 `D` 的互作和距离分数 |
| `tissue_score` | PPI 评分 | 与组织核心锚点 `T` 的互作和距离分数 |
| `topology_score` | PPI 评分 | 全局 degree 和 betweenness 拓扑分数 |
| `score_mode` | PPI 评分 | PPI 融合模式，例如 `FULL_ANCHOR`、`NO_D_REWEIGHTED`、`TOPOLOGY_ONLY` |
| `score_weight_sum` | PPI 评分 | 本行 PPI 融合实际参与的权重和 |
| `note` | PPI 评分 | 边界情况标记，例如 `OK`、`EMPTY_D`、`EMPTY_T`、`NOT_IN_STRING` |
| `gene_in_d` | PPI 评分 | 该候选基因是否进入本次疾病锚点 `D` |
| `gene_d_evidence_score` | PPI 评分 | 该基因在 D 集证据字典中的加权证据分；未命中为 0 |
| `gene_d_sources_json` | PPI 评分 | 支持该基因进入 D 集的来源列表 JSON |
| `gene_in_t` | PPI 评分 | 该候选基因是否进入本次组织核心锚点 `T` |
| `gene_t_weight` | PPI 评分 | 该基因的 T 层支持权重；未命中为 0 |
| `gene_t_layers_json` | PPI 评分 | 支持该基因进入 T 集的层来源 JSON，例如表达层、DepMap 必需层、通路层 |
| `gene_t_tissues_json` | PPI 评分 | 支持该基因进入 T 集的组织列表 JSON |
| `mapped_tissues_json` | PPI 评分 | HPO 解析得到并按映射次数排序取 Top 3 的组织列表 JSON |
| `d_gene_count` | PPI 评分 | 本次最终 D 集基因数 |
| `t_gene_count` | PPI 评分 | 本次最终 T 集基因数 |
| `top_neighbors_json` | PPI 评分 | STRING 互作最强的 Top N 邻居及 D/T 标签 |
| `top_neighbors_count` | PPI 评分 | 返回的邻居数量 |
| `gene_rank` | phenotype CSV | phenotype-gene 输入表中的基因排名 |
| `ppi_rank` | PPI 评分 | 只按 `ppi_final` 排序得到的 PPI 名次 |
| `best_pathogenic_rank` | VEP CSV | 该基因所有 VEP 记录中最小的 `pathogenic_rank` |
| `variant_row_count` | VEP CSV | VEP 表中落到该基因的记录数 |
| `max_cadd_phred` | VEP CSV | 该基因所有 VEP 记录中的最大 `cadd_phred` |
| `mapped_tissues` | PPI 评分 | 本次映射组织的逗号分隔字符串，便于表格查看 |
| `mapped_tissue_counts_json` | PPI 评分 | HPO 到组织映射计数字典 JSON |
| `conclusion_code` | phenotype CSV | phenotype-gene 输入表中的结论标签 |
| `best_disease_score` | phenotype CSV | phenotype-gene 输入表中的最佳疾病匹配分 |
| `best_disease_name` | phenotype CSV | phenotype-gene 输入表中的最佳疾病名称 |
| `best_omim_id` | phenotype CSV | phenotype-gene 输入表中的最佳 OMIM ID |
| `best_orpha_id` | phenotype CSV | phenotype-gene 输入表中的最佳 Orphanet ID |
| `best_mondo_id` | phenotype CSV | phenotype-gene 输入表中的最佳 MONDO ID |
| `best_disease_match_status` | phenotype CSV | phenotype-gene 输入表中的疾病匹配状态 |
| `mapping_basis` | phenotype CSV | phenotype-gene 输入表中的匹配依据 |

## 推荐解读方式

最终候选基因优先级建议先看 `final_rank` 非空的行。这些基因同时具有 phenotype 证据和 PPI 网络证据。

`final_rank` 为空的行可以按下表理解：

| 情况 | 含义 |
| --- | --- |
| `gene_score` 为空，但 `ppi_final` 有值 | 有 PPI 网络证据，但 phenotype 分数缺失，不能进入综合排名 |
| `in_network=false` | 该基因不在 STRING 网络中，PPI 分数不可用或不具备可比性 |
| `final_rank` 为空，但 `ppi_rank` 靠前 | 该基因网络相关性强，但不满足 phenotype + PPI 融合条件 |

如果只做网络证据复核，推荐按 `*_ppi_score.csv` 的 `ppi_final` 排序，或按 `*_final_score.csv` 中的 `ppi_rank` 查看。

## 输出路径

API 和命令行都可以显式指定两张表路径：

```json
{
  "output_csv": "../output/case5/case5_final_score.csv",
  "ppi_output_csv": "../output/case5/case5_ppi_score.csv"
}
```

如果不传 `ppi_output_csv`，程序会根据 `output_csv` 自动生成路径，例如：

```text
case5_final_score.csv -> case5_ppi_score.csv
final_score.csv       -> ppi_score.csv
```
