# 基因组变异分析报告

> **报告版本**：v1.1  
> **生成日期**：2026-06-15  
> **分析基础**：基于样本 26B01490717 的排序宽表 /mnt/workspace/lixinhang/code/search_agent/test_data/test_case/v3_P001_case/06_result_sorting/vep_output.sorted.csv

---

## 1. 报告头部（Header）

| 项目 | 内容 |
|------|------|
| 样本 ID | 26B01490717 |
| 家系类型 | 单人 |
| 家系关系 | 先证者 |
| 临床诊断 / 指征 | 从小听力有问题，带助听器，目前语言发育差，理解能力差，学习成绩差，韦氏评分50分，出生体重9斤 |
| HPO 表型 | 719b5408-70fe-4ee7-bb8f-dd81a7637688 |
| 报告受众 | clinician（临床医生） |
| 分析目的 | 基于全外显子/基因组测序变异注释宽表，识别与临床表型相关的候选致病变异 |
| 排序宽表来源 | /mnt/workspace/lixinhang/code/search_agent/test_data/test_case/v3_P001_case/06_result_sorting/vep_output.sorted.csv |
| VCF 来源 | /mnt/workspace/siwei/vcf_data/26B01490717_3a1e48.vcf |
| GRCh38 转换 | 172.27.206.113/mnt/workspace/changan/grch37_to_grch38_liftover/api_service/runs/26B01490717_3a1e48/output/output.grch38.vcf.gz |
| 分析日期 | 2026-06-15 |
| 报告人 | AI 辅助基因组解读系统（需临床遗传学专家复核） |

**关键提示**：本报告为**辅助决策**性质，所有候选变异需经实验验证（Sanger、功能实验）后方可用于临床决策。
---

## 2. 分析摘要（Executive Summary）

### 2.1 Top 基因快速列表

本次分析从排序宽表中提取 **Top 5 基因**，共涉及 5 个基因、215 个关键变异位点。

| 排名 | 基因 | 变异数 | 最高排序名次 | ClinVar | 主要关联表型 | 主要关联通路 |
|------|------|--------|--------------|---------|--------------|--------------|
| 1 | **AURKAIP1** | 20 | #16 | - | neurodegenerative disease; triple-negative breast cancer | Mitochondrial ribosome-associated quality control |
| 2 | **VWA1** | 20 | #27 | - | neuronopathy, distal hereditary motor, autosomal recessive 7; neuromuscular disease | - |
| 3 | **ATAD3B** | 78 | #33 | - | ovarian neoplasm; ulcerative colitis | - |
| 4 | **CCNL2** | 33 | #44 | - | infection; breast cancer | - |
| 5 | **ENSG00000241860** | 64 | #53 | - | myelodysplastic syndrome | - |

### 2.2 关键发现提示

- VWA1 检出 frameshift_variant（c.961_967del，p.Pro321SerfsTer28），为潜在功能缺失变异，但 ClinVar 无注释，且典型疾病表型（ distal hereditary motor neuropathy ）与患者听力障碍、语言发育差、智力低下不完全匹配；需家系验证与功能实验进一步确认。
- AURKAIP1 检出错义变异 p.Ala122Glu（CADD 14.09），位于调控元件附近，证据总分 +30，但 EAS_AF=0，仍需更多功能证据支持致病性。
- ATAD3B 检出两个高 CADD 错义变异（p.Arg219Gly，CADD 25.9；p.Arg386Gln，CADD 33），但疾病关联以卵巢肿瘤、溃疡性结肠炎为主，与当前神经发育表型关联性弱。
- 多个变异存在测序 reads 比例与 GATK 基因型 AF 不一致、深度偏低等问题，解读时优先参考 reads 支持，并推荐 Sanger 验证。
- strict_drug_candidates 中无符合标准的用药建议，本报告不提供针对上述基因的特异性药物治疗方案。

### 2.3 排序得分白盒展示（示例）

以 AURKAIP1 为例，排序得分构成如下：

```
evidence_score: +30
  ├── consequence=missense_variant(+15)
  ├── CADD=14.09(+2)
  ├── EAS_AF=0.000000e+00
  ├── frequency(+10)
  ├── domain(+3)
```
---

## 3. 基因详细分析（Gene Cards）

### 3.1 基因卡片 1：AURKAIP1


#### 3.1.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | AURKAIP1 |
| 染色体位置 | chr1:1374133（GRCh38） |
| 主要转录本 | NM_017900.3 |
| 基因功能 | Acts upstream of or within positive regulation of proteolysis. Located in mitochondrial matrix and nucleoplasm. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 | - |
| 主要关联表型 | neurodegenerative disease; triple-negative breast cancer |
| 主要关联通路 | Mitochondrial ribosome-associated quality control |
| 致病性排名 | #16 |

#### 3.1.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| AURKAIP1 p.Ala122Glu | chr1:1374133 G>T | ENST00000338338.10 | missense_variant | 14.09 | 0 | 0.0000 | - | **20.0%** |
| AURKAIP1 p.Ala122= | chr1:1374132 C>T | ENST00000338338.10 | synonymous_variant | 1.360 | 0 | 0.0000 | - | **20.0%** |
| AURKAIP1 chr1:1373333 C>T | chr1:1373333 C>T | ENST00000338338.10 | downstream_gene_variant | 1.995 | - | 0.003089 | - | **63.6%** |
| AURKAIP1 chr1:1377408 C>A | chr1:1377408 C>A | ENST00000338338.10 | upstream_gene_variant | 0.192 | - | 0.01548 | - | **23.5%** |
| AURKAIP1 chr1:1379143 G>A | chr1:1379143 G>A | ENST00000338338.10 | upstream_gene_variant | 2.914 | - | 0.01625 | - | **54.2%** |
| AURKAIP1 chr1:1375678 TA>T | chr1:1375678 TA>T | ENST00000338338.10 | upstream_gene_variant | 1.038 | - | 0.04147 | - | **42.9%** |
| AURKAIP1 chr1:1375788 G>C | chr1:1375788 G>C | ENST00000338338.10 | upstream_gene_variant | 2.213 | - | 0.01831 | - | **47.8%** |
| AURKAIP1 chr1:1374694 C>G | chr1:1374694 C>G | ENST00000338338.10 | intron_variant | 3.869 | 0 | 0.8998 | - | **46.2%** |
| AURKAIP1 chr1:1371178 T>C | chr1:1371178 T>C | ENST00000338338.10 | downstream_gene_variant | 1.740 | - | 0.9081 | - | **62.5%** |
| AURKAIP1 chr1:1372258 T>C | chr1:1372258 T>C | ENST00000338338.10 | downstream_gene_variant | 4.136 | - | 0.9072 | - | **63.6%** |
| AURKAIP1 chr1:1373248 A>G | chr1:1373248 A>G | ENST00000338338.10 | downstream_gene_variant | 0.278 | - | 0.9121 | - | **64.7%** |
| AURKAIP1 chr1:1373491 A>T | chr1:1373491 A>T | ENST00000338338.10 | downstream_gene_variant | 0.160 | - | 0.9114 | - | **64.3%** |
| AURKAIP1 chr1:1373602 A>G | chr1:1373602 A>G | ENST00000338338.10 | downstream_gene_variant | 1.416 | - | 0.9065 | - | **67.9%** |
| AURKAIP1 chr1:1375544 T>C | chr1:1375544 T>C | ENST00000338338.10 | upstream_gene_variant | 1.215 | - | 0.907 | - | **54.5%** |
| AURKAIP1 chr1:1376054 T>A | chr1:1376054 T>A | ENST00000338338.10 | upstream_gene_variant | 1.586 | - | 0.9069 | - | **41.7%** |
| AURKAIP1 chr1:1377962 A>G | chr1:1377962 A>G | ENST00000338338.10 | upstream_gene_variant | 1.597 | - | 0.9065 | - | **38.5%** |
| AURKAIP1 chr1:1379091 T>G | chr1:1379091 T>G | ENST00000338338.10 | upstream_gene_variant | 0.436 | - | 0.1104 | - | **42.9%** |
| AURKAIP1 chr1:1379327 A>G | chr1:1379327 A>G | ENST00000338338.10 | upstream_gene_variant | 0.367 | - | 0.9066 | - | **69.0%** |
| AURKAIP1 chr1:1379895 CA>C/CAA | chr1:1379895 CA>C/CAA | ENST00000338338.10 | upstream_gene_variant | 0.440 | - | 0.9069 | - | **50.0%** |
| AURKAIP1 chr1:1379963 G>A | chr1:1379963 G>A | ENST00000338338.10 | upstream_gene_variant | 0.740 | - | 0.9073 | - | **57.1%** |

#### 3.1.3 变异详细分析

##### 3.1.3.1 AURKAIP1 p.Ala122Glu

###### 3.1.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1374133 G>T（GRCh38） |
| 测序等位基因比例 | **20.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 2 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=5.26；FS（链偏倚）=3.522；MQ（比对质量）=60 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/4 |

###### 3.1.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | c.365C>A |
| HGVSp | p.Ala122Glu |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.1.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 14.09 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | 0.072 | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 1.33223e-05 |
| gnomAD 纯合数 | 0 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:3j9m.A3,PDB-ENSP_mappings:6nu3.A3,PDB-ENSP_mappings:6rw4.3,PDB-ENSP_mappings:6rw5.3,PDB-ENSP_mappings:6vlz.A3,PDB-ENSP_mappings:6vmi.A3,PDB-ENSP_mappings:6zm5.A3,PDB-ENSP_mappings:6zm6.A3,PDB-ENSP_mappings:6zs9.A3,PDB-ENSP_mappings:6zsa.A3,PDB-ENSP_mappings:6zsb.A3,PDB-ENSP_mappings:6zsc.A3,PDB-ENSP_mappings:6zsd.A3,PDB-ENSP_mappings:6zse.A3,PDB-ENSP_mappings:6zsg.A3,PDB-ENSP_mappings:7a5f.d6,PDB-ENSP_mappings:7a5g.d6,PDB-ENSP_mappings:7a5i.d6,PDB-ENSP_mappings:7a5k.d6,PDB-ENSP_mappings:7l08.A3,PDB-ENSP_mappings:7og4.A3,PDB-ENSP_mappings:7p2e.3,PDB-ENSP_mappings:7pnx.3,PDB-ENSP_mappings:7pny.3,PDB-ENSP_mappings:7pnz.3,PDB-ENSP_mappings:7po0.3,PDB-ENSP_mappings:7po1.3,PDB-ENSP_mappings:7po2.3,PDB-ENSP_mappings:7po3.3,PDB-ENSP_mappings:7qi4.A3,PDB-ENSP_mappings:7qi5.A3,PDB-ENSP_mappings:7qi6.A3,PDB-ENSP_mappings:8any.A3,PDB-ENSP_mappings:8csq.3,PDB-ENSP_mappings:8csr.3,PDB-ENSP_mappings:8css.3,PDB-ENSP_mappings:8cst.3,PDB-ENSP_mappings:8csu.3,PDB-ENSP_mappings:8k2a.Sn,PDB-ENSP_mappings:8oir.AD,PDB-ENSP_mappings:8ois.AD,PDB-ENSP_mappings:8qrk.3,PDB-ENSP_mappings:8qrl.3,PDB-ENSP_mappings:8qrm.3,PDB-ENSP_mappings:8qrn.3,PDB-ENSP_mappings:8xt0.Sn,PDB-ENSP_mappings:8xt2.Sn,AFDB-ENSP_mappings:AF-Q9NWT8-F1,PANTHER:PTHR32035 |
| 证据摘要 | consequence=missense_variant(+15); CADD=14.09(+2); EAS_AF=0.000000e+00; frequency(+10); domain(+3); total=+30 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.2 AURKAIP1 p.Ala122=

###### 3.1.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1374132 C>T（GRCh38） |
| 测序等位基因比例 | **20.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 2 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=5.26；FS（链偏倚）=3.522；MQ（比对质量）=60 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/4 |

###### 3.1.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | c.366G>A |
| HGVSp | p.Ala122= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.1.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.360 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0002319 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:3j9m.A3,PDB-ENSP_mappings:6nu3.A3,PDB-ENSP_mappings:6rw4.3,PDB-ENSP_mappings:6rw5.3,PDB-ENSP_mappings:6vlz.A3,PDB-ENSP_mappings:6vmi.A3,PDB-ENSP_mappings:6zm5.A3,PDB-ENSP_mappings:6zm6.A3,PDB-ENSP_mappings:6zs9.A3,PDB-ENSP_mappings:6zsa.A3,PDB-ENSP_mappings:6zsb.A3,PDB-ENSP_mappings:6zsc.A3,PDB-ENSP_mappings:6zsd.A3,PDB-ENSP_mappings:6zse.A3,PDB-ENSP_mappings:6zsg.A3,PDB-ENSP_mappings:7a5f.d6,PDB-ENSP_mappings:7a5g.d6,PDB-ENSP_mappings:7a5i.d6,PDB-ENSP_mappings:7a5k.d6,PDB-ENSP_mappings:7l08.A3,PDB-ENSP_mappings:7og4.A3,PDB-ENSP_mappings:7p2e.3,PDB-ENSP_mappings:7pnx.3,PDB-ENSP_mappings:7pny.3,PDB-ENSP_mappings:7pnz.3,PDB-ENSP_mappings:7po0.3,PDB-ENSP_mappings:7po1.3,PDB-ENSP_mappings:7po2.3,PDB-ENSP_mappings:7po3.3,PDB-ENSP_mappings:7qi4.A3,PDB-ENSP_mappings:7qi5.A3,PDB-ENSP_mappings:7qi6.A3,PDB-ENSP_mappings:8any.A3,PDB-ENSP_mappings:8csq.3,PDB-ENSP_mappings:8csr.3,PDB-ENSP_mappings:8css.3,PDB-ENSP_mappings:8cst.3,PDB-ENSP_mappings:8csu.3,PDB-ENSP_mappings:8k2a.Sn,PDB-ENSP_mappings:8oir.AD,PDB-ENSP_mappings:8ois.AD,PDB-ENSP_mappings:8qrk.3,PDB-ENSP_mappings:8qrl.3,PDB-ENSP_mappings:8qrm.3,PDB-ENSP_mappings:8qrn.3,PDB-ENSP_mappings:8xt0.Sn,PDB-ENSP_mappings:8xt2.Sn,AFDB-ENSP_mappings:AF-Q9NWT8-F1,PANTHER:PTHR32035 |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0; frequency(+10); domain(+3); total=+15 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.3 AURKAIP1 chr1:1373333 C>T

###### 3.1.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1373333 C>T（GRCh38） |
| 测序等位基因比例 | **63.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 7 条（合计 11 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=18.15；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.3.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 2 例，ALT 等位基因计数 2 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.995 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.003089 |
| gnomAD Popmax AF | 0.003089 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.003089; frequency(+3); total=-3 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.4 AURKAIP1 chr1:1377408 C>A

###### 3.1.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1377408 C>A（GRCh38） |
| 测序等位基因比例 | **23.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 4 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=3.68；FS（链偏倚）=2.336；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.4.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 7 例，ALT 等位基因计数 7 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.192 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01548 |
| gnomAD Popmax AF | 0.01548 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.01548; frequency(-15); total=-21 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.5 AURKAIP1 chr1:1379143 G>A

###### 3.1.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1379143 G>A（GRCh38） |
| 测序等位基因比例 | **54.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 11 条 / 变异序列 13 条（合计 24 条 reads） |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=12.4；FS（链偏倚）=16.333；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.1.3.5.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 7 例，ALT 等位基因计数 7 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.914 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01625 |
| gnomAD Popmax AF | 0.01625 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.01625; frequency(-15); total=-21 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.6 AURKAIP1 chr1:1375678 TA>T

###### 3.1.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1375678 TA>T（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 3 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=8.37；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.6.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 30 例，ALT 等位基因计数 31 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.038 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.04147 |
| gnomAD Popmax AF | 0.8733 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.04147; frequency(-20); total=-26 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.7 AURKAIP1 chr1:1375788 G>C

###### 3.1.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1375788 G>C（GRCh38） |
| 测序等位基因比例 | **47.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 11 条（合计 23 条 reads） |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=10.29；FS（链偏倚）=1.648；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.1.3.7.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.213 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01831 |
| gnomAD Popmax AF | 0.1297 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.01831; frequency(-20); total=-26 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.8 AURKAIP1 chr1:1374694 C>G

###### 3.1.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1374694 C>G（GRCh38） |
| 测序等位基因比例 | **46.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 6 条（合计 13 条 reads） |
| 测序深度 | 15 |
| 碱基质量指标 | QD（质量/深度）=8.59；FS（链偏倚）=2.276；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.1.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 662 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | c.52+11G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.869 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.8998 |
| gnomAD Popmax AF | 0.9657 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.8998; frequency(-35); total=-38 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.9 AURKAIP1 chr1:1371178 T>C

###### 3.1.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1371178 T>C（GRCh38） |
| 测序等位基因比例 | **62.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 15 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=15.57；FS（链偏倚）=1.685；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.740 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9081 |
| gnomAD Popmax AF | 0.988 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9081; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.10 AURKAIP1 chr1:1372258 T>C

###### 3.1.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1372258 T>C（GRCh38） |
| 测序等位基因比例 | **63.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 21 条（合计 33 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=18.6；FS（链偏倚）=11.714；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.136 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9072 |
| gnomAD Popmax AF | 0.9749 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9072; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.11 AURKAIP1 chr1:1373248 A>G

###### 3.1.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1373248 A>G（GRCh38） |
| 测序等位基因比例 | **64.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 11 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=17.1；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.11.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 667 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.278 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9121 |
| gnomAD Popmax AF | 0.9898 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9121; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.12 AURKAIP1 chr1:1373491 A>T

###### 3.1.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1373491 A>T（GRCh38） |
| 测序等位基因比例 | **64.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 18 条（合计 28 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=17.13；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.12.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 664 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.160 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9114 |
| gnomAD Popmax AF | 0.9843 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9114; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.13 AURKAIP1 chr1:1373602 A>G

###### 3.1.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1373602 A>G（GRCh38） |
| 测序等位基因比例 | **67.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 19 条（合计 28 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=18.67；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 659 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.416 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9065 |
| gnomAD Popmax AF | 0.9883 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9065; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.14 AURKAIP1 chr1:1375544 T>C

###### 3.1.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1375544 T>C（GRCh38） |
| 测序等位基因比例 | **54.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 5 条 / 变异序列 6 条（合计 11 条 reads） |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=13.88；FS（链偏倚）=2.632；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.1.3.14.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.215 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.907 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.907; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.15 AURKAIP1 chr1:1376054 T>A

###### 3.1.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1376054 T>A（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 10 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=10.32；FS（链偏倚）=6.908；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.586 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9069 |
| gnomAD Popmax AF | 0.9882 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9069; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.16 AURKAIP1 chr1:1377962 A>G

###### 3.1.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1377962 A>G（GRCh38） |
| 测序等位基因比例 | **38.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 16 条 / 变异序列 10 条（合计 26 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 27 |
| 碱基质量指标 | QD（质量/深度）=8.1；FS（链偏倚）=1.775；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.1.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.597 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9065 |
| gnomAD Popmax AF | 0.9882 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9065; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.17 AURKAIP1 chr1:1379091 T>G

###### 3.1.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1379091 T>G（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 16 条 / 变异序列 12 条（合计 28 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 29 |
| 碱基质量指标 | QD（质量/深度）=11.09；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.17.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 30 例，ALT 等位基因计数 30 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.436 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1104 |
| gnomAD Popmax AF | 0.9342 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.1104; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.18 AURKAIP1 chr1:1379327 A>G

###### 3.1.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1379327 A>G（GRCh38） |
| 测序等位基因比例 | **69.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 20 条（合计 29 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=15.5；FS（链偏倚）=6.107；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.18.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.367 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9066 |
| gnomAD Popmax AF | 0.9741 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9066; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.19 AURKAIP1 chr1:1379895 CA>C/CAA

###### 3.1.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1379895 CA>C/CAA（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=20.5；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |


###### 3.1.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.440 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9069 |
| gnomAD Popmax AF | 0.9817 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9069; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |

##### 3.1.3.20 AURKAIP1 chr1:1379963 G>A

###### 3.1.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1379963 G>A（GRCh38） |
| 测序等位基因比例 | **57.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 4 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=14.52；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.1.3.20.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000338338.10 |
| RefSeq | NM_017900.3 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.1.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.740 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9073 |
| gnomAD Popmax AF | 0.9881 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9073; frequency(-35); total=-41 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，脚本严格筛选后无匹配用药候选；本报告不提供针对该基因的靶向用药建议。 |

