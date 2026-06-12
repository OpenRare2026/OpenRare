# CRE 调控区 + ncRNA 注释模块

本模块用于对 hg38/GRCh38 VCF 做两类区域注释，并把结果写入 VCF `INFO` 字段：

- ENCODE SCREEN cCRE 调控区注释：`REG_*`
- GENCODE v49 非编码 RNA gene 注释：`NCRNA_*`

本模块可以单独运行，也可以由根目录的 `前置VCF处理.sh` 在 VAF 前置处理之后自动调用。

## 输入

- `input.vcf` 或 `input.vcf.gz`
- 参考基因组应为 hg38/GRCh38。
- 染色体命名需要和资源一致，默认资源使用 `chr1`、`chr2` 这种格式。

## 资源文件

默认需要以下资源文件：

```text
resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz
resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz.tbi
resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz.tbi
```

资源文件不提交到 GitHub，需要部署时单独准备。

### cCRE 资源来源

ENCODE SCREEN cCRE：

```text
https://www.encodeproject.org/files/ENCFF420VPZ/@@download/ENCFF420VPZ.bed.gz
```

生成精简 BED：

```bash
python3 scripts/prepare_encode_ccre_bed.py ENCFF420VPZ.bed.gz resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
sort -k1,1 -k2,2n resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed > /tmp/ccre.slim.bed
mv /tmp/ccre.slim.bed resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
bgzip -f resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
tabix -f -p bed resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz
```

### ncRNA 资源来源

GENCODE v49 GRCh38 GTF：

```text
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_49/gencode.v49.annotation.gtf.gz
```

生成精简 BED：

```bash
python3 scripts/prepare_gencode_ncrna_bed.py gencode.v49.annotation.gtf.gz resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
sort -k1,1 -k2,2n resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed > /tmp/ncrna.slim.bed
mv /tmp/ncrna.slim.bed resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
bgzip -f resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
tabix -f -p bed resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
```

## 单独运行

```bash
./scripts/run_regulatory_annotation.sh input.vcf.gz output_prefix
```

也可以显式指定资源：

```bash
./scripts/run_regulatory_annotation.sh input.vcf.gz output_prefix ccre.bed.gz ncrna.bed.gz
```

## 输出

最终 VCF：

```text
<output_prefix>.regulatory.vcf.gz
<output_prefix>.regulatory.vcf.gz.tbi
```

统计文件：

```text
<output_prefix>.regulatory.summary.tsv
<output_prefix>.ncrna.summary.tsv
```

## 写入的 INFO 字段

cCRE 字段：

```text
REG_CCRE_ID
REG_CCRE_CLASS
REG_CCRE_COUNT
REG_CCRE_SOURCE
```

ncRNA 字段：

```text
NCRNA_GENE_ID
NCRNA_GENE_NAME
NCRNA_GENE_TYPE
NCRNA_GENE_COUNT
NCRNA_SOURCE
```

## 单模块 FastAPI

如只想调用 CRE + ncRNA 注释，不做 VAF 前置处理，可以启动：

```bash
pip install -r requirements.txt
./start_regulatory_api.sh
```

默认端口为 `10086`，接口为：

```text
POST /annotate
GET  /jobs/{job_id}
GET  /health
```
