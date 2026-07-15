# GTEx v11 表达数据预处理

将 GTEx 官网原始 TPM 与样本注释整理为流水线使用的 `gtex_v11_transcript_tpm.parquet`。

流水线读取路径（由 `OPENRARE_DATA_ROOT` 展开）：

```text
${OPENRARE_DATA_ROOT}/vep_data/GTEx/v11/expression/gtex_v11_transcript_tpm.parquet
```

配置见 [`modules/vep_runner/config/vep_runner_config.json`](../../modules/vep_runner/config/vep_runner_config.json) 中的 `gtex_transcript_tpm`。

---

## 输入文件

### 1. 转录本 TPM（gzip）

| 项目 | 说明 |
|------|------|
| 官网原始文件名 | `GTEx_Analysis_2025-08-22_V11_RSEMv1.3.3_transcripts_tpm.txt.gz` |
| 本地使用路径（示例） | `/path/to/GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz` |
| 下载页面 | [GTEx Portal — Bulk tissue expression](https://gtexportal.org/home/downloads/adult-gtex/bulk_tissue_expression) |

说明：本地文件名与官网仅大小写略有差异（`V11` → `v11`），内容为同一文件，下载后按脚本内 `TPM_FILE` 配置即可。

### 2. 样本注释

| 项目 | 说明 |
|------|------|
| 官网文件名 | `GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt` |
| 本地使用路径（示例） | `/path/to/GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt` |
| 下载页面 | [GTEx Portal — Metadata](https://gtexportal.org/home/downloads/adult-gtex/metadata) |

脚本用 `SAMPID` → `SMTSD` 将样本映射到组织类型。

---

## 输出文件

| 项目 | 说明 |
|------|------|
| 文件名 | `gtex_v11_transcript_tpm.parquet` |
| 生成方式 | 本目录 [`convert_gtex_simple.py`](convert_gtex_simple.py) 预计算 |
| 推荐部署路径 | `${OPENRARE_DATA_ROOT}/vep_data/GTEx/v11/expression/gtex_v11_transcript_tpm.parquet` |

处理逻辑概要：

1. 读取样本注释，按组织汇总样本 ID。
2. 流式读取 TPM 表（PyArrow），按组织对每个转录本取样本 TPM 的中位数（仅统计 `> 0` 的值）。
3. 写出 Parquet（`zstd` 压缩），行索引为 `transcript_id`，列为各组织 TPM 中位数。

---

## 运行转换

依赖（仅转换时需要，正式流水线不依赖 `pyarrow`）：

```bash
pip install pandas numpy pyarrow
```

编辑 `convert_gtex_simple.py` 顶部三个路径后执行：

```bash
cd modules/pipeline/resource_mock/gtex_preprocess
python convert_gtex_simple.py
```

将生成的 parquet 放到数据根目录：

```bash
mkdir -p "${OPENRARE_DATA_ROOT}/vep_data/GTEx/v11/expression"
cp /path/to/gtex_v11_transcript_tpm.parquet \
   "${OPENRARE_DATA_ROOT}/vep_data/GTEx/v11/expression/"
```

或在 `.env` 中设置 `OPENRARE_DATA_ROOT` 后，直接把 `OUTPUT_FILE` 指向上述目标路径。