###### 3.1.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41504393 | Meta-GWAS of Pig Semen Quality Traits Reveals Conserved Genes Regulating Mammalian Fertility. | Lin Q, Cai X, Zhong Z, Li T, Chen X, Ayalew W, Xu Z, Wei C, Zhang Z, Li X, Tang Y, Chen S, Zhou J, Si W, Ning C, Wang Q, Pan Y, Gao H, Yu Y, Zhang Z, Zhao Y, Fang L, Zhang Z, Cheng H, Li X, Zhou J, Chen X, Tang Y, Zhang Z. Adv Sci. 2026. | 跨品种猪精子质量性状 GWAS meta 分析显示 AURKAIP1 为保守的哺乳动物生育力调控基因，其同源基因亦与人类出生体重和身高遗传度显著相关。 | PubMed 检索结果 |


#### 3.1.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | neurodegenerative disease; triple-negative breast cancer |
| 关联通路 | Mitochondrial ribosome-associated quality control |
| 临床建议 | 受试者表现为先天性听力障碍、语言发育迟缓、认知功能受损（韦氏评分50分）及出生体重偏大（9斤）。AURKAIP1 定位于线粒体基质并参与蛋白酶解正调控及线粒体核糖体相关质量控制，其功能异常与神经退行性病变存在潜在关联。报告中最优先的编码区变异为 chr1:1374133 G>T（p.Ala122Glu，错义变异），CADD=14.09，证据评分+30，EAS_AF=0；但该变异及同相位 chr1:1374132 C>T（同义变异）的支持 reads 仅 2/10，且 reads VAF（0.2）与 GATK 基因型 AF（0.5）明显不一致，解读时优先参考 reads 支持，强烈建议 Sanger 验证。其余变异以启动子上游/下游变异为主，多位于增强子样调控元件（pELS/dELS）区域，EAS_AF 多在 0.003–0.91 之间，部分在中国参考人群中有携带记录，整体人群频率较高，独立致病证据有限。综合来看，AURKAIP1 作为神经发育相关候选基因具有生物学合理性，但当前测序数据对 p.Ala122Glu 的杂合状态支持不足，且未见明确 LoF 或 ClinVar 致病记录，该变异尚未达到可以独立解释临床表型的确定性水平。 |

#### 3.1.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.2 基因卡片 2：VWA1


#### 3.2.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | VWA1 |
| 染色体位置 | chr1:1439408（GRCh38） |
| 主要转录本 | NM_022834.5 |
| 基因功能 | VWA1 belongs to the von Willebrand factor (VWF; MIM 613160) A (VWFA) domain superfamily of extracellular matrix proteins and appears to play a role in cartilage structure and function (Fitzgerald et al., 2002 [PubMed 12062410]).[supplied by OMIM, Nov 2010] |
| 遗传模式 | Neuronopathy, distal hereditary motor, autosomal recessive 7 (Autosomal recessive) |
| 主要关联表型 | neuronopathy, distal hereditary motor, autosomal recessive 7; neuromuscular disease |
| 主要关联通路 | - |
| 致病性排名 | #27 |

#### 3.2.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| VWA1 p.Pro321SerfsTer28 | chr1:1439408 CCCCCACG>C | ENST00000476993.2 | frameshift_variant | - | - | 0.0000 | - | **50.0%** |
| VWA1 p.Leu324Ile | chr1:1439419 C>A | ENST00000476993.2 | missense_variant | 2.129 | 0 | 0.0000 | - | **40.0%** |
| VWA1 chr1:1442628 C>G | chr1:1442628 C>G | ENST00000476993.2 | 3_prime_UTR_variant | 1.994 | 0 | 0.01254 | - | **39.4%** |
| VWA1 chr1:1436060 CG>C | chr1:1436060 CG>C | ENST00000476993.2 | intron_variant | 2.304 | - | 0.01338 | - | **100.0%** |
| VWA1 chr1:1438298 C>T | chr1:1438298 C>T | ENST00000476993.2 | intron_variant | 4.460 | 0 | 0.01218 | - | **48.3%** |
| VWA1 chr1:1442722 A>G | chr1:1442722 A>G | ENST00000476993.2 | 3_prime_UTR_variant | 2.687 | 0 | 0.0226 | - | **21.7%** |
| VWA1 chr1:1436079 A>G | chr1:1436079 A>G | ENST00000476993.2 | intron_variant | 0.084 | 0 | 0.993 | - | **100.0%** |
| VWA1 chr1:1436388 CA>C | chr1:1436388 CA>C | ENST00000476993.2 | intron_variant | 0.086 | - | 0.8741 | - | **100.0%** |
| VWA1 chr1:1437955 C>G | chr1:1437955 C>G | ENST00000476993.2 | intron_variant | 0.164 | 0 | 0.908 | - | **95.7%** |
| VWA1 chr1:1437993 G>A | chr1:1437993 G>A | ENST00000476993.2 | intron_variant | 0.371 | 0 | 0.8563 | - | **100.0%** |
| VWA1 chr1:1438102 G>C | chr1:1438102 G>C | ENST00000476993.2 | intron_variant | 6.022 | 0 | 0.9714 | - | **48.5%** |
| VWA1 chr1:1440430 C>G | chr1:1440430 C>G | ENST00000476993.2 | 3_prime_UTR_variant | 2.218 | 0 | 1 | - | **70.6%** |
| VWA1 chr1:1440834 C>G | chr1:1440834 C>G | ENST00000476993.2 | 3_prime_UTR_variant | 1.112 | 0 | 1 | - | **100.0%** |
| VWA1 chr1:1441187 A>G | chr1:1441187 A>G | ENST00000476993.2 | 3_prime_UTR_variant | 0.155 | 0 | 0.8692 | - | **100.0%** |
| VWA1 chr1:1443133 T>C | chr1:1443133 T>C | ENST00000476993.2 | downstream_gene_variant | 0.988 | - | 0.9139 | - | **100.0%** |
| VWA1 chr1:1443457 T>C | chr1:1443457 T>C | ENST00000476993.2 | downstream_gene_variant | 1.941 | - | 0.9941 | - | **100.0%** |
| VWA1 p.Ala326Pro | chr1:1439425 G>C | ENST00000476993.2 | missense_variant | 0.118 | 0.01 | 0.0168522 | Benign | **66.7%** |
| VWA1 chr1:1439827 T>C | chr1:1439827 T>C | ENST00000476993.2 | 3_prime_UTR_variant | 1.244 | 0 | 0.01307 | Benign | **55.6%** |
| VWA1 p.Pro335= | chr1:1439454 A>G | ENST00000476993.2 | synonymous_variant | 0.257 | 0.01 | 0.9974 | Benign | **100.0%** |
| VWA1 chr1:1439805 G>C | chr1:1439805 G>C | ENST00000476993.2 | 3_prime_UTR_variant | 3.333 | 0 | 0.8568 | Benign | **40.0%** |

#### 3.2.3 变异详细分析

##### 3.2.3.1 VWA1 p.Pro321SerfsTer28

###### 3.2.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439408 CCCCCACG>C（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 2 条 / 变异序列 2 条（合计 4 条 reads） |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=16.4；FS（链偏倚）=0；MQ（比对质量）=57.01 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | 3/3 |

###### 3.2.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.961_967del |
| HGVSp | p.Pro321SerfsTer28 |
| VEP 后果 | frameshift_variant |
| VEP 影响等级 | HIGH |

###### 3.2.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | LC | LoF 预测标记 |

###### 3.2.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q6PCB0-F1,Phobius:NON_CYTOPLASMIC_DOMAIN,PANTHER:PTHR24020,MobiDB_lite:mobidb-lite,MobiDB_lite:mobidb-lite,Low_complexity_(Seg):seg |
| 证据摘要 | consequence=frameshift_variant(+33); splice_lof=SpliceAI:unknown(-8); domain(+3); total=+28 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.2 VWA1 p.Leu324Ile

###### 3.2.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439419 C>A（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 2 条（合计 5 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=12.53；FS（链偏倚）=0；MQ（比对质量）=57.52 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.970C>A |
| HGVSp | p.Leu324Ile |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.129 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | 0.014 | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 9.13714e-07 |
| gnomAD 纯合数 | 0 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q6PCB0-F1,Phobius:NON_CYTOPLASMIC_DOMAIN,PANTHER:PTHR24020,MobiDB_lite:mobidb-lite,MobiDB_lite:mobidb-lite,Low_complexity_(Seg):seg |
| 证据摘要 | consequence=missense_variant(+15); EAS_AF=0.000000e+00; frequency(+10); domain(+3); total=+28 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.3 VWA1 chr1:1442628 C>G

###### 3.2.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1442628 C>G（GRCh38） |
| 测序等位基因比例 | **39.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 20 条 / 变异序列 13 条（合计 33 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=10.05；FS（链偏倚）=5.567；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.3.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*2841C>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.994 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01254 |
| gnomAD Popmax AF | 0.04606 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.01254; frequency(-15); total=-18 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.4 VWA1 chr1:1436060 CG>C

###### 3.2.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1436060 CG>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 5 条（合计 5 条 reads） |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=32.98；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.2.3.4.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.73+242del |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.304 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01338 |
| gnomAD Popmax AF | 0.09127 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.01338; frequency(-20); total=-23 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.5 VWA1 chr1:1438298 C>T

###### 3.2.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1438298 C>T（GRCh38） |
| 测序等位基因比例 | **48.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 14 条（合计 29 条 reads） |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=13.82；FS（链偏倚）=5.649；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.5.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.632-783C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.460 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01218 |
| gnomAD Popmax AF | 0.09184 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.01218; frequency(-20); total=-23 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.6 VWA1 chr1:1442722 A>G

###### 3.2.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1442722 A>G（GRCh38） |
| 测序等位基因比例 | **21.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 18 条 / 变异序列 5 条（合计 23 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=4.64；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.6.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 14 例，ALT 等位基因计数 14 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*2935A>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.687 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0226 |
| gnomAD Popmax AF | 0.3253 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.0226; frequency(-20); total=-23 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.7 VWA1 chr1:1436079 A>G

###### 3.2.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1436079 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 6 条（合计 6 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=26.33；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.2.3.7.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 712 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.73+258A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.084 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.993 |
| gnomAD Popmax AF | 0.993 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.993; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.8 VWA1 chr1:1436388 CA>C

###### 3.2.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1436388 CA>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 10 条（合计 10 条 reads） |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 356 例，ALT 等位基因计数 647 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.74-538del |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.086 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.8741 |
| gnomAD Popmax AF | 0.8741 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.8741; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.9 VWA1 chr1:1437955 C>G

###### 3.2.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1437955 C>G（GRCh38） |
| 测序等位基因比例 | **95.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 22 条（合计 23 条 reads） |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=29.79；FS（链偏倚）=3.617；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 357 例，ALT 等位基因计数 658 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.631+471C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.164 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.908 |
| gnomAD Popmax AF | 0.908 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.908; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.10 VWA1 chr1:1437993 G>A

###### 3.2.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1437993 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 19 条（合计 19 条 reads） |
| 测序深度 | 19 |
| 碱基质量指标 | QD（质量/深度）=32.16；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 353 例，ALT 等位基因计数 625 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.631+509G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.371 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.8563 |
| gnomAD Popmax AF | 0.8563 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.8563; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.11 VWA1 chr1:1438102 G>C

###### 3.2.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1438102 G>C（GRCh38） |
| 测序等位基因比例 | **48.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 17 条 / 变异序列 16 条（合计 33 条 reads） |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=11.14；FS（链偏倚）=1.377；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.11.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 699 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.631+618G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 6.022 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9714 |
| gnomAD Popmax AF | 0.9714 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9714; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.12 VWA1 chr1:1440430 C>G

###### 3.2.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1440430 C>G（GRCh38） |
| 测序等位基因比例 | **70.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 5 条 / 变异序列 12 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=19.21；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.12.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 703 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*643C>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.218 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.13 VWA1 chr1:1440834 C>G

###### 3.2.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1440834 C>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 26 条（合计 26 条 reads） |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=33.27；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 3/3 |

###### 3.2.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 713 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*1047C>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.112 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.14 VWA1 chr1:1441187 A>G

###### 3.2.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1441187 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 17 条（合计 17 条 reads） |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=27.53；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 3/3 |

###### 3.2.3.14.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 356 例，ALT 等位基因计数 639 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*1400A>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.155 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.8692 |
| gnomAD Popmax AF | 0.8692 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.8692; frequency(-35); total=-38 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.15 VWA1 chr1:1443133 T>C

###### 3.2.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1443133 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 24 条（合计 24 条 reads） |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=30.04；FS（链偏倚）=0；MQ（比对质量）=58.54 |
| 外显子 | - |

###### 3.2.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 355 例，ALT 等位基因计数 642 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.988 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9139 |
| gnomAD Popmax AF | 0.9923 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9139; frequency(-35); total=-41 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.16 VWA1 chr1:1443457 T>C

###### 3.2.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1443457 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 16 条（合计 16 条 reads） |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=31.07；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.2.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 713 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.941 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9941 |
| gnomAD Popmax AF | 0.9941 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9941; frequency(-35); total=-41 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.17 VWA1 p.Ala326Pro

###### 3.2.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439425 G>C（GRCh38） |
| 测序等位基因比例 | **66.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 2 条（合计 3 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=15.55；FS（链偏倚）=0；MQ（比对质量）=57.01 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.17.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.976G>C |
| HGVSp | p.Ala326Pro |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.118 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | 0.012 | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0168522 |
| gnomAD Popmax AF | 0.107896 |
| gnomAD 纯合数 | 776 |
| ClinVar | Benign（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q6PCB0-F1,Phobius:NON_CYTOPLASMIC_DOMAIN,PANTHER:PTHR24020,Low_complexity_(Seg):seg |
| 证据摘要 | ClinVar=benign(base=-35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=0.95,score=-40); consequence=missense_variant(+15); EAS_AF=1.685220e-02; frequency(-35); domain(+3); total=-57 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.18 VWA1 chr1:1439827 T>C

###### 3.2.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439827 T>C（GRCh38） |
| 测序等位基因比例 | **55.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 5 条（合计 9 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=14.96；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.18.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*40T>C |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.244 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01307 |
| gnomAD Popmax AF | 0.1652 |
| gnomAD 纯合数 | - |
| ClinVar | Benign（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | ClinVar=benign(base=-35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=0.95,score=-40); consequence=3_prime_utr_variant(-3); EAS_AF=0.01307; frequency(-20); total=-63 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.19 VWA1 p.Pro335=

###### 3.2.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439454 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=33.28；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | 3/3 |

###### 3.2.3.19.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 713 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.1005A>G |
| HGVSp | p.Pro335= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.2.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.257 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9974 |
| gnomAD Popmax AF | 0.9974 |
| gnomAD 纯合数 | - |
| ClinVar | Benign（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:2.60.40.10,AFDB-ENSP_mappings:AF-Q6PCB0-F1,Phobius:NON_CYTOPLASMIC_DOMAIN,Pfam:PF00041,PROSITE_profiles:PS50853,PANTHER:PTHR24020,SMART:SM00060,Superfamily:SSF49265,CDD:cd00063,Low_complexity_(Seg):seg |
| 证据摘要 | ClinVar=benign(base=-35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=0.95,score=-40); consequence=synonymous_variant(+2); EAS_AF=0.9974; frequency(-35); domain(+3); total=-70 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |

##### 3.2.3.20 VWA1 chr1:1439805 G>C

###### 3.2.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1439805 G>C（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 4 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=10.46；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 3/3 |

###### 3.2.3.20.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 353 例，ALT 等位基因计数 619 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000476993.2 |
| RefSeq | NM_022834.5 |
| HGVSc | c.*18G>C |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.333 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.8568 |
| gnomAD Popmax AF | 0.8568 |
| gnomAD 纯合数 | - |
| ClinVar | Benign（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | ClinVar=benign(base=-35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=0.95,score=-40); consequence=3_prime_utr_variant(-3); EAS_AF=0.8568; frequency(-35); total=-78 |
| 治疗意义 | 经脚本严格筛选，当前暂无符合标准的用药候选。建议以对症/支持治疗（如听力干预、语言康复、教育支持）与遗传咨询为主；如有条件，建议纳入神经肌肉疾病专科随访。 |

###### 3.2.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41331965 | A Distinctive MRI Pattern Resembling Type VI Collagen Myopathy in Novel VWA1-Related Distal Hereditary Motor Neuronopathy With Myopathic Features in a Patient From Spain. | Costa AF; Gómez Caravaca T; Rodríguez Navas S; Rivas Infante E; 2025 | 报道一例携带 VWA1 双等位基因截断突变的 51 岁女性，表现为远端遗传性运动神经元病伴肌病特征；肌肉 MRI 呈现特征性的脂肪酸浸润模式，提示 VWA1 双等位基因突变可解释部分未确诊的神经肌病病例。 | 病例报告 |


#### 3.2.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | neuronopathy, distal hereditary motor, autosomal recessive 7; neuromuscular disease |
| 关联通路 | - |
| 临床建议 | 样本 26B01490717 来自一名自幼听力障碍、语言及理解能力发育落后、学习成绩差（韦氏评分 50）的儿童，出生体重 9 斤。VWA1 基因检出 1 个 frameshift_variant（c.961_967del，p.Pro321SerfsTer28）及多个内含子/3'UTR 变异；其中 c.961_967del 为截断变异，对蛋白功能影响较大，且已完成相位推断，可用于复合杂合/顺反式判断。多项变异存在测序深度偏低、reads 比例与 GATK AF 不一致等情况，建议 Sanger 验证并结合家系样本确认。VWA1 与远端遗传性运动神经元病 7 型（常染色体隐性遗传）明确相关，患者神经发育落后的表型与该基因的神经肌肉表型谱存在一定重叠，但需结合完整临床评估及家系分析。 |

#### 3.2.5 严格筛选用药建议

经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.3 基因卡片 3：ATAD3B


#### 3.3.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | ATAD3B |
| 染色体位置 | chr1:1482278（GRCh38） |
| 主要转录本 | NM_031921.6 |
| 基因功能 | The protein encoded by this gene is localized to the mitochondrial inner membrane, where it can bind to a highly-related protein, ATAD3A. ATAD3A appears to interact with matrix nucleoid complexes, and the encoded protein negatively regulates that interaction. This gene is expressed almost exclusively in pluripotent embryonic stem cells and some cancer cells. Two transcript variants encoding different isoforms have been found for this gene. [provided by RefSeq, Nov 2015] |
| 遗传模式 | - |
| 主要关联表型 | ovarian neoplasm; ulcerative colitis |
| 主要关联通路 | - |
| 致病性排名 | #33 |

