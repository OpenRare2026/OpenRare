# OpenRare 基因组变异分析报告

> **报告版本**：v1.1  
> **生成日期**：2026-07-03  
> **分析基础**：基于样本 26B03487389 的排序宽表

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
| VCF 来源 | 未提供 |
| GRCh38 转换 | 未提供 |
| 分析日期 | 2026-07-03 |
| 报告人 | AI 辅助基因组解读系统（需临床遗传学专家复核） |

**关键提示**：本报告为**辅助决策**性质，所有候选变异需经实验验证（Sanger、功能实验）后方可用于临床决策。
---

## 2. 分析摘要（Executive Summary）

### 2.1 Top 基因快速列表

本次分析从排序宽表中提取 **Top 5 基因**，共涉及 5 个基因、5 个关键变异位点。

| 排名 | 基因 | 变异数 | 最高排序名次 | PPI 得分 | ClinVar | 主要关联表型 | 主要关联通路 |
|------|------|--------|--------------|----------|---------|--------------|--------------|
| 1 | **HLA-DPA1** | 1 | #1 | 0.6265 | - | - | - |
| 2 | **CXCL17** | 1 | #2 | 0.4378 | - | - | - |
| 3 | **DDI2** | 1 | #4 | 0.4574 | - | - | - |
| 4 | **BMP8B** | 1 | #5 | 0.5393 | - | - | - |
| 5 | **TAS2R19** | 1 | #8 | 0.5175 | - | - | - |

### 2.2 关键发现提示

- **HLA-DPA1**（致病性排名 #1）：暂无明确关联表型记录，需结合临床与变异证据评估。
- **CXCL17**（致病性排名 #2）：暂无明确关联表型记录，需结合临床与变异证据评估。
- **DDI2**（致病性排名 #4）：暂无明确关联表型记录，需结合临床与变异证据评估。
- **BMP8B**（致病性排名 #5）：暂无明确关联表型记录，需结合临床与变异证据评估。
- **TAS2R19**（致病性排名 #8）：暂无明确关联表型记录，需结合临床与变异证据评估。

### 2.3 排序得分白盒展示（示例）

以 HLA-DPA1 为例，排序得分构成如下：

```
evidence_score: -32
  ├── consequence=missense_variant(+15)
  ├── EAS_AF=6.409020e-01
  ├── frequency(-50)
  ├── domain(+3)
```
---

## 3. 基因详细分析（Gene Cards）

### 3.1 基因卡片 1：HLA-DPA1


#### 3.1.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | HLA-DPA1 |
| 染色体位置 | chr6:33068658（GRCh38） |
| 主要转录本 | NM_033554.4 |
| 基因功能 | HLA-DPA1 belongs to the HLA class II alpha chain paralogues. This class II molecule is a heterodimer consisting of an alpha (DPA) and a beta (DPB) chain, both anchored in the membrane. It plays a central role in the immune system by presenting peptides derived from extracellular proteins. Class II molecules are expressed in antigen presenting cells (APC: B lymphocytes, dendritic cells, macrophages). The alpha chain is approximately 33-35 kDa and its gene contains 5 exons. Exon one encodes the leader peptide, exons 2 and 3 encode the two extracellular domains, exon 4 encodes the transmembrane domain and the cytoplasmic tail. Within the DP molecule both the alpha chain and the beta chain contain the polymorphisms specifying the peptide binding specificities, resulting in up to 4 different molecules. [provided by RefSeq, Jul 2008] |
| 遗传模式 |  |
| 主要关联表型 | - |
| 主要关联通路 | - |
| 致病性排名 | #1 |
| PPI 得分 | 0.6265 |
| GENOS-VarRisk | - |

#### 3.1.2 变异列表

| 变异 | 转录本 / 后果 | GENOS-VarRisk | 评分 | ClinVar（VAF） |
|------|---------------|------------|------|----------------|
| HLA-DPA1 p.Thr259Pro | ENST00000692443.1 · missense_variant | - | CADD 3.450 | -（VAF 100.0%） |

#### 3.1.3 变异详细分析

##### 3.1.3.1 HLA-DPA1 p.Thr259Pro

###### 3.1.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr6:33068658 T>G（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 48 条（合计 48 条 reads） |
| 测序深度 | 50 |
| 碱基质量指标 | QD（质量/深度）=33.19；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 4/5 |

###### 3.1.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 中国参考人群 | 携带该 ALT 约 337 例，ALT 等位基因计数 510 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.1.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000692443.1 |
| RefSeq | NM_033554.4,NM_001405020.1 |
| GENOS-VarRisk | - |
| HGVSc | c.775A>C |
| HGVSp | p.Thr259Pro |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.1.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.450 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.640902 |
| gnomAD Popmax AF | 0.640902 |
| gnomAD 纯合数 | 47124 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Nerve - Tibial（TPM 129.8） |
| GTEx Top5 | Cells - EBV-transformed lymphocytes:573.9;Small Intestine - Terminal Ileum - Lymphoid Aggregate:327.7;Spleen:280;Lung:259.6;Liver - Portal Tract:189 |

