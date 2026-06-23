# PPI 评分逻辑简述

本项目用于对罕见病候选基因做 PPI 网络优先级排序。当前推荐从
`pixi_ppi_score/` 运行服务，本文只说明评分逻辑。

## 核心思想

候选基因不只在候选列表内部做互作分析，而是放到完整 STRING 网络背景下，分别计算：

| 轴 | 含义 |
| --- | --- |
| 疾病锚点 `D` | 与已知疾病/相近表型基因的网络关系。 |
| 组织锚点 `T` | 与 HPO 映射目标组织核心基因的网络关系。 |
| 拓扑 `Topology` | 在全局 STRING 网络中的 degree、betweenness 等特征。 |

默认权重：

```text
W_disease  = 0.30
W_tissue   = 0.45
W_topology = 0.25
```

如果某个轴不可用，该轴不参与融合，剩余权重重新归一化：

```text
ppi_final = sum(W_i * score_i for available axes) / sum(W_i for available axes)
```

## 输入

基础 PPI 评分输入：

| 字段 | 说明 |
| --- | --- |
| `candidate_genes` | HGNC 标准化后的候选基因 SYMBOL 列表。 |
| `hpo_ids` | 患者 HPO ID 列表。 |

clean-case 流程会从 phenotype-gene CSV 和 VEP CSV 中自动构建候选基因集合。

## 输出

核心字段：

| 字段 | 说明 |
| --- | --- |
| `gene` | 候选基因。 |
| `in_network` | 是否在 STRING 网络中。 |
| `disease_score` | 与疾病锚点 `D` 的网络分数。 |
| `tissue_score` | 与组织锚点 `T` 的网络分数。 |
| `topology_score` | 全局拓扑分数。 |
| `ppi_final` | 加权融合后的 PPI 综合分数。 |
| `score_mode` | 本次融合模式。 |
| `mapped_tissues_json` | HPO 映射得到的目标组织。 |

最终病例融合表字段见 `docs/FINAL_SCORE_README.md`。