#### 3.3.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| ATAD3B p.Arg219Gly | chr1:1482278 C>G | ENST00000673477.1 | missense_variant | 25.9 | 0.01 | 0.0000 | - | **62.5%** |
| ATAD3B chr1:1480604 G>A | chr1:1480604 G>A | ENST00000673477.1 | intron_variant | 0.167 | 0.1 | 0.0002056 | - | **100.0%** |
| ATAD3B chr1:1496597 T>G | chr1:1496597 T>G | ENST00000673477.1 | 3_prime_UTR_variant | 0.863 | 0 | 0.0000 | - | **39.1%** |
| ATAD3B chr1:1477892 C>T | chr1:1477892 C>T | ENST00000673477.1 | intron_variant | 2.331 | 0 | 0.00158 | - | **50.0%** |
| ATAD3B chr1:1502273 G>GAC | chr1:1502273 G>GAC | ENST00000673477.1 | downstream_gene_variant | - | - | 0.0000 | - | **33.3%** |
| ATAD3B chr1:1502303 C>T | chr1:1502303 C>T | ENST00000673477.1 | downstream_gene_variant | 1.843 | - | 0.0000 | - | **75.0%** |
| ATAD3B chr1:1500680 G>A | chr1:1500680 G>A | ENST00000673477.1 | downstream_gene_variant | 2.022 | - | 0.007275 | - | **42.9%** |
| ATAD3B p.Arg386Gln | chr1:1486611 G>A | ENST00000673477.1 | missense_variant | 33 | 0 | 0.59277 | - | **75.9%** |
| ATAD3B chr1:1500682 A>G | chr1:1500682 A>G | ENST00000673477.1 | downstream_gene_variant | 1.248 | - | 0.02721 | - | **42.9%** |
| ATAD3B chr1:1500691 T>C | chr1:1500691 T>C | ENST00000673477.1 | downstream_gene_variant | 1.445 | - | 0.02047 | - | **42.9%** |
| ATAD3B chr1:1486536 T>C | chr1:1486536 T>C | ENST00000673477.1 | splice_region_variant,splice_polypyrimidine_tract_variant,intron_variant | 0.965 | 0.01 | 0.08296 | - | **17.4%** |
| ATAD3B p.Thr335= | chr1:1486151 C>A | ENST00000673477.1 | synonymous_variant | 0.049 | 0.01 | 0.6316 | - | **100.0%** |
| ATAD3B p.Ala413= | chr1:1487887 A>G | ENST00000673477.1 | synonymous_variant | 0.032 | 0.01 | 0.6341 | - | **100.0%** |
| ATAD3B p.Ile467= | chr1:1490320 T>C | ENST00000673477.1 | synonymous_variant | 0.032 | 0.02 | 0.632 | - | **100.0%** |
| ATAD3B p.Arg579Cys | chr1:1495605 C>T | ENST00000673477.1 | missense_variant | 13.60 | 0 | 0.157473 | - | **53.6%** |
| ATAD3B chr1:1476266 T>C | chr1:1476266 T>C | ENST00000673477.1 | intron_variant | 0.517 | 0 | 0.582 | - | **100.0%** |
| ATAD3B chr1:1476515 AT>A | chr1:1476515 AT>A | ENST00000673477.1 | intron_variant | 0.088 | - | 0.6036 | - | **100.0%** |
| ATAD3B chr1:1477677 TTTTTA>T | chr1:1477677 TTTTTA>T | ENST00000673477.1 | intron_variant | 0.608 | - | 0.4385 | - | **100.0%** |
| ATAD3B chr1:1477850 C>G | chr1:1477850 C>G | ENST00000673477.1 | intron_variant | 0.400 | 0 | 0.4332 | - | **50.0%** |
| ATAD3B chr1:1477855 G>C | chr1:1477855 G>C | ENST00000673477.1 | intron_variant | 0.289 | 0 | 0.4314 | - | **50.0%** |
| ATAD3B chr1:1479205 A>C | chr1:1479205 A>C | ENST00000673477.1 | intron_variant | 3.692 | 0 | 0.5158 | - | **100.0%** |
| ATAD3B chr1:1479324 C>G | chr1:1479324 C>G | ENST00000673477.1 | intron_variant | 0.357 | 0 | 0.5386 | - | **100.0%** |
| ATAD3B chr1:1479334 A>G | chr1:1479334 A>G | ENST00000673477.1 | intron_variant | 0.253 | 0 | 0.5541 | - | **100.0%** |
| ATAD3B chr1:1479683 T>G | chr1:1479683 T>G | ENST00000673477.1 | intron_variant | 0.517 | 0 | 0.5629 | - | **100.0%** |
| ATAD3B chr1:1479719 T>C | chr1:1479719 T>C | ENST00000673477.1 | intron_variant | 0.710 | 0 | 0.9893 | - | **100.0%** |
| ATAD3B chr1:1480096 G>C | chr1:1480096 G>C | ENST00000673477.1 | intron_variant | 0.765 | 0 | 0.5523 | - | **100.0%** |
| ATAD3B chr1:1480990 T>C | chr1:1480990 T>C | ENST00000673477.1 | intron_variant | 3.291 | 0 | 0.5573 | - | **100.0%** |
| ATAD3B chr1:1481656 G>C | chr1:1481656 G>C | ENST00000673477.1 | intron_variant | 3.065 | 0.01 | 0.4462 | - | **41.7%** |
| ATAD3B chr1:1481959 C>T | chr1:1481959 C>T | ENST00000673477.1 | intron_variant | 0.626 | 0 | 0.6198 | - | **100.0%** |
| ATAD3B chr1:1482316 C>G | chr1:1482316 C>G | ENST00000673477.1 | intron_variant | 0.017 | 0 | 0.9995 | - | **100.0%** |
| ATAD3B chr1:1482402 A>G | chr1:1482402 A>G | ENST00000673477.1 | intron_variant | 0.030 | 0 | 0.6839 | - | **100.0%** |
| ATAD3B chr1:1482624 T>C | chr1:1482624 T>C | ENST00000673477.1 | intron_variant | 0.009 | 0.02 | 0.6313 | - | **100.0%** |
| ATAD3B chr1:1483151 G>A | chr1:1483151 G>A | ENST00000673477.1 | intron_variant | 0.611 | 0.01 | 0.988 | - | **100.0%** |
| ATAD3B chr1:1483898 G>A | chr1:1483898 G>A | ENST00000673477.1 | intron_variant | 1.173 | 0 | 1 | - | **100.0%** |
| ATAD3B chr1:1484012 C>T | chr1:1484012 C>T | ENST00000673477.1 | intron_variant | 4.586 | 0 | 0.461 | - | **50.0%** |
| ATAD3B chr1:1485282 A>G | chr1:1485282 A>G | ENST00000673477.1 | intron_variant | 0.003 | 0 | 0.4747 | - | **42.9%** |
| ATAD3B chr1:1485510 G>A | chr1:1485510 G>A | ENST00000673477.1 | intron_variant | 0.976 | 0 | 0.1438 | - | **40.9%** |
| ATAD3B chr1:1486354 G>C | chr1:1486354 G>C | ENST00000673477.1 | intron_variant | 0.136 | 0.01 | 0.4616 | - | **44.4%** |
| ATAD3B chr1:1486372 G>A | chr1:1486372 G>A | ENST00000673477.1 | intron_variant | 0.604 | 0 | 0.1601 | - | **57.7%** |
| ATAD3B chr1:1486396 C>G | chr1:1486396 C>G | ENST00000673477.1 | intron_variant | 0.842 | 0 | 0.4614 | - | **41.7%** |
| ATAD3B chr1:1488349 C>T | chr1:1488349 C>T | ENST00000673477.1 | intron_variant | 0.766 | 0 | 0.4657 | - | **60.6%** |
| ATAD3B chr1:1488652 A>G | chr1:1488652 A>G | ENST00000673477.1 | intron_variant | 1.427 | 0.02 | 0.6226 | - | **100.0%** |
| ATAD3B chr1:1489578 C>CTA | chr1:1489578 C>CTA | ENST00000673477.1 | intron_variant | 0.954 | - | 0.4647 | - | **71.4%** |
| ATAD3B chr1:1489767 T>C | chr1:1489767 T>C | ENST00000673477.1 | intron_variant | 1.674 | 0.02 | 0.485 | - | **51.9%** |
| ATAD3B chr1:1489916 C>T | chr1:1489916 C>T | ENST00000673477.1 | intron_variant | 0.337 | 0 | 0.6268 | - | **100.0%** |
| ATAD3B chr1:1490027 A>G | chr1:1490027 A>G | ENST00000673477.1 | intron_variant | 0.324 | 0 | 0.6274 | - | **100.0%** |
| ATAD3B chr1:1490032 A>G | chr1:1490032 A>G | ENST00000673477.1 | intron_variant | 0.170 | 0 | 0.6288 | - | **100.0%** |
| ATAD3B chr1:1490046 G>A | chr1:1490046 G>A | ENST00000673477.1 | intron_variant | 1.137 | 0 | 0.179 | - | **60.0%** |
| ATAD3B chr1:1490047 A>G | chr1:1490047 A>G | ENST00000673477.1 | intron_variant | 2.137 | 0 | 0.1783 | - | **60.0%** |
| ATAD3B chr1:1490122 A>G | chr1:1490122 A>G | ENST00000673477.1 | intron_variant | 1.665 | 0 | 0.4652 | - | **50.0%** |
| ATAD3B chr1:1490436 G>A | chr1:1490436 G>A | ENST00000673477.1 | intron_variant | 3.022 | 0 | 0.1597 | - | **52.4%** |
| ATAD3B chr1:1492292 C>G | chr1:1492292 C>G | ENST00000673477.1 | intron_variant | 0.987 | 0 | 0.6222 | - | **100.0%** |
| ATAD3B chr1:1492619 A>AC | chr1:1492619 A>AC | ENST00000673477.1 | intron_variant | 1.490 | - | 0.6213 | - | **100.0%** |
| ATAD3B chr1:1492850 G>A | chr1:1492850 G>A | ENST00000673477.1 | intron_variant | 0.042 | 0 | 0.622 | - | **100.0%** |
| ATAD3B chr1:1494105 G>A | chr1:1494105 G>A | ENST00000673477.1 | intron_variant | 1.479 | 0 | 0.4646 | - | **51.7%** |
| ATAD3B chr1:1494616 G>A | chr1:1494616 G>A | ENST00000673477.1 | intron_variant | 0.546 | 0.03 | 0.1417 | - | **41.7%** |
| ATAD3B chr1:1495204 T>C | chr1:1495204 T>C | ENST00000673477.1 | intron_variant | 1.140 | 0 | 0.6196 | - | **100.0%** |
| ATAD3B chr1:1495205 G>A | chr1:1495205 G>A | ENST00000673477.1 | intron_variant | 0.084 | 0.01 | 0.4626 | - | **30.0%** |
| ATAD3B chr1:1495221 G>A | chr1:1495221 G>A | ENST00000673477.1 | intron_variant | 0.538 | 0.02 | 0.4638 | - | **29.4%** |
| ATAD3B chr1:1495222 T>G | chr1:1495222 T>G | ENST00000673477.1 | intron_variant | 3.311 | 0 | 0.4644 | - | **29.4%** |
| ATAD3B chr1:1495236 T>C | chr1:1495236 T>C | ENST00000673477.1 | intron_variant | 2.611 | 0 | 0.4642 | - | **27.8%** |
| ATAD3B chr1:1495327 C>T | chr1:1495327 C>T | ENST00000673477.1 | intron_variant | 0.559 | 0 | 0.4636 | - | **54.5%** |
| ATAD3B chr1:1495357 G>A | chr1:1495357 G>A | ENST00000673477.1 | intron_variant | 1.063 | 0.01 | 0.4648 | - | **45.5%** |
| ATAD3B chr1:1496122 G>A | chr1:1496122 G>A | ENST00000673477.1 | 3_prime_UTR_variant | 1.913 | 0 | 0.1592 | - | **29.4%** |
| ATAD3B chr1:1496953 T>C | chr1:1496953 T>C | ENST00000673477.1 | 3_prime_UTR_variant | 0.427 | 0 | 0.5236 | - | **100.0%** |
| ATAD3B chr1:1496973 G>A | chr1:1496973 G>A | ENST00000673477.1 | 3_prime_UTR_variant | 0.705 | 0 | 0.4914 | - | **100.0%** |
| ATAD3B chr1:1497105 T>G | chr1:1497105 T>G | ENST00000673477.1 | 3_prime_UTR_variant | 1.016 | 0 | 0.1604 | - | **42.3%** |
| ATAD3B chr1:1497605 G>C | chr1:1497605 G>C | ENST00000673477.1 | 3_prime_UTR_variant | 0.082 | 0 | 1 | - | **100.0%** |
| ATAD3B chr1:1497606 C>G | chr1:1497606 C>G | ENST00000673477.1 | 3_prime_UTR_variant | 0.927 | 0 | 0.4624 | - | **70.8%** |
| ATAD3B chr1:1497741 CTG>C | chr1:1497741 CTG>C | ENST00000673477.1 | 3_prime_UTR_variant | 0.735 | - | 0.4412 | - | **40.0%** |
| ATAD3B chr1:1500719 C>T | chr1:1500719 C>T | ENST00000673477.1 | downstream_gene_variant | 2.331 | - | 0.3242 | - | **57.1%** |
| ATAD3B chr1:1500729 G>A | chr1:1500729 G>A | ENST00000673477.1 | downstream_gene_variant | 3.232 | - | 0.3829 | - | **66.7%** |
| ATAD3B chr1:1500745 A>C | chr1:1500745 A>C | ENST00000673477.1 | downstream_gene_variant | 0.373 | - | 0.5569 | - | **100.0%** |
| ATAD3B chr1:1501155 C>T | chr1:1501155 C>T | ENST00000673477.1 | downstream_gene_variant | 0.068 | - | 0.3225 | - | **23.1%** |
| ATAD3B chr1:1501403 T>C | chr1:1501403 T>C | ENST00000673477.1 | downstream_gene_variant | 1.491 | - | 0.4912 | - | **100.0%** |
| ATAD3B chr1:1502220 C>CT | chr1:1502220 C>CT | ENST00000673477.1 | downstream_gene_variant | 0.536 | - | 0.1403 | - | **44.4%** |
| ATAD3B chr1:1502497 C>T | chr1:1502497 C>T | ENST00000673477.1 | downstream_gene_variant | 4.773 | - | 0.1309 | - | **100.0%** |
| ATAD3B p.Pro639Ser | chr1:1495785 C>T | ENST00000673477.1 | missense_variant | 6.970 | 0 | 0.1524 | Benign | **19.2%** |

#### 3.3.3 变异详细分析

##### 3.3.3.1 ATAD3B p.Arg219Gly

###### 3.3.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1482278 C>G（GRCh38） |
| 测序等位基因比例 | **62.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 5 条（合计 8 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 9 |
| 碱基质量指标 | QD（质量/深度）=12.45；FS（链偏倚）=0；MQ（比对质量）=47.61 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 6/16 |


###### 3.3.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.655C>G |
| HGVSp | p.Arg219Gly |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.3.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 25.9 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q5T9A4-F1,Pfam:PF12037,PANTHER:PTHR23075 |
| 证据摘要 | consequence=missense_variant(+15); CADD=25.9(+9); domain(+3); total=+27 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.2 ATAD3B chr1:1480604 G>A

###### 3.3.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1480604 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 12 条（合计 12 条 reads） |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=33.42；FS（链偏倚）=0；MQ（比对质量）=59.36 |
| 外显子 | - |

###### 3.3.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.445-263G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.167 | 需结合其他证据 |
| SpliceAI DS max | 0.1 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0002056 |
| gnomAD Popmax AF | 0.0002056 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.1(+3); EAS_AF=0.0002056; frequency(+8); total=+8 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.3 ATAD3B chr1:1496597 T>G

###### 3.3.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1496597 T>G（GRCh38） |
| 测序等位基因比例 | **39.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 9 条（合计 23 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=8.55；FS（链偏倚）=1.674；MQ（比对质量）=37.74 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |


###### 3.3.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*780T>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.863 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0002078 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0; frequency(+10); total=+7 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.4 ATAD3B chr1:1477892 C>T

###### 3.3.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1477892 C>T（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 8 条（合计 16 条 reads） |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=16.79；FS（链偏倚）=0；MQ（比对质量）=58.61 |
| 外显子 | - |


###### 3.3.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.282+542C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.331 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.00158 |
| gnomAD Popmax AF | 0.00158 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.00158; frequency(+3); total=+0 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.5 ATAD3B chr1:1502273 G>GAC

###### 3.3.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1502273 G>GAC（GRCh38） |
| 测序等位基因比例 | **33.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 2 条（合计 6 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=5.6；FS（链偏倚）=0；MQ（比对质量）=57.08 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.3.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); total=-6 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.6 ATAD3B chr1:1502303 C>T

###### 3.3.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1502303 C>T（GRCh38） |
| 测序等位基因比例 | **75.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 3 条（合计 4 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=22.42；FS（链偏倚）=0；MQ（比对质量）=55.56 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.3.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.843 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); total=-6 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.7 ATAD3B chr1:1500680 G>A

###### 3.3.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500680 G>A（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 3 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=15.23；FS（链偏倚）=3.68；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.7.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 4 例，ALT 等位基因计数 4 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.022 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.007275 |
| gnomAD Popmax AF | 0.04488 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.007275; frequency(-2); total=-8 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.8 ATAD3B p.Arg386Gln

###### 3.3.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486611 G>A（GRCh38） |
| 测序等位基因比例 | **75.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 22 条（合计 29 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 29 |
| 碱基质量指标 | QD（质量/深度）=21.23；FS（链偏倚）=0；MQ（比对质量）=37.3 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 11/16 |

###### 3.3.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 309 例，ALT 等位基因计数 454 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1157G>A |
| HGVSp | p.Arg386Gln |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.3.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 33 | > 20，高度可疑有害 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.59277 |
| gnomAD Popmax AF | 0.59277 |
| gnomAD 纯合数 | 23526 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:3.40.50.300,AFDB-ENSP_mappings:AF-Q5T9A4-F1,Pfam:PF00004,PANTHER:PTHR23075,SMART:SM00382,Superfamily:SSF52540,CDD:cd19512 |
| 证据摘要 | consequence=missense_variant(+15); CADD=33(+12); EAS_AF=5.927700e-01; frequency(-50); domain(+3); total=-20 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.9 ATAD3B chr1:1500682 A>G

###### 3.3.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500682 A>G（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 3 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=15.23；FS（链偏倚）=3.68；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 9 例，ALT 等位基因计数 9 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.248 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.02721 |
| gnomAD Popmax AF | 0.05025 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.02721; frequency(-20); total=-26 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.10 ATAD3B chr1:1500691 T>C

###### 3.3.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500691 T>C（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 3 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=15.23；FS（链偏倚）=3.68；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 8 例，ALT 等位基因计数 8 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.445 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.02047 |
| gnomAD Popmax AF | 0.05473 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.02047; frequency(-20); total=-26 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.11 ATAD3B chr1:1486536 T>C

###### 3.3.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486536 T>C（GRCh38） |
| 测序等位基因比例 | **17.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 19 条 / 变异序列 4 条（合计 23 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=2.07；FS（链偏倚）=2.682；MQ（比对质量）=44.14 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.11.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 10 例，ALT 等位基因计数 10 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1090-8T>C |
| HGVSp | - |
| VEP 后果 | splice_region_variant,splice_polypyrimidine_tract_variant,intron_variant |
| VEP 影响等级 | LOW |

###### 3.3.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.965 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.08296 |
| gnomAD Popmax AF | 0.2716 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=splice_region_variant(+6); EAS_AF=0.08296; frequency(-35); total=-29 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.12 ATAD3B p.Thr335=

###### 3.3.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486151 C>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 15 条（合计 15 条 reads） |
| 测序深度 | 15 |
| 碱基质量指标 | QD（质量/深度）=34.67；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 10/16 |

###### 3.3.3.12.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 311 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 转录因子结合相关元件 (CA-TF)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1005C>A |
| HGVSp | p.Thr335= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.3.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.049 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6316 |
| gnomAD Popmax AF | 0.7669 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:3.40.50.300,AFDB-ENSP_mappings:AF-Q5T9A4-F1,PANTHER:PTHR23075,Superfamily:SSF52540,CDD:cd19512 |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0.6316; frequency(-35); domain(+3); total=-30 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.13 ATAD3B p.Ala413=

###### 3.3.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1487887 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 27 条（合计 27 条 reads） |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=30.11；FS（链偏倚）=0；MQ（比对质量）=59.27 |
| 外显子 | 12/16 |

###### 3.3.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 313 例，ALT 等位基因计数 467 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1239A>G |
| HGVSp | p.Ala413= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.3.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.032 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6341 |
| gnomAD Popmax AF | 0.7655 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:3.40.50.300,AFDB-ENSP_mappings:AF-Q5T9A4-F1,Pfam:PF00004,PANTHER:PTHR23075,SMART:SM00382,Superfamily:SSF52540,CDD:cd19512 |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0.6341; frequency(-35); domain(+3); total=-30 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.14 ATAD3B p.Ile467=

###### 3.3.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490320 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 19 条（合计 19 条 reads） |
| 测序深度 | 19 |
| 碱基质量指标 | QD（质量/深度）=26.74；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 14/16 |

###### 3.3.3.14.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1401T>C |
| HGVSp | p.Ile467= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.3.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.032 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.632 |
| gnomAD Popmax AF | 0.7686 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:3.40.50.300,AFDB-ENSP_mappings:AF-Q5T9A4-F1,Pfam:PF00004,PANTHER:PTHR23075,SMART:SM00382,Superfamily:SSF52540,CDD:cd19512 |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0.632; frequency(-35); domain(+3); total=-30 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.15 ATAD3B p.Arg579Cys

###### 3.3.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495605 C>T（GRCh38） |
| 测序等位基因比例 | **53.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 15 条（合计 28 条 reads） |
| 测序深度 | 29 |
| 碱基质量指标 | QD（质量/深度）=13.88；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 16/16 |

###### 3.3.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 76 例，ALT 等位基因计数 79 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1735C>T |
| HGVSp | p.Arg579Cys |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.3.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 13.60 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.157473 |
| gnomAD Popmax AF | 0.157473 |
| gnomAD 纯合数 | 5249 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q5T9A4-F1 |
| 证据摘要 | consequence=missense_variant(+15); CADD=13.6(+2); EAS_AF=1.574730e-01; frequency(-50); domain(+3); total=-30 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.16 ATAD3B chr1:1476266 T>C

