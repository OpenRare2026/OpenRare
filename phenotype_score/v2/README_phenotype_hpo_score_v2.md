# 表型-HPO 评分模块 v2

## 1. 模块简要介绍

本模块用于回答一个核心问题：

> 对于输入变异涉及的基因，该基因的已知疾病表型谱在多大程度上能够解释患者的 HPO 表型？

模块输入患者 HPO list 和已注释变异 CSV，先从变异表中提取候选基因，再查询 OMIM、Orphanet、MONDO、HPOA 等公共知识库，构建 gene-disease-HPO 关系。随后将患者 HPO 与每个候选 gene 的疾病 HPO 进行语义相似性匹配，输出 gene 维度和 variant 维度两个结果文件。

当前 v2 版本的定位是表型解释评分，不是变异致病性判定。`gene_score` 仅表示“该基因关联疾病的表型谱与患者 HPO 的相似程度”，不能单独作为诊断结论。最终诊断仍需结合变异类型、频率、ClinVar、ACMG、遗传模式、家系信息和临床证据。

当前实现要点：

- 从输入 CSV 的 `all_genes` 提取候选 gene，并用 `gene_symbol` 将 gene-level 结果回填到 variant-level 输出。
- 对 gene symbol 进行 HGNC 归一化，正式 HGNC symbol 优先；若某个 alias 与另一个正式 symbol 冲突，不再用 alias 覆盖正式 symbol。
- 使用 HPO 层级结构计算 HPO 语义相似性，支持精确匹配和祖先/后代层级相关匹配。
- 使用 HPOA 计算 IC，按患者 HPO 的 IC 权重汇总 disease-level score。
- OMIM 与 Orphanet 疾病通过 MONDO exact/equivalent xref 进行明确映射；匹配到同一 MONDO disease 时合并为一条 disease profile，并保留原始 OMIM/ORPHA ID。
- 非编码区或无 gene 注释位点暂不做目标 gene 推断；这类记录在 variant-level 输出中保留，并标记为 `NO_GENE_ANNOTATION`。

## 2. 输入输出和字段解释

### 输入

#### 输入 1：患者 HPO list

默认测试文件：

```text
/mnt/workspace/xiongliwen/03.phenotype_score/v2/hpo_test.txt
```

格式要求：

- 每行一个 HPO ID，例如 `HP:0001324`
- 空行和以 `#` 开头的注释行会被跳过
- HPO alt_id 或 obsolete HPO 会尽量映射到当前 HPO ID
- 无法识别的 HPO 不参与主评分

示例：

```text
HP:0003560
HP:0001324
HP:0003704
HP:0003697
HP:0009027
```

#### 输入 2：变异注释 CSV

默认测试文件：

```text
/mnt/workspace/pangjiangshuan/vep_runner/output/all_900_genes_mutations1_pass_weak_germline.vep.csv
```

必须包含字段：

| 字段 | 作用 |
|---|---|
| `all_genes` | 用于提取候选 gene。一个位点可能包含多个 gene。 |
| `gene_symbol` | variant-level 输出回填时使用的 gene。最终每个 variant row 按该字段关联 gene-level 评分。 |

推荐包含字段：

| 字段 | 作用 |
|---|---|
| `chrom`, `pos`, `ref`, `alt` | 用于生成 `variant_id`。 |
| `consequence`, `impact`, `hgvsc`, `hgvsp` | 原始变异注释字段，会原样保留在 variant-level 输出。 |
| `revel_score`, `cadd_phred`, `gnomAD_*`, `spliceAI_*`, `clinvar_*` | 原始变异证据字段，会原样保留；当前表型模块不直接参与这些字段的打分。 |

### 输出

输出目录默认：

```text
/mnt/workspace/xiongliwen/03.phenotype_score/v2/results_v2
```

输出 3 个文件：

| 文件 | 说明 |
|---|---|
| `gene_phenotype_score.csv` | gene 维度结果。每个候选 gene 一行。 |
| `variant_phenotype_score.csv` | variant 维度结果。保留输入 CSV 原始字段，并追加该 variant 对应 gene 的表型评分字段。 |
| `run_summary.json` | 本次运行摘要，包括输入路径、候选 gene 数、输出文件路径等。 |

