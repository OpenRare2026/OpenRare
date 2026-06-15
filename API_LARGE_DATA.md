# 大数据 API 使用说明

大 VEP CSV 推荐使用 clean-case 异步 API。

该入口针对 9GB 以上 VEP CSV 做了优化：

- VEP CSV 按 chunk 流式读取。
- 只读取 `gene_symbol`、`pathogenic_rank`、`cadd_phred` 三类必要列。
- PPI 评分使用锚点侧批量最短路径映射，避免对每个候选基因单独遍历图。
- 邻居 JSON 默认可关闭；只有调试或需要完整证据时再打开。
- 默认候选基因取 top 30000 VEP 基因和 top 30000 phenotype-ranked 基因的并集。设置 `candidate_top_n=0` 表示使用全部基因。

## 启动 API

```bash
cd script1
RARE_PPI_PORT=9000 ./run_api.sh
```

确认当前服务是支持大数据参数的新版本：

```bash
curl http://127.0.0.1:9000/version | python -m json.tool
```

返回结果的 `supports_parameters` 应包含：

```text
candidate_top_n
output_all_ppi_fields
ppi_output_csv
vep_chunksize
```

如果请求返回 422，并提示这些字段不存在，说明 9000 端口还在跑旧代码，需要重新拉取代码并重启 `run_api.sh`。

## 每个样本输出两张表

clean-case 每次运行会写两个 CSV：

```text
ppi_output_csv  纯 PPI 评分表，字段与主 README 的 PPI 输出表一致
output_csv      最终病例融合表，合并 phenotype-gene 分数、VEP 汇总和 PPI 分数
```

最终融合表 `*_final_score.csv` 的完整字段、排名规则和解读方式见：

```text
FINAL_SCORE_README.md
```

如果不传 `ppi_output_csv`，程序会根据 `output_csv` 自动生成，例如：

```text
case_final_score.csv -> case_ppi_score.csv
final_score.csv      -> ppi_score.csv
```

## 用 curl -F 上传大文件

当客户端需要通过 HTTP 上传文件时，使用 upload 异步接口：

```bash
curl -X POST http://127.0.0.1:9000/score/clean-case/upload/async \
  -F "phenotype_gene_csv=@/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/gene_phenotype_score.csv" \
  -F "vep_output_csv=@/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/tes1.vep.csv" \
  -F "hpo_file=@/path/to/hpo_ids.txt" \
  -F "output_csv=/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/output/case_final_score.csv" \
  -F "ppi_output_csv=/home/xiesiwei/vep_runner/26B01490717_3a1e48_fork16_hpo_/output/case_ppi_score.csv" \
  -F "clean_output_dir=true" \
  -F "candidate_top_n=30000" \
  -F "output_all_ppi_fields=true" \
  -F "include_audit=false" \
  -F "vep_chunksize=250000"
```

返回结果会包含 `job_id`。用下面命令查看进度：

```bash
curl http://127.0.0.1:9000/score/<job_id> | python -m json.tool
```

任务状态会包含：

```text
stage
message
progress
```

## 直接提交服务器上的已有路径

如果 VEP 和 phenotype CSV 已经在 API 所在服务器上，推荐用路径型异步接口，避免把 9GB 文件再上传复制一份：

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
    "include_neighbors": false,
    "include_evidence_json": false,
    "include_audit": false,
    "output_all_ppi_fields": false,
    "candidate_top_n": 30000,
    "timeout": 0,
    "vep_chunksize": 250000
  }'
```

如果需要完整 PPI 证据字段，包括证据 JSON 和 `top_neighbors_json`，设置：

```json
{
  "output_all_ppi_fields": true,
  "candidate_top_n": 30000
}
```

注意：完整证据字段会让 CSV 更大，因为每个保留基因都写入证据 JSON 和 STRING Top 邻居。

## 查询和下载

```bash
curl http://127.0.0.1:9000/score/<job_id>
curl -L -o final_score.csv http://127.0.0.1:9000/score/<job_id>/csv
curl -L -o ppi_score.csv http://127.0.0.1:9000/score/<job_id>/ppi-csv
```

## 常用表单字段

```text
phenotype_gene_csv=@gene_phenotype_score.csv
vep_output_csv=@tes1.vep.csv
hpo_file=@hpo_ids.txt
output_csv=../output/case_final_score.csv
ppi_output_csv=../output/case_ppi_score.csv
include_neighbors=false
include_evidence_json=false
include_audit=false
output_all_ppi_fields=false
candidate_top_n=30000
vep_chunksize=250000
```
