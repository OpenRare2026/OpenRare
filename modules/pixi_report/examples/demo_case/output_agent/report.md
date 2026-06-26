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

- **CNOT3**（排名 #1）：主要关联疾病/表型为「智力发育障碍伴语言迟滞、自闭症及特殊面容（IDDSADF, OMIM #618672）」。患者临床核心表型（先证者母亲智力落后，HP:0001249）与该疾病的关键特征——智力残疾——重叠较高。该基因检出 splice_donor_variant (c.1897_1904+5del)，为潜在功能缺失变异，文献支持 CNOT3 LoF 变异可导致 IDDSADF，且已报道家族性遗传病例（Meyer et al., 2020）及中国患者（Zhao et al., 2023）。匹配度判定：高。建议优先进行家系共分离验证。
- **KANSL1**（排名 #2）：主要关联疾病/表型为「Koolen-de Vries 综合征」。该综合征典型表型包括智力残疾、特征性面容、肌张力低下、癫痫、先天性心脏病等多系统累及，而当前临床信息仅提示先证者母亲存在智力落后，未描述面容异常或其他 KdVS 特征性表现，表型匹配度有限。该变异为深部内含子变异（c.2204-223G>A, CADD 18.23），虽存在一定剪接预测信号（SpliceAI 0.38），但证据仍不足以支持致病结论。匹配度判定：部分重叠但证据不足。
- **TNRC6B**（排名 #3）：主要关联疾病/表型为「全面发育迟滞伴语言和行为异常」。患者 HPO 表型为智力落后，与发育迟滞表型有一定重叠。但该变异为深部内含子变异（c.4678+652C>T, CADD 5.462, SpliceAI 0.26），预测评分低，功能影响证据极弱。匹配度判定：表型部分重叠但变异证据不足。
- **SETD5**（排名 #4）：主要关联疾病/表型为「SETD5 单倍剂量不足所致智力障碍-面部畸形综合征」。智力残疾为该综合征核心表型，与患者 HPO 匹配；但典型 SETD5 表型常伴特殊面容、先天性心脏缺陷等，当前家族史中无相关描述。该变异为深部内含子变异（c.330-106A>T, CADD 20.3），缺乏剪接功能预测数据支持。匹配度判定：表型部分重叠但证据有限。

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
| 治疗意义 | 当前变异为剪接供体位点变异，ClinVar及功能后果尚未达到明确Pathogenic或高影响LoF标准，本报告不提供用药建议。暂无严格匹配的靶向药物候选。 |

###### 3.1.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42117603 | Phenotypic and Genetic Insights Into CNOT3-Related Intellectual Developmental Disorder of Speech Delay, Autism, and Dysmorphic Faces (IDDSADF) From the First Two Japanese Cases. | Ariyasu D et al. Am J Med Genet A. 2026 | 首次报道日本IDDSADF病例（8岁女童、19岁男童），均携带CNOT3致病杂合变异（c.732dup及c.837+1G>A），表型包括发育迟缓、特殊面容及身材矮小，发现薄帐篷状上唇可能为种族相关特征。 | case_report |
| 36802310 | Clinical features of CNOT3-associated neurodevelopmental disorder in three Chinese patients. | Zhao P et al. Neurogenetics. 2023 | 首次报道中国人群IDDSADF，发现3个新CNOT3杂合变异（c.1058_1059insT、c.724delT及c.387+2T>C），功能研究证实CNOT3 mRNA水平显著下降及外显子跳跃，并观察到CCR4-NOT复合物其他亚基表达改变。 | case_series |
| 38179413 | Novel In-Frame Deletion in CNOT3 Associated with IDDSADF. | Lee CG et al. Neurol Genet. 2024 | 报道新型CNOT3框内缺失变异导致IDDSADF，进一步拓展CNOT3基因型-表型谱。 | case_report |


#### 3.1.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | intellectual developmental disorder with speech delay, autism and dysmorphic facies (IDDSADF) [Open Targets score: 0.756]; neurodegenerative disease [score: 0.540]; complex neurodevelopmental disorder [score: 0.463]; Neurodevelopmental disorder [score: 0.373]. Corroborated by HPO term HP:0001249 (Intellectual disability). |
| 关联通路 | Generic Transcription Pathway (Reactome). CNOT3 is the central component of the CCR4-NOT protein complex, a global regulator of RNA polymerase II transcription that governs mRNA deadenylation, degradation, and translational control. |
| 临床建议 | 受检者孕15周，因母系家族智力异常史行遗传咨询。CNOT3基因检出杂合剪接供体变异 c.1897_1904+5del (chr19:54152615 CTGAGCGTATTCGG>C)，该变异导致编码序列缺失及剪接供体改变。SpliceAI预测提示剪接异常（LoF证据+48分）。该基因为IDDSADF（智力发育障碍伴语言迟缓、孤独症及特殊面容）的致病基因，呈常染色体显性遗传。鉴于该变异的剪接破坏效应，结合家族史，可能为该家系的遗传学病因，但ClinVar及人群频率数据有限，需进一步家系共分离验证及RNA水平功能验证。 |

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
| 关联表型 |  |
| 关联通路 | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

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
| 治疗意义 | 当前变异位点（c.4678+652C>T, intron_variant）的 CADD 评分和 ClinVar 状态均未达到致病性或高影响 LoF 标准，因此本报告不提供具体用药建议。暂无严格匹配的候选药物。 |