###### 3.3.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1476266 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 8 条（合计 8 条 reads） |
| 测序深度 | 8 |
| 碱基质量指标 | QD（质量/深度）=24.75；FS（链偏倚）=0；MQ（比对质量）=38.23 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.206-1008T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.517 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.582 |
| gnomAD Popmax AF | 0.7272 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.582; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.17 ATAD3B chr1:1476515 AT>A

###### 3.3.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1476515 AT>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=22.27；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.17.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 308 例，ALT 等位基因计数 459 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.206-746del |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.088 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6036 |
| gnomAD Popmax AF | 0.6036 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6036; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.18 ATAD3B chr1:1477677 TTTTTA>T

###### 3.3.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1477677 TTTTTA>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 1 条（合计 1 条 reads） |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.18.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 270 例，ALT 等位基因计数 365 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.282+366_282+370del |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.608 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4385 |
| gnomAD Popmax AF | 0.4385 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4385; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.19 ATAD3B chr1:1477850 C>G

###### 3.3.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1477850 C>G（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 8 条（合计 16 条 reads） |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=17.98；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |


###### 3.3.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.282+500C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.400 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4332 |
| gnomAD Popmax AF | 0.4332 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4332; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.20 ATAD3B chr1:1477855 G>C

###### 3.3.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1477855 G>C（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 8 条（合计 16 条 reads） |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=17.98；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |


###### 3.3.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.282+505G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.289 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4314 |
| gnomAD Popmax AF | 0.4314 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4314; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.21 ATAD3B chr1:1479205 A>C

###### 3.3.3.21.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1479205 A>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 8 条（合计 8 条 reads） |
| 测序深度 | 8 |
| 碱基质量指标 | QD（质量/深度）=32.88；FS（链偏倚）=0；MQ（比对质量）=41.41 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |


###### 3.3.3.21.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.444+97A>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.21.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.692 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.21.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5158 |
| gnomAD Popmax AF | 0.5158 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.21.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5158; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.21.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.22 ATAD3B chr1:1479324 C>G

###### 3.3.3.22.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1479324 C>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 11 条（合计 11 条 reads） |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=58.93 |
| 外显子 | - |


###### 3.3.3.22.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.444+216C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.22.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.357 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.22.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5386 |
| gnomAD Popmax AF | 0.5386 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.22.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5386; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.22.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.23 ATAD3B chr1:1479334 A>G

###### 3.3.3.23.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1479334 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 13 条（合计 13 条 reads） |
| 测序深度 | 14 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=59.79 |
| 外显子 | - |


###### 3.3.3.23.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.444+226A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.23.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.253 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.23.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5541 |
| gnomAD Popmax AF | 0.7121 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.23.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5541; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.23.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.24 ATAD3B chr1:1479683 T>G

###### 3.3.3.24.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1479683 T>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 4 条（合计 4 条 reads） |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=23.79；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |


###### 3.3.3.24.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.444+575T>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.24.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.517 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.24.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5629 |
| gnomAD Popmax AF | 0.7117 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.24.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5629; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.24.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.25 ATAD3B chr1:1479719 T>C

###### 3.3.3.25.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1479719 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 4 条（合计 4 条 reads） |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=26.29；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |


###### 3.3.3.25.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.444+611T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.25.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.710 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.25.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9893 |
| gnomAD Popmax AF | 0.9893 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.25.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9893; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.25.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.26 ATAD3B chr1:1480096 G>C

###### 3.3.3.26.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1480096 G>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 2 条（合计 2 条 reads） |
| 测序深度 | 2 |
| 碱基质量指标 | QD（质量/深度）=18.66；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |


###### 3.3.3.26.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.445-771G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.26.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.765 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.26.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5523 |
| gnomAD Popmax AF | 0.7018 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.26.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5523; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.26.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.27 ATAD3B chr1:1480990 T>C

###### 3.3.3.27.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1480990 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 6 条（合计 6 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=22.99；FS（链偏倚）=0；MQ（比对质量）=31.49 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.27.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 转录因子结合相关元件 (CA-TF)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.27.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.514+54T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.27.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.291 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.27.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5573 |
| gnomAD Popmax AF | 0.7423 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.27.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5573; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.27.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.28 ATAD3B chr1:1481656 G>C

###### 3.3.3.28.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1481656 G>C（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 5 条（合计 12 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=10.97；FS（链偏倚）=0；MQ（比对质量）=40 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.28.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 275 例，ALT 等位基因计数 372 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.28.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.515-482G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.28.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.065 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.28.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4462 |
| gnomAD Popmax AF | 0.4462 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.28.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4462; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.28.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.29 ATAD3B chr1:1481959 C>T

###### 3.3.3.29.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1481959 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 28 条（合计 28 条 reads） |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=31.5；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.29.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 311 例，ALT 等位基因计数 463 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.29.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.515-179C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.29.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.626 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.29.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6198 |
| gnomAD Popmax AF | 0.6704 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.29.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6198; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.29.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.30 ATAD3B chr1:1482316 C>G

###### 3.3.3.30.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1482316 C>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 6 条（合计 6 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=28；FS（链偏倚）=0；MQ（比对质量）=40.72 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.30.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 718 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.30.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.680+13C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.30.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.017 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.30.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9995 |
| gnomAD Popmax AF | 0.9995 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.30.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9995; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.30.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.31 ATAD3B chr1:1482402 A>G

###### 3.3.3.31.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1482402 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 12 条（合计 12 条 reads） |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=26.17；FS（链偏倚）=0；MQ（比对质量）=40.93 |
| 外显子 | - |

###### 3.3.3.31.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 325 例，ALT 等位基因计数 496 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.31.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.680+99A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.31.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.030 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.31.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6839 |
| gnomAD Popmax AF | 0.8627 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.31.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6839; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.31.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.32 ATAD3B chr1:1482624 T>C

###### 3.3.3.32.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1482624 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 23 条（合计 23 条 reads） |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=33.52；FS（链偏倚）=0；MQ（比对质量）=49.39 |
| 外显子 | - |

###### 3.3.3.32.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 311 例，ALT 等位基因计数 463 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.32.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.750+10T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.32.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.009 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | donor_loss |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.32.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6313 |
| gnomAD Popmax AF | 0.769 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.32.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6313; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.32.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.33 ATAD3B chr1:1483151 G>A

###### 3.3.3.33.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1483151 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 5 条（合计 5 条 reads） |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=32.19；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.33.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 708 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.33.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.750+537G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.33.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.611 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.33.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.988 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.33.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.988; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.33.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.34 ATAD3B chr1:1483898 G>A

###### 3.3.3.34.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1483898 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 19 条（合计 19 条 reads） |
| 测序深度 | 19 |
| 碱基质量指标 | QD（质量/深度）=30.48；FS（链偏倚）=0；MQ（比对质量）=57.29 |
| 外显子 | - |

###### 3.3.3.34.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 311 例，ALT 等位基因计数 463 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 转录因子结合相关元件 (CA-TF)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.34.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.751-1118G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.34.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.173 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.34.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.34.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.34.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.35 ATAD3B chr1:1484012 C>T

###### 3.3.3.35.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1484012 C>T（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 8 条（合计 16 条 reads） |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=14.54；FS（链偏倚）=5.021；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.35.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 278 例，ALT 等位基因计数 382 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 转录因子结合相关元件 (CA-TF)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.35.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.751-1004C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.35.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.586 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.35.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.461 |
| gnomAD Popmax AF | 0.461 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.35.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.461; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.35.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.36 ATAD3B chr1:1485282 A>G

###### 3.3.3.36.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1485282 A>G（GRCh38） |
| 测序等位基因比例 | **42.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 6 条（合计 14 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 14 |
| 碱基质量指标 | QD（质量/深度）=7.9；FS（链偏倚）=0；MQ（比对质量）=50.63 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.36.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 385 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.36.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.906+111A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.36.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.003 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.36.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4747 |
| gnomAD Popmax AF | 0.5387 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.36.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4747; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.36.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.37 ATAD3B chr1:1485510 G>A

###### 3.3.3.37.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1485510 G>A（GRCh38） |
| 测序等位基因比例 | **40.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 9 条（合计 22 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=12.03；FS（链偏倚）=11.29；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.37.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 78 例，ALT 等位基因计数 81 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.37.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.907-272G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.37.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.976 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.37.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1438 |
| gnomAD Popmax AF | 0.1438 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.37.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1438; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.37.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.38 ATAD3B chr1:1486354 G>C

###### 3.3.3.38.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486354 G>C（GRCh38） |
| 测序等位基因比例 | **44.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 12 条（合计 27 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 27 |
| 碱基质量指标 | QD（质量/深度）=11.54；FS（链偏倚）=3.473；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.38.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 277 例，ALT 等位基因计数 381 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.38.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1089+119G>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.38.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.136 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.38.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4616 |
| gnomAD Popmax AF | 0.4616 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.38.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4616; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.38.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.39 ATAD3B chr1:1486372 G>A

###### 3.3.3.39.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486372 G>A（GRCh38） |
| 测序等位基因比例 | **57.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 11 条 / 变异序列 15 条（合计 26 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=16.14；FS（链偏倚）=3.707；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.39.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 78 例，ALT 等位基因计数 81 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.39.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1089+137G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.39.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.604 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.39.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1601 |
| gnomAD Popmax AF | 0.1601 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.39.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1601; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.39.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.40 ATAD3B chr1:1486396 C>G

###### 3.3.3.40.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1486396 C>G（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 10 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=10.86；FS（链偏倚）=4.06；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.40.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 277 例，ALT 等位基因计数 381 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.40.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1090-148C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.40.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.842 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.40.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4614 |
| gnomAD Popmax AF | 0.4614 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.40.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4614; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.40.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.41 ATAD3B chr1:1488349 C>T

###### 3.3.3.41.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1488349 C>T（GRCh38） |
| 测序等位基因比例 | **60.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 20 条（合计 33 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 35 |
| 碱基质量指标 | QD（质量/深度）=16.81；FS（链偏倚）=5.287；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.41.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 280 例，ALT 等位基因计数 386 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.41.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1266+435C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.41.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.766 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.41.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4657 |
| gnomAD Popmax AF | 0.4657 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.41.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4657; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.41.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.42 ATAD3B chr1:1488652 A>G

###### 3.3.3.42.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1488652 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 29 条（合计 29 条 reads） |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=27.76；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.42.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 467 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.42.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1267-552A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.42.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.427 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.42.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6226 |
| gnomAD Popmax AF | 0.7458 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.42.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6226; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.42.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.43 ATAD3B chr1:1489578 C>CTA

###### 3.3.3.43.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1489578 C>CTA（GRCh38） |
| 测序等位基因比例 | **71.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 4 条 / 变异序列 10 条（合计 14 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=28.61；FS（链偏倚）=2.363；MQ（比对质量）=59.13 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.43.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 280 例，ALT 等位基因计数 385 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.43.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1337+305_1337+306insAT |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.43.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.954 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.43.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4647 |
| gnomAD Popmax AF | 0.4647 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.43.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4647; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.43.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.44 ATAD3B chr1:1489767 T>C

###### 3.3.3.44.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1489767 T>C（GRCh38） |
| 测序等位基因比例 | **51.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 14 条（合计 27 条 reads） |
| 测序深度 | 27 |
| 碱基质量指标 | QD（质量/深度）=11.39；FS（链偏倚）=1.583；MQ（比对质量）=59.89 |
| 外显子 | - |

###### 3.3.3.44.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 280 例，ALT 等位基因计数 385 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.44.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-490T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.44.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.674 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.44.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.485 |
| gnomAD Popmax AF | 0.485 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.44.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.485; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.44.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.45 ATAD3B chr1:1489916 C>T

###### 3.3.3.45.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1489916 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 14 条（合计 14 条 reads） |
| 测序深度 | 15 |
| 碱基质量指标 | QD（质量/深度）=32.29；FS（链偏倚）=0；MQ（比对质量）=58.74 |
| 外显子 | - |

###### 3.3.3.45.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.45.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-341C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.45.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.337 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.45.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6268 |
| gnomAD Popmax AF | 0.6268 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.45.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6268; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.45.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.46 ATAD3B chr1:1490027 A>G

###### 3.3.3.46.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490027 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 17 条（合计 17 条 reads） |
| 测序深度 | 18 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=53.6 |
| 外显子 | - |

###### 3.3.3.46.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.46.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-230A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.46.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.324 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.46.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6274 |
| gnomAD Popmax AF | 0.7176 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.46.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6274; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.46.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.47 ATAD3B chr1:1490032 A>G

###### 3.3.3.47.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490032 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 17 条（合计 17 条 reads） |
| 测序深度 | 18 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=53.6 |
| 外显子 | - |

###### 3.3.3.47.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.47.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-225A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.47.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.170 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.47.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6288 |
| gnomAD Popmax AF | 0.7122 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.47.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6288; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.47.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.48 ATAD3B chr1:1490046 G>A

###### 3.3.3.48.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490046 G>A（GRCh38） |
| 测序等位基因比例 | **60.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 9 条（合计 15 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=22.11；FS（链偏倚）=0；MQ（比对质量）=52.89 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.48.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 85 例，ALT 等位基因计数 89 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.48.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-211G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.48.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.137 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.48.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.179 |
| gnomAD Popmax AF | 0.2488 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.48.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.179; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.48.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.49 ATAD3B chr1:1490047 A>G

###### 3.3.3.49.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490047 A>G（GRCh38） |
| 测序等位基因比例 | **60.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 9 条（合计 15 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=22.11；FS（链偏倚）=0；MQ（比对质量）=52.89 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.49.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 85 例，ALT 等位基因计数 89 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.49.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-210A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.49.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.137 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.49.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1783 |
| gnomAD Popmax AF | 0.2486 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.49.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1783; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.49.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.50 ATAD3B chr1:1490122 A>G

###### 3.3.3.50.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490122 A>G（GRCh38） |
| 测序等位基因比例 | **50.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 6 条（合计 12 条 reads） |
| 测序深度 | 14 |
| 碱基质量指标 | QD（质量/深度）=9.47；FS（链偏倚）=3.424；MQ（比对质量）=59.46 |
| 外显子 | - |

###### 3.3.3.50.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 280 例，ALT 等位基因计数 385 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.50.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1338-135A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.50.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.665 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.50.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4652 |
| gnomAD Popmax AF | 0.4652 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.50.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4652; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.50.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.51 ATAD3B chr1:1490436 G>A

###### 3.3.3.51.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1490436 G>A（GRCh38） |
| 测序等位基因比例 | **52.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 11 条（合计 21 条 reads） |
| 测序深度 | 22 |
| 碱基质量指标 | QD（质量/深度）=12.98；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.51.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 78 例，ALT 等位基因计数 81 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.51.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1505+12G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.51.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.022 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.51.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1597 |
| gnomAD Popmax AF | 0.1597 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.51.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1597; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.51.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.52 ATAD3B chr1:1492292 C>G

###### 3.3.3.52.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1492292 C>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 35 条（合计 35 条 reads） |
| 测序深度 | 36 |
| 碱基质量指标 | QD（质量/深度）=33.86；FS（链偏倚）=0；MQ（比对质量）=59.82 |
| 外显子 | - |

###### 3.3.3.52.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.52.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1614+1621C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.52.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.987 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.52.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6222 |
| gnomAD Popmax AF | 0.7456 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.52.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6222; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.52.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.53 ATAD3B chr1:1492619 A>AC

###### 3.3.3.53.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1492619 A>AC（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 8 条（合计 8 条 reads） |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=28.87；FS（链偏倚）=0；MQ（比对质量）=59.91 |
| 外显子 | - |

###### 3.3.3.53.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.53.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1614+1952dup |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.53.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.490 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.53.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6213 |
| gnomAD Popmax AF | 0.7457 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.53.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6213; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.53.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.54 ATAD3B chr1:1492850 G>A

###### 3.3.3.54.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1492850 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 17 条（合计 17 条 reads） |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=33.89；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.54.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.54.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1614+2179G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.54.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.042 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.54.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.622 |
| gnomAD Popmax AF | 0.7451 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.54.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.622; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.54.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.55 ATAD3B chr1:1494105 G>A

###### 3.3.3.55.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1494105 G>A（GRCh38） |
| 测序等位基因比例 | **51.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 15 条（合计 29 条 reads） |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=14.71；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.55.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.55.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-1380G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.55.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.479 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.55.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4646 |
| gnomAD Popmax AF | 0.4646 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.55.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4646; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.55.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.56 ATAD3B chr1:1494616 G>A

###### 3.3.3.56.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1494616 G>A（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 5 条（合计 12 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=10.55；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.56.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 76 例，ALT 等位基因计数 79 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.56.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-869G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.56.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.546 | 需结合其他证据 |
| SpliceAI DS max | 0.03 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.56.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1417 |
| gnomAD Popmax AF | 0.1417 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.56.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1417; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.56.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.57 ATAD3B chr1:1495204 T>C

###### 3.3.3.57.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495204 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 20 条（合计 20 条 reads） |
| 测序深度 | 20 |
| 碱基质量指标 | QD（质量/深度）=34.6；FS（链偏倚）=0；MQ（比对质量）=52.89 |
| 外显子 | - |

###### 3.3.3.57.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 312 例，ALT 等位基因计数 466 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.57.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-281T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.57.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.140 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.57.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.6196 |
| gnomAD Popmax AF | 0.6523 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.57.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.6196; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.57.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.58 ATAD3B chr1:1495205 G>A

###### 3.3.3.58.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495205 G>A（GRCh38） |
| 测序等位基因比例 | **30.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 6 条（合计 20 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 20 |
| 碱基质量指标 | QD（质量/深度）=9.63；FS（链偏倚）=1.922；MQ（比对质量）=52.89 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.58.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.58.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-280G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.58.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.084 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.58.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4626 |
| gnomAD Popmax AF | 0.4626 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.58.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4626; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.58.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.59 ATAD3B chr1:1495221 G>A

###### 3.3.3.59.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495221 G>A（GRCh38） |
| 测序等位基因比例 | **29.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 5 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=9.8；FS（链偏倚）=2.077；MQ（比对质量）=54.4 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.59.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.59.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-264G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.59.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.538 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.59.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4638 |
| gnomAD Popmax AF | 0.4638 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.59.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4638; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.59.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.60 ATAD3B chr1:1495222 T>G

###### 3.3.3.60.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495222 T>G（GRCh38） |
| 测序等位基因比例 | **29.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 5 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=9.8；FS（链偏倚）=2.077；MQ（比对质量）=54.4 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.60.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.60.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-263T>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.60.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.311 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.60.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4644 |
| gnomAD Popmax AF | 0.4644 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.60.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4644; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.60.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.61 ATAD3B chr1:1495236 T>C

###### 3.3.3.61.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495236 T>C（GRCh38） |
| 测序等位基因比例 | **27.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 5 条（合计 18 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 18 |
| 碱基质量指标 | QD（质量/深度）=8.42；FS（链偏倚）=2.112；MQ（比对质量）=56.72 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.61.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.61.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-249T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.61.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.611 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.61.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4642 |
| gnomAD Popmax AF | 0.4642 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.61.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4642; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.61.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.62 ATAD3B chr1:1495327 C>T

###### 3.3.3.62.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495327 C>T（GRCh38） |
| 测序等位基因比例 | **54.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 12 条（合计 22 条 reads） |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=15.07；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.62.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 279 例，ALT 等位基因计数 384 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.62.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-158C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.62.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.559 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.62.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4636 |
| gnomAD Popmax AF | 0.4636 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.62.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4636; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.62.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.63 ATAD3B chr1:1495357 G>A

###### 3.3.3.63.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495357 G>A（GRCh38） |
| 测序等位基因比例 | **45.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 10 条（合计 22 条 reads） |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=10.89；FS（链偏倚）=1.603；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.3.3.63.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 281 例，ALT 等位基因计数 387 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.63.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1615-128G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.63.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.063 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.63.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4648 |
| gnomAD Popmax AF | 0.4648 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.63.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4648; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.63.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.64 ATAD3B chr1:1496122 G>A

###### 3.3.3.64.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1496122 G>A（GRCh38） |
| 测序等位基因比例 | **29.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 5 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=5.57；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |

###### 3.3.3.64.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 76 例，ALT 等位基因计数 79 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.64.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*305G>A |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.64.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.913 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.64.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1592 |
| gnomAD Popmax AF | 0.1592 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.64.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.1592; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.64.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.65 ATAD3B chr1:1496953 T>C