###### 3.1.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | AFDB-ENSP_mappings:AF-P20036-F1,Phobius:CYTOPLASMIC_DOMAIN |
| 治疗意义 | 药物数据库查询失败，未生成用药建议。 |

**证据摘要**

```
evidence_score: -32
  ├── consequence=missense_variant(+15)
  ├── EAS_AF=6.409020e-01
  ├── frequency(-50)
  ├── domain(+3)
```

###### 3.1.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.1.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.1.5 严格筛选用药建议

药物数据库查询失败，未生成用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.2 基因卡片 2：CXCL17


#### 3.2.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | CXCL17 |
| 染色体位置 | chr19:42433801（GRCh38） |
| 主要转录本 | NM_198477.3 |
| 基因功能 | The protein encoded by this gene is a mucosal chemokine that attracts immature dendritic cells and blood monocytes to the lungs. The encoded protein also promotes tumorigenesis through an angiogenic activity. Finally, this protein exhibits strong antimicrobial activity against E. coli, S. aureus, Salmonella, P. aeruginosa, and C. albicans. Two transcript variants, one protein-coding and the other non-protein coding, have been found for this gene. [provided by RefSeq, Dec 2015] |
| 遗传模式 |  |
| 主要关联表型 | - |
| 主要关联通路 | - |
| 致病性排名 | #2 |
| PPI 得分 | 0.4378 |
| GENOS-VarRisk | - |

#### 3.2.2 变异列表

| 变异 | 转录本 / 后果 | GENOS-VarRisk | 评分 | ClinVar（VAF） |
|------|---------------|------------|------|----------------|
| CXCL17 p.Glu45Asp | ENST00000601181.6 · missense_variant | - | CADD 13.65 | -（VAF 61.8%） |

#### 3.2.3 变异详细分析

##### 3.2.3.1 CXCL17 p.Glu45Asp

###### 3.2.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr19:42433801 T>G（GRCh38） |
| 测序等位基因比例 | **61.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 21 条 / 变异序列 34 条（合计 55 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 56 |
| 碱基质量指标 | QD（质量/深度）=14.27；FS（链偏倚）=2.341；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 2/4 |

###### 3.2.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 中国参考人群 | 携带该 ALT 约 20 例，ALT 等位基因计数 20 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | LIPE-AS1（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.2.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000601181.6 |
| RefSeq | NM_198477.3 |
| GENOS-VarRisk | - |
| HGVSc | c.135A>C |
| HGVSp | p.Glu45Asp |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 13.65 | 需结合其他证据 |
| SpliceAI DS max | 0.1 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0154155 |
| gnomAD Popmax AF | 0.0154155 |
| gnomAD 纯合数 | 7 |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Nerve - Tibial（TPM 0.09） |
| GTEx Top5 | Stomach - Mixed Cell:160.3;Stomach:143.5;Stomach - Mucosa:141.8;Minor Salivary Gland:131.9;Esophagus - Mucosa:83.81 |

###### 3.2.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Pfam:PF15211,Phobius:NON_CYTOPLASMIC_DOMAIN,PANTHER:PTHR37351,AFDB-ENSP_mappings:AF-Q6UXB2-F1 |
| 治疗意义 | 药物数据库查询失败，未生成用药建议。 |

**证据摘要**

```
evidence_score: +0
  ├── consequence=missense_variant(+15)
  ├── splice_lof=SpliceAI:0.1(+3)
  ├── CADD=13.65(+2)
  ├── EAS_AF=1.541550e-02
  ├── frequency(-23)
  ├── domain(+3)
```

###### 3.2.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.2.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.2.5 严格筛选用药建议

药物数据库查询失败，未生成用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.3 基因卡片 3：DDI2


#### 3.3.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | DDI2 |
| 染色体位置 | chr1:15660052（GRCh38） |
| 主要转录本 | NM_032341.5 |
| 基因功能 | Enables aspartic-type endopeptidase activity; identical protein binding activity; and ubiquitin binding activity. Involved in several processes, including cellular response to hydroxyurea; proteolysis; and regulation of DNA stability. Located in cytosol and nucleoplasm. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 |  |
| 主要关联表型 | - |
| 主要关联通路 | - |
| 致病性排名 | #4 |
| PPI 得分 | 0.4574 |
| GENOS-VarRisk | - |

#### 3.3.2 变异列表