### gene_phenotype_score.csv 字段

| 字段 | 含义 |
|---|---|
| `gene_symbol` | HGNC 归一化后的 gene symbol。 |
| `hgnc_id` | HGNC ID。 |
| `gene_score` | gene 的最终表型匹配分，取该 gene 所有关联 disease profile 中最高的 disease score。范围通常为 0-1。 |
| `conclusion_code` | 表型匹配结论分层。只表示表型相似性，不表示致病性。 |
| `best_disease_score` | 当前 gene 下最佳匹配疾病的 score，通常等于 `gene_score`。 |
| `best_disease_name` | 最佳匹配疾病名称。 |
| `best_omim_id` | 最佳匹配疾病对应的 OMIM ID；无则为空。 |
| `best_orpha_id` | 最佳匹配疾病对应的 Orphanet ID；无则为空。 |
| `best_mondo_id` | 最佳匹配疾病对应的 MONDO ID；无则为空。 |
| `best_disease_source_dbs` | 最佳疾病记录来源，例如 `OMIM`、`ORPHA`、`OMIM;ORPHA`。 |
| `best_disease_match_status` | OMIM/ORPHA 疾病匹配状态。`matched_same_disease` 表示通过 MONDO 明确匹配为同一疾病；`separate_omim_record` 或 `separate_orpha_record` 表示单库记录。 |
| `mapping_basis` | 疾病映射依据，例如 `MONDO_equivalentTo`；无明确跨库映射时为 `none`。 |
| `second_best_disease_score` | 同一 gene 下第二高 disease score；无第二个 disease profile 时为空。 |
| `score_gap_to_second_best` | 最佳疾病与第二佳疾病的分差。分差越大，说明最佳疾病在该 gene 内更突出。 |
| `disease_profile_count` | 该 gene 可用于评分的疾病模型数量。 |
| `input_hpo_count` | 输入 HPO 数量。 |
| `scoring_hpo_count` | 有效并参与评分的 HPO 数量。 |
| `matched_hpo_count` | 患者 HPO 中与最佳疾病 HPO 匹配成功的数量。 |
| `unmatched_hpo_count` | 患者 HPO 中未匹配成功的数量。 |
| `mean_input_hpo_ic` | 输入 HPO 的平均 IC，反映输入表型整体特异性。 |
| `candidate_variant_count_in_gene` | 输入 CSV 中该 gene 涉及的候选 variant 数。 |
| `gene_sources` | gene 来源；当前主要为 `annotated_gene`。 |
| `best_term_evidence_summary` | 每个患者 HPO 的最佳疾病 HPO 匹配摘要，格式为 `patient_hpo->disease_hpo:similarity`。 |
| `db_versions` | 本次使用的知识库版本摘要。 |
| `warning` | 该 gene 的警告信息，例如无疾病模型。 |
| `sample_id` | 样本 ID，默认取 HPO 文件名。 |
| `gene_rank` | 按 `gene_score` 从高到低排序得到的 gene 排名。 |

### variant_phenotype_score.csv 字段

该文件保留输入 CSV 的全部原始字段，并追加以下字段：