###### 3.3.3.65.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1496953 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 5 条（合计 5 条 reads） |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=28.39；FS（链偏倚）=0；MQ（比对质量）=40 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | 16/16 |


###### 3.3.3.65.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1136T>C |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.65.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.427 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.65.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5236 |
| gnomAD Popmax AF | 0.6496 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.65.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.5236; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.65.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.66 ATAD3B chr1:1496973 G>A

###### 3.3.3.66.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1496973 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=30.28；FS（链偏倚）=0；MQ（比对质量）=40 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | 16/16 |


###### 3.3.3.66.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1156G>A |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.66.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.705 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.66.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4914 |
| gnomAD Popmax AF | 0.5002 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.66.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.4914; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.66.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.67 ATAD3B chr1:1497105 T>G

###### 3.3.3.67.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1497105 T>G（GRCh38） |
| 测序等位基因比例 | **42.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 11 条（合计 26 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=11.18；FS（链偏倚）=8.852；MQ（比对质量）=57.06 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |

###### 3.3.3.67.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 79 例，ALT 等位基因计数 82 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.67.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1288T>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.67.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.016 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.67.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1604 |
| gnomAD Popmax AF | 0.25 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.67.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.1604; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.67.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.68 ATAD3B chr1:1497605 G>C

###### 3.3.3.68.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1497605 G>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 24 条（合计 24 条 reads） |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=58.84 |
| 外显子 | 16/16 |

###### 3.3.3.68.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 704 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.68.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1788G>C |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.68.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.082 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.68.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.68.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.68.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.69 ATAD3B chr1:1497606 C>G

###### 3.3.3.69.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1497606 C>G（GRCh38） |
| 测序等位基因比例 | **70.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 17 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=19.19；FS（链偏倚）=0；MQ（比对质量）=58.84 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |

###### 3.3.3.69.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 233 例，ALT 等位基因计数 292 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.69.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1789C>G |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.69.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.927 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.69.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4624 |
| gnomAD Popmax AF | 0.4624 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.69.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.4624; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.69.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.70 ATAD3B chr1:1497741 CTG>C

###### 3.3.3.70.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1497741 CTG>C（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 6 条（合计 15 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=14.17；FS（链偏倚）=10.51；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |

###### 3.3.3.70.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 276 例，ALT 等位基因计数 377 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.70.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.*1926_*1927del |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.70.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.735 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.70.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4412 |
| gnomAD Popmax AF | 0.4919 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.70.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); EAS_AF=0.4412; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.70.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.71 ATAD3B chr1:1500719 C>T

###### 3.3.3.71.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500719 C>T（GRCh38） |
| 测序等位基因比例 | **57.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 4 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=21.66；FS（链偏倚）=3.68；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.71.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 213 例，ALT 等位基因计数 265 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.71.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.71.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.331 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.71.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3242 |
| gnomAD Popmax AF | 0.3242 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.71.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.3242; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.71.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.72 ATAD3B chr1:1500729 G>A

###### 3.3.3.72.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500729 G>A（GRCh38） |
| 测序等位基因比例 | **66.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 2 条 / 变异序列 4 条（合计 6 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=25.77；FS（链偏倚）=4.771；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.72.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 242 例，ALT 等位基因计数 304 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.72.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.72.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.232 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.72.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3829 |
| gnomAD Popmax AF | 0.6955 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.72.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.3829; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.72.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.73 ATAD3B chr1:1500745 A>C

###### 3.3.3.73.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1500745 A>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 5 条（合计 5 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.73.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 303 例，ALT 等位基因计数 431 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.73.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.73.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.373 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.73.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5569 |
| gnomAD Popmax AF | 0.8229 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.73.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.5569; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.73.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.74 ATAD3B chr1:1501155 C>T

###### 3.3.3.74.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1501155 C>T（GRCh38） |
| 测序等位基因比例 | **23.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 3 条（合计 13 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=4.51；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.74.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 211 例，ALT 等位基因计数 259 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.74.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.74.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.068 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.74.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3225 |
| gnomAD Popmax AF | 0.3225 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.74.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.3225; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.74.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.75 ATAD3B chr1:1501403 T>C

###### 3.3.3.75.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1501403 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 10 条（合计 10 条 reads） |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=32.91；FS（链偏倚）=0；MQ（比对质量）=55.48 |
| 外显子 | - |

###### 3.3.3.75.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 288 例，ALT 等位基因计数 380 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.75.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.75.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.491 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.75.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4912 |
| gnomAD Popmax AF | 0.7325 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.75.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.4912; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.75.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.76 ATAD3B chr1:1502220 C>CT

###### 3.3.3.76.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1502220 C>CT（GRCh38） |
| 测序等位基因比例 | **44.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 5 条 / 变异序列 4 条（合计 9 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=8.07；FS（链偏倚）=2.808；MQ（比对质量）=59.43 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.3.3.76.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 91 例，ALT 等位基因计数 99 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.76.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.76.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.536 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.76.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1403 |
| gnomAD Popmax AF | 0.1403 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.76.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.1403; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.76.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.77 ATAD3B chr1:1502497 C>T

###### 3.3.3.77.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1502497 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=26.61；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.3.3.77.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 90 例，ALT 等位基因计数 98 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.3.3.77.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.77.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.773 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.77.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1309 |
| gnomAD Popmax AF | 0.1309 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.77.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.1309; frequency(-35); total=-41 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.77.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |

##### 3.3.3.78 ATAD3B p.Pro639Ser

###### 3.3.3.78.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1495785 C>T（GRCh38） |
| 测序等位基因比例 | **19.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 21 条 / 变异序列 5 条（合计 26 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=2.29；FS（链偏倚）=0；MQ（比对质量）=54.7 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 16/16 |

###### 3.3.3.78.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.78.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000673477.1 |
| RefSeq | NM_031921.6,NM_001317238.2 |
| HGVSc | c.1915C>T |
| HGVSp | p.Pro639Ser |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.3.3.78.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 6.970 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.78.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1524 |
| gnomAD Popmax AF | 0.2107 |
| gnomAD 纯合数 | - |
| ClinVar | Benign（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.78.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-Q5T9A4-F1 |
| 证据摘要 | ClinVar=benign(base=-35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=0.95,score=-40); consequence=missense_variant(+15); EAS_AF=0.1524; frequency(-35); domain(+3); total=-57 |
| 治疗意义 | 暂无严格匹配用药。当前变异未达到致病性或高影响功能缺失标准，亦无匹配的靶向治疗或药物干预建议。 |

###### 3.3.3.78.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42001994 | SEC62 at mitochondria-associated membranes drives MASH progression by suppressing ATAD3B-mediated mitochondrial quality control | Lin J, Wu T, Wang C, Zhou W, Liu Y, Yang G, Zhou H, Luo J, Fan Z, Da Y, He J, Xu B, Jiang M, Fan D, Wu K, Liang J; Metabolism, 2026 | 该研究揭示 ATAD3B 在线粒体质量控制中的作用，SEC62 通过抑制 ATAD3B 介导的线粒体质量控制促进代谢功能障碍相关脂肪性肝炎（MASH）进展。提示 ATAD3B 在线粒体-内质网互作及代谢性疾病中的潜在功能意义。 | PubMed 文献支持 |
| 41280066 | Allele-specific correction of ATAD3A pathogenic variants via template-free CRISPR-Cas9 editing and gene conversion | Bae T, Park Y, LaGrone A, Suvakov M, Zhang P, Park H, Remmen HV, Lupski JR, Harel T, Kim JJ, Abyzov A, Yoon WH; bioRxiv, 2025 | 研究利用无模板 CRISPR-Cas9 介导的基因转换纠正 ATAD3A 致病变异，并在纠正过程中发现一个克隆携带 ATAD3B 位点杂合缺失，提示 ATAD3A/ATAD3B 基因座在基因组编辑中的相互影响及同源重组修复机制。 | PubMed 文献支持 |
| 40688112 | Exploring potential therapeutic targets for colorectal tumors based on whole genome sequencing of colorectal tumors and paracancerous tissues | Sheng Y, Niu S, Li D, Meng C, Wang T; Front Mol Biosci, 2025 | 基于全基因组测序探索结直肠肿瘤治疗靶点的研究，将 ATAD3B 列为潜在候选基因之一，提示其在肿瘤基因组中的 altered 表达或拷贝数变异可能与结直肠癌发生相关。 | PubMed 文献支持 |


#### 3.3.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | ovarian neoplasm; ulcerative colitis; inflammatory bowel disease; hypertriglyceridemia 2; familial hypercholesterolemia |
| 关联通路 | - |
| 临床建议 | 患者表现为先天性听力障碍（佩戴助听器）、语言发育迟缓、理解能力差、认知功能受损（韦氏评分50分）及出生体重偏大（9斤）。ATAD3B 编码定位于线粒体内膜的蛋白，可与 ATAD3A 结合并负向调控其与基质核型复合体的相互作用。本样本检出 3 个错义变异（p.Arg219Gly、p.Arg386Gln、p.Arg579Cys）及大量内含子/UTR/下游变异；其中 p.Arg219Gly 的 CADD=25.9，p.Arg386Gln 的 CADD=33，但 p.Arg386Gln 在东亚人群参考频率高达 59.3%（EAS_AF=5.93e-01），p.Arg579Cys 的 EAS_AF=15.7%，提示该变异在人群中较为常见。所有变异 ClinVar 标注均为空或 Benign（p.Pro639Ser），证据评分提示为良性或低影响。综上，目前缺乏功能验证明确的致病变异，ATAD3B 与患者听力-语言-认知发育迟缓的临床表型之间尚未建立明确的分子关联。 |

#### 3.3.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.4 基因卡片 4：CCNL2


#### 3.4.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | CCNL2 |
| 染色体位置 | chr1:1398672（GRCh38） |
| 主要转录本 | NM_030937.6 |
| 基因功能 | The protein encoded by this gene belongs to the cyclin family. Through its interaction with several proteins, such as RNA polymerase II, splicing factors, and cyclin-dependent kinases, this protein functions as a regulator of the pre-mRNA splicing process, as well as in inducing apoptosis by modulating the expression of apoptotic and antiapoptotic proteins. Alternatively spliced transcript variants encoding different isoforms have been described for this gene. [provided by RefSeq, Aug 2011] |
| 遗传模式 | - |
| 主要关联表型 | infection; breast cancer |
| 主要关联通路 | - |
| 致病性排名 | #44 |

#### 3.4.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| CCNL2 chr1:1398672 CTAGAG>C | chr1:1398672 CTAGAG>C | ENST00000400809.8 | splice_acceptor_variant,splice_polypyrimidine_tract_variant,intron_variant | 24.8 | - | 0.1015 | - | **60.0%** |
| CCNL2 chr1:1396191 GAA>G/GA | chr1:1396191 GAA>G/GA | ENST00000400809.8 | intron_variant | 0.559 | - | 0.001663 | - | **0.3,0.6** |
| CCNL2 chr1:1393592 G>A | chr1:1393592 G>A | ENST00000400809.8 | intron_variant | 1.714 | 0 | 0.01543 | - | **55.9%** |
| CCNL2 chr1:1393591 C>T | chr1:1393591 C>T | ENST00000400809.8 | intron_variant | 0.192 | 0 | 0.02109 | - | **44.1%** |
| CCNL2 chr1:1381507 G>A | chr1:1381507 G>A | ENST00000400809.8 | downstream_gene_variant | 7.307 | - | 0.01814 | - | **46.2%** |
| CCNL2 chr1:1382885 A>G | chr1:1382885 A>G | ENST00000400809.8 | downstream_gene_variant | 4.651 | - | 0.0183 | - | **54.5%** |
| CCNL2 chr1:1401102 T>C | chr1:1401102 T>C | ENST00000400809.8 | upstream_gene_variant | 0.779 | - | 0.0183 | - | **45.5%** |
| CCNL2 chr1:1401840 G>A | chr1:1401840 G>A | ENST00000400809.8 | upstream_gene_variant | 5.259 | - | 0.02146 | - | **53.3%** |
| CCNL2 chr1:1402944 C>T | chr1:1402944 C>T | ENST00000400809.8 | upstream_gene_variant | 0.671 | - | 0.01787 | - | **45.0%** |
| CCNL2 chr1:1386861 TTGAG>T | chr1:1386861 TTGAG>T | ENST00000400809.8 | 3_prime_UTR_variant | 11.30 | - | 0.1129 | - | **61.1%** |
| CCNL2 chr1:1387650 G>A | chr1:1387650 G>A | ENST00000400809.8 | intron_variant | 2.692 | 0.01 | 0.1026 | - | **58.3%** |
| CCNL2 chr1:1388266 T>C | chr1:1388266 T>C | ENST00000400809.8 | intron_variant | 3.249 | 0.02 | 0.1047 | - | **51.7%** |
| CCNL2 chr1:1394423 A>G | chr1:1394423 A>G | ENST00000400809.8 | intron_variant | 0.139 | 0 | 0.9832 | - | **100.0%** |
| CCNL2 chr1:1395050 G>A | chr1:1395050 G>A | ENST00000400809.8 | intron_variant | 0.469 | 0 | 0.1278 | - | **100.0%** |
| CCNL2 chr1:1395346 A>G | chr1:1395346 A>G | ENST00000400809.8 | intron_variant | 1.935 | 0 | 0.9885 | - | **100.0%** |
| CCNL2 chr1:1398056 C>A | chr1:1398056 C>A | ENST00000400809.8 | intron_variant | 2.851 | 0 | 0.9981 | - | **100.0%** |
| CCNL2 chr1:1381088 A>G | chr1:1381088 A>G | ENST00000400809.8 | downstream_gene_variant | 3.239 | - | 0.9079 | - | **46.4%** |
| CCNL2 chr1:1382614 C>T | chr1:1382614 C>T | ENST00000400809.8 | downstream_gene_variant | 4.521 | - | 0.3313 | - | **57.1%** |
| CCNL2 chr1:1382631 T>C | chr1:1382631 T>C | ENST00000400809.8 | downstream_gene_variant | 2.051 | - | 0.4268 | - | **80.0%** |
| CCNL2 chr1:1382658 T>C | chr1:1382658 T>C | ENST00000400809.8 | downstream_gene_variant | 5.539 | - | 0.4437 | - | **40.0%** |
| CCNL2 chr1:1382971 T>C | chr1:1382971 T>C | ENST00000400809.8 | downstream_gene_variant | 1.000 | - | 0.9071 | - | **51.6%** |
| CCNL2 chr1:1385710 C>T | chr1:1385710 C>T | ENST00000400809.8 | downstream_gene_variant | 4.366 | - | 0.09082 | - | **59.1%** |
| CCNL2 chr1:1399838 G>A | chr1:1399838 G>A | ENST00000400809.8 | upstream_gene_variant | 2.655 | - | 0.09007 | - | **40.0%** |
| CCNL2 chr1:1399922 C>T | chr1:1399922 C>T | ENST00000400809.8 | upstream_gene_variant | 2.390 | - | 0.1164 | - | **100.0%** |
| CCNL2 chr1:1400410 A>G | chr1:1400410 A>G | ENST00000400809.8 | upstream_gene_variant | 5.006 | - | 0.9837 | - | **100.0%** |
| CCNL2 chr1:1401098 G>A | chr1:1401098 G>A | ENST00000400809.8 | upstream_gene_variant | 0.218 | - | 0.09655 | - | **52.9%** |
| CCNL2 chr1:1401246 G>A | chr1:1401246 G>A | ENST00000400809.8 | upstream_gene_variant | 3.896 | - | 0.091 | - | **37.0%** |
| CCNL2 chr1:1401298 G>A | chr1:1401298 G>A | ENST00000400809.8 | upstream_gene_variant | 5.719 | - | 0.06638 | - | **56.7%** |
| CCNL2 chr1:1402457 A>G | chr1:1402457 A>G | ENST00000400809.8 | upstream_gene_variant | 3.607 | - | 0.989 | - | **100.0%** |
| CCNL2 chr1:1402900 A>G | chr1:1402900 A>G | ENST00000400809.8 | upstream_gene_variant | 0.286 | - | 0.1164 | - | **100.0%** |
| CCNL2 chr1:1403127 C>CAAAAAAAA | chr1:1403127 C>CAAAAAAAA | ENST00000400809.8 | upstream_gene_variant | 0.795 | - | 0.07394 | - | **100.0%** |
| CCNL2 chr1:1403240 CCTTT>C | chr1:1403240 CCTTT>C | ENST00000400809.8 | upstream_gene_variant | 0.727 | - | 0.1144 | - | **100.0%** |
| CCNL2 chr1:1403908 C>G | chr1:1403908 C>G | ENST00000400809.8 | upstream_gene_variant | 1.278 | - | 0.09193 | - | **61.9%** |

#### 3.4.3 变异详细分析

##### 3.4.3.1 CCNL2 chr1:1398672 CTAGAG>C

###### 3.4.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1398672 CTAGAG>C（GRCh38） |
| 测序等位基因比例 | **60.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 9 条（合计 15 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 15 |
| 碱基质量指标 | QD（质量/深度）=23.51；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.289-6_289-2del |
| HGVSp | - |
| VEP 后果 | splice_acceptor_variant,splice_polypyrimidine_tract_variant,intron_variant |
| VEP 影响等级 | HIGH |

###### 3.4.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 24.8 | > 20，高度可疑有害 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | HC | LoF 预测标记 |

###### 3.4.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1015 |
| gnomAD Popmax AF | 0.1021 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=splice_acceptor_variant(+33); splice_lof=SpliceAI:unknown(+15); CADD=24.8(+6); EAS_AF=0.1015; frequency(-35); total=+19 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.2 CCNL2 chr1:1396191 GAA>G/GA

###### 3.4.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1396191 GAA>G/GA（GRCh38） |
| 测序等位基因比例 | **0.3,0.6**（基于测序 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=14.8；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.4.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.474-678_474-677del |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.559 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.001663 |
| gnomAD Popmax AF | 0.01342 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.001663; frequency(-2); total=-5 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.3 CCNL2 chr1:1393592 G>A

###### 3.4.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1393592 G>A（GRCh38） |
| 测序等位基因比例 | **55.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 19 条（合计 34 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=16.34；FS（链偏倚）=23.102；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.3.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 7 例，ALT 等位基因计数 7 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.595-132C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.714 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01543 |
| gnomAD Popmax AF | 0.01543 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.01543; frequency(-15); total=-18 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.4 CCNL2 chr1:1393591 C>T

###### 3.4.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1393591 C>T（GRCh38） |
| 测序等位基因比例 | **44.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 19 条 / 变异序列 15 条（合计 34 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=12.46；FS（链偏倚）=23.102；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.4.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.595-131G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.192 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.02109 |
| gnomAD Popmax AF | 0.1618 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.02109; frequency(-20); total=-23 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.5 CCNL2 chr1:1381507 G>A

###### 3.4.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1381507 G>A（GRCh38） |
| 测序等位基因比例 | **46.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 12 条（合计 26 条 reads） |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=11.91；FS（链偏倚）=1.471；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.5.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.307 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01814 |
| gnomAD Popmax AF | 0.1292 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.01814; frequency(-20); total=-26 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.6 CCNL2 chr1:1382885 A>G

###### 3.4.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1382885 A>G（GRCh38） |
| 测序等位基因比例 | **54.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 18 条（合计 33 条 reads） |
| 测序深度 | 33 |
| 碱基质量指标 | QD（质量/深度）=10.9；FS（链偏倚）=1.414；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.6.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.651 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0183 |
| gnomAD Popmax AF | 0.1286 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.0183; frequency(-20); total=-26 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.7 CCNL2 chr1:1401102 T>C

###### 3.4.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1401102 T>C（GRCh38） |
| 测序等位基因比例 | **45.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 18 条 / 变异序列 15 条（合计 33 条 reads） |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=11.08；FS（链偏倚）=1.356；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.7.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.779 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0183 |
| gnomAD Popmax AF | 0.1631 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.0183; frequency(-20); total=-26 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.8 CCNL2 chr1:1401840 G>A

###### 3.4.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1401840 G>A（GRCh38） |
| 测序等位基因比例 | **53.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 16 条（合计 30 条 reads） |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=12.45；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.259 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.02146 |
| gnomAD Popmax AF | 0.163 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.02146; frequency(-20); total=-26 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.9 CCNL2 chr1:1402944 C>T

