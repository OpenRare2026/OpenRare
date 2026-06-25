# 基因组变异分析报告

> **报告版本**：v1.1  
> **生成日期**：2026-06-17  
> **分析基础**：基于样本 26B03487389 的排序宽表 /mnt/workspace/lixinhang/code/search_agent/examples/demo_case/wide_table.csv

---

## 1. 报告头部（Header）

| 项目 | 内容 |
|------|------|
| 样本 ID | 26B03487389 |
| 家系类型 | 单人 |
| 家系关系 | 先证者 |
| 临床诊断 / 指征 | 遗传咨询#主诉：咨询1天余，伴随 #现病史：孕15周，自诉孕妇母亲陶彩萍智力异常，智力落后，语言，运动无异常，未做遗传学检查，否认家族史。 |
| HPO 表型 | HP:0001249 |
| 报告受众 | clinician（临床医生） |
| 分析目的 | 基于全外显子/基因组测序变异注释宽表，识别与临床表型相关的候选致病变异 |
| 排序宽表来源 | /mnt/workspace/lixinhang/code/search_agent/examples/demo_case/wide_table.csv |
| VCF 来源 | 未提供 |
| GRCh38 转换 | 未提供 |
| 分析日期 | 2026-06-17 |
| 报告人 | AI 辅助基因组解读系统（需临床遗传学专家复核） |

**关键提示**：本报告为**辅助决策**性质，所有候选变异需经实验验证（Sanger、功能实验）后方可用于临床决策。
---

## 2. 分析摘要（Executive Summary）

### 2.1 Top 基因快速列表

本次分析从排序宽表中提取 **Top 4 基因**，共涉及 4 个基因、4 个关键变异位点。

| 排名 | 基因 | 变异数 | 最高排序名次 | ClinVar | 主要关联表型 | 主要关联通路 |
|------|------|--------|--------------|---------|--------------|--------------|
| 1 | **CNOT3** | 1 | #498 | - | intellectual developmental disorder with speech delay, autism and dysmorphic facies; neurodegenerative disease | Generic Transcription Pathway |
| 2 | **KANSL1** | 1 | #4604 | - | Koolen-de Vries syndrome; Intellectual disability | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 3 | **TNRC6B** | 1 | #57238 | - | global developmental delay with speech and behavioral abnormalities; genetic disorder | - |
| 4 | **SETD5** | 1 | #192603 | - | intellectual disability-facial dysmorphism syndrome due to SETD5 haploinsufficiency; genetic disorder | - |

### 2.2 关键发现提示

- **CNOT3**（致病性排名 #498）：主要关联疾病/表型为「intellectual developmental disorder with speech delay, autism and dysmorphic facies; neurodegenerative disease」；关键词未直接重叠（疾病名为英文、临床为中文时可能低估匹配度，需结合临床判断）。患者表型：遗传咨询#主诉：咨询1天余，伴随 #现病史：孕15周，自诉孕妇母亲陶彩萍智力异常，智力落后，语言，运动无异常，未做遗传学检查，否认家族史。；HP:0001249。
- **KANSL1**（致病性排名 #4604）：主要关联疾病/表型为「Koolen-de Vries syndrome; Intellectual disability」；关键词未直接重叠（疾病名为英文、临床为中文时可能低估匹配度，需结合临床判断）。患者表型：遗传咨询#主诉：咨询1天余，伴随 #现病史：孕15周，自诉孕妇母亲陶彩萍智力异常，智力落后，语言，运动无异常，未做遗传学检查，否认家族史。；HP:0001249。
- **TNRC6B**（致病性排名 #57238）：主要关联疾病/表型为「global developmental delay with speech and behavioral abnormalities; genetic disorder」；关键词未直接重叠（疾病名为英文、临床为中文时可能低估匹配度，需结合临床判断）。患者表型：遗传咨询#主诉：咨询1天余，伴随 #现病史：孕15周，自诉孕妇母亲陶彩萍智力异常，智力落后，语言，运动无异常，未做遗传学检查，否认家族史。；HP:0001249。
- **SETD5**（致病性排名 #192603）：主要关联疾病/表型为「intellectual disability-facial dysmorphism syndrome due to SETD5 haploinsufficiency; genetic disorder」；关键词未直接重叠（疾病名为英文、临床为中文时可能低估匹配度，需结合临床判断）。患者表型：遗传咨询#主诉：咨询1天余，伴随 #现病史：孕15周，自诉孕妇母亲陶彩萍智力异常，智力落后，语言，运动无异常，未做遗传学检查，否认家族史。；HP:0001249。