| 字段 | 含义 |
|---|---|
| `sample_id` | 样本 ID，默认取 HPO 文件名。 |
| `variant_id` | 由 `chrom-pos-ref-alt` 拼接得到的位点 ID。 |
| `gene_symbol_raw` | 输入 CSV 中原始 `gene_symbol`。 |
| `gene_symbol_normalized` | HGNC 归一化后的 gene symbol。 |
| `hgnc_id_v2` | 归一化 gene 对应 HGNC ID。 |
| `gene_source` | gene 来源。无 gene 注释时为 `no_gene_annotation`，否则为 `annotated_gene`。 |
| `gene_score` | 该 variant 对应 gene 的 gene-level 表型分。 |
| `gene_rank` | 该 variant 对应 gene 在 gene-level 结果中的排名。 |
| `conclusion_code` | 该 variant 对应 gene 的表型匹配结论。 |
| `best_disease_score` | 该 variant 对应 gene 的最佳 disease score。 |
| `best_disease_name` | 该 variant 对应 gene 的最佳匹配疾病名称。 |
| `best_omim_id` | 最佳匹配疾病 OMIM ID。 |
| `best_orpha_id` | 最佳匹配疾病 Orphanet ID。 |
| `best_mondo_id` | 最佳匹配疾病 MONDO ID。 |
| `best_disease_source_dbs` | 最佳匹配疾病来源数据库。 |
| `matched_hpo_count` | 患者 HPO 与最佳疾病 HPO 匹配成功数量。 |
| `unmatched_hpo_count` | 患者 HPO 未匹配数量。 |
| `phenotype_score_reused` | 是否复用 gene-level 评分结果。当前同一 gene 的所有 variant 复用同一个 gene-level 表型分。 |
| `phenotype_score_source_gene` | 该 variant 表型分来自哪个归一化 gene。 |
| `warning` | variant-level 警告，例如 `no_gene_annotation` 或 `no_gene_disease_model`。 |

### conclusion_code 解释

| conclusion_code | 含义 |
|---|---|
| `PHENOTYPE_MATCH_STRONG` | 强表型匹配，`gene_score >= 0.80`。 |
| `PHENOTYPE_MATCH_MODERATE` | 中等表型匹配，`0.50 <= gene_score < 0.80`。 |
| `PHENOTYPE_MATCH_WEAK` | 弱表型匹配，`0.20 <= gene_score < 0.50`。 |
| `PHENOTYPE_MATCH_NONE` | 无明显表型匹配，`gene_score < 0.20` 或匹配贡献为 0。 |
| `NO_GENE_DISEASE_MODEL` | 该 gene 在当前知识库中没有可用于评分的 gene-disease-HPO 模型。 |
| `NO_VALID_SCORING_HPO` | 输入 HPO 中没有可用于评分的有效 HPO。 |
| `NO_GENE_ANNOTATION` | variant 无 gene 注释；当前 v2 不做非编码区目标 gene 推断。 |

## 3. 使用方法

### FastAPI 服务方式

推荐用 API 方式提交任务。服务启动后，每次提交会立即返回一个 `uid` 和当前 `status`。客户端后续用该 `uid` 查询任务状态；当 `status=completion` 时，再下载输出文件。

状态约定：

| status | 含义 |
|---|---|
| `queuing` | 任务已进入队列或正在运行。 |
| `completion` | 任务完成，可以下载输出文件。 |
| `failure` | 任务失败，查看返回 JSON 中的 `message` 和 `log_tail`。 |

启动 API 服务：

```bash
cd /mnt/workspace/xiongliwen/03.phenotype_score/v2

/mnt/workspace/xiongliwen/miniconda3/bin/conda run --no-capture-output -n hpo \
  uvicorn phenotype_hpo_score_api:app --host 0.0.0.0 --port 7002
```

提交任务：

```bash
curl -s -X POST http://172.27.206.113:7002/runs \
  -F file=@/path/to/input.csv \
  -F hpo_file=@/path/to/hpo.txt \
  -F hgvs=true
```

也可以不上传 HPO 文件，直接传 HPO 文本：

```bash
curl -s -X POST http://172.27.206.113:7002/runs \
  -F file=@/path/to/input.csv \
  -F 'hpo_list=HP:0003560,HP:0001324,HP:0003704' \
  -F hgvs=true
```

提交后返回示例：

```json
{
  "uid": "2f4f8d6e6e3f4f8c9b7a4a7f5c2d1e9a",
  "status": "queuing",
  "phase": "queued",
  "message": "Job queued",
  "status_url": "/runs/2f4f8d6e6e3f4f8c9b7a4a7f5c2d1e9a",
  "files_url": "/runs/2f4f8d6e6e3f4f8c9b7a4a7f5c2d1e9a/files"
}
```