###### 3.4.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1402944 C>T（GRCh38） |
| 测序等位基因比例 | **45.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 11 条 / 变异序列 9 条（合计 20 条 reads） |
| 测序深度 | 21 |
| 碱基质量指标 | QD（质量/深度）=12.68；FS（链偏倚）=2.098；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.671 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01787 |
| gnomAD Popmax AF | 0.2001 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.01787; frequency(-20); total=-26 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.10 CCNL2 chr1:1386861 TTGAG>T

###### 3.4.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1386861 TTGAG>T（GRCh38） |
| 测序等位基因比例 | **61.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 11 条（合计 18 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 20 |
| 碱基质量指标 | QD（质量/深度）=24.09；FS（链偏倚）=4.786；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 11/11 |

###### 3.4.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 51 例，ALT 等位基因计数 51 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.*366_*369del |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 11.30 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1129 |
| gnomAD Popmax AF | 0.1129 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=3_prime_utr_variant(-3); CADD=11.3(+2); EAS_AF=0.1129; frequency(-35); total=-36 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.11 CCNL2 chr1:1387650 G>A

###### 3.4.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1387650 G>A（GRCh38） |
| 测序等位基因比例 | **58.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 21 条（合计 36 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 36 |
| 碱基质量指标 | QD（质量/深度）=14.68；FS（链偏倚）=1.301；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.11.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 55 例，ALT 等位基因计数 55 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.1212-68C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.692 | 需结合其他证据 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1026 |
| gnomAD Popmax AF | 0.1026 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1026; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.12 CCNL2 chr1:1388266 T>C

###### 3.4.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1388266 T>C（GRCh38） |
| 测序等位基因比例 | **51.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 15 条（合计 29 条 reads） |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=9.33；FS（链偏倚）=0；MQ（比对质量）=59.25 |
| 外显子 | - |

###### 3.4.3.12.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 55 例，ALT 等位基因计数 55 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 转录因子相关元件 (TF)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.1007-201A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.249 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1047 |
| gnomAD Popmax AF | 0.1047 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1047; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.13 CCNL2 chr1:1394423 A>G

###### 3.4.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1394423 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 31 条（合计 31 条 reads） |
| 测序深度 | 33 |
| 碱基质量指标 | QD（质量/深度）=34.36；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 704 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.595-963T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.139 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9832 |
| gnomAD Popmax AF | 0.9832 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9832; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.14 CCNL2 chr1:1395050 G>A

###### 3.4.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1395050 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 7 条（合计 7 条 reads） |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=31.43；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.4.3.14.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 67 例，ALT 等位基因计数 69 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.594+344C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.469 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1278 |
| gnomAD Popmax AF | 0.3533 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1278; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.15 CCNL2 chr1:1395346 A>G

###### 3.4.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1395346 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 29 条（合计 29 条 reads） |
| 测序深度 | 33 |
| 碱基质量指标 | QD（质量/深度）=30.73；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 704 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.594+48T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.935 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9885 |
| gnomAD Popmax AF | 0.9885 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9885; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.16 CCNL2 chr1:1398056 C>A

###### 3.4.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1398056 C>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 31 条（合计 31 条 reads） |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=33.13；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 717 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | c.473+177G>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.851 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9981 |
| gnomAD Popmax AF | 0.9981 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9981; frequency(-35); total=-38 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.17 CCNL2 chr1:1381088 A>G

###### 3.4.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1381088 A>G（GRCh38） |
| 测序等位基因比例 | **46.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 13 条（合计 28 条 reads） |
| 测序深度 | 28 |
| 碱基质量指标 | QD（质量/深度）=13.59；FS（链偏倚）=5.943；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.17.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | CA-H3K4me3（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.239 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9079 |
| gnomAD Popmax AF | 0.9883 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9079; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.18 CCNL2 chr1:1382614 C>T

###### 3.4.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1382614 C>T（GRCh38） |
| 测序等位基因比例 | **57.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 4 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 7 |
| 碱基质量指标 | QD（质量/深度）=18.38；FS（链偏倚）=8.451；MQ（比对质量）=34.29 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.4.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.521 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3313 |
| gnomAD Popmax AF | 0.379 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.3313; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.19 CCNL2 chr1:1382631 T>C

###### 3.4.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1382631 T>C（GRCh38） |
| 测序等位基因比例 | **80.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 4 条（合计 5 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=29.33；FS（链偏倚）=3.979；MQ（比对质量）=32.47 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.4.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.051 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4268 |
| gnomAD Popmax AF | 0.4703 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.4268; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.20 CCNL2 chr1:1382658 T>C

###### 3.4.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1382658 T>C（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 2 条（合计 5 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 5 |
| 碱基质量指标 | QD（质量/深度）=6.53；FS（链偏倚）=0；MQ（比对质量）=46.32 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.4.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.539 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4437 |
| gnomAD Popmax AF | 0.4857 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.4437; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.21 CCNL2 chr1:1382971 T>C

###### 3.4.3.21.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1382971 T>C（GRCh38） |
| 测序等位基因比例 | **51.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 16 条（合计 31 条 reads） |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=11.41；FS（链偏倚）=3.393；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.21.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 665 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.21.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.21.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.000 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.21.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9071 |
| gnomAD Popmax AF | 0.9883 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.21.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.9071; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.21.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.22 CCNL2 chr1:1385710 C>T

###### 3.4.3.22.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1385710 C>T（GRCh38） |
| 测序等位基因比例 | **59.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 13 条（合计 22 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=17.62；FS（链偏倚）=1.837；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.22.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.22.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | downstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.22.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.366 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.22.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.09082 |
| gnomAD Popmax AF | 0.09082 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.22.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=downstream_gene_variant(-6); EAS_AF=0.09082; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.22.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.23 CCNL2 chr1:1399838 G>A

###### 3.4.3.23.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1399838 G>A（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 4 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=11.16；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.23.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.23.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.23.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.655 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.23.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.09007 |
| gnomAD Popmax AF | 0.09007 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.23.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.09007; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.23.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.24 CCNL2 chr1:1399922 C>T

###### 3.4.3.24.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1399922 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 10 条（合计 10 条 reads） |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=33.31；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.24.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 67 例，ALT 等位基因计数 69 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.24.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.24.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.390 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.24.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1164 |
| gnomAD Popmax AF | 0.3492 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.24.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.1164; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.24.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.25 CCNL2 chr1:1400410 A>G

###### 3.4.3.25.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1400410 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 31 条（合计 31 条 reads） |
| 测序深度 | 31 |
| 碱基质量指标 | QD（质量/深度）=31.13；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.25.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 704 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 启动子样元件 (PLS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.25.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.25.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.006 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.25.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9837 |
| gnomAD Popmax AF | 0.9837 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.25.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.9837; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.25.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.26 CCNL2 chr1:1401098 G>A

###### 3.4.3.26.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1401098 G>A（GRCh38） |
| 测序等位基因比例 | **52.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 16 条 / 变异序列 18 条（合计 34 条 reads） |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=12.99；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.26.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.26.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.26.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.218 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.26.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.09655 |
| gnomAD Popmax AF | 0.1117 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.26.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.09655; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.26.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.27 CCNL2 chr1:1401246 G>A

###### 3.4.3.27.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1401246 G>A（GRCh38） |
| 测序等位基因比例 | **37.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 17 条 / 变异序列 10 条（合计 27 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 31 |
| 碱基质量指标 | QD（质量/深度）=8.69；FS（链偏倚）=1.632；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.27.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.27.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.27.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.896 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.27.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.091 |
| gnomAD Popmax AF | 0.1029 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.27.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.091; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.27.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.28 CCNL2 chr1:1401298 G>A

###### 3.4.3.28.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1401298 G>A（GRCh38） |
| 测序等位基因比例 | **56.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 17 条（合计 30 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 34 |
| 碱基质量指标 | QD（质量/深度）=16.05；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.28.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 49 例，ALT 等位基因计数 51 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |
| 非编码 RNA | MRPL20-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.4.3.28.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.28.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.719 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.28.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.06638 |
| gnomAD Popmax AF | 0.1629 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.28.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.06638; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.28.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.29 CCNL2 chr1:1402457 A>G

###### 3.4.3.29.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1402457 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 24 条（合计 24 条 reads） |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=34.5；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.29.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 704 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.29.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.29.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.607 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.29.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.989 |
| gnomAD Popmax AF | 0.989 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.29.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.989; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.29.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.30 CCNL2 chr1:1402900 A>G

###### 3.4.3.30.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1402900 A>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 20 条（合计 20 条 reads） |
| 测序深度 | 21 |
| 碱基质量指标 | QD（质量/深度）=31.45；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.30.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 67 例，ALT 等位基因计数 69 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.30.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.30.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.286 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.30.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1164 |
| gnomAD Popmax AF | 0.3417 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.30.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.1164; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.30.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.31 CCNL2 chr1:1403127 C>CAAAAAAAA

###### 3.4.3.31.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1403127 C>CAAAAAAAA（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.31.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 46 例，ALT 等位基因计数 46 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.31.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.31.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.795 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.31.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.07394 |
| gnomAD Popmax AF | 0.08011 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.31.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.07394; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.31.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.32 CCNL2 chr1:1403240 CCTTT>C

###### 3.4.3.32.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1403240 CCTTT>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 14 条（合计 14 条 reads） |
| 测序深度 | 18 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | - |

###### 3.4.3.32.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 69 例，ALT 等位基因计数 71 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.32.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.32.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.727 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.32.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1144 |
| gnomAD Popmax AF | 0.3396 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.32.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.1144; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.32.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |

##### 3.4.3.33 CCNL2 chr1:1403908 C>G

###### 3.4.3.33.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:1403908 C>G（GRCh38） |
| 测序等位基因比例 | **61.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 13 条（合计 21 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=18.22；FS（链偏倚）=4.123；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.33.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 53 例，ALT 等位基因计数 53 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.33.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000400809.8 |
| RefSeq | NM_030937.6 |
| HGVSc | - |
| HGVSp | - |
| VEP 后果 | upstream_gene_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.33.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.278 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.33.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.09193 |
| gnomAD Popmax AF | 0.1026 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.33.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=upstream_gene_variant(-6); EAS_AF=0.09193; frequency(-35); total=-41 |
| 治疗意义 | 当前报告未检出 ClinVar 致病性注释变异或明确的高影响 LoF 变异，严格用药候选为空，暂无针对 CCNL2 相关神经发育表型的匹配用药建议。文献提示 CCNL2 作为 CDK11 的激活 cyclin，其复合物参与 Hippo 通路调控及肿瘤（如宫颈癌、乳腺癌）化疗耐药，但该分子机制与神经发育疾病无直接治疗关联。 |

###### 3.4.3.33.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41074747 | CDK11 Promotes Paclitaxel Resistance in Cervical Cancer by Regulating LATS1-Mediated Hippo Signaling Pathway Through Phosphorylation of NF2 | Zhang Y, Lu J, Qi M, Zhang X, Ou D; 2025 | 通过 co-IP 和异种移植模型证实，CDK11 与 CCNL2 形成复合物，通过磷酸化 NF2 抑制 Hippo 信号通路，促进宫颈癌细胞紫杉醇耐药，明确了 CCNL2 在肿瘤化疗耐药中的功能角色。 | In vitro/in vivo mechanistic study |
| 40766692 | On-target toxicity limits the efficacy of CDK11 inhibition against cancers with 1p36 deletions | Julian L, Crozier L, Lukow D, Mishra S, Sausville EL, Mendelson B, et al.; 2025 | 功能基因组学分析发现 1p36 缺失（包含 CDK11 及其激活 cyclin CCNL2）是 CDK11 抑制剂敏感性的预测性生物标志物，强调 CCNL2 对维持 CDK11 激酶活性的必要性。 | Functional genomics and drug discovery study |
| 41200172 | Differential gene expression profiling and machine learning-based discovery of key genetic markers in VTE and CKD | Li H, Lin C, Kuang J; 2025 | 通过转录组学与机器学习分析，在静脉血栓栓塞 (VTE) 和慢性肾脏病 (CKD) 的差异表达基因筛选中识别到 CCNL2，但该研究属于多因素疾病生物信息学关联，与神经发育表型无直接关联。 | Bioinformatic association study |


#### 3.4.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | CCNL2 与感染 (infection) 和乳腺癌 (breast cancer) 具有最强的基因-疾病关联证据（Open Targets score ≈ 0.078–0.079），此外还与胃癌、卵巢癌及腹股沟疝存在中度关联（score: 0.058–0.068）。目前未检索到 CCNL2 单基因变异导致神经发育障碍、听力损失或智力障碍的明确孟德尔遗传病记录。 |
| 关联通路 | CCNL2 编码 cyclin 家族蛋白，通过与 CDK11 形成复合物参与 RNA 聚合酶 II 介导的转录调控及 pre-mRNA 剪接。研究提示 CCNL2/CDK11 复合物可磷酸化 Hippo 通路蛋白 NF2，在肿瘤细胞增殖与化疗耐药中发挥作用。 |
| 临床建议 | 受试者 26B01490717 的临床表现为自幼听力障碍、语言发育迟缓、认知理解能力差、学习困难，韦氏评分 50 分（提示轻度至中度智力障碍），出生体重 9 斤（巨大儿）。在 CCNL2 基因区域内检出 1 个剪接位点附近变异（chr1:1398672, c.289-6_289-2del，位于 polypyrimidine tract 区，CADD=24.8）及 29 个非编码/上下游变异。该首要变异在东亚人群 (EAS) 中携带频率较高（EAS_AF≈0.1015），且多个变异位点的 reads 比例与 GATK 基因型 AF 不一致，提示可能存在克隆异质性或嵌合现象。综合现有证据，CCNL2 基因区域内未见明确致病变异，与受试者神经发育表型的因果关联尚未确立，建议结合家系 Sanger 验证、RNA 剪接功能实验及全外显子/转录组数据进一步评估。 |

#### 3.4.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.5 基因卡片 5：ENSG00000241860


#### 3.5.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | ENSG00000241860 |
| 染色体位置 | chr1:168098（GRCh38） |
| 主要转录本 | ENST00000831102.1 |
| 基因功能 | - |
| 遗传模式 | - |
| 主要关联表型 | myelodysplastic syndrome |
| 主要关联通路 | - |
| 致病性排名 | #53 |

#### 3.5.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| ENSG00000241860 chr1:168098 A>G | chr1:168098 A>G | ENST00000831102.1 | splice_donor_variant,non_coding_transcript_variant | 18.47 | - | 0.04896 | - | **83.3%** |
| ENSG00000241860 chr1:120277 C>T | chr1:120277 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.705 | - | 0.0000 | - | **37.0%** |
| ENSG00000241860 chr1:111059 T>C | chr1:111059 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.469 | - | 0.00021 | - | **16.7%** |
| ENSG00000241860 chr1:119723 G>A | chr1:119723 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.381 | - | 0.001511 | - | **44.4%** |
| ENSG00000241860 chr1:111057 C>CA | chr1:111057 C>CA | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | - | - | 0.0000 | - | **16.7%** |
| ENSG00000241860 chr1:128342 G>A | chr1:128342 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.097 | - | 0.0000 | - | **66.7%** |
| ENSG00000241860 chr1:128343 CCTA>C | chr1:128343 CCTA>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | - | - | 0.0000 | - | **66.7%** |
| ENSG00000241860 chr1:129444 AGTGC>A | chr1:129444 AGTGC>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | - | - | 0.0000 | - | **15.4%** |
| ENSG00000241860 chr1:129452 G>A | chr1:129452 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.504 | - | 0.0000 | - | **14.3%** |
| ENSG00000241860 chr1:129453 G>T | chr1:129453 G>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.236 | - | 0.0000 | - | **14.3%** |
| ENSG00000241860 chr1:103210 G>T | chr1:103210 G>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.393 | - | 0.007514 | - | **16.7%** |
| ENSG00000241860 chr1:103983 C>T | chr1:103983 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.432 | - | 0.008505 | - | **15.2%** |
| ENSG00000241860 chr1:109107 G>GT | chr1:109107 G>GT | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.626 | - | 0.006588 | - | **15.4%** |
| ENSG00000241860 chr1:102951 C>T | chr1:102951 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 5.761 | - | 0.04526 | - | **13.8%** |
| ENSG00000241860 chr1:103233 C>T | chr1:103233 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.069 | - | 0.01735 | - | **25.6%** |
| ENSG00000241860 chr1:104018 C>T | chr1:104018 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 7.790 | - | 0.02783 | - | **20.8%** |
| ENSG00000241860 chr1:105774 GT>G | chr1:105774 GT>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 5.210 | - | 0.03982 | - | **52.9%** |
| ENSG00000241860 chr1:105867 C>T | chr1:105867 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.392 | - | 0.03397 | - | **29.8%** |
| ENSG00000241860 chr1:109309 G>A | chr1:109309 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.861 | - | 0.0137 | - | **23.5%** |
| ENSG00000241860 chr1:109576 CGTGT>C/CGTGTGTGT | chr1:109576 CGTGT>C/CGTGTGTGT | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.437 | - | 0.03509 | - | **0.8,0.2** |
| ENSG00000241860 chr1:97953 A>G | chr1:97953 A>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.123 | - | 0.327 | - | **22.7%** |
| ENSG00000241860 chr1:100876 T>C | chr1:100876 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 6.586 | - | 0.06049 | - | **41.4%** |
| ENSG00000241860 chr1:101158 T>C | chr1:101158 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.471 | - | 0.9997 | - | **100.0%** |
| ENSG00000241860 chr1:101225 C>A | chr1:101225 C>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.543 | - | 0.08649 | - | **40.0%** |
| ENSG00000241860 chr1:101268 G>A | chr1:101268 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.192 | - | 0.2827 | - | **27.3%** |
| ENSG00000241860 chr1:101393 T>C | chr1:101393 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.049 | - | 0.07791 | - | **70.0%** |
| ENSG00000241860 chr1:101550 C>T | chr1:101550 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.709 | - | 0.1552 | - | **46.2%** |
| ENSG00000241860 chr1:101895 G>A | chr1:101895 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 7.021 | - | 0.2779 | - | **19.2%** |
| ENSG00000241860 chr1:103241 C>T | chr1:103241 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.248 | - | 0.4691 | - | **17.8%** |
| ENSG00000241860 chr1:104033 T>C | chr1:104033 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.613 | - | 0.5025 | - | **34.8%** |
| ENSG00000241860 chr1:104160 A>AACAC | chr1:104160 A>AACAC | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.486 | - | 0.4663 | - | **100.0%** |
| ENSG00000241860 chr1:104320 T>C | chr1:104320 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 5.999 | - | 0.1273 | - | **18.8%** |
| ENSG00000241860 chr1:104326 A>G | chr1:104326 A>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.913 | - | 0.1235 | - | **23.5%** |
| ENSG00000241860 chr1:106544 C>G | chr1:106544 C>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.312 | - | 1 | - | **100.0%** |
| ENSG00000241860 chr1:108297 A>C | chr1:108297 A>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.103 | - | 0.1824 | - | **23.8%** |
| ENSG00000241860 chr1:108310 T>C | chr1:108310 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 5.727 | - | 0.1131 | - | **28.6%** |
| ENSG00000241860 chr1:108413 T>G | chr1:108413 T>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.142 | - | 0.151 | - | **43.1%** |
| ENSG00000241860 chr1:108545 C>CA | chr1:108545 C>CA | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.824 | - | 0.5684 | - | **88.9%** |
| ENSG00000241860 chr1:108893 C>T | chr1:108893 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 8.297 | - | 0.422 | - | **44.3%** |
| ENSG00000241860 chr1:109488 G>A | chr1:109488 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.040 | - | 0.09029 | - | **52.2%** |
| ENSG00000241860 chr1:109580 G>A | chr1:109580 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.955 | - | 0.06697 | - | **57.1%** |
| ENSG00000241860 chr1:110598 G>A | chr1:110598 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 7.101 | - | 0.1361 | - | **29.2%** |
| ENSG00000241860 chr1:110703 C>T | chr1:110703 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.052 | - | 0.4983 | - | **27.8%** |
| ENSG00000241860 chr1:110752 C>A | chr1:110752 C>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 5.070 | - | 0.1448 | - | **21.6%** |
| ENSG00000241860 chr1:112531 G>A | chr1:112531 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.813 | - | 0.2653 | - | **44.4%** |
| ENSG00000241860 chr1:113969 C>T | chr1:113969 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.644 | - | 0.5073 | - | **22.6%** |
| ENSG00000241860 chr1:114810 C>T | chr1:114810 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.088 | - | 0.5932 | - | **31.6%** |
| ENSG00000241860 chr1:115474 A>G | chr1:115474 A>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.657 | - | 0.3013 | - | **58.6%** |
| ENSG00000241860 chr1:116134 A>G | chr1:116134 A>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.331 | - | 0.3138 | - | **30.8%** |
| ENSG00000241860 chr1:120458 T>C | chr1:120458 T>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.691 | - | 0.9992 | - | **90.9%** |
| ENSG00000241860 chr1:121552 C>T | chr1:121552 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 4.037 | - | 0.5021 | - | **75.0%** |
| ENSG00000241860 chr1:122815 A>G | chr1:122815 A>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 7.005 | - | 0.4767 | - | **58.1%** |
| ENSG00000241860 chr1:122872 T>G | chr1:122872 T>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.195 | - | 0.4181 | - | **30.6%** |
| ENSG00000241860 chr1:123511 G>A | chr1:123511 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 2.140 | - | 0.9007 | - | **100.0%** |
| ENSG00000241860 chr1:123642 T>G | chr1:123642 T>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 6.842 | - | 0.9449 | - | **100.0%** |
| ENSG00000241860 chr1:125271 C>T | chr1:125271 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.176 | - | 1 | - | **100.0%** |
| ENSG00000241860 chr1:126113 C>A | chr1:126113 C>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.831 | - | 0.9998 | - | **100.0%** |
| ENSG00000241860 chr1:127972 G>A | chr1:127972 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.605 | - | 0.08238 | - | **41.7%** |
| ENSG00000241860 chr1:128595 CT>C | chr1:128595 CT>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 0.678 | - | 0.3392 | - | **100.0%** |
| ENSG00000241860 chr1:128798 C>T | chr1:128798 C>T | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.773 | - | 0.9995 | - | **100.0%** |
| ENSG00000241860 chr1:129285 G>A | chr1:129285 G>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.663 | - | 0.5138 | - | **36.2%** |
| ENSG00000241860 chr1:129477 T>G | chr1:129477 T>G | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.623 | - | 0.2842 | - | **41.7%** |
| ENSG00000241860 chr1:150462 A>C | chr1:150462 A>C | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 3.898 | - | 0.757 | - | **100.0%** |
| ENSG00000241860 chr1:168066 C>A | chr1:168066 C>A | ENST00000831081.1 | intron_variant,non_coding_transcript_variant | 1.328 | - | 0.1366 | - | **100.0%** |

#### 3.5.3 变异详细分析

##### 3.5.3.1 ENSG00000241860 chr1:168098 A>G

###### 3.5.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:168098 A>G（GRCh38） |
| 测序等位基因比例 | **83.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 5 条（合计 6 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=15.79；FS（链偏倚）=0；MQ（比对质量）=20 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000310528（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831102.1 |
| RefSeq | - |
| HGVSc | n.649+2T>C |
| HGVSp | - |
| VEP 后果 | splice_donor_variant,non_coding_transcript_variant |
| VEP 影响等级 | HIGH |

###### 3.5.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 18.47 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.04896 |
| gnomAD Popmax AF | 0.25 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=splice_donor_variant(+33); CADD=18.47(+2); EAS_AF=0.04896; frequency(-20); total=+15 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.2 ENSG00000241860 chr1:120277 C>T

###### 3.5.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:120277 C>T（GRCh38） |
| 测序等位基因比例 | **37.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 34 条 / 变异序列 20 条（合计 54 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 54 |
| 碱基质量指标 | QD（质量/深度）=6.35；FS（链偏倚）=0；MQ（比对质量）=27.34 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-28037G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.705 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0; frequency(+10); total=+7 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.3 ENSG00000241860 chr1:111059 T>C

###### 3.5.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:111059 T>C（GRCh38） |
| 测序等位基因比例 | **16.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 2 条（合计 12 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=3.89；FS（链偏倚）=0；MQ（比对质量）=24.85 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.3.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-18819A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.469 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.00021 |
| gnomAD Popmax AF | 0.00021 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.00021; frequency(+8); total=+5 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.4 ENSG00000241860 chr1:119723 G>A

###### 3.5.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:119723 G>A（GRCh38） |
| 测序等位基因比例 | **44.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 8 条（合计 18 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 18 |
| 碱基质量指标 | QD（质量/深度）=8.65；FS（链偏倚）=4.359；MQ（比对质量）=24.88 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.4.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-27483C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.381 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.001511 |
| gnomAD Popmax AF | 0.001511 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.001511; frequency(+3); total=+0 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.5 ENSG00000241860 chr1:111057 C>CA

###### 3.5.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:111057 C>CA（GRCh38） |
| 测序等位基因比例 | **16.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 10 条 / 变异序列 2 条（合计 12 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=3.88；FS（链偏倚）=0；MQ（比对质量）=24.85 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.5.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-18818dup |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.6 ENSG00000241860 chr1:128342 G>A

###### 3.5.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:128342 G>A（GRCh38） |
| 测序等位基因比例 | **66.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 2 条（合计 3 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=24.55；FS（链偏倚）=4.771；MQ（比对质量）=31.93 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.6.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-36102C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.097 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.7 ENSG00000241860 chr1:128343 CCTA>C

###### 3.5.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:128343 CCTA>C（GRCh38） |
| 测序等位基因比例 | **66.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 2 条（合计 3 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=24.53；FS（链偏倚）=4.771；MQ（比对质量）=31.93 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.7.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-36106_689-36104del |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.8 ENSG00000241860 chr1:129444 AGTGC>A

###### 3.5.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:129444 AGTGC>A（GRCh38） |
| 测序等位基因比例 | **15.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 11 条 / 变异序列 2 条（合计 13 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 15 |
| 碱基质量指标 | QD（质量/深度）=3.35；FS（链偏倚）=0；MQ（比对质量）=24.07 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+36436_688+36439del |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.9 ENSG00000241860 chr1:129452 G>A

###### 3.5.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:129452 G>A（GRCh38） |
| 测序等位基因比例 | **14.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 2 条（合计 14 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 14 |
| 碱基质量指标 | QD（质量/深度）=2.9；FS（链偏倚）=0；MQ（比对质量）=22.51 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+36432C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.504 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.10 ENSG00000241860 chr1:129453 G>T

###### 3.5.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:129453 G>T（GRCh38） |
| 测序等位基因比例 | **14.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 2 条（合计 14 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 14 |
| 碱基质量指标 | QD（质量/深度）=2.9；FS（链偏倚）=0；MQ（比对质量）=22.51 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+36431C>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.236 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); total=-3 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.11 ENSG00000241860 chr1:103210 G>T