| 变异 | 转录本 / 后果 | GENOS-VarRisk | 评分 | ClinVar（VAF） |
|------|---------------|------------|------|----------------|
| DDI2 chr1:15660052 T>C | ENST00000480945.6 · 3_prime_UTR_variant | - | CADD 16.17 | -（VAF 66.7%） |

#### 3.3.3 变异详细分析

##### 3.3.3.1 DDI2 chr1:15660052 T>C

###### 3.3.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:15660052 T>C（GRCh38） |
| 测序等位基因比例 | **66.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 13 条 / 变异序列 26 条（合计 39 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 40 |
| 碱基质量指标 | QD（质量/深度）=17.73；FS（链偏倚）=10.184；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 10/10 |

###### 3.3.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 中国参考人群 | 携带该 ALT 约 13 例，ALT 等位基因计数 13 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 调控元件 | 近端增强子样元件 (pELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.3.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000480945.6 |
| RefSeq | NM_032341.5 |
| GENOS-VarRisk | - |
| HGVSc | c.*262T>C |
| HGVSp | - |
| VEP 后果 | 3_prime_UTR_variant |
| VEP 影响等级 | MODIFIER |

###### 3.3.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 16.17 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.05091 |
| gnomAD Popmax AF | 0.4303 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Nerve - Tibial（TPM 1.78） |
| GTEx Top5 | Cells - EBV-transformed lymphocytes:9.25;Esophagus - Mucosa:7.86;Cells - Cultured fibroblasts:6.465;Minor Salivary Gland:5.62;Skin - Sun Exposed (Lower leg):4.61 |

###### 3.3.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 治疗意义 | 药物数据库查询失败，未生成用药建议。 |

**证据摘要**

```
evidence_score: -36
  ├── consequence=3_prime_utr_variant(-3)
  ├── CADD=16.17(+2)
  ├── EAS_AF=0.05091
  ├── frequency(-35)
```

###### 3.3.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.3.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.3.5 严格筛选用药建议

药物数据库查询失败，未生成用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.4 基因卡片 4：BMP8B


#### 3.4.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | BMP8B |
| 染色体位置 | chr1:39769817（GRCh38） |
| 主要转录本 | NM_001720.5 |
| 基因功能 | This gene encodes a secreted ligand of the TGF-beta (transforming growth factor-beta) superfamily of proteins. Ligands of this family bind various TGF-beta receptors leading to recruitment and activation of SMAD family transcription factors that regulate gene expression. The encoded preproprotein is proteolytically processed to generate each subunit of the disulfide-linked homodimer. The encoded protein stimulates thermogenesis in brown adipose tissue. Expression of this gene may be downregulated in pancreatic cancer. This gene may have arose from a gene duplication event and its gene duplicate is also present on chromosome 1. [provided by RefSeq, Jul 2016] |
| 遗传模式 |  |
| 主要关联表型 | - |
| 主要关联通路 | - |
| 致病性排名 | #5 |
| PPI 得分 | 0.5393 |
| GENOS-VarRisk | - |

#### 3.4.2 变异列表

| 变异 | 转录本 / 后果 | GENOS-VarRisk | 评分 | ClinVar（VAF） |
|------|---------------|------------|------|----------------|
| BMP8B chr1:39769817 T>C | ENST00000372827.8 · intron_variant | - | CADD 9.907 | -（VAF 34.5%） |

#### 3.4.3 变异详细分析

##### 3.4.3.1 BMP8B chr1:39769817 T>C

###### 3.4.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr1:39769817 T>C（GRCh38） |
| 测序等位基因比例 | **34.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 57 条 / 变异序列 30 条（合计 87 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 89 |
| 碱基质量指标 | QD（质量/深度）=5.78；FS（链偏倚）=7.443；MQ（比对质量）=49.96 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.4.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | CA（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.4.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000372827.8 |
| RefSeq | NM_001720.5 |
| GENOS-VarRisk | - |
| HGVSc | c.673+4491A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.4.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 9.907 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4376 |
| gnomAD Popmax AF | 0.4376 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Nerve - Tibial（TPM 30.09） |
| GTEx Top5 | Nerve - Tibial:30.09;Colon - Transverse - Mucosa:4.295;Colon - Transverse - Mixed Cell:3.73;Pancreas - Islets:3.15;Thyroid:3.125 |

###### 3.4.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 治疗意义 | 药物数据库查询失败，未生成用药建议。 |

**证据摘要**

```
evidence_score: -38
  ├── consequence=intron_variant(-3)
  ├── EAS_AF=0.4376
  ├── frequency(-35)
```

###### 3.4.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.4.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.4.5 严格筛选用药建议

药物数据库查询失败，未生成用药建议。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.5 基因卡片 5：TAS2R19


