# Rare Disease Dual-Anchor PPI Scoring

This repository keeps the runnable workflow in `script1/`. Large reference databases, local Python environments, logs, and generated outputs are intentionally excluded from Git so other users can clone the code and reproduce the workflow with their own `data/` directory.

Clean-case runs produce two result tables per sample:

```text
*_ppi_score.csv    Pure PPI table; columns match the PPI output table below.
*_final_score.csv  Final phenotype + VEP + PPI fusion table; see FINAL_SCORE_README.md.
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
| --- | --- |
| `gene` | 候选基因 |
| `in_network` | 是否存在于 STRING 网络 |
| `disease_score` | 与疾病锚点 `D` 的互作和距离分数 |
| `tissue_score` | 与组织核心锚点 `T` 的互作和距离分数 |
| `topology_score` | 全局 degree 和 betweenness 拓扑分数 |
| `ppi_final` | 最终 PPI 综合分数 |
| `score_mode` | 本次融合模式，例如 `FULL_ANCHOR`、`NO_D_REWEIGHTED`、`TOPOLOGY_ONLY` |
| `score_weight_sum` | 本次参与融合的权重和 |
| `note` | 边界情况标记，例如 `EMPTY_D`、`EMPTY_T`、`NOT_IN_STRING` |
| `gene_in_d` | 该候选基因是否进入本次疾病锚点 `D` |
| `gene_d_evidence_score` | 该候选基因在 D 集证据字典中的加权证据分；未命中为 0 |
| `gene_d_sources_json` | 支持该候选基因进入 D 集的来源列表 JSON |
| `gene_in_t` | 该候选基因是否进入本次组织核心锚点 `T` |
| `gene_t_weight` | 该候选基因的 T 层支持权重；未命中为 0 |
| `gene_t_layers_json` | 支持该候选基因进入 T 集的层来源 JSON，例如表达层、DepMap 必需层、通路层 |
| `gene_t_tissues_json` | 支持该候选基因进入 T 集的组织列表 JSON |
| `mapped_tissues_json` | 本次 HPO 解析得到并按映射次数排序取 Top 3 的组织列表 JSON |
| `d_gene_count` | 本次最终 D 集基因数 |
| `t_gene_count` | 本次最终 T 集基因数 |
| `top_neighbors_json` | STRING 互作最强的 Top N 邻居及 D/T 标签 |
| `top_neighbors_count` | 返回的邻居数量 |

上表是纯 PPI 输出，字段与 README 保持一致。clean-case 病例入口会同时生成两张表：

```text
ppi_score.csv    # 纯 PPI 表，字段与上表一致
final_score.csv  # 最终病例融合表，合并 phenotype、VEP 和 PPI，详见 FINAL_SCORE_README.md
```

### Clean-case 最终 CSV 字段

`run_clean_case.py`、`/score/clean-case`、`/score/clean-case/async` 和 `/score/clean-case/upload/async` 还会生成最终病例融合表。使用 `output_all_ppi_fields=true` 时，最终 CSV 字段如下：

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `final_rank` | 融合结果 | 最终综合排名；只给 `gene_score` 非空且 `in_network=true` 的基因编号，不是文件行号 |
| `gene` | 候选基因 | 候选基因 SYMBOL |
| `combined_score` | 融合结果 | `(gene_score + ppi_final) / 2`；如果缺少 `gene_score` 或不在 STRING 中则为空 |
| `gene_score` | phenotype CSV | 表型-gene 打分；原始输入为空时这里也为空 |
| `ppi_final` | PPI 表 | 最终 PPI 综合分数 |
| `in_network` | PPI 表 | 是否存在于 STRING 网络 |
| `disease_score` | PPI 表 | 与疾病锚点 `D` 的互作和距离分数 |
| `tissue_score` | PPI 表 | 与组织核心锚点 `T` 的互作和距离分数 |
| `topology_score` | PPI 表 | 全局 degree 和 betweenness 拓扑分数 |
| `score_mode` | PPI 表 | 本次融合模式 |
| `score_weight_sum` | PPI 表 | 本次参与 PPI 融合的权重和 |
| `note` | PPI 表 | 边界情况标记 |
| `gene_in_d` | PPI 表 | 该候选基因是否进入本次疾病锚点 `D` |
| `gene_d_evidence_score` | PPI 表 | 该候选基因在 D 集证据字典中的加权证据分；未命中为 0 |
| `gene_d_sources_json` | PPI 表 | 支持该候选基因进入 D 集的来源列表 JSON |
| `gene_in_t` | PPI 表 | 该候选基因是否进入本次组织核心锚点 `T` |
| `gene_t_weight` | PPI 表 | 该候选基因的 T 层支持权重；未命中为 0 |
| `gene_t_layers_json` | PPI 表 | 支持该候选基因进入 T 集的层来源 JSON |
| `gene_t_tissues_json` | PPI 表 | 支持该候选基因进入 T 集的组织列表 JSON |
| `mapped_tissues_json` | PPI 表 | 本次 HPO 解析得到并按映射次数排序取 Top 3 的组织列表 JSON |
| `d_gene_count` | PPI 表 | 本次最终 D 集基因数 |
| `t_gene_count` | PPI 表 | 本次最终 T 集基因数 |
| `top_neighbors_json` | PPI 表 | STRING 互作最强的 Top N 邻居及 D/T 标签 |
| `top_neighbors_count` | PPI 表 | 返回的邻居数量 |
| `gene_rank` | phenotype CSV | phenotype-gene 输入表中的基因排名 |
| `ppi_rank` | PPI 表 | 仅按 `ppi_final` 排序得到的 PPI 排名 |
| `best_pathogenic_rank` | VEP CSV | 该基因所有 VEP 记录中最小的 `pathogenic_rank` |
| `variant_row_count` | VEP CSV | VEP 表中落到该基因的记录数 |
| `max_cadd_phred` | VEP CSV | 该基因所有 VEP 记录中的最大 `cadd_phred` |
| `mapped_tissues` | PPI 表 | 本次映射组织的逗号分隔字符串，便于表格查看 |
| `mapped_tissue_counts_json` | PPI 表 | 本次 HPO 到组织映射计数字典 JSON |
| `conclusion_code` | phenotype CSV | phenotype-gene 输入表中的结论标签 |
| `best_disease_score` | phenotype CSV | phenotype-gene 输入表中的最佳疾病匹配分 |
| `best_disease_name` | phenotype CSV | phenotype-gene 输入表中的最佳疾病名 |
| `best_omim_id` | phenotype CSV | phenotype-gene 输入表中的最佳 OMIM ID |
| `best_orpha_id` | phenotype CSV | phenotype-gene 输入表中的最佳 Orphanet ID |
| `best_mondo_id` | phenotype CSV | phenotype-gene 输入表中的最佳 MONDO ID |
| `best_disease_match_status` | phenotype CSV | phenotype-gene 输入表中的疾病匹配状态 |
| `mapping_basis` | phenotype CSV | phenotype-gene 输入表中的匹配依据 |

`final_rank` 是最终融合排名，不是所有输出行的连续编号。某个基因如果有 `ppi_final` 但 phenotype 输入中的 `gene_score` 为空，最终 CSV 会保留该基因及其 PPI 字段，但 `combined_score` 和 `final_rank` 会为空。需要只看 PPI 排名时使用 `ppi_score.csv` 或最终表中的 `ppi_rank`。

`gene_d_sources_json`、`gene_t_layers_json`、`gene_t_tissues_json` 只有在 `include_evidence_json=true` 或 `output_all_ppi_fields=true` 时输出；`top_neighbors_json` 和 `top_neighbors_count` 只有在 `include_neighbors=true` 或 `output_all_ppi_fields=true` 时输出。

完整的本次运行中间结果不再重复写入每一行结果表。Python API 可从 `scorer.last_audit` 读取；命令行可用 `--audit-json audit.json` 单独写出，其中包含输入、最终 `D`、`T`、证据分、支持来源、T 层来源和映射组织。

`audit.json["input"]` 会记录两类变长输入：

| 字段 | 说明 |
| --- | --- |
| `candidate_genes` | 候选基因列表 |
| `hpo_ids` | 输入的 HPO 列表 |

组织不作为输入传入，而是由 `hpo_ids` 自动映射。每个 HPO 映射到的组织会计数，一个 HPO 对同一个 coarse tissue 最多计 1 次；如果同一个 HPO 在输入中重复出现，会按出现次数参与组织投票。所有组织按计数降序排序后取 Top 3。最终用于构建 T 集的组织写在 `audit.json["mapped_tissues"]` 和结果表的 `mapped_tissues_json`。

`audit.json` 还会记录组织定位过程：

| 字段 | 说明 |
| --- | --- |
| `mapped_tissue_counts` | 所有被 HPO 映射到的组织及其计数，按排名顺序记录 |
| `hpo_tissue_map` | 每个 HPO 映射到的 coarse tissue 列表 |

## FastAPI 服务

配置已经抽到 `config.py`，命令行和 API 共用同一套 `RunParameters` 校验逻辑。默认数据库目录为项目根目录下的 `data/`，也可以通过环境变量 `RARE_PPI_DATA_DIR` 或请求体里的 `data_dir` 覆盖。

启动服务：

```bash
cd script1
./run_api.sh
```

接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/health` | 检查服务、默认数据目录和已缓存模型数 |
| `GET` | `/config` | 返回当前默认配置；可加 `?include_missing_files=true` |
| `POST` | `/initialize` | 按参数预加载数据库，首次调用耗时较长 |
| `POST` | `/score` | 输入候选基因和 HPO，生成 CSV 文件并返回 `csv_path` |
| `POST` | `/score/async` | 提交异步评分任务，立即返回 `job_id` 和 `status=queuing` |
| `GET` | `/score/{job_id}` | 查询异步任务结果 |
| `GET` | `/score/{job_id}/csv` | 下载异步任务生成的 CSV 文件 |

