# VCF preprocessing 依赖梳理

来源代码目录：`/mnt/workspace/wangzilu1/openrare_submit/repo`
来源资源目录：`/mnt/workspace/wangzilu1/regulatory_annotation/resources`

## 主入口

- `run_vcf_preprocessing.sh`
  - 总流程入口。
  - 顺序调用 VAF 前置处理和 CRE/NCRNA 调控区注释。
- `preprocessing_api.py`
  - FastAPI 包装，默认端口曾配置为 10087。
- `start_preprocessing_api.sh`
  - API 启动脚本。

## VAF 模块

- `add_vaf_to_vcf_info/step2_add_vaf_to_vcf_info.py`
  - 从 FORMAT 字段计算/写入 INFO/VAF。
  - 要求输入 VCF 有样本列和可用 genotype/depth 信息。

## CRE + NCRNA 注释模块

- `regulatory_annotation/regulatory_annotation_api.py`
  - CRE/NCRNA 注释 API，默认端口曾配置为 10086。
- `regulatory_annotation/scripts/run_regulatory_annotation.sh`
  - 调控注释 shell 入口。
- `regulatory_annotation/scripts/annotate_vcf_regulatory.py`
  - 使用 ENCODE SCREEN cCRE BED 注释 VCF INFO。
- `regulatory_annotation/scripts/annotate_vcf_ncrna.py`
  - 使用 GENCODE ncRNA BED 注释 VCF INFO。
- `regulatory_annotation/scripts/prepare_encode_ccre_bed.py`
  - 从 ENCODE/S屏幕数据制备 slim BED。
- `regulatory_annotation/scripts/prepare_gencode_ncrna_bed.py`
  - 从 GENCODE GTF 制备 ncRNA slim BED。

## 已复制依赖数据

- `resources/regulatory/hg38/ENCFF420VPZ.bed.gz`
  - ENCODE SCREEN / WengLab cCRE 原始 BED。
- `resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz`
  - 实际 CRE 注释使用的 slim BED。
- `resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz.tbi`
  - tabix 索引。
- `resources/ncrna/hg38/gencode.v49.annotation.gtf.gz`
  - GENCODE v49 原始 GTF。
- `resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz`
  - 实际 ncRNA 注释使用的 slim BED。
- `resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz.tbi`
  - tabix 索引。

## 软件依赖

- `python3`
- `bash`
- `bcftools`
- `bgzip`
- `tabix`
- Python FastAPI/uvicorn，用于 API 服务。

## 输出

典型输出：

- `<prefix>.vaf.vcf.gz`
- `<prefix>.vaf.vcf.gz.tbi`
- `<prefix>.vaf.summary.txt`
- `<prefix>.regulatory.vcf.gz`
- `<prefix>.regulatory.vcf.gz.tbi`
- `<prefix>.regulatory.summary.tsv`
- `<prefix>.ncrna.summary.tsv`

## V3 当前策略

本目录是 V3 梳理副本。脚本保留原始逻辑，资源也复制了一份，便于后续在 `pipline_V3` 内重排主流程。后续若正式整合到总 API，建议把资源路径改成统一配置，而不是依赖原始工作目录。