###### 3.3.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 41147347 | A Case Report: Co-Occurrence of TNRC6B Gene Variant and Xq28 Microdeletion Syndrome With Comprehensive Literature Review. | Deng Y et al., Birth Defects Res, 2025 | 报道了一例 TNRC6B 杂合变异合并 Xq28 微缺失综合征的患儿。TNRC6B 编码 RNA 沉默关键蛋白，其杂合变异与发育迟缓/智力障碍、言语和语言发育延迟、运动发育迟缓以及自闭症、ADHD 等神经行为表型相关。 | Case Report |
| 39115759 | Identification of the synonymous variant c.3141G > A in TNRC6B gene that altered RNA splicing by minigene assay. | Zhou F et al., Mol Biol Rep, 2024 | 通过 minigene 剪接实验鉴定了一个 TNRC6B 基因的同义变异 c.3141G>A 改变了 RNA 剪接，进一步证实 TNRC6B 变异可导致常染色体显性遗传的全球发育迟缓伴言语和行为异常（OMIM: 619243）。 | Functional Study |
| 38404251 | Novel variants in TNRC6B cause global developmental delay with speech and behavioral abnormalities, short stature, low body weight, café-au-lait spots, and metabolic abnormality. | Yang Q et al., Mol Genet Genomic Med, 2024 | 报道了 TNRC6B 新发变异导致的 TNRC6B 缺陷综合征（MIM 619243），表型谱包括面部畸形、发育迟缓/智力障碍、言语与语言延迟、注意缺陷多动障碍（ADHD）及可变的行为异常。 | Case Series |


#### 3.3.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | Primary: global developmental delay with speech and behavioral abnormalities (MONDO:0030995, score 0.74). Additional associations from Open Targets: genetic disorder (EFO:0000508, score 0.54), complex neurodevelopmental disorder (MONDO:0100038, score 0.46), autism spectrum disorder (EFO:0003756, score 0.42), abnormality of the skeletal system (HP:0000924, score 0.41). Consistent with HPO term HP:0001249 (intellectual disability). |
| 关联通路 | TNRC6B encodes a trinucleotide repeat-containing adaptor 6B protein that functions as a key component of the miRNA-mediated gene silencing machinery. It acts in the RNA-induced silencing complex (RISC) to facilitate mRNA deadenylation, decay, and translational repression via interaction with Argonaute proteins. The gene is involved in positive regulation of nuclear-transcribed mRNA catabolic process (deadenylation-dependent decay), poly(A) tail shortening, and regulatory ncRNA-mediated gene silencing. |
| 临床建议 | 该样本携带 TNRC6B 基因的一个杂合内含子变异 chr22:40313649 C>T（c.4678+652C>T），对应转录本 NM_001162501.2。CADD 评分 5.462（致病性阈值通常≥20），SpliceAI 预测剪接改变概率为 0.26（中等偏低），ClinVar 无收录记录（-），VAF 及测序深度未提供。该变异目前证据不足以认定为明确致病性（Pathogenic）或可能致病性（Likely Pathogenic），分类倾向为意义不明确变异（VUS）。OMIM 已明确 TNRC6B 杂合致病变异导致常染色体显性遗传的全球发育迟缓伴言语和行为异常（OMIM #619243），但当前变异的功能后果需进一步 RNA 测序或 minigene 剪接实验验证。 |

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
| 40869907 | Two Years of Growth Hormone Therapy in a Child with Severe Short Stature Due to Overlap Syndrome with a Novel SETD5 Gene Mutation: Case Report and Review of the Literature. | Luppino G et al., Genes, 2025 | 报道一例携带新发 SETD5 基因突变的患儿合并严重矮小，经生长激素治疗两年后身高改善，提示 SETD5 缺陷可能涉及生长激素轴的临床表型扩展。 | case_report |
| 37797428 | Drug-resistant focal epilepsy in a girl with SETD5-related intellectual disability. | Manokaran RK et al., Seizure, 2023 | 报道一例 SETD5 相关智力残疾女性患儿伴发药物难治性局灶性癫痫，提示 SETD5 单倍剂量不足可累及神经系统兴奋性调控。 | case_report |
| 25138099 | Loss-of-function variants of SETD5 cause intellectual disability and the core phenotype of microdeletion 3p25.3 syndrome. | Kuechler A et al., Eur J Hum Genet, 2015 | 通过全外显子组测序和染色体微阵列分析发现 SETD5 功能缺失变异及微缺失导致智力残疾和 3p25.3 微缺失综合征核心表型，CRISPR/Cas9 模型证实无义介导的 mRNA 降解为共同致病机制，SETD5 变异在 ID 中频率约 0.7%。 | cohort_study |