所有 API 都返回顶层 `status` 字段：

| `status` | 含义 |
| --- | --- |
| `completion` | 完成 |
| `failure` | 失败 |
| `queuing` | 等待 |

示例：

```bash
curl -X POST http://127.0.0.1:8000/score \
  -H 'Content-Type: application/json' \
  -d '{
    "candidate_genes": ["ABCA4", "USH2A", "CEP290"],
    "hpo_ids": ["HP:0000488", "HP:0000505"]
  }'
```

同步评分默认会把 CSV 写到项目根目录下的 `output/ppi_score_<随机ID>.csv`，响应示例：

```json
{
  "status": "completion",
  "count": 3,
  "output_format": "csv",
  "csv_path": "../output/ppi_score_xxx.csv",
  "columns": ["gene", "in_network", "disease_score"]
}
```

也可以在请求中指定输出位置：

```json
{
  "candidate_genes": ["ABCA4", "USH2A", "CEP290"],
  "hpo_ids": ["HP:0000488", "HP:0000505"],
  "output_csv": "../output/my_result.csv"
}
```

## 数据依赖

默认路径集中在 `config.py` 的 `Config` 类中。

| 模块 | 数据源 | 用途 |
| --- | --- | --- |
| ID 映射 | HGNC、BioMart、UniProt、STRING info | 建立 HGNC SYMBOL 与 STRING 节点的桥梁 |
| HPO 映射 | `phenotype_to_anatomy.txt`、`hp.obo` | 将 HPO 收敛到目标组织 |
| D 集 | OMIM genemap2、HPO genes、Orphanet、ClinVar、PanelApp | 构建疾病锚点 |
| T 集表达层 | GTEx、HPA | 提取目标组织表达基因；GTEx 使用 TPM + tau，HPA 使用 nTPM |
| T 集必需层 | DepMap `CRISPRGeneEffect.csv`、`Model.csv` | 提取组织或相近细胞系必需基因 |
| T 集通路层 | Reactome | 提取组织相关通路核心基因 |
| PPI 网络 | STRING v12 | 构建主互作网络 |