###### 3.5.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:103210 G>T（GRCh38） |
| 测序等位基因比例 | **16.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 35 条 / 变异序列 7 条（合计 42 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 42 |
| 碱基质量指标 | QD（质量/深度）=0.99；FS（链偏倚）=27.287；MQ（比对质量）=28.35 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.5.3.11.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-10970C>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.393 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.007514 |
| gnomAD Popmax AF | 0.1982 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.007514; frequency(-7); total=-10 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.12 ENSG00000241860 chr1:103983 C>T

###### 3.5.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:103983 C>T（GRCh38） |
| 测序等位基因比例 | **15.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 28 条 / 变异序列 5 条（合计 33 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 35 |
| 碱基质量指标 | QD（质量/深度）=1.87；FS（链偏倚）=0；MQ（比对质量）=41.22 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.5.3.12.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-11743G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.432 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.008505 |
| gnomAD Popmax AF | 0.1923 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.008505; frequency(-7); total=-10 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.13 ENSG00000241860 chr1:109107 G>GT

###### 3.5.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:109107 G>GT（GRCh38） |
| 测序等位基因比例 | **15.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 33 条 / 变异序列 6 条（合计 39 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 43 |
| 碱基质量指标 | QD（质量/深度）=2.25；FS（链偏倚）=19.673；MQ（比对质量）=44.66 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.5.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16868dup |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.626 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.006588 |
| gnomAD Popmax AF | 0.141 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.006588; frequency(-7); total=-10 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.14 ENSG00000241860 chr1:102951 C>T

###### 3.5.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:102951 C>T（GRCh38） |
| 测序等位基因比例 | **13.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 50 条 / 变异序列 8 条（合计 58 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 62 |
| 碱基质量指标 | QD（质量/深度）=1.63；FS（链偏倚）=9.187；MQ（比对质量）=40.89 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.5.3.14.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-10711G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.761 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.04526 |
| gnomAD Popmax AF | 0.2088 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.04526; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.15 ENSG00000241860 chr1:103233 C>T

###### 3.5.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:103233 C>T（GRCh38） |
| 测序等位基因比例 | **25.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 32 条 / 变异序列 11 条（合计 43 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 45 |
| 碱基质量指标 | QD（质量/深度）=6.15；FS（链偏倚）=5.558；MQ（比对质量）=28.71 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-10993G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.069 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.01735 |
| gnomAD Popmax AF | 0.2299 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.01735; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.16 ENSG00000241860 chr1:104018 C>T

###### 3.5.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:104018 C>T（GRCh38） |
| 测序等位基因比例 | **20.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 19 条 / 变异序列 5 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 25 |
| 碱基质量指标 | QD（质量/深度）=2.36；FS（链偏倚）=0；MQ（比对质量）=33.1 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-11778G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.790 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.02783 |
| gnomAD Popmax AF | 0.3215 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.02783; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.17 ENSG00000241860 chr1:105774 GT>G

###### 3.5.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:105774 GT>G（GRCh38） |
| 测序等位基因比例 | **52.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 9 条（合计 17 条 reads） |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=13.86；FS（链偏倚）=3.274；MQ（比对质量）=23.13 |
| 外显子 | - |

###### 3.5.3.17.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-13535del |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.210 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.03982 |
| gnomAD Popmax AF | 0.336 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.03982; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.18 ENSG00000241860 chr1:105867 C>T

###### 3.5.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:105867 C>T（GRCh38） |
| 测序等位基因比例 | **29.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 33 条 / 变异序列 14 条（合计 47 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 47 |
| 碱基质量指标 | QD（质量/深度）=4.91；FS（链偏倚）=37.559；MQ（比对质量）=25.06 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.18.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-13627G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.392 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.03397 |
| gnomAD Popmax AF | 0.3173 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.03397; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.19 ENSG00000241860 chr1:109309 G>A

###### 3.5.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:109309 G>A（GRCh38） |
| 测序等位基因比例 | **23.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 65 条 / 变异序列 20 条（合计 85 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 87 |
| 碱基质量指标 | QD（质量/深度）=3.62；FS（链偏倚）=13.87；MQ（比对质量）=30.5 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.19.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-17069C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.861 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0137 |
| gnomAD Popmax AF | 0.3036 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.0137; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.20 ENSG00000241860 chr1:109576 CGTGT>C/CGTGTGTGT

###### 3.5.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:109576 CGTGT>C/CGTGTGTGT（GRCh38） |
| 测序等位基因比例 | **0.8,0.2**（基于测序 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 8 |
| 碱基质量指标 | QD（质量/深度）=22.4；FS（链偏倚）=0；MQ（比对质量）=32.02 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.20.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-17339_689-17336del |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.437 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.03509 |
| gnomAD Popmax AF | 0.3272 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.03509; frequency(-20); total=-23 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.21 ENSG00000241860 chr1:97953 A>G

###### 3.5.3.21.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:97953 A>G（GRCh38） |
| 测序等位基因比例 | **22.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 34 条 / 变异序列 10 条（合计 44 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 45 |
| 碱基质量指标 | QD（质量/深度）=2.83；FS（链偏倚）=0；MQ（比对质量）=23.92 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.21.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.21.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-5713T>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.21.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.123 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.21.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.327 |
| gnomAD Popmax AF | 0.4157 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.21.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.327; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.21.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.22 ENSG00000241860 chr1:100876 T>C

###### 3.5.3.22.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:100876 T>C（GRCh38） |
| 测序等位基因比例 | **41.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 17 条 / 变异序列 12 条（合计 29 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 30 |
| 碱基质量指标 | QD（质量/深度）=7.82；FS（链偏倚）=24.829；MQ（比对质量）=28.42 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.22.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.22.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-8636A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.22.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 6.586 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.22.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.06049 |
| gnomAD Popmax AF | 0.4035 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.22.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.06049; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.22.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.23 ENSG00000241860 chr1:101158 T>C

###### 3.5.3.23.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101158 T>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 9 条（合计 9 条 reads） |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=25.01；FS（链偏倚）=0；MQ（比对质量）=22.95 |
| 外显子 | - |

###### 3.5.3.23.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.23.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-8918A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.23.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.471 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.23.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9997 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.23.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9997; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.23.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.24 ENSG00000241860 chr1:101225 C>A

###### 3.5.3.24.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101225 C>A（GRCh38） |
| 测序等位基因比例 | **40.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 6 条 / 变异序列 4 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=9.46；FS（链偏倚）=3.979；MQ（比对质量）=34.71 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.24.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.24.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-8985G>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.24.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.543 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.24.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.08649 |
| gnomAD Popmax AF | 0.3981 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.24.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.08649; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.24.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.25 ENSG00000241860 chr1:101268 G>A

###### 3.5.3.25.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101268 G>A（GRCh38） |
| 测序等位基因比例 | **27.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 8 条 / 变异序列 3 条（合计 11 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=5.51；FS（链偏倚）=0；MQ（比对质量）=33.94 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.25.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.25.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-9028C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.25.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.192 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.25.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.2827 |
| gnomAD Popmax AF | 0.4165 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.25.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.2827; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.25.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.26 ENSG00000241860 chr1:101393 T>C

###### 3.5.3.26.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101393 T>C（GRCh38） |
| 测序等位基因比例 | **70.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 7 条（合计 10 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=17.66；FS（链偏倚）=0；MQ（比对质量）=40.58 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.26.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.26.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-9153A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.26.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.049 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.26.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.07791 |
| gnomAD Popmax AF | 0.3808 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.26.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.07791; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.26.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.27 ENSG00000241860 chr1:101550 C>T

###### 3.5.3.27.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101550 C>T（GRCh38） |
| 测序等位基因比例 | **46.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 6 条（合计 13 条 reads） |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=9.36；FS（链偏倚）=0；MQ（比对质量）=31.9 |
| 外显子 | - |

###### 3.5.3.27.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.27.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-9310G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.27.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.709 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.27.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1552 |
| gnomAD Popmax AF | 0.2561 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.27.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1552; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.27.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.28 ENSG00000241860 chr1:101895 G>A

###### 3.5.3.28.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:101895 G>A（GRCh38） |
| 测序等位基因比例 | **19.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 21 条 / 变异序列 5 条（合计 26 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 26 |
| 碱基质量指标 | QD（质量/深度）=3.14；FS（链偏倚）=1.974；MQ（比对质量）=40.96 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.28.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.28.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-9655C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.28.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.021 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.28.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.2779 |
| gnomAD Popmax AF | 0.424 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.28.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.2779; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.28.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.29 ENSG00000241860 chr1:103241 C>T

###### 3.5.3.29.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:103241 C>T（GRCh38） |
| 测序等位基因比例 | **17.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 37 条 / 变异序列 8 条（合计 45 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 45 |
| 碱基质量指标 | QD（质量/深度）=2.66；FS（链偏倚）=14.366；MQ（比对质量）=28.71 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.29.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.29.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-11001G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.29.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.248 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.29.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4691 |
| gnomAD Popmax AF | 0.4814 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.29.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4691; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.29.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.30 ENSG00000241860 chr1:104033 T>C

###### 3.5.3.30.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:104033 T>C（GRCh38） |
| 测序等位基因比例 | **34.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 15 条 / 变异序列 8 条（合计 23 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 23 |
| 碱基质量指标 | QD（质量/深度）=5.68；FS（链偏倚）=0；MQ（比对质量）=31.83 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.30.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.30.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-11793A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.30.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.613 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.30.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5025 |
| gnomAD Popmax AF | 0.5407 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.30.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5025; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.30.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.31 ENSG00000241860 chr1:104160 A>AACAC

###### 3.5.3.31.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:104160 A>AACAC（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 2 条（合计 2 条 reads） |
| 测序深度 | 2 |
| 碱基质量指标 | QD（质量/深度）=35；FS（链偏倚）=0；MQ（比对质量）=32.25 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.31.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.31.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-11924_689-11921dup |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.31.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.486 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.31.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4663 |
| gnomAD Popmax AF | 0.4663 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.31.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4663; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.31.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.32 ENSG00000241860 chr1:104320 T>C

###### 3.5.3.32.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:104320 T>C（GRCh38） |
| 测序等位基因比例 | **18.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 3 条（合计 16 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 16 |
| 碱基质量指标 | QD（质量/深度）=4.6；FS（链偏倚）=0；MQ（比对质量）=25.63 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.32.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.32.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-12080A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.32.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.999 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.32.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1273 |
| gnomAD Popmax AF | 0.2128 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.32.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1273; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.32.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.33 ENSG00000241860 chr1:104326 A>G

###### 3.5.3.33.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:104326 A>G（GRCh38） |
| 测序等位基因比例 | **23.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 4 条（合计 17 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=5.92；FS（链偏倚）=0；MQ（比对质量）=25.59 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.33.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000308314（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.33.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-12086T>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.33.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.913 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.33.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1235 |
| gnomAD Popmax AF | 0.2128 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.33.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1235; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.33.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.34 ENSG00000241860 chr1:106544 C>G

###### 3.5.3.34.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:106544 C>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 2 条（合计 2 条 reads） |
| 测序深度 | 2 |
| 碱基质量指标 | QD（质量/深度）=28.16；FS（链偏倚）=0；MQ（比对质量）=42.53 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.34.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.34.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-14304G>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.34.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.312 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.34.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.34.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.34.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.35 ENSG00000241860 chr1:108297 A>C

###### 3.5.3.35.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:108297 A>C（GRCh38） |
| 测序等位基因比例 | **23.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 48 条 / 变异序列 15 条（合计 63 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 67 |
| 碱基质量指标 | QD（质量/深度）=3.87；FS（链偏倚）=10.958；MQ（比对质量）=49.75 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.35.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.35.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16057T>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.35.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.103 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.35.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1824 |
| gnomAD Popmax AF | 0.5574 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.35.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1824; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.35.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.36 ENSG00000241860 chr1:108310 T>C

###### 3.5.3.36.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:108310 T>C（GRCh38） |
| 测序等位基因比例 | **28.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 45 条 / 变异序列 18 条（合计 63 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 65 |
| 碱基质量指标 | QD（质量/深度）=5.44；FS（链偏倚）=13.662；MQ（比对质量）=49.33 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.36.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 137 例，ALT 等位基因计数 137 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.36.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16070A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.36.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.727 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.36.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1131 |
| gnomAD Popmax AF | 0.4586 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.36.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1131; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.36.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.37 ENSG00000241860 chr1:108413 T>G

###### 3.5.3.37.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:108413 T>G（GRCh38） |
| 测序等位基因比例 | **43.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 41 条 / 变异序列 31 条（合计 72 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 72 |
| 碱基质量指标 | QD（质量/深度）=9.38；FS（链偏倚）=0；MQ（比对质量）=36.29 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.37.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.37.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16173A>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.37.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.142 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.37.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.151 |
| gnomAD Popmax AF | 0.4374 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.37.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.151; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.37.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.38 ENSG00000241860 chr1:108545 C>CA

###### 3.5.3.38.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:108545 C>CA（GRCh38） |
| 测序等位基因比例 | **88.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 8 条（合计 9 条 reads） |
| GATK 基因型 AF | 100.0% |
| 测序深度 | 10 |
| 碱基质量指标 | QD（质量/深度）=17.88；FS（链偏倚）=5.229；MQ（比对质量）=34.59 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.38.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.38.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16306dup |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.38.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.824 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.38.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5684 |
| gnomAD Popmax AF | 0.5684 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.38.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5684; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.38.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.39 ENSG00000241860 chr1:108893 C>T

###### 3.5.3.39.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:108893 C>T（GRCh38） |
| 测序等位基因比例 | **44.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 34 条 / 变异序列 27 条（合计 61 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 63 |
| 碱基质量指标 | QD（质量/深度）=9.88；FS（链偏倚）=9.078；MQ（比对质量）=29.58 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.39.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.39.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-16653G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.39.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 8.297 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.39.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.422 |
| gnomAD Popmax AF | 0.422 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.39.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.422; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.39.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.40 ENSG00000241860 chr1:109488 G>A

###### 3.5.3.40.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:109488 G>A（GRCh38） |
| 测序等位基因比例 | **52.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 11 条 / 变异序列 12 条（合计 23 条 reads） |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=10.68；FS（链偏倚）=0；MQ（比对质量）=31.04 |
| 外显子 | - |