### 2.3 排序得分白盒展示（示例）

以 CNOT3 为例，排序得分构成如下：

```
evidence_score: +48
  ├── consequence=splice_donor_variant(+33)
  ├── splice_lof=SpliceAI:unknown(+15)
```
---

## 3. 基因详细分析（Gene Cards）

### 3.1 基因卡片 1：CNOT3


#### 3.1.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | CNOT3 |
| 染色体位置 | chr19:54152615（GRCh38） |
| 主要转录本 | NM_014516.4 |
| 基因功能 | Involved in regulation of stem cell population maintenance. Part of CCR4-NOT complex. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 | Intellectual developmental disorder with speech delay, autism, and dysmorphic facies (Autosomal dominant) |
| 主要关联表型 | intellectual developmental disorder with speech delay, autism and dysmorphic facies; neurodegenerative disease |
| 主要关联通路 | Generic Transcription Pathway |
| 致病性排名 | #498 |

#### 3.1.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| CNOT3 chr19:54152615 CTGAGCGTATTCGG>C | chr19:54152615 CTGAGCGTATTCGG>C | ENST00000221232.11 | splice_donor_variant,coding_sequence_variant | - | - | 0.0000 | - | **-** |

#### 3.1.3 变异详细分析

##### 3.1.3.1 CNOT3 chr19:54152615 CTGAGCGTATTCGG>C

###### 3.1.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr19:54152615 CTGAGCGTATTCGG>C（GRCh38） |
| 测序等位基因比例 | **-**（基于 GATK 基因型 AF，当前宽表无 read 计数） |
| 测序深度 | - |
| 外显子 | 15/18 |


###### 3.1.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000221232.11 |
| RefSeq | NM_014516.4 |
| HGVSc | c.1897_1904+5del |
| HGVSp | - |
| VEP 后果 | splice_donor_variant,coding_sequence_variant |
| VEP 影响等级 | HIGH |

###### 3.1.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | - | 未提供 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | HC | LoF 预测标记 |

###### 3.1.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Brain - Cerebellum（TPM 16.39） |
| GTEx Top5 | Testis:27.74;Cells - EBV-transformed lymphocytes:20.96;Uterus:17.47;Cells - Cultured fibroblasts:17.18;Fallopian Tube:17.05 |

###### 3.1.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=splice_donor_variant(+33); splice_lof=SpliceAI:unknown(+15); total=+48 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。 |

###### 3.1.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.1.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | intellectual developmental disorder with speech delay, autism and dysmorphic facies; neurodegenerative disease |
| 关联通路 | Generic Transcription Pathway |
| 临床建议 | consequence=splice_donor_variant(+33); splice_lof=SpliceAI:unknown(+15); total=+48 |

#### 3.1.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.2 基因卡片 2：KANSL1


#### 3.2.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | KANSL1 |
| 染色体位置 | chr17:46039438（GRCh38） |
| 主要转录本 | NM_015443.4 |
| 基因功能 | This gene encodes a nuclear protein that is a subunit of two protein complexes involved with histone acetylation, the MLL1 complex and the NSL1 complex. The encoded protein has been implicated in a variety of cellular processes including enhancer regulation, cell proliferation, and mitosis. Mutations in this gene are associated with Koolen-de Vries Syndrome. [provided by RefSeq, May 2022] |
| 遗传模式 | Koolen-De Vries syndrome (Autosomal dominant) |
| 主要关联表型 | Koolen-de Vries syndrome; Intellectual disability |
| 主要关联通路 | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 致病性排名 | #4604 |

#### 3.2.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| KANSL1 chr17:46039438 C>T | chr17:46039438 C>T | ENST00000432791.7 | intron_variant | 18.23 | 0.38 | 0.0001934 | - | **-** |

#### 3.2.3 变异详细分析

##### 3.2.3.1 KANSL1 chr17:46039438 C>T