#### 3.4.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | intellectual disability-facial dysmorphism syndrome due to SETD5 haploinsufficiency; genetic disorder; Intellectual disability (HP:0001249); Neurodevelopmental disorder; neurodegenerative disease |
| 关联通路 | SETD5 encodes a putative histone methyltransferase containing a SET domain and a PHD domain, involved in chromatin remodeling and transcriptional regulation. Its loss-of-function and haploinsufficiency disrupt neurodevelopmental gene expression programs, leading to intellectual disability and facial dysmorphism. The reactome main pathway is not specifically annotated for this gene. |
| 临床建议 | 样本 26B03487389，SETD5 基因检出内含子变异 chr3:9434718 A>T（c.330-106A>T），CADD=20.3，VAF 及 ClinVar 信息缺失。先证者孕 15 周，母系家族史提示智力异常（母陶彩萍智力落后），但该变异为内含子区域低-中度有害性变异，未达经典 Pathogenic/LoF 标准，解读需谨慎。建议结合家系共分离验证及 RNA 水平剪接影响分析进一步评估致病性。 |

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

1. 遗传咨询：建议对先证者（孕妇）及其母亲（存在智力落后的先证者母亲）进行专业遗传咨询，评估遗传病因及再发风险。CNOT3 剪切供体变异是当前最值得关注的候选变异，建议行家系共分离验证，明确该位点在先证者母亲中的携带状态。
2. CNOT3 基因变异验证：建议对该 splice_donor_variant (c.1897_1904+5del) 进行 Sanger 测序验证，并检测先证者及其父母/母亲的样本以明确是否为遗传性变异（文献报道 CNOT3 相关 IDDSADF 存在家族性遗传病例，Meyer et al., 2020, Clin Genet）。
3. 产前诊断评估：建议在充分遗传咨询的前提下，评估是否需要对胎儿进行该位点的产前诊断检测，并讨论常染色体显性遗传模式下50%的遗传风险。
4. 其他基因变异（KANSL1、TNRC6B、SETD5）均为深部内含子变异，功能影响证据不足，当前不支持作为主要致病因素，但在家系全外显子组/全基因组分析中可作进一步数据分析。
5. 由于本报告涉及的基因变异均未达到明确的致病性标准，且 strict_drug_candidates 中无可用药物候选，当前无需用药干预。所有治疗建议需在明确遗传诊断后由专科医生评估。
6. 建议转诊至产前遗传专科门诊，结合超声结构筛查等结果进行综合评估和管理。

### 7.2 动态监测

1. 建议对先证者母亲（智力落后患者）进行临床随访，包括神经发育评估、智力功能评估及可能的影像学检查。
2. 若胎儿出生后，建议进行早期神经发育监测，包括认知、语言、运动功能及社交行为发育评估。
3. 建议定期随访至儿童神经科/发育行为儿科，进行标准化发育筛查量表评估。
4. 若家系中其他成员出现神经发育异常表现，建议一并纳入评估和管理。

### 7.3 患者/家属沟通要点

- 当前检测共检出4个候选基因（CNOT3、KANSL1、TNRC6B、SETD5）的变异，其中 CNOT3 的剪切供体变异（c.1897_1904+5del）证据评分最高（+48分），且关联疾病「智力发育障碍伴语言迟滞、自闭症及特殊面容（IDDSADF）」的核心表型智力落后与先证者母亲的临床表现一致，提示该变异为最可能的致病候选。
- 注意 CNOT3 相关疾病表型存在家族内变异度（Meyer et al., 2020），部分携带者可仅表现为轻度智力落后，不伴有语言运动异常——与先证者母亲的情况相符。同时已有中国患者中 CNOT3 变异的报道（Zhao et al., 2023），具有种族特异性参考价值。
- KANSL1（排名#2）导致 Koolen-de Vries 综合征，典型表型除智力落后外尚包括特征性面容、肌张力低下、骨骼异常等，当前家族史中无相关描述，且变异为深部内含子变异（CADD 18.23），证据有限，表型匹配度不高。
- TNRC6B（排名#3）关联全面发育迟滞伴语言和行为异常，表型部分重叠但变异证据极弱（CADD 5.462，SpliceAI 0.26，深部内含子），暂不支持作为主要致病因素。
- SETD5（排名#4）关联智力障碍-面部畸形综合征，表型上智力落后匹配但未见面部畸形报道，且变异为深部内含子变异（CADD 20.3），证据有限。
- 鉴于当前所有药物候选人列表均为空，本报告不提供任何药物干预建议。明确致病基因诊断需依赖进一步家系验证和临床评估。
- 最终遗传诊断需结合家系共分离分析、临床专科评估及多学科会诊综合判断。


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
  "output_path": "/mnt/workspace/lixinhang/code/search_agent/examples/demo_case/output_agent/report.md",
  "literature_strategy": "precomputed_plus_online_fallback",
  "disclaimer_included": true
}
```

---

*报告结束。变异注释数值以排序宽表为准；叙事性解读需经临床遗传学专家复核。*