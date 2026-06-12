# VCF 前置处理总流程 API

本仓库新增了一个 VCF 前置处理总流程，按顺序完成：

1. 使用 `add_vaf_to_vcf_info/` 从样本 `FORMAT/AD` 计算并写入 `VAF/REF_DP/ALT_DP`。
2. 使用 `regulatory_annotation/` 写入 ENCODE cCRE 调控区注释 `REG_*`。
3. 使用 `regulatory_annotation/` 写入 GENCODE v49 ncRNA gene 注释 `NCRNA_*`。

总流程 shell：

```text
前置VCF处理.sh
```

总流程 FastAPI：

```text
preprocessing_api.py
start_preprocessing_api.sh
```

## 启动 API

```bash
pip install -r regulatory_annotation/requirements.txt
./start_preprocessing_api.sh
```

默认端口：

```text
10087
```

可以用环境变量调整：

```bash
PREPROCESS_API_PORT=10088 ./start_preprocessing_api.sh
```

## 调用示例

```bash
curl -X POST http://127.0.0.1:10087/preprocess \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/mnt/workspace/wangzilu1/test1.vcf",
    "output_prefix": "/mnt/workspace/wangzilu1/OpenRare/results/preprocess/api/test1"
  }'
```

指定样本：

```bash
curl -X POST http://127.0.0.1:10087/preprocess \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/mnt/workspace/wangzilu1/test1.vcf",
    "output_prefix": "/mnt/workspace/wangzilu1/OpenRare/results/preprocess/api/test1",
    "sample": "P001"
  }'
```

查询任务：

```bash
curl http://127.0.0.1:10087/jobs/<job_id>
```

## 输出文件

VAF 中间结果：

```text
<output_prefix>.vaf.vcf.gz
<output_prefix>.vaf.vcf.gz.tbi
<output_prefix>.vaf.summary.txt
```

最终注释结果：

```text
<output_prefix>.regulatory.vcf.gz
<output_prefix>.regulatory.vcf.gz.tbi
<output_prefix>.regulatory.summary.tsv
<output_prefix>.ncrna.summary.tsv
```

最终 VCF 同时包含：

```text
VAF / REF_DP / ALT_DP
REG_CCRE_ID / REG_CCRE_CLASS / REG_CCRE_COUNT / REG_CCRE_SOURCE
NCRNA_GENE_ID / NCRNA_GENE_NAME / NCRNA_GENE_TYPE / NCRNA_GENE_COUNT / NCRNA_SOURCE
```

## 路径规则

`input_vcf`、`output_prefix`、`ccre_bed`、`ncrna_bed` 支持绝对路径，也支持相对于 `PREPROCESS_API_BASE_WORKDIR` 的相对路径。

为了避免误用危险路径，API 会拒绝包含 `..` 的路径。
