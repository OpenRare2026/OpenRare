# 05 VCF INFO 回填到 VEP CSV 模块

功能：读取进入 04 VEP runner 的 VCF，把 VCF 中所有 INFO 字段展开为 `vcf_info_<INFO_ID>` 列，并把样本 FORMAT 展开为 `vcf_format_*` 列，追加到 04 生成的 VEP CSV 中。

主流程中本模块为第 **05** 步；输出 `vep_output.with_info.csv` 进入 **06** GENOS-EVEE 注释，再经 **07** HLA 过滤（默认）得到最终宽表。

## 输入

- `--input-csv`：04 VEP runner 生成的基础 CSV。
- `--input-vcf`：04 VEP runner 实际使用的 VCF，支持 `.vcf` 和 `.vcf.gz`。
- `--output-csv`：带 VCF INFO 列的新 CSV。

## 坐标匹配规则

- SNV 按 `chrom,pos,ref,alt` 精确匹配。
- Indel 同时支持 VCF 原始坐标和 VEP 常见的右移 1bp 表达方式，也支持 `-/插入序列`、`删除序列/-` 这类 VEP normalized allele 表达。
- 多等位位点会按 ALT 等位基因拆开；`Number=A` 和 `Number=R` 的 INFO 会按对应 ALT 取值。

## 单独运行示例

```bash
python3 modules/vcf_info_to_csv/scripts/add_vcf_info_to_vep_csv.py \
  --input-csv test/output/example/04_vep/vep_output.base.csv \
  --input-vcf test/output/example/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz \
  --output-csv test/output/example/05_vcf_info_to_csv/vep_output.with_info.csv \
  --log-json test/output/example/05_vcf_info_to_csv/vcf_info_to_csv.log.json
```