查询任务状态：

```bash
curl -s http://172.27.206.113:7002/runs/{uid}
```

若返回 `status=completion`，可查看输出文件列表：

```bash
curl -s http://172.27.206.113:7002/runs/{uid}/files
```

每个完成任务只对外提供 3 个结果文件：

| 文件 | 说明 |
|---|---|
| `README_phenotype_hpo_score_v2.md` | 模块 README。 |
| `gene_phenotype_score.csv` | gene 维度评分结果。 |
| `variant_phenotype_score.csv` | variant 维度评分结果。 |

下载文件：

```bash
curl -O http://172.27.206.113:7002/runs/{uid}/files/README_phenotype_hpo_score_v2.md
curl -O http://172.27.206.113:7002/runs/{uid}/files/gene_phenotype_score.csv
curl -O http://172.27.206.113:7002/runs/{uid}/files/variant_phenotype_score.csv
```

说明：

- API 内部仍会读取评分脚本产生的 summary 内容，用于状态 JSON 和日志；但不再把 `run_summary.json` 作为最终下载文件输出。
- `hgvs` 参数当前仅作为兼容字段接收，v2 表型评分不使用该参数。
- 如果不传 `hpo_file` 或 `hpo_list`，API 会使用工作目录中的默认测试 HPO 文件 `hpo_test.txt`。

### 运行环境

远程服务器：

```text
172.27.206.113
```

工作目录：

```text
/mnt/workspace/xiongliwen/03.phenotype_score/v2
```

推荐 conda 环境：

```text
hpo
```

### 默认测试命令

```bash
cd /mnt/workspace/xiongliwen/03.phenotype_score/v2

/mnt/workspace/xiongliwen/miniconda3/bin/conda run --no-capture-output -n hpo python phenotype_hpo_score_v2.py \
  --input-csv /mnt/workspace/pangjiangshuan/vep_runner/output/all_900_genes_mutations1_pass_weak_germline.vep.csv \
  --hpo-file /mnt/workspace/xiongliwen/03.phenotype_score/v2/hpo_test.txt \
  --data-dir /mnt/workspace/xiongliwen/00.PublicData \
  --outdir /mnt/workspace/xiongliwen/03.phenotype_score/v2/results_v2
```

`--no-capture-output` 用于让日志实时打印，便于观察程序当前运行到哪一步。

### 参数说明

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--input-csv` | 测试 VEP CSV 文件 | 输入变异注释 CSV。 |
| `--hpo-file` | `hpo_test.txt` | 患者 HPO list 文件。 |
| `--data-dir` | `/mnt/workspace/xiongliwen/00.PublicData` | 公共数据库根目录。 |
| `--outdir` | `results_v2` | 输出目录。 |
| `--min-similarity` | `0.20` | HPO 语义匹配的最低 similarity 阈值。低于该值视为未匹配。 |
| `--max-orpha-files` | `0` | 调试参数。0 表示解析全部 Orphapacket YAML。 |

### 运行日志

程序会打印主要步骤和耗时：

```text
[1/9] Loading HPO ontology
[2/9] Loading patient HPO
[3/9] Loading HPOA and computing IC
[4/9] Loading HGNC aliases
[5/9] Reading variant CSV and candidate genes
[6/9] Loading OMIM branch
[7/9] Loading ORPHA branch
[8/9] Loading MONDO xrefs
[9/9] Scoring genes
[post] Building variant-level output
[done] Run completed
```

ORPHA 解析会每 1000 个 Orphapacket 文件打印一次进度；gene scoring 会每 100 个 gene 打印一次进度。

### 当前 v2 限制

- 不做非编码区目标 gene 推断。
- 不直接判断变异致病性。
- 不使用频率、ClinVar、REVEL、CADD 等变异证据参与表型分；这些字段只在 variant-level 输出中保留。
- HPO 分数依赖公共数据库的 gene-disease-HPO 记录质量；若数据库记录缺失或疾病 HPO 不完整，分数会受影响。
