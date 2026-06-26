# VCF VAF 前置注释模块

本模块用于在 VCF 的 `INFO` 字段中补充基于样本 `FORMAT/AD` 计算得到的 VAF 信息。它是 CRE 调控区注释和 ncRNA 注释之前的前置步骤。

## 输入

- `input.vcf` 或 `input.vcf.gz`
- VCF 必须包含样本列。
- 样本 `FORMAT` 中建议包含 `AD` 字段，即 `REF,ALT1,ALT2...` 的 allele depth。

## 输出 INFO 字段

脚本会新增或替换以下 INFO 字段：

```text
VAF     每个 ALT 等位基因的变异等位基因频率，Number=A
REF_DP  参考等位基因深度，Number=1
ALT_DP  每个 ALT 等位基因深度，Number=A
```

VAF 计算公式：

```text
VAF = ALT_DEPTH / (REF_DEPTH + sum(ALT_DEPTHS))
```

多 ALT 位点会输出逗号分隔的多个值。

## 单独运行

```bash
python3 step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz
```

指定样本：

```bash
python3 step2_add_vaf_to_vcf_info.py input.vcf.gz output.vaf.vcf.gz --sample P001
```

如果输出文件以 `.gz` 结尾，脚本会优先使用 `bgzip` 压缩，并在存在 `tabix` 时自动生成 `.tbi` 索引。

## 与总流程的关系

总流程脚本 `run_vcf_preprocessing.sh` 会先调用本模块生成：

```text
<output_prefix>.vaf.vcf.gz
<output_prefix>.vaf.vcf.gz.tbi
<output_prefix>.vaf.summary.txt
```

随后把 VAF 后的 VCF 继续交给 `regulatory_annotation/` 模块，生成最终的 CRE + ncRNA 注释 VCF。