## 流程

### 1. 准备候选基因

候选基因输入必须已经完成 HGNC 标准化。当前实现不会再对 `candidate_genes` 做别名转换，只会去空值和去重。

```python
candidate_genes = ["ABCA4", "USH2A", "CEP290"]
```

### 2. HPO 到组织

HPOMapper 思路：
1. 从 `uberon.obo` 读取 UBERON ID 对应的可读组织名。
2. 从 `hp.obo` 读取 HPO 名称和 `is_a` 父节点关系。
3. 从 `phenotype_to_anatomy.txt` 读取官方 direct HPO -> UBERON 映射。
4. 从 `hp-full.owl` 的 logical definitions 中补充 HPO -> UBERON 映射。
5. 对每个输入 HPO，沿 `is_a` 祖先链向上查找，直到命中最近的可用 UBERON 组织。
6. 只有整条祖先链都没有可用 UBERON 组织时，才使用 HPO 名称关键词兜底。

```text
HPO IDs -> UBERON / tissue names -> count tissues -> Top 3 tissues -> database-specific tissue names
```



### 3. 构建疾病锚点 D

`D` 来自多库整合：

```text
OMIM + Orphanet + ClinVar + HPO genes + PanelApp -> weighted evidence score -> D
```

不同来源按独立性和可信度加权：

| 来源 | 权重 |
| --- | --- |
| OMIM | 1.0 |
| Orphanet | 0.8 |
| PanelApp | 0.9 |
| ClinVar | 0.6 |
| HPO genes | 0.3 |

默认要求加权证据分至少达到 `2.0`。如果严格阈值下 `D` 为空，则降级到保底阈值 `1.0`；如果仍为空，则通过 HPO 父节点扩展到更宽的表型。

OMIM 来源使用 `phenotype.hpoa` 中的 `OMIM:xxxxxx` 表型编号连接 `genemap2.txt` 的 `Phenotypes` 字段，再映射到该行的 `Approved Symbol`。这样避免把表型 MIM 和基因 MIM 混用；`mim2gene.txt` 只在 `genemap2.txt` 不可用时作为兜底。

### 4. 构建组织核心锚点 T

`T` 由三层组成：

1. 表达层：针对 HPO 映射计数 Top 3 目标组织，提取 GTEx 中 gene-level TPM 高且 tau 相对特异的基因，以及 HPA 中 nTPM 高的基因。
2. 必需层：DepMap 中目标组织或近似细胞系必需基因。代码用 `Model.csv` 按组织关键词匹配模型，再在 `CRISPRGeneEffect.csv` 中取这些模型的基因效应中位数，低于 `DEPMAP_EFFECT_CUTOFF` 的基因进入该层。
3. 通路层：用表达层和必需层作为种子，提取   富集通路中的核心基因。

通路核心阈值由 `T_PATHWAY_TOP_PCT` 控制，默认 70。代码会在命中的 Reactome 通路基因上构建 STRING 子图，并选取子图 degree 位于该百分位以上的核心基因。命令行运行时可用 `--t-pathway-top-pct` 覆盖，JSON 参数文件中对应字段为 `t_pathway_top_pct`。

每个 Top 3 组织分别构建三层 T 集，最终 `T` 是这些组织和三层结果的并集，`T_weights[gene]` 表示该基因被多少层支持。

```text
T_weights = {
  "GENE1": 1,
  "GENE2": 2,
  "GENE3": 3
}
```

### 5. PPI 锚点评分

对每个候选基因 `g`，先在完整 STRING 网络中做一次单源最短路径计算：

```text
dist_from_g = single_source_shortest_path_length(STRING, g)
```

`disease_score` 和 `tissue_score` 共用这份距离表：

1. 直接互作：`g` 是否直接连到 `D` 或 `T`。
2. 网络邻近：从 `dist_from_g` 查出 `g` 到 `D` 或 `T` 的最短路径，再取距离倒数。

这样评分本质上是“候选基因和 `D + T` 锚点在完整 STRING 背景中做分析”，不会被候选基因列表内部是否互连所限制。