#### 3.5.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | TAS2R19 |
| 染色体位置 | chr12:11021683（GRCh38） |
| 主要转录本 | NM_176888.2 |
| 基因功能 | Predicted to enable G protein-coupled receptor activity and bitter taste receptor activity. Predicted to be involved in G protein-coupled receptor signaling pathway and detection of chemical stimulus involved in sensory perception of bitter taste. Located in membrane. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 |  |
| 主要关联表型 | - |
| 主要关联通路 | - |
| 致病性排名 | #8 |
| PPI 得分 | 0.5175 |
| GENOS-VarRisk | - |

#### 3.5.2 变异列表

| 变异 | 转录本 / 后果 | GENOS-VarRisk | 评分 | ClinVar（VAF） |
|------|---------------|------------|------|----------------|
| TAS2R19 p.Met297Val | ENST00000390673.2 · missense_variant | - | CADD 0.002 | -（VAF 49.6%） |

#### 3.5.3 变异详细分析

##### 3.5.3.1 TAS2R19 p.Met297Val

###### 3.5.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr12:11021683 T>C（GRCh38） |
| 测序等位基因比例 | **49.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 58 条 / 变异序列 57 条（合计 115 条 reads） |
| 测序深度 | 115 |
| 碱基质量指标 | QD（质量/深度）=18.88；FS（链偏倚）=7.158；MQ（比对质量）=59.07 |
| 外显子 | 1/1 |


###### 3.5.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000390673.2 |
| RefSeq | NM_176888.2 |
| GENOS-VarRisk | - |
| HGVSc | c.889A>G |
| HGVSp | p.Met297Val |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.5.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 0.002 | 需结合其他证据 |
| SpliceAI DS max | 0.03 | acceptor_gain |
| REVEL | 0.057 | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.5.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.4974 |
| gnomAD Popmax AF | 0.4974 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | Nerve - Tibial（TPM 0.94） |
| GTEx Top5 | Brain - Cerebellum:1.56;Brain - Cerebellar Hemisphere:1.51;Ovary:1.17;Pituitary:1.08;Nerve - Tibial:0.94 |

###### 3.5.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Gene3D:1.20.1070.10,Pfam:PF05296,PANTHER:PTHR11394,Phobius:CYTOPLASMIC_DOMAIN,AFDB-ENSP_mappings:AF-P59542-F1 |
| 治疗意义 | 药物数据库查询失败，未生成用药建议。 |

**证据摘要**

```
evidence_score: -17
  ├── consequence=missense_variant(+15)
  ├── EAS_AF=0.4974
  ├── frequency(-35)
  ├── domain(+3)
```

###### 3.5.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| - | - | - | 暂无检索到相关文献 | - |


#### 3.5.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.5.5 严格筛选用药建议

药物数据库查询失败，未生成用药建议。

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
排序宽表输出（examples/demo_case/wide_table.csv）
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
| 去重后变异数 | 5 |
| 注释基因数 | 5 |
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
| 未进入 Top 5 的基因 | 宽表共注释 5 个基因，其中 0 个未纳入本报告 Top 列表；可应要求扩展分析 |
| 总变异位点数 | 去重后共 5 个变异位点 |
| 拷贝数变异（CNV） | 当前输入为 SNV/Indel 排序宽表，未包含 CNV 信息 |
| 融合基因 | 未纳入本次 SNV/Indel 宽表分析范围 |
| 非编码区 / 深度内含子变异 | 默认过滤阈值以外区域未重点解读 |

---

## 7. 临床建议摘要（遗传咨询师视角）

### 7.1 立即建议

1. 结合 Top 基因列表安排遗传咨询与验证实验。

### 7.2 动态监测

1. HLA-DPA1（ClinVar=未提供）建议结合表型与家系信息进一步评估。
2. CXCL17（ClinVar=未提供）建议结合表型与家系信息进一步评估。
3. DDI2（ClinVar=未提供）建议结合表型与家系信息进一步评估。
4. BMP8B（ClinVar=未提供）建议结合表型与家系信息进一步评估。
5. TAS2R19（ClinVar=未提供）建议结合表型与家系信息进一步评估。

### 7.3 患者/家属沟通要点

- 本报告为计算注释与数据库证据的辅助解读，不构成最终临床诊断。
- 所有候选变异建议经实验验证并由临床遗传学专家复核后用于临床决策。


---

## 8. 报告输出元信息（ReportOutput）

```json
{
  "report_version": "v1.1",
  "report_title": "26B03487389 基因组变异分析报告",
  "gene_count": 5,
  "variant_count": 5,
  "top_genes": [
    "HLA-DPA1",
    "CXCL17",
    "DDI2",
    "BMP8B",
    "TAS2R19"
  ],
  "output_path": "report.md",
  "literature_strategy": "precomputed_plus_online_fallback",
  "disclaimer_included": true
}
```

---

*报告结束。变异注释数值以排序宽表为准；叙事性解读需经临床遗传学专家复核。*