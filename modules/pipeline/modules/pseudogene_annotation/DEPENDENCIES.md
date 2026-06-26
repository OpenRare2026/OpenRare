# Pseudogene annotation module

来源目录：`/mnt/workspace/xiongliwen/04.Pseudogene_anno`

## 已复制文件

- `scripts/annotate_pseudogene.py`
- `docs/README_pseudogene_anno_module.md`

## 功能

对 VCF 增加假基因相关 INFO 字段：

- `is_pseudogene`
- `pseudogene_name`
- `pseudogene_source`

模块先做 HGNC 支持的 GENCODE/Pseudogene.org 坐标区间注释；数据库未命中的位点再进入 reads-level 规则判断。

## 默认数据依赖

当前未复制大数据，脚本默认读取原始公共数据路径：

- GENCODE v49 pseudogene GTF：`/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/GENCODE/release_49/gencode.v49.2wayconspseudos.gtf.gz`
- Pseudogene.org Human90：`/mnt/workspace/xiongliwen/00.PublicData/Pseudogene/Pseudogene.org/Human90/Human90.txt`
- HGNC：`/mnt/workspace/xiongliwen/00.PublicData/phenotype_hpo_v1/hgnc_complete_set.txt`

## 主流程接入方式

总流程在 `scripts/run_full_pipeline.sh` 的第 03 步直接调用此模块（可通过 `--pseudogene-annotation no` 跳过）。总入口内部会：

1. 调用 `annotate_pseudogene.py --input tmp.vcf --output tmp.pseudogene.vcf --log-json ...`
2. 使用 `bgzip` 压缩为 `.vcf.gz`
3. 使用 `bcftools index` 或 `tabix` 建索引

这样后续 VEP runner 可以稳定读取 gzip VCF。
