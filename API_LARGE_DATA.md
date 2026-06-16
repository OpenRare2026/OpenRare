# Rare Disease Dual-Anchor PPI Scoring

This repository keeps the runnable workflow in `script1/`. Large reference databases, local Python environments, logs, and generated outputs are intentionally excluded from Git so other users can clone the code and reproduce the workflow with their own `data/` directory.

Clean-case 病例流程会为每个样本输出两张结果表：

```text
*_ppi_score.csv    纯 PPI 评分表；字段与下方 PPI 输出字段一致
*_final_score.csv  最终病例融合表；合并 phenotype、VEP 和 PPI 证据，详见 FINAL_SCORE_README.md
```

## Quick Start

```bash

git clone https://github.com/ChangQing-LU/PPI_network.git
cd PPI_network/script1
./setup_env.sh

./download_data.sh
```

Unless otherwise noted, the commands below are run from `script1/`.


本项目用于对罕见病候选基因做 PPI 网络优先级排序。核心思想是把每个候选基因分别放到疾病锚点 `D` 和组织核心锚点 `T` 构成的锚点网络中评分，而不是只分析候选基因列表内部的互作。

## 核心逻辑

候选基因列表 `G` 已经是 HGNC 标准化后的基因名。

评分目标：

```text
candidate gene g
  -> 在完整 STRING 网络中计算一次从 g 出发的单源最短路径
  -> 对 D ∪ T 锚点查表得到网络邻近分
  -> 计算 disease_score、tissue_score、topology_score
  -> 加权融合得到 ppi_final
```

三条轴的含义：

1. `D` 轴：这个病或相近表型已知哪些基因致病。
2. `T` 轴：目标组织离不开哪些核心基因。
3. `Topology` 轴：候选基因在 STRING 网络中的拓扑重要性。

基础权重：

```text
W_disease  = 0.30
W_tissue   = 0.45
W_topology = 0.25
```

最终融合时只使用可用轴，并按参与权重重归一化：

```text
ppi_final = sum(W_i * score_i for available axes)
          / sum(W_i for available axes)
```

如果 `D` 或 `T` 为空，不给常数分，也不用 degree 伪造锚点分；该轴直接不参与最终融合。

组织轴权重最高，因为罕见病的新致病基因往往不在已知疾病基因集 `D` 中，但可能和目标组织核心功能模块 `T` 紧密互作。

## 输入与输出

输入：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `candidate_genes` | `List[str]` | 已 HGNC 标准化的候选基因 SYMBOL 列表 |
| `hpo_ids` | `List[str]` | 患者 HPO ID 列表，例如 `["HP:0000488", "HP:0000505"]` |

输出：

`RareDiseasePPIScorer.run()` 返回 `pandas.DataFrame`，每行对应一个候选基因。

| 字段 | 说明 |