###### 3.5.3.40.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.40.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-17248C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.40.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.040 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.40.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.09029 |
| gnomAD Popmax AF | 0.4026 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.40.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.09029; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.40.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.41 ENSG00000241860 chr1:109580 G>A

###### 3.5.3.41.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:109580 G>A（GRCh38） |
| 测序等位基因比例 | **57.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 3 条 / 变异序列 4 条（合计 7 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 8 |
| 碱基质量指标 | QD（质量/深度）=9.52；FS（链偏倚）=8.451；MQ（比对质量）=32.02 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.41.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.41.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-17340C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.41.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.955 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.41.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.06697 |
| gnomAD Popmax AF | 0.2531 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.41.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.06697; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.41.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.42 ENSG00000241860 chr1:110598 G>A

###### 3.5.3.42.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:110598 G>A（GRCh38） |
| 测序等位基因比例 | **29.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 17 条 / 变异序列 7 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=5.07；FS（链偏倚）=0；MQ（比对质量）=24.17 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.42.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 112 例，ALT 等位基因计数 112 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.42.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-18358C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.42.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.101 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.42.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1361 |
| gnomAD Popmax AF | 0.4178 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.42.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1361; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.42.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.43 ENSG00000241860 chr1:110703 C>T

###### 3.5.3.43.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:110703 C>T（GRCh38） |
| 测序等位基因比例 | **27.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 26 条 / 变异序列 10 条（合计 36 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 40 |
| 碱基质量指标 | QD（质量/深度）=4.74；FS（链偏倚）=0；MQ（比对质量）=24 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.43.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.43.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-18463G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.43.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.052 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.43.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4983 |
| gnomAD Popmax AF | 0.4983 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.43.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4983; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.43.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.44 ENSG00000241860 chr1:110752 C>A

###### 3.5.3.44.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:110752 C>A（GRCh38） |
| 测序等位基因比例 | **21.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 40 条 / 变异序列 11 条（合计 51 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 52 |
| 碱基质量指标 | QD（质量/深度）=2.54；FS（链偏倚）=0；MQ（比对质量）=24.18 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.44.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.44.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-18512G>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.44.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.070 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.44.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1448 |
| gnomAD Popmax AF | 0.4213 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.44.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1448; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.44.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.45 ENSG00000241860 chr1:112531 G>A

###### 3.5.3.45.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:112531 G>A（GRCh38） |
| 测序等位基因比例 | **44.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 5 条 / 变异序列 4 条（合计 9 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 9 |
| 碱基质量指标 | QD（质量/深度）=5.52；FS（链偏倚）=0；MQ（比对质量）=20.11 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.45.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.45.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-20291C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.45.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.813 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.45.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.2653 |
| gnomAD Popmax AF | 0.2653 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.45.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.2653; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.45.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.46 ENSG00000241860 chr1:113969 C>T

###### 3.5.3.46.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:113969 C>T（GRCh38） |
| 测序等位基因比例 | **22.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 48 条 / 变异序列 14 条（合计 62 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 63 |
| 碱基质量指标 | QD（质量/深度）=2.56；FS（链偏倚）=7.168；MQ（比对质量）=35.06 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.46.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 351 例，ALT 等位基因计数 364 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.46.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-21729G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.46.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.644 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.46.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5073 |
| gnomAD Popmax AF | 0.6501 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.46.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5073; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.46.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.47 ENSG00000241860 chr1:114810 C>T

###### 3.5.3.47.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:114810 C>T（GRCh38） |
| 测序等位基因比例 | **31.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 6 条（合计 19 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 19 |
| 碱基质量指标 | QD（质量/深度）=4.82；FS（链偏倚）=29.863；MQ（比对质量）=26.31 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.47.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.47.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-22570G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.47.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.088 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.47.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5932 |
| gnomAD Popmax AF | 0.6025 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.47.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5932; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.47.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.48 ENSG00000241860 chr1:115474 A>G

###### 3.5.3.48.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:115474 A>G（GRCh38） |
| 测序等位基因比例 | **58.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 12 条 / 变异序列 17 条（合计 29 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 29 |
| 碱基质量指标 | QD（质量/深度）=14.95；FS（链偏倚）=0；MQ（比对质量）=39.9 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.48.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.48.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-23234T>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.48.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.657 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.48.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3013 |
| gnomAD Popmax AF | 0.3013 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.48.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.3013; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.48.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.49 ENSG00000241860 chr1:116134 A>G

###### 3.5.3.49.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:116134 A>G（GRCh38） |
| 测序等位基因比例 | **30.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 9 条 / 变异序列 4 条（合计 13 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 13 |
| 碱基质量指标 | QD（质量/深度）=5.13；FS（链偏倚）=0；MQ（比对质量）=24.44 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.49.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 250 例，ALT 等位基因计数 250 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.49.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-23894T>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.49.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.331 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.49.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3138 |
| gnomAD Popmax AF | 0.3138 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.49.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.3138; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.49.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.50 ENSG00000241860 chr1:120458 T>C

###### 3.5.3.50.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:120458 T>C（GRCh38） |
| 测序等位基因比例 | **90.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 10 条（合计 11 条 reads） |
| GATK 基因型 AF | 100.0% |
| 测序深度 | 11 |
| 碱基质量指标 | QD（质量/深度）=22.09；FS（链偏倚）=10.414；MQ（比对质量）=22.01 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.50.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.50.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-28218A>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.50.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.691 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.50.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9992 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.50.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9992; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.50.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.51 ENSG00000241860 chr1:121552 C>T

###### 3.5.3.51.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:121552 C>T（GRCh38） |
| 测序等位基因比例 | **75.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 1 条 / 变异序列 3 条（合计 4 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=16.66；FS（链偏倚）=0；MQ（比对质量）=24 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限；测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.51.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.51.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-29312G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.51.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 4.037 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.51.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5021 |
| gnomAD Popmax AF | 0.5021 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.51.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5021; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.51.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.52 ENSG00000241860 chr1:122815 A>G

###### 3.5.3.52.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:122815 A>G（GRCh38） |
| 测序等位基因比例 | **58.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 18 条 / 变异序列 25 条（合计 43 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 44 |
| 碱基质量指标 | QD（质量/深度）=11.88；FS（链偏倚）=2.67；MQ（比对质量）=27.14 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.52.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 348 例，ALT 等位基因计数 348 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.52.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-30575T>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.52.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.005 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.52.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4767 |
| gnomAD Popmax AF | 0.4767 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.52.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4767; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.52.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.53 ENSG00000241860 chr1:122872 T>G

###### 3.5.3.53.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:122872 T>G（GRCh38） |
| 测序等位基因比例 | **30.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 34 条 / 变异序列 15 条（合计 49 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 51 |
| 碱基质量指标 | QD（质量/深度）=4.48；FS（链偏倚）=0；MQ（比对质量）=26.65 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.53.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.53.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-30632A>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.53.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.195 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.53.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4181 |
| gnomAD Popmax AF | 0.4181 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.53.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.4181; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.53.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.54 ENSG00000241860 chr1:123511 G>A

###### 3.5.3.54.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:123511 G>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 22 条（合计 22 条 reads） |
| 测序深度 | 22 |
| 碱基质量指标 | QD（质量/深度）=22.82；FS（链偏倚）=0；MQ（比对质量）=20.19 |
| 外显子 | - |

###### 3.5.3.54.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 628 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.54.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-31271C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.54.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 2.140 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.54.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9007 |
| gnomAD Popmax AF | 0.9007 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.54.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9007; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.54.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.55 ENSG00000241860 chr1:123642 T>G

###### 3.5.3.55.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:123642 T>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 10 条（合计 10 条 reads） |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=23.31；FS（链偏倚）=0；MQ（比对质量）=21.49 |
| 外显子 | - |

###### 3.5.3.55.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.55.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-31402A>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.55.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 6.842 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.55.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9449 |
| gnomAD Popmax AF | 0.9449 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.55.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9449; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.55.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.56 ENSG00000241860 chr1:125271 C>T

###### 3.5.3.56.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:125271 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 9 条（合计 9 条 reads） |
| 测序深度 | 9 |
| 碱基质量指标 | QD（质量/深度）=23.23；FS（链偏倚）=0；MQ（比对质量）=20 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.56.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.56.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-33031G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.56.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.176 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.56.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 1 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.56.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=1; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.56.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.57 ENSG00000241860 chr1:126113 C>A

###### 3.5.3.57.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:126113 C>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 29 条（合计 29 条 reads） |
| 测序深度 | 31 |
| 碱基质量指标 | QD（质量/深度）=30.69；FS（链偏倚）=0；MQ（比对质量）=34.77 |
| 外显子 | - |

###### 3.5.3.57.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 716 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.57.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-33873G>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.57.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.831 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.57.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9998 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.57.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9998; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.57.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.58 ENSG00000241860 chr1:127972 G>A

###### 3.5.3.58.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:127972 G>A（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 14 条 / 变异序列 10 条（合计 24 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 24 |
| 碱基质量指标 | QD（质量/深度）=9.78；FS（链偏倚）=21.919；MQ（比对质量）=28.44 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.58.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.58.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-35732C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.58.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.605 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.58.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.08238 |
| gnomAD Popmax AF | 0.09914 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.58.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.08238; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.58.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.59 ENSG00000241860 chr1:128595 CT>C

###### 3.5.3.59.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:128595 CT>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 2 条（合计 2 条 reads） |
| 测序深度 | 6 |
| 碱基质量指标 | QD（质量/深度）=26.47；FS（链偏倚）=0；MQ（比对质量）=42.19 |
| 解读提示 | 支持变异的 reads 偏少，建议 Sanger 验证；测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.59.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.59.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-36356del |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.59.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.678 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.59.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.3392 |
| gnomAD Popmax AF | 0.3392 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.59.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.3392; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.59.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.60 ENSG00000241860 chr1:128798 C>T

###### 3.5.3.60.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:128798 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 17 条（合计 17 条 reads） |
| 测序深度 | 17 |
| 碱基质量指标 | QD（质量/深度）=28；FS（链偏倚）=0；MQ（比对质量）=30.49 |
| 外显子 | - |

###### 3.5.3.60.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 359 例，ALT 等位基因计数 716 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.60.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.689-36558G>A |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.60.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.773 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.60.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.9995 |
| gnomAD Popmax AF | 1 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.60.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.9995; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.60.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.61 ENSG00000241860 chr1:129285 G>A

###### 3.5.3.61.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:129285 G>A（GRCh38） |
| 测序等位基因比例 | **36.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 30 条 / 变异序列 17 条（合计 47 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 48 |
| 碱基质量指标 | QD（质量/深度）=6.16；FS（链偏倚）=0；MQ（比对质量）=25.33 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.61.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.61.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+36599C>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.61.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.663 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.61.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.5138 |
| gnomAD Popmax AF | 0.7206 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.61.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.5138; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.61.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.62 ENSG00000241860 chr1:129477 T>G

###### 3.5.3.62.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:129477 T>G（GRCh38） |
| 测序等位基因比例 | **41.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 7 条 / 变异序列 5 条（合计 12 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 12 |
| 碱基质量指标 | QD（质量/深度）=5.47；FS（链偏倚）=0；MQ（比对质量）=20.43 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.5.3.62.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 198 例，ALT 等位基因计数 198 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000241860（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.62.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+36407A>C |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.62.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.623 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.62.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.2842 |
| gnomAD Popmax AF | 0.2908 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.62.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.2842; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.62.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.63 ENSG00000241860 chr1:150462 A>C

###### 3.5.3.63.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:150462 A>C（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 4 条（合计 4 条 reads） |
| 测序深度 | 4 |
| 碱基质量指标 | QD（质量/深度）=32.79；FS（链偏倚）=0；MQ（比对质量）=35.7 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.63.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000310528（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.63.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.688+15422T>G |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.63.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.898 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.63.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.757 |
| gnomAD Popmax AF | 0.9877 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.63.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.757; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.63.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.5.3.64 ENSG00000241860 chr1:168066 C>A

###### 3.5.3.64.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:168066 C>A（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 3 条（合计 3 条 reads） |
| 测序深度 | 3 |
| 碱基质量指标 | QD（质量/深度）=20.28；FS（链偏倚）=0；MQ（比对质量）=20 |
| 解读提示 | 测序深度偏低，等位基因比例可信度有限 |
| 外显子 | - |

###### 3.5.3.64.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 非编码 RNA | ENSG00000241860,ENSG00000310528（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.5.3.64.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000831081.1 |
| RefSeq | - |
| HGVSc | n.629+983G>T |
| HGVSp | - |
| VEP 后果 | intron_variant,non_coding_transcript_variant |
| VEP 影响等级 | MODIFIER |

###### 3.5.3.64.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 1.328 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.64.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.1366 |
| gnomAD Popmax AF | 0.1518 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.64.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); EAS_AF=0.1366; frequency(-35); total=-38 |
| 治疗意义 | 暂无严格匹配用药。当前检出变异位于非编码RNA区域，ClinVar/功能后果未达到Pathogenic或高影响LoF标准，且缺乏明确的疾病-用药关联证据，不提供针对性用药建议。建议以康复干预（听力辅助、语言训练、特殊教育）为主。 |

###### 3.5.3.64.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |


#### 3.5.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | 根据Open Targets数据库，ENSG00000241860与骨髓增生异常综合征（myelodysplastic syndrome, EFO_0000198）存在极弱关联（score: 0.0019）。该基因属于非编码RNA（lncRNA），功能注释有限。患者临床表现为先天性听力障碍、语言发育迟缓及智力障碍（韦氏评分50分），与骨髓增生异常综合征的血液系统肿瘤表型无明确重叠，提示该基因变异可能为偶然检出或需进一步功能验证的非编码调控变异。 |
| 关联通路 | - |
| 临床建议 | 患儿（26B01490717）自幼听力障碍（佩戴助听器）、语言发育迟缓、理解力差、学习成绩落后（韦氏评分50分，提示中度智力障碍），出生体重9斤（巨大儿）。基因检测在ENSG00000241860（非编码RNA/lncRNA基因）中检出多个剪接供体位点及内含子变异，包括chr1:168098 A>G（n.649+2T>C，CADD=18.47，证据评分+15）及26个内含子变异（CADD多<10）。所有变异ClinVar信息缺失，且均位于非编码区，无蛋白功能改变证据。多个位点等位基因比例（reads VAF）与GATK基因型AF不一致，部分位点测序深度偏低（<20×）或支持变异reads<5，需Sanger验证及家系共分离分析。Open Targets提示该基因与骨髓增生异常综合征存在极弱关联（score~0.002），但与患者神经发育表型无重叠。综合致病性排名（#53）及证据，当前变异不支持为该患儿临床症状的单基因致病原因，建议优先排查蛋白编码区或拷贝数变异。 |

#### 3.5.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

## 4. 方法学与数据质量

### 4.1 分析流程

```
原始 VCF
    ↓
GRCh37 → GRCh38 liftover（如适用）
    ↓
VEP 注释（转录本、功能后果、CADD、SpliceAI 等）
    ↓
gnomAD / ClinVar / GTEx 注释
    ↓
转录本选择与致病性规则排序
    ↓
排序宽表输出（/mnt/workspace/lixinhang/code/search_agent/test_data/test_case/v3_P001_case/06_result_sorting/vep_output.sorted.csv）
    ↓
本报告渲染（v1.1 结构）
```

### 4.2 数据质量说明

| 项目 | 状态 |
|------|------|
| 样本编号 | 26B01490717 |
| VCF 路径 | /mnt/workspace/siwei/vcf_data/26B01490717_3a1e48.vcf |
| Liftover 输出 | 172.27.206.113/mnt/workspace/changan/grch37_to_grch38_liftover/api_service/runs/26B01490717_3a1e48/output/output.grch38.vcf.gz |
| 比对参考基因组 | GRCh38 |
| 宽表总行数 | 注释展开行（含多转录本） |
| 去重后变异数 | 10000 |
| 注释基因数 | 194 |
| 已验证变异 | 无；所有候选均需 Sanger / 功能实验验证 |

### 4.3 排序方法说明

本报告基于排序宽表的 `pathogenic_rank` 与 `evidence_summary`，综合考虑：

- 变异本身影响（CADD、SpliceAI、REVEL、VEP 后果）
- 表型相关组织表达（GTEx / 临床 tissue 白名单）
- 人群频率（gnomAD AF、纯合数）
- 数据库证据（ClinVar 致病性、review status、星级）
- 蛋白结构域与 LoF 预测（LOFTEE）
---

## 5. 免责声明

1. **辅助决策性质**：本报告基于计算预测、公开数据库信息和文献关联生成，仅供研究参考和临床辅助决策使用，**不构成最终临床诊断意见**。
2. **验证要求**：所有候选变异的致病性和临床意义需经实验验证（如 Sanger 测序、功能实验）和**临床遗传学专家复核**。
3. **数据时效性**：数据库信息（ClinVar、gnomAD、OMIM 等）存在更新延迟，解读结果可能随数据更新而变化。
4. **样本范围**：本报告仅用于该样本本次检测，不能外推至其他样本或家系。
5. **表型关联限制**：基因-表型关联解读依赖提供的临床信息与 HPO 术语，可能存在未收录或误判的表型。
6. **治疗建议**：本报告中的建议基于基因组信息和文献证据，不替代临床医生的综合判断。
---

## 6. 阴性结果说明

本次分析基于排序宽表 Top 5 基因生成报告。以下情况未在本报告中展开讨论：

| 项目 | 说明 |
|------|------|
| 未进入 Top 5 的基因 | 宽表共注释 194 个基因，其中 189 个未纳入本报告 Top 列表；可应要求扩展分析 |
| 总变异位点数 | 去重后共 10000 个变异位点 |
| 拷贝数变异（CNV） | 当前输入为 SNV/Indel 排序宽表，未包含 CNV 信息 |
| 融合基因 | 未纳入本次 SNV/Indel 宽表分析范围 |
| 非编码区 / 深度内含子变异 | 默认过滤阈值以外区域未重点解读 |

---

## 7. 临床建议摘要（遗传咨询师视角）

### 7.1 立即建议

1. 对 VWA1 c.961_967del（p.Pro321SerfsTer28）移码变异及 AURKAIP1 c.365C>A（p.Ala122Glu）错义变异进行 Sanger 测序验证，确认 reads 支持偏少等位基因比例的可信度。
2. 结合家系样本（父母、兄弟姐妹）进行分离分析，明确上述变异的遗传模式与共分离情况。
3. 建议扩展神经发育相关基因 panel 或全外显子组数据分析，以排查与本例听力障碍、语言发育差、智力低下（韦氏评分 50 分）及出生体重偏重更匹配的致病变异。
4. 所有用药建议需由儿科神经遗传专科医生复核；当前证据不支持针对 AURKAIP1/VWA1/ATAD3B 的特异性药物治疗。

### 7.2 动态监测

1. 定期听力评估与言语康复训练。
2. 神经发育随访：监测运动、语言、认知发育轨迹，必要时每 6–12 个月复测智力量表。
3. 神经系统查体：关注肌无力、肌萎缩、反射异常等远端神经病变体征，以鉴别 VWA1 相关远端遗传性运动神经元病。
4. 出生体重偏大（9 斤）需关注代谢与内分泌指标，排查过度生长综合征可能。

### 7.3 患者/家属沟通要点

- 当前检测到的变异多为非编码/调控区或低频变异，ClinVar 注释缺失，临床意义未明（VUS），不构成确诊依据。
- VWA1 移码变异虽具潜在功能影响，但其典型表型为远端遗传性运动神经元病（ autosomal recessive 7），与本例神经发育迟缓/听力障碍的表型关联性不确定，需专家共同解读。
- AURKAIP1 错义变异证据评分有限，且无明确致病性 ClinVar 记录。
- ATAD3B 错义变异（CADD 25.9、33）与肿瘤/炎症性疾病关联，与本例表型无直接对应，需谨慎评估。
- 建议患者及家属接受正规遗传咨询，了解再发风险、携带者筛查及生育选择。


---

## 8. 报告输出元信息（ReportOutput）

```json
{
  "report_version": "v1.1",
  "report_title": "26B01490717 基因组变异分析报告",
  "gene_count": 5,
  "variant_count": 215,
  "top_genes": [
    "AURKAIP1",
    "VWA1",
    "ATAD3B",
    "CCNL2",
    "ENSG00000241860"
  ],
  "output_path": "/mnt/workspace/lixinhang/code/search_agent/test_data/test_case/v3_P001_case/06_result_sorting/report.md",
  "literature_strategy": "precomputed_plus_online_fallback",
  "disclaimer_included": true
}
```

---

*报告结束。变异注释数值以排序宽表为准；叙事性解读需经临床遗传学专家复核。*