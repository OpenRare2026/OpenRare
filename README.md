# Rare Disease Dual-Anchor PPI Scoring

## 项目简介

本项目用于对罕见病候选基因进行 PPI 网络优先级排序。

核心思路是：不只分析候选基因列表内部的互作，而是把每个候选基因放到完整 STRING PPI 网络中，分别计算它与疾病锚点 `D`、组织核心锚点 `T`、全局拓扑特征的关系，最后得到 PPI 综合分数。

clean-case 病例流程支持输入：

```text
phenotype-gene CSV + VEP CSV + HPO 列表
```

每个样本会输出两张表：

```text
*_ppi_score.csv    纯 PPI 评分表
*_final_score.csv  最终病例融合表，合并 phenotype、VEP 和 PPI 证据
```

## 使用方法

### 1. 克隆项目

```bash
git clone -b dev_lq https://github.com/OpenRare2026/OpenRare.git
cd OpenRare/script1
```

### 2. 准备环境和数据

```bash
./setup_env.sh
./download_data.sh
```

大型参考数据库、虚拟环境、日志和输出结果不上传 GitHub。复现时需要在本地或服务器准备 `data/` 目录。

### 3. 启动 API

```bash
cd script1
RARE_PPI_DATA_DIR=../data RARE_PPI_PORT=9000 ./run_api.sh
```

API 基础地址：

```text
http://127.0.0.1:9000
```

常用检查接口：

```bash
curl http://127.0.0.1:9000/health
curl http://127.0.0.1:9000/version
```

`/version` 中应包含这些参数：

```text
candidate_top_n
output_all_ppi_fields
ppi_output_csv
vep_chunksize
```

### 4. 推荐接口：clean-case 异步评分

如果输入文件已经在 API 所在服务器上，推荐使用路径型接口，避免重复上传 9GB 以上的大 VEP 文件：

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/async \
  -H 'Content-Type: application/json' \
  -d '{
    "phenotype_gene_csv": "../input/gene_phenotype_score.csv",
    "vep_output_csv": "../input/tes1.vep.csv",
    "hpo_file": "../input/hpo_ids.txt",
    "output_csv": "../output/case_final_score.csv",
    "ppi_output_csv": "../output/case_ppi_score.csv",
    "clean_output_dir": true,
    "candidate_top_n": 30000,
    "output_all_ppi_fields": true,
    "include_audit": false,
    "vep_chunksize": 250000
  }'
```

返回示例：

```json
{
  "job_id": "...",
  "status": "queuing",
  "mode": "clean_case"
}
```

查询进度：

```bash
curl http://127.0.0.1:9000/score/<job_id> | python -m json.tool
```

下载结果：

```bash
curl -L -o final_score.csv http://127.0.0.1:9000/score/<job_id>/csv
curl -L -o ppi_score.csv http://127.0.0.1:9000/score/<job_id>/ppi-csv
```

### 5. curl -F 上传文件

如果需要通过 HTTP 上传输入文件，使用 upload 异步接口：

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/upload/async \
  -F "phenotype_gene_csv=@gene_phenotype_score.csv" \
  -F "vep_output_csv=@tes1.vep.csv" \
  -F "hpo_file=@hpo_ids.txt" \
  -F "output_csv=../output/case_final_score.csv" \
  -F "ppi_output_csv=../output/case_ppi_score.csv" \
  -F "clean_output_dir=true" \
  -F "candidate_top_n=30000" \
  -F "output_all_ppi_fields=true" \
  -F "include_audit=false" \
  -F "vep_chunksize=250000"
```

## 输入

### phenotype-gene CSV

必须包含：

| 字段 | 说明 |
| --- | --- |
| `gene_symbol` | HGNC gene symbol |

推荐包含：

| 字段 | 说明 |
| --- | --- |
| `gene_score` | phenotype-gene 分数；用于最终融合排名 |
| `gene_rank` | phenotype-gene 排名 |
| `conclusion_code` | phenotype 结论标签 |
| `best_disease_score` | 最佳疾病匹配分 |
| `best_disease_name` | 最佳疾病名称 |
| `best_omim_id` | 最佳 OMIM ID |
| `best_orpha_id` | 最佳 Orphanet ID |
| `best_mondo_id` | 最佳 MONDO ID |
| `best_disease_match_status` | 疾病匹配状态 |
| `mapping_basis` | 疾病匹配依据 |

### VEP CSV

必须包含：

| 字段 | 说明 |
| --- | --- |
| `gene_symbol` | 变异对应的基因 |

推荐包含：

| 字段 | 说明 |
| --- | --- |
| `pathogenic_rank` | 变异致病性排序；按基因取最小值 |
| `cadd_phred` | CADD PHRED 分数；按基因取最大值 |

大文件模式只读取 `gene_symbol`、`pathogenic_rank`、`cadd_phred`，避免全量加载 9GB 以上 VEP CSV。

### HPO 输入

可以传：

```text
hpo_file
```

或：

```text
hpo_ids
```

示例：

```text
HP:0001250
HP:0001259
HP:0410263
```

## 输出

### 1. `*_ppi_score.csv`

纯 PPI 评分表。字段与 `RareDiseasePPIScorer.run()` 输出一致。

| 字段 | 说明 |
| --- | --- |
| `gene` | 候选基因 |
| `in_network` | 是否存在于 STRING 网络 |
| `disease_score` | 与疾病锚点 `D` 的互作和距离分数 |
| `tissue_score` | 与组织核心锚点 `T` 的互作和距离分数 |
| `topology_score` | 全局 degree 和 betweenness 拓扑分数 |
| `ppi_final` | 最终 PPI 综合分数 |
| `score_mode` | PPI 融合模式 |
| `score_weight_sum` | 本次参与 PPI 融合的权重和 |
| `note` | 边界情况标记 |
| `gene_in_d` | 是否进入疾病锚点 `D` |
| `gene_d_evidence_score` | D 集证据加权分 |
| `gene_d_sources_json` | D 集支持来源 JSON |
| `gene_in_t` | 是否进入组织锚点 `T` |
| `gene_t_weight` | T 层支持权重 |
| `gene_t_layers_json` | T 集层来源 JSON |
| `gene_t_tissues_json` | T 集组织来源 JSON |
| `mapped_tissues_json` | HPO 映射得到的 Top 组织 JSON |
| `d_gene_count` | D 集基因数 |
| `t_gene_count` | T 集基因数 |
| `top_neighbors_json` | STRING Top 邻居及 D/T 标签 |
| `top_neighbors_count` | 返回的邻居数量 |

### 2. `*_final_score.csv`

最终病例融合表，合并 phenotype-gene 分数、VEP 基因汇总和 PPI 网络分数。

核心字段：

| 字段 | 说明 |
| --- | --- |
| `final_rank` | 最终综合排名；只给 `gene_score` 非空且 `in_network=true` 的基因编号 |
| `combined_score` | `(gene_score + ppi_final) / 2` |
| `gene_score` | phenotype-gene 分数 |
| `ppi_final` | PPI 综合分数 |
| `ppi_rank` | 只按 `ppi_final` 排序的 PPI 名次 |
| `best_pathogenic_rank` | 该基因 VEP 记录中的最佳致病性排名 |
| `variant_row_count` | 该基因对应的 VEP 记录数 |
| `max_cadd_phred` | 该基因 VEP 记录中的最大 CADD PHRED |

`final_rank` 不是文件行号。若某个基因有 PPI 分数，但 phenotype 输入中的 `gene_score` 为空，则该基因会保留在最终表里，但 `combined_score` 和 `final_rank` 为空。

完整字段解释见：

```text
FINAL_SCORE_README.md
```

## 主要参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `candidate_top_n` | `30000` | 取 VEP top N 和 phenotype top N 基因的并集；`0` 表示全部基因 |
| `vep_chunksize` | `250000` | VEP CSV 分块读取行数 |
| `output_all_ppi_fields` | `false` | 是否输出完整 PPI 证据字段和 Top 邻居 |
| `include_neighbors` | `false` | 是否输出 `top_neighbors_json` |
| `include_evidence_json` | `false` | 是否输出 D/T 证据 JSON |
| `clean_output_dir` | `true` | 写出前清理输出目录中的旧普通文件 |
| `ppi_output_csv` | 自动派生 | 纯 PPI 表路径 |
| `output_csv` | 自动生成 | 最终融合表路径 |

