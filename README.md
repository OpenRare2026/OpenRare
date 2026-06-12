# OpenRare VCF 前置处理与注释模块

本分支新增一套 VCF 前置处理和区域注释流程，目标是把样本 VCF 处理成带有以下 INFO 注释的 VCF：

```text
VAF / REF_DP / ALT_DP
REG_CCRE_ID / REG_CCRE_CLASS / REG_CCRE_COUNT / REG_CCRE_SOURCE
NCRNA_GENE_ID / NCRNA_GENE_NAME / NCRNA_GENE_TYPE / NCRNA_GENE_COUNT / NCRNA_SOURCE
```

整体流程顺序：

1. `add_vaf_to_vcf_info/`：从样本 `FORMAT/AD` 计算 VAF，并写入 `VAF/REF_DP/ALT_DP`。
2. `regulatory_annotation/`：用 ENCODE SCREEN cCRE 注释调控区，写入 `REG_*`。
3. `regulatory_annotation/`：用 GENCODE v49 ncRNA gene BED 注释非编码 RNA 区域，写入 `NCRNA_*`。
4. `run_vcf_preprocessing.sh`：把上面两块串起来。
5. `preprocessing_api.py`：把总流程封装成 FastAPI。

## 目录说明

```text
add_vaf_to_vcf_info/
  step2_add_vaf_to_vcf_info.py   # VAF/REF_DP/ALT_DP 前置处理脚本
  README.md                      # VAF 模块中文说明

regulatory_annotation/
  regulatory_annotation_api.py   # 单独 CRE + ncRNA 注释 API，默认端口 10086
  start_regulatory_api.sh        # 单独注释 API 启动脚本
  scripts/                       # CRE/ncRNA 资源准备和 VCF 注释脚本
  README.md                      # CRE + ncRNA 模块中文说明

run_vcf_preprocessing.sh         # 总流程 shell：VAF -> CRE -> ncRNA
preprocessing_api.py             # 总流程 FastAPI，默认端口 10087
start_preprocessing_api.sh       # 总流程 API 启动脚本
```

大资源文件和结果文件不会提交到 GitHub，需要部署时单独放置。

## 资源准备

默认需要以下资源：

```text
regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz
regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz.tbi
regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz.tbi
```

资源生成方法见：

```text
regulatory_annotation/README.md
```

## 1. 单独运行 VAF 前置处理

```bash
python3 add_vaf_to_vcf_info/step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz
```

指定样本：

```bash
python3 add_vaf_to_vcf_info/step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz --sample P001
```

输出：

```text
output.vaf.vcf.gz
output.vaf.vcf.gz.tbi
```

## 2. 单独运行 CRE + ncRNA 注释

```bash
./regulatory_annotation/scripts/run_regulatory_annotation.sh input.vcf.gz output_prefix
```

显式指定资源：

```bash
./regulatory_annotation/scripts/run_regulatory_annotation.sh \
  input.vcf.gz \
  output_prefix \
  regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz \
  regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
```

输出：

```text
output_prefix.regulatory.vcf.gz
output_prefix.regulatory.vcf.gz.tbi
output_prefix.regulatory.summary.tsv
output_prefix.ncrna.summary.tsv
```

## 3. 运行总流程 shell

总流程脚本英文名为：

```text
run_vcf_preprocessing.sh
```

基础用法：

```bash
./run_vcf_preprocessing.sh input.vcf.gz output_prefix
```

指定样本：

```bash
./run_vcf_preprocessing.sh input.vcf.gz output_prefix P001
```

显式指定资源：

```bash
./run_vcf_preprocessing.sh \
  input.vcf.gz \
  output_prefix \
  P001 \
  regulatory_annotation/resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz \
  regulatory_annotation/resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
```

输出：

```text
output_prefix.vaf.vcf.gz
output_prefix.vaf.vcf.gz.tbi
output_prefix.vaf.summary.txt
output_prefix.regulatory.vcf.gz
output_prefix.regulatory.vcf.gz.tbi
output_prefix.regulatory.summary.tsv
output_prefix.ncrna.summary.tsv
```

最终的 `output_prefix.regulatory.vcf.gz` 是完整结果，包含 VAF、CRE、ncRNA 三类注释。

## 4. 启动总流程 FastAPI

安装依赖：

```bash
pip install -r regulatory_annotation/requirements.txt
```

启动：

```bash
./start_preprocessing_api.sh
```

默认端口：

```text
10087
```

可用环境变量修改端口：

```bash
PREPROCESS_API_PORT=10088 ./start_preprocessing_api.sh
```

健康检查：

```bash
curl http://127.0.0.1:10087/health
```

提交任务：

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

查询任务状态：

```bash
curl http://127.0.0.1:10087/jobs/<job_id>
```

返回结果中包含：

```text
vaf_vcf
vaf_index
vaf_summary
output_vcf
output_index
regulatory_summary
ncrna_summary
```

## 5. 单独启动 CRE + ncRNA 注释 API

如果不需要 VAF 前置处理，只想调用 CRE + ncRNA 注释：

```bash
cd regulatory_annotation
./start_regulatory_api.sh
```

默认端口：

```text
10086
```

接口：

```text
POST /annotate
GET  /jobs/{job_id}
GET  /health
```

## 路径规则

API 中的 `input_vcf`、`output_prefix`、`ccre_bed`、`ncrna_bed` 支持绝对路径，也支持相对于 `PREPROCESS_API_BASE_WORKDIR` 的相对路径。

为了避免误用危险路径，API 会拒绝包含 `..` 的路径。