性能上，每个候选基因只做一次 SSSP，然后对所有 `D/T` 锚点查表。避免对每个候选基因和每个锚点反复调用 `shortest_path_length()`，复杂度从约 `O(|G| * (|D| + |T|) * (V + E))` 降为约 `O(|G| * (V + E) + |G| * (|D| + |T|))`。

### 6. 拓扑评分

`topology_score` 基于完整 STRING 网络，并始终参与融合：

```text
topology_score = 0.5 * sigmoid(degree_z)
               + 0.5 * betweenness_rank_percentile
```

其中 degree 使用全局 Z-score 后 sigmoid 压缩，betweenness 使用 rank percentile 标准化。

### 7. 可用轴重归一化

`D` 和 `T` 代表锚点证据，空集表示证据缺失，不表示弱阳性或弱阴性。因此空轴不参与最终融合。

```text
D/T 都可用:
ppi_final = (0.30 * D + 0.45 * T + 0.25 * Topology) / 1.00

D 为空或 D 不在 STRING:
ppi_final = (0.45 * T + 0.25 * Topology) / 0.70

T 为空或 T 不在 STRING:
ppi_final = (0.30 * D + 0.25 * Topology) / 0.55

D 和 T 都不可用:
ppi_final = Topology
```

`score_mode` 用于标记解释强度：

| `score_mode` | 含义 |
| --- | --- |
| `FULL_ANCHOR` | D、T、Topology 三轴都参与 |
| `NO_D_REWEIGHTED` | D 轴不可用，T 和 Topology 重归一化 |
| `NO_T_REWEIGHTED` | T 轴不可用，D 和 Topology 重归一化 |
| `TOPOLOGY_ONLY` | D/T 都不可用，只能解释为网络拓扑排序 |
| `NOT_IN_STRING` | 候选基因不在 STRING，无法计算 PPI |

## 边界情况

| 情况 | 处理 |
| --- | --- |
| 候选基因不在 STRING 中 | `ppi_final = 0`，标记 `NOT_IN_STRING` |
| `D` 为空 | D 轴不参与融合，标记 `EMPTY_D` |
| `D` 非空但 D 基因都不在 STRING 中 | D 轴不参与融合，标记 `NO_D_IN_STRING` |
| `T` 为空 | T 轴不参与融合，标记 `EMPTY_T` |
| `T` 非空但 T 基因都不在 STRING 中 | T 轴不参与融合，标记 `NO_T_IN_STRING` |
| 候选基因在 STRING 中孤立 | 标记 `ISOLATED` |

## 使用示例

```python
from Network import Config, RareDiseasePPIScorer

cfg = Config()
scorer = RareDiseasePPIScorer(cfg)
scorer.initialize()

candidate_genes = ["ABCA4", "USH2A", "CEP290"]
hpo_ids = ["HP:0000488", "HP:0000505"]

df = scorer.run(candidate_genes=candidate_genes, hpo_ids=hpo_ids)
df = df.sort_values("ppi_final", ascending=False)
print(df[[
    "gene",
    "ppi_final",
    "disease_score",
    "tissue_score",
    "topology_score",
    "gene_in_d",
    "gene_d_evidence_score",
    "gene_in_t",
    "gene_t_weight",
    "score_mode",
    "score_weight_sum",
    "note",
]])
```

命令行/Docker 入口支持 JSON 参数文件，也支持直接传参。日志写入 stderr；未指定 `--output-csv` 时，结果 JSON 写入 stdout，便于容器管道读取。

```bash
../ppi_env/bin/python Network.py \
  --data-dir ../data \
  --candidate-file candidates.txt \
  --hpo-ids HP:0000488 HP:0000505 \
  --output-csv result.csv \
  --audit-json audit.json
```

该命令会同时生成：

```text
result.csv
audit.json
```

### 只保留最终 CSV 的病例入口

如果输入是“表型-Gene 评分 CSV + VEP 输出 CSV + HPO 列表”，推荐使用 `run_clean_case.py`。这个入口会把中间表保存在内存里，只写一个最终 CSV；`gene` 列保留 VEP 输入里的标准基因名，不把内部 ID 映射后的别名写回输出。

```bash
../ppi_env/bin/python run_clean_case.py \
  --phenotype-gene-csv ../input/gene_phenotype_score.csv \
  --vep-output-csv ../input/vep_output.csv \
  --hpo-file ../input/hpo_ids.txt \
  --output-csv ../output/case5_final_score.csv \
  --ppi-output-csv ../output/case5_ppi_score.csv \
  --clean-output-dir
```

`--clean-output-dir` 会在写入前清理输出目录里的旧普通文件，跑完目录中保留 `--output-csv` 指定的最终 CSV 和 `--ppi-output-csv` 指定的纯 PPI CSV。脚本会拒绝清理项目根目录和 `script1/`，避免误删工作区。若不指定 `--ppi-output-csv`，会从 `--output-csv` 自动派生，例如 `case5_final_score.csv` 对应 `case5_ppi_score.csv`。

API 也提供同样的干净病例入口，路径为 `POST /score/clean-case`。这个接口内部复用 `run_clean_case.py` 的逻辑，默认只写最终 CSV，不保留中间 CSV。

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case \
  -H 'Content-Type: application/json' \
  -d '{
    "phenotype_gene_csv": "../input/gene_phenotype_score.csv",
    "vep_output_csv": "../input/vep_output.csv",
    "hpo_file": "../input/hpo_ids.txt",
    "output_csv": "../output/case5_api_clean/final_score.csv",
    "ppi_output_csv": "../output/case5_api_clean/ppi_score.csv",
    "clean_output_dir": true
  }'
```

异步接口为 `POST /score/clean-case/async`，查询和下载仍使用已有的 `GET /score/{job_id}` 与 `GET /score/{job_id}/csv`。

常用可调参数包括：

| 参数 | 说明 |
| --- | --- |
| `--d-min-evidence` / `--d-fallback-evidence` | D 集加权证据阈值 |
| `--hpo-ids` / `--hpo-file` | HPO 输入；最多 2000 个，重复 HPO 会参与组织 Top 3 计数 |
| `--t-gtex-tpm-cutoff` / `--t-tau-cutoff` / `--t-top-n-expr` | 表达层阈值；GTEx 使用 TPM 和 tau，HPA 使用 nTPM 阈值 |
| `--depmap-effect-cutoff` | DepMap Gene Effect 必需性阈值 |
| `--t-pathway-top-pct` | Reactome 通路 STRING 子图核心基因 degree 百分位 |
| `--t-pathway-top-n` | 通路层最多使用命中数最高的 Reactome 通路数 |
| `--string-score-cutoff` | STRING combined score 入图阈值 |
| `--sssp-cutoff` | 单源最短路径最大深度；默认 4，设 0 表示不截断 |
| `--top-n-neighbors` | 每个候选基因输出的 Top STRING 邻居数量 |
| `--betweenness-sample-k` | betweenness 采样规模 |

## 主要实现文件

```text
Network.py
```

模块结构：

| 模块 | 责任 |
| --- | --- |
| `Config` | 路径、阈值、权重配置 |
| `IDStandardizer` | 加载 ID 映射，供数据库和 STRING 对齐使用 |
| `HPOMapper` | HPO 到目标组织 |
| `DiseaseModuleBuilder` | 构建 `D` |
| `TissueModuleBuilder` | 构建 `T` 和 `T_weights` |
| `PPIEngine` | 构建 STRING 图，执行完整网络背景下的 D/T 锚点评分 |
| `RareDiseasePPIScorer` | 串联主流程 |

## 当前注意事项

1. `candidate_genes` 必须在进入流程前完成 HGNC 标准化。
2. HPO 到组织会按映射次数取 Top 3；组织到 GTEx/HPA/DepMap 名称的映射需要人工校对。
3. Reactome 通路层是组织种子基因反推通路，不是 Reactome 自带组织标签。
4. `D` 和 `T` 的构建质量会直接影响 PPI 排序解释性。