###### 3.2.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr17:46039438 C>T（GRCh38） |
| 测序等位基因比例 | **-**（基于 GATK 基因型 AF，当前宽表无 read 计数） |
| 测序深度 | - |
| 外显子 | - |


###### 3.2.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000432791.7 |
| RefSeq | NM_001405855.1,NM_015443.4 |
| HGVSc | c.2204-223G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 18.23 | 需结合其他证据 |
| SpliceAI DS max | 0.38 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0001934 |
| gnomAD Popmax AF | 0.0001934 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Brain - Cerebellar Hemisphere（TPM 1.555） |
| GTEx Top5 | Uterus:1.58;Brain - Cerebellar Hemisphere:1.555;Cervix - Endocervix:1.46;Fallopian Tube:1.44;Brain - Cerebellum:1.24 |

###### 3.2.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.38(+10); CADD=18.23(+2); EAS_AF=0.0001934; frequency(+8); total=+17 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。 |

###### 3.2.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.2.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | Koolen-de Vries syndrome; Intellectual disability |
| 关联通路 | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 临床建议 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.38(+10); CADD=18.23(+2); EAS_AF=0.0001934; frequency(+8); total=+17 |

#### 3.2.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.3 基因卡片 3：TNRC6B


#### 3.3.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | TNRC6B |
| 染色体位置 | chr22:40313649（GRCh38） |
| 主要转录本 | NM_001162501.2 |
| 基因功能 | Enables RNA binding activity. Involved in positive regulation of nuclear-transcribed mRNA catabolic process, deadenylation-dependent decay; positive regulation of nuclear-transcribed mRNA poly(A) tail shortening; and regulatory ncRNA-mediated gene silencing. Acts upstream of with a positive effect on miRNA-mediated gene silencing by inhibition of translation. Predicted to be located in cytosol. Predicted to be active in P-body and nucleoplasm. Implicated in subserous uterine fibroid and uterine fibroid. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 | Global developmental delay with speech and behavioral abnormalities (Autosomal dominant) |
| 主要关联表型 | global developmental delay with speech and behavioral abnormalities; genetic disorder |
| 主要关联通路 | - |
| 致病性排名 | #57238 |

#### 3.3.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| TNRC6B chr22:40313649 C>T | chr22:40313649 C>T | ENST00000454349.7 | intron_variant | 5.462 | 0.26 | 0.0000 | - | **-** |

#### 3.3.3 变异详细分析

##### 3.3.3.1 TNRC6B chr22:40313649 C>T

###### 3.3.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr22:40313649 C>T（GRCh38） |
| 测序等位基因比例 | **-**（基于 GATK 基因型 AF，当前宽表无 read 计数） |
| 测序深度 | - |
| 外显子 | - |


###### 3.3.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000454349.7 |
| RefSeq | NM_001162501.2 |
| HGVSc | c.4678+652C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 5.462 | 需结合其他证据 |
| SpliceAI DS max | 0.26 | acceptor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Brain - Cerebellum（TPM 0.42） |
| GTEx Top5 | Testis:0.42;Brain - Cerebellum:0.42;Brain - Cerebellar Hemisphere:0.34;Stomach - Muscularis:0.225;Pancreas - Islets:0.225 |

###### 3.3.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.26(+10); total=+7 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。 |

###### 3.3.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.3.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | global developmental delay with speech and behavioral abnormalities; genetic disorder |
| 关联通路 | - |
| 临床建议 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.26(+10); total=+7 |

#### 3.3.5 严格筛选用药建议

当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.4 基因卡片 4：SETD5


#### 3.4.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | SETD5 |
| 染色体位置 | chr3:9434718（GRCh38） |
| 主要转录本 | NM_001080517.3 |
| 基因功能 | This function of this gene has yet to be determined but based on sequence similarity to other SET domain proteins it may function as a histone methyltransferase. Mutations in this gene have been associated with an autosomal dominant form of intellectual disability. Alternative splicing results in multiple transcript variants encoding different isoforms. [provided by RefSeq, Jul 2017] |
| 遗传模式 | Intellectual developmental disorder, autosomal dominant 23 (Autosomal dominant) |
| 主要关联表型 | intellectual disability-facial dysmorphism syndrome due to SETD5 haploinsufficiency; genetic disorder |
| 主要关联通路 | - |
| 致病性排名 | #192603 |

#### 3.4.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| SETD5 chr3:9434718 A>T | chr3:9434718 A>T | ENST00000402198.7 | intron_variant | 20.3 | 0 | 0.0000 | - | **-** |

#### 3.4.3 变异详细分析

##### 3.4.3.1 SETD5 chr3:9434718 A>T

###### 3.4.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr3:9434718 A>T（GRCh38） |
| 测序等位基因比例 | **-**（基于 GATK 基因型 AF，当前宽表无 read 计数） |
| 测序深度 | - |
| 外显子 | - |


###### 3.4.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000402198.7 |
| RefSeq | NM_001080517.3 |
| HGVSc | c.330-106A>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 20.3 | > 20，高度可疑有害 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Brain - Cerebellum（TPM 2.69） |
| GTEx Top5 | Uterus:3.12;Artery - Aorta:2.78;Brain - Cerebellum:2.69;Thyroid:2.66;Colon - Sigmoid:2.65 |

###### 3.4.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=20.3(+6); total=+3 |
| 治疗意义 | 当前变异 ClinVar/功能后果未达到 Pathogenic 或高影响 LoF 标准，本报告不提供用药建议。 |

###### 3.4.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.4.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | intellectual disability-facial dysmorphism syndrome due to SETD5 haploinsufficiency; genetic disorder |
| 关联通路 | - |
| 临床建议 | consequence=intron_variant(-3); CADD=20.3(+6); total=+3 |

#### 3.4.5 严格筛选用药建议

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
排序宽表输出（/mnt/workspace/lixinhang/code/search_agent/examples/demo_case/wide_table.csv）
    ↓
本报告渲染（v1.1 结构）
```

### 4.2 数据质量说明

| 项目 | 状态 |
|------|------|
| 样本编号 | 26B03487389 |
| VCF 路径 | 未提供 |
| Liftover 输出 | 未提供 |
| 比对参考基因组 | GRCh38 |
| 宽表总行数 | 注释展开行（含多转录本） |
| 去重后变异数 | 4 |
| 注释基因数 | 4 |
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

本次分析基于排序宽表 Top 4 基因生成报告。以下情况未在本报告中展开讨论：

| 项目 | 说明 |
|------|------|
| 未进入 Top 4 的基因 | 宽表共注释 4 个基因，其中 0 个未纳入本报告 Top 列表；可应要求扩展分析 |
| 总变异位点数 | 去重后共 4 个变异位点 |
| 拷贝数变异（CNV） | 当前输入为 SNV/Indel 排序宽表，未包含 CNV 信息 |
| 融合基因 | 未纳入本次 SNV/Indel 宽表分析范围 |
| 非编码区 / 深度内含子变异 | 默认过滤阈值以外区域未重点解读 |

---

## 7. 临床建议摘要（遗传咨询师视角）

### 7.1 立即建议

1. 结合 Top 基因列表安排遗传咨询与验证实验。

### 7.2 动态监测

1. CNOT3（ClinVar=未提供）建议结合表型与家系信息进一步评估。
2. KANSL1（ClinVar=未提供）建议结合表型与家系信息进一步评估。
3. TNRC6B（ClinVar=未提供）建议结合表型与家系信息进一步评估。
4. SETD5（ClinVar=未提供）建议结合表型与家系信息进一步评估。

### 7.3 患者/家属沟通要点

- 本报告为计算注释与数据库证据的辅助解读，不构成最终临床诊断。
- 所有候选变异建议经实验验证并由临床遗传学专家复核后用于临床决策。


---

## 8. 报告输出元信息（ReportOutput）

```json
{
  "report_version": "v1.1",
  "report_title": "26B03487389 基因组变异分析报告",
  "gene_count": 4,
  "variant_count": 4,
  "top_genes": [
    "CNOT3",
    "KANSL1",
    "TNRC6B",
    "SETD5"
  ],
  "output_path": "/mnt/workspace/lixinhang/code/search_agent/examples/demo_case/output/report.md",
  "literature_strategy": "precomputed_plus_online_fallback",
  "disclaimer_included": true
}
```

---

*报告结束。变异注释数值以排序宽表为准；叙事性解读需经临床遗传学专家复核。*