# 基因组变异分析报告

> **报告版本**：v1.1  
> **生成日期**：2026-06-16  
> **分析基础**：基于样本 26B03419791 的排序宽表 /mnt/workspace/lixinhang/code/search_agent/test_data/test_case/case_v3_26B03419791/vep_output.with_info.ranked_large.top10000.csv

---

## 1. 报告头部（Header）

| 项目 | 内容 |
|------|------|
| 样本 ID | 26B03419791 |
| 家系类型 | 单人 |
| 家系关系 | 先证者 |
| 临床诊断 / 指征 | 目前患儿重度矮小，轻微漏斗胸，肋外翻，右脚内翻，现爬楼梯困难，不能双脚跳，查血提示低磷，低碳酸氢根。 |
| HPO 表型 | HP:0000767, HP:0000887, HP:0002148, HP:0003510, HP:0003551, HP:0025802, HP:0032066, HP:5200134 |
| 报告受众 | clinician（临床医生） |
| 分析目的 | 基于全外显子/基因组测序变异注释宽表，识别与临床表型相关的候选致病变异 |
| 排序宽表来源 | /mnt/workspace/lixinhang/code/search_agent/test_data/test_case/case_v3_26B03419791/vep_output.with_info.ranked_large.top10000.csv |
| VCF 来源 | 未提供 |
| GRCh38 转换 | 未提供 |
| 分析日期 | 2026-06-16 |
| 报告人 | AI 辅助基因组解读系统（需临床遗传学专家复核） |

**关键提示**：本报告为**辅助决策**性质，所有候选变异需经实验验证（Sanger、功能实验）后方可用于临床决策。
---

## 2. 分析摘要（Executive Summary）

### 2.1 Top 基因快速列表

本次分析从排序宽表中提取 **Top 5 基因**，共涉及 5 个基因、28 个关键变异位点。

| 排名 | 基因 | 变异数 | 最高排序名次 | ClinVar | 主要关联表型 | 主要关联通路 |
|------|------|--------|--------------|---------|--------------|--------------|
| 1 | **CFTR** | 3 | #1 | Pathogenic/Likely pathogenic | cystic fibrosis; congenital bilateral aplasia of vas deferens from CFTR mutation | Defective CFTR causes cystic fibrosis |
| 2 | **KMT2C** | 21 | #6 | Pathogenic | Kleefstra syndrome 2; prostate adenocarcinoma | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 3 | **GJB2** | 2 | #10 | Pathogenic | palmoplantar keratoderma-deafness syndrome; keratoderma hereditarium mutilans | Gap junction assembly |
| 4 | **SLC4A1** | 1 | #15 | Pathogenic/Likely pathogenic | hereditary spherocytosis type 4; autosomal dominant distal renal tubular acidosis | - |
| 5 | **FER1L6** | 1 | #16 | - | atrioventricular block; diverticulitis | - |

### 2.2 关键发现提示

- **CFTR**：missense_variant,splice_region_variant，ClinVar=Pathogenic/Likely pathogenic，致病性排名 #1；Open Targets 主要关联表型：cystic fibrosis; congenital bilateral aplasia of vas deferens from CFTR mutation。
- **KMT2C**：stop_gained，ClinVar=Pathogenic，致病性排名 #6；Open Targets 主要关联表型：Kleefstra syndrome 2; prostate adenocarcinoma。
- **KMT2C 用药**：经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。
- **GJB2**：frameshift_variant，ClinVar=Pathogenic，致病性排名 #10；Open Targets 主要关联表型：palmoplantar keratoderma-deafness syndrome; keratoderma hereditarium mutilans。
- **GJB2 用药**：经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。
- **SLC4A1**：missense_variant，ClinVar=Pathogenic/Likely pathogenic，致病性排名 #15；Open Targets 主要关联表型：hereditary spherocytosis type 4; autosomal dominant distal renal tubular acidosis。
- **SLC4A1 用药**：经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。
- **FER1L6**：splice_donor_variant，ClinVar=未提供，致病性排名 #16；Open Targets 主要关联表型：atrioventricular block; diverticulitis。
- **FER1L6 用药**：经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。
- 临床 HPO 表型 HP:0000767, HP:0000887, HP:0002148, HP:0003510, HP:0003551, HP:0025802, HP:0032066, HP:5200134 需在解读中与候选基因逐一比对。
- **CFTR 用药候选（严格筛选）**：IVACAFTOR（strong，cystic fibrosis）；LUMACAFTOR（strong，cystic fibrosis）；TEZACAFTOR（strong，cystic fibrosis） — 需临床专家复核，不得视为最终处方。

### 2.3 排序得分白盒展示（示例）

以 CFTR 为例，排序得分构成如下：

```
evidence_score: +119
  ├── ClinVar=pathogenic/likely_pathogenic(base=35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=1.00,score=42)
  ├── consequence=missense_variant(+15)
  ├── splice_lof=SpliceAI:0.94(+22)
  ├── REVEL=0.938(+15)
  ├── CADD=34(+12)
  ├── EAS_AF=0
  ├── frequency(+10)
  ├── domain(+3)
```
---

## 3. 基因详细分析（Gene Cards）

### 3.1 基因卡片 1：CFTR


#### 3.1.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | CFTR |
| 染色体位置 | chr7:117548823（GRCh38） |
| 主要转录本 | NM_000492.4 |
| 基因功能 | This gene encodes a member of the ATP-binding cassette (ABC) transporter superfamily. The encoded protein functions as a chloride channel, making it unique among members of this protein family, and controls ion and water secretion and absorption in epithelial tissues. Channel activation is mediated by cycles of regulatory domain phosphorylation, ATP-binding by the nucleotide-binding domains, and ATP hydrolysis. Mutations in this gene cause cystic fibrosis, the most common lethal genetic disorder in populations of Northern European descent. The most frequently occurring mutation in cystic fibrosis, DeltaF508, results in impaired folding and trafficking of the encoded protein. Multiple pseudogenes have been identified in the human genome. [provided by RefSeq, Aug 2017] |
| 遗传模式 | {Bronchiectasis with or without elevated sweat chloride 1, modifier of} (Autosomal dominant); {Hypertrypsinemia, neonatal}; {Pancreatitis, hereditary} (Autosomal dominant); Congenital bilateral absence of vas deferens (Autosomal recessive); Cystic fibrosis (Autosomal recessive); Sweat chloride elevation without CF |
| 主要关联表型 | cystic fibrosis; congenital bilateral aplasia of vas deferens from CFTR mutation |
| 主要关联通路 | Defective CFTR causes cystic fibrosis |
| 致病性排名 | #1 |

#### 3.1.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| CFTR p.Lys464Asn | chr7:117548823 G>T | ENST00000003084.11 | missense_variant,splice_region_variant | 34 | 0.94 | 0.0000 | Pathogenic/Likely pathogenic | **12.5%** |
| CFTR p.Leu454del | chr7:117548786 AGTT>A | ENST00000003084.11 | inframe_deletion | 17.82 | - | 0.002789 | Conflicting classifications of pathogenicity | **10.5%** |
| CFTR chr7:117548828 T>TC | chr7:117548828 T>TC | ENST00000003084.11 | splice_donor_region_variant,intron_variant | 13.10 | - | 0.0000 | - | **9.4%** |

#### 3.1.3 变异详细分析

##### 3.1.3.1 CFTR p.Lys464Asn

###### 3.1.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:117548823 G>T（GRCh38） |
| 测序等位基因比例 | **12.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 28 条 / 变异序列 4 条（合计 32 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 37 |
| 碱基质量指标 | QD（质量/深度）=1.96；FS（链偏倚）=1.463；MQ（比对质量）=52.73 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | 10/27 |

###### 3.1.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.1.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000003084.11 |
| RefSeq | NM_000492.4 |
| HGVSc | c.1392G>T |
| HGVSp | p.Lys464Asn |
| VEP 后果 | missense_variant,splice_region_variant |
| VEP 影响等级 | MODERATE |

###### 3.1.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 34 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.94 | donor_loss |
| REVEL | 0.938 | ≥ 0.5，可疑有害 |
| LOFTEE | OS | LoF 预测标记 |

###### 3.1.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0003088 |
| gnomAD 纯合数 | - |
| ClinVar | Pathogenic/Likely pathogenic（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:1xmi.A,PDB-ENSP_mappings:1xmi.B,PDB-ENSP_mappings:1xmi.C,PDB-ENSP_mappings:1xmi.D,PDB-ENSP_mappings:1xmi.E,PDB-ENSP_mappings:1xmj.A,PDB-ENSP_mappings:2bbo.A,PDB-ENSP_mappings:2bbs.A,PDB-ENSP_mappings:2bbs.B,PDB-ENSP_mappings:2bbt.A,PDB-ENSP_mappings:2bbt.B,PDB-ENSP_mappings:2pze.A,PDB-ENSP_mappings:2pze.B,PDB-ENSP_mappings:2pzf.A,PDB-ENSP_mappings:2pzf.B,PDB-ENSP_mappings:2pzg.A,PDB-ENSP_mappings:2pzg.B,PDB-ENSP_mappings:4wz6.A,PDB-ENSP_mappings:5tf7.A,PDB-ENSP_mappings:5tf8.A,PDB-ENSP_mappings:5tfa.A,PDB-ENSP_mappings:5tfb.A,PDB-ENSP_mappings:5tfc.A,PDB-ENSP_mappings:5tfd.A,PDB-ENSP_mappings:5tff.A,PDB-ENSP_mappings:5tfg.A,PDB-ENSP_mappings:5tfi.A,PDB-ENSP_mappings:5tfj.A,PDB-ENSP_mappings:5tgk.A,PDB-ENSP_mappings:5uak.A,PDB-ENSP_mappings:6gjq.A,PDB-ENSP_mappings:6gjq.C,PDB-ENSP_mappings:6gjq.E,PDB-ENSP_mappings:6gjq.G,PDB-ENSP_mappings:6gjs.A,PDB-ENSP_mappings:6gju.A,PDB-ENSP_mappings:6gk4.A,PDB-ENSP_mappings:6gk4.D,PDB-ENSP_mappings:6gkd.A,PDB-ENSP_mappings:6gkd.F,PDB-ENSP_mappings:6gkd.I,PDB-ENSP_mappings:6gkd.L,PDB-ENSP_mappings:6gkd.O,PDB-ENSP_mappings:6gkd.R,PDB-ENSP_mappings:6msm.A,PDB-ENSP_mappings:6o1v.A,PDB-ENSP_mappings:6o2p.A,PDB-ENSP_mappings:6wbs.A,PDB-ENSP_mappings:6wbs.B,PDB-ENSP_mappings:6ze1.A,PDB-ENSP_mappings:7sv7.A,PDB-ENSP_mappings:7svd.A,PDB-ENSP_mappings:7svr.A,PDB-ENSP_mappings:8eig.A,PDB-ENSP_mappings:8eio.A,PDB-ENSP_mappings:8eiq.A,PDB-ENSP_mappings:8ej1.A,PDB-ENSP_mappings:8fzq.A,PDB-ENSP_mappings:8gls.A,PDB-ENSP_mappings:8ubr.A,PDB-ENSP_mappings:8v7z.A,PDB-ENSP_mappings:8v81.A,PDB-ENSP_mappings:9dw4.A,PDB-ENSP_mappings:9dw5.A,PDB-ENSP_mappings:9dw7.A,PDB-ENSP_mappings:9dw8.A,PDB-ENSP_mappings:9dw9.A,CDD:cd03291,Pfam:PF00005,NCBIFAM:TIGR01271,Gene3D:3.40.50.300,Superfamily:SSF52540,SMART:SM00382,Phobius:CYTOPLASMIC_DOMAIN,PROSITE_profiles:PS50893,PANTHER:PTHR24223,AFDB-ENSP_mappings:AF-P13569-F1 |
| 证据摘要 | ClinVar=pathogenic/likely_pathogenic(base=35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=1.00,score=42); consequence=missense_variant(+15); splice_lof=SpliceAI:0.94(+22); REVEL=0.938(+15); CADD=34(+12); EAS_AF=0; frequency(+10); domain(+3); total=+119 |
| 治疗意义 | 基于 Open Targets 严格筛选保留 3 项已获批（APPROVAL）候选药物：IVACAFTOR、LUMACAFTOR、TEZACAFTOR，三者均用于 cystic fibrosis，作用机制为 CFTR 蛋白功能调节，适用于特定突变类型（如 F508del）的 CF 患者。具体用药须结合患者基因型（尤其是否为响应突变）、年龄、肝肾功能及合并症，由临床专家复核后决策。 |

###### 3.1.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42272190 | Real-World Clinical Outcomes of Lumacaftor-Ivacaftor or Tezacaftor-Ivacaftor Therapy in Children With Cystic Fibrosis Homozygous for Phe508del. | Aerssens N, Vermeulen F, Boon M, Proesmans M. Pediatric Pulmonology. 2026. | 真实世界研究评估 lumacaftor/ivacaftor 或 tezacaftor/ivacaftor 双联 CFTR 调节剂对 Phe508del 纯合儿童 1 年治疗结局的影响，显示临床获益。 | moderate |
| 42234158 | Early effect of CFTR modulators on the mental health of patients with cystic fibrosis and parents. | Yetişgin H, Akyan Soydaş ŞS, Özkan Tabakçı S, Bilgiç I, Kürtül Çakar M, Akca Dinç G, Ünlü A, Yıldırım Ç, Çetin MA, Tuğcu GD, Ademhan Tural D, Eryılmaz Polat E, Şenses Dinç G, Çöp E, Cinel G. European Journal of Pediatrics. 2026. | 前瞻性观察研究显示，使用 CFTR 调节剂治疗的患儿焦虑评分显著低于未治疗组，且家长抑郁焦虑评分也更低，提示调节剂对患者及家庭心理健康有早期获益。 | moderate |
| 42206906 | Comparison of Long Term Effects of Treatment of Different CFTR Modulators in People With Cystic Fibrosis. | Famulska P, Więckowska B, Narożna B, Sapiejka E, Osińska M, Musiał A, Szczepankiewicz A, Tąpolska-Jóźwiak K, Wiesner A, Steinert-Dymecki A, Jóźwiak M, Wojsyk-Banaszak I. Pediatric Pulmonology. 2026. | 比较不同 CFTR 调节剂的长期治疗效果，证明 CFTR 调节剂在改善患者健康结局与生活质量方面的突破性作用。 | moderate |

##### 3.1.3.2 CFTR p.Leu454del

###### 3.1.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:117548786 AGTT>A（GRCh38） |
| 测序等位基因比例 | **10.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 34 条 / 变异序列 4 条（合计 38 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 45 |
| 碱基质量指标 | QD（质量/深度）=1.38；FS（链偏倚）=1.482；MQ（比对质量）=50.24 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | 10/27 |

###### 3.1.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.1.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000003084.11 |
| RefSeq | NM_000492.4 |
| HGVSc | c.1360_1362del |
| HGVSp | p.Leu454del |
| VEP 后果 | inframe_deletion |
| VEP 影响等级 | MODERATE |

###### 3.1.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 17.82 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.002789 |
| gnomAD Popmax AF | 0.009077 |
| gnomAD 纯合数 | - |
| ClinVar | Conflicting classifications of pathogenicity（criteria provided, conflicting classifications，1 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:1xmi.A,PDB-ENSP_mappings:1xmi.B,PDB-ENSP_mappings:1xmi.C,PDB-ENSP_mappings:1xmi.D,PDB-ENSP_mappings:1xmi.E,PDB-ENSP_mappings:1xmj.A,PDB-ENSP_mappings:2bbo.A,PDB-ENSP_mappings:2bbs.A,PDB-ENSP_mappings:2bbs.B,PDB-ENSP_mappings:2bbt.A,PDB-ENSP_mappings:2bbt.B,PDB-ENSP_mappings:2pze.A,PDB-ENSP_mappings:2pze.B,PDB-ENSP_mappings:2pzf.A,PDB-ENSP_mappings:2pzf.B,PDB-ENSP_mappings:2pzg.A,PDB-ENSP_mappings:2pzg.B,PDB-ENSP_mappings:4wz6.A,PDB-ENSP_mappings:5tf7.A,PDB-ENSP_mappings:5tf8.A,PDB-ENSP_mappings:5tfa.A,PDB-ENSP_mappings:5tfb.A,PDB-ENSP_mappings:5tfc.A,PDB-ENSP_mappings:5tfd.A,PDB-ENSP_mappings:5tff.A,PDB-ENSP_mappings:5tfg.A,PDB-ENSP_mappings:5tfi.A,PDB-ENSP_mappings:5tfj.A,PDB-ENSP_mappings:5tgk.A,PDB-ENSP_mappings:5uak.A,PDB-ENSP_mappings:6gjq.A,PDB-ENSP_mappings:6gjq.C,PDB-ENSP_mappings:6gjq.E,PDB-ENSP_mappings:6gjq.G,PDB-ENSP_mappings:6gjs.A,PDB-ENSP_mappings:6gju.A,PDB-ENSP_mappings:6gk4.A,PDB-ENSP_mappings:6gk4.D,PDB-ENSP_mappings:6gkd.A,PDB-ENSP_mappings:6gkd.F,PDB-ENSP_mappings:6gkd.I,PDB-ENSP_mappings:6gkd.L,PDB-ENSP_mappings:6gkd.O,PDB-ENSP_mappings:6gkd.R,PDB-ENSP_mappings:6msm.A,PDB-ENSP_mappings:6o1v.A,PDB-ENSP_mappings:6o2p.A,PDB-ENSP_mappings:6wbs.A,PDB-ENSP_mappings:6wbs.B,PDB-ENSP_mappings:6ze1.A,PDB-ENSP_mappings:7sv7.A,PDB-ENSP_mappings:7svd.A,PDB-ENSP_mappings:7svr.A,PDB-ENSP_mappings:8eig.A,PDB-ENSP_mappings:8eio.A,PDB-ENSP_mappings:8eiq.A,PDB-ENSP_mappings:8ej1.A,PDB-ENSP_mappings:8fzq.A,PDB-ENSP_mappings:8gls.A,PDB-ENSP_mappings:8ubr.A,PDB-ENSP_mappings:8v7z.A,PDB-ENSP_mappings:8v81.A,PDB-ENSP_mappings:9dw4.A,PDB-ENSP_mappings:9dw5.A,PDB-ENSP_mappings:9dw7.A,PDB-ENSP_mappings:9dw8.A,PDB-ENSP_mappings:9dw9.A,CDD:cd03291,Pfam:PF00005,NCBIFAM:TIGR01271,Gene3D:3.40.50.300,Superfamily:SSF52540,SMART:SM00382,Phobius:CYTOPLASMIC_DOMAIN,PROSITE_profiles:PS50893,PANTHER:PTHR24223,AFDB-ENSP_mappings:AF-P13569-F1 |
| 证据摘要 | consequence=inframe_deletion(+13); CADD=17.82(+2); EAS_AF=0.002789; frequency(+3); domain(+3); total=+21 |
| 治疗意义 | 基于 Open Targets 严格筛选保留 3 项已获批（APPROVAL）候选药物：IVACAFTOR、LUMACAFTOR、TEZACAFTOR，三者均用于 cystic fibrosis，作用机制为 CFTR 蛋白功能调节，适用于特定突变类型（如 F508del）的 CF 患者。具体用药须结合患者基因型（尤其是否为响应突变）、年龄、肝肾功能及合并症，由临床专家复核后决策。 |

###### 3.1.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42272190 | Real-World Clinical Outcomes of Lumacaftor-Ivacaftor or Tezacaftor-Ivacaftor Therapy in Children With Cystic Fibrosis Homozygous for Phe508del. | Aerssens N, Vermeulen F, Boon M, Proesmans M. Pediatric Pulmonology. 2026. | 真实世界研究评估 lumacaftor/ivacaftor 或 tezacaftor/ivacaftor 双联 CFTR 调节剂对 Phe508del 纯合儿童 1 年治疗结局的影响，显示临床获益。 | moderate |
| 42234158 | Early effect of CFTR modulators on the mental health of patients with cystic fibrosis and parents. | Yetişgin H, Akyan Soydaş ŞS, Özkan Tabakçı S, Bilgiç I, Kürtül Çakar M, Akca Dinç G, Ünlü A, Yıldırım Ç, Çetin MA, Tuğcu GD, Ademhan Tural D, Eryılmaz Polat E, Şenses Dinç G, Çöp E, Cinel G. European Journal of Pediatrics. 2026. | 前瞻性观察研究显示，使用 CFTR 调节剂治疗的患儿焦虑评分显著低于未治疗组，且家长抑郁焦虑评分也更低，提示调节剂对患者及家庭心理健康有早期获益。 | moderate |
| 42206906 | Comparison of Long Term Effects of Treatment of Different CFTR Modulators in People With Cystic Fibrosis. | Famulska P, Więckowska B, Narożna B, Sapiejka E, Osińska M, Musiał A, Szczepankiewicz A, Tąpolska-Jóźwiak K, Wiesner A, Steinert-Dymecki A, Jóźwiak M, Wojsyk-Banaszak I. Pediatric Pulmonology. 2026. | 比较不同 CFTR 调节剂的长期治疗效果，证明 CFTR 调节剂在改善患者健康结局与生活质量方面的突破性作用。 | moderate |

##### 3.1.3.3 CFTR chr7:117548828 T>TC

###### 3.1.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:117548828 T>TC（GRCh38） |
| 测序等位基因比例 | **9.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 29 条 / 变异序列 3 条（合计 32 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 37 |
| 碱基质量指标 | QD（质量/深度）=0.99；FS（链偏倚）=1.614；MQ（比对质量）=54.46 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.1.3.3.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.1.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000003084.11 |
| RefSeq | NM_000492.4 |
| HGVSc | c.1392+5_1392+6insC |
| HGVSp | - |
| VEP 后果 | splice_donor_region_variant,intron_variant |
| VEP 影响等级 | LOW |

###### 3.1.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 13.10 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.1.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 2.438e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.1.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | CADD=13.1(+2); EAS_AF=0; frequency(+10); total=+12 |
| 治疗意义 | 基于 Open Targets 严格筛选保留 3 项已获批（APPROVAL）候选药物：IVACAFTOR、LUMACAFTOR、TEZACAFTOR，三者均用于 cystic fibrosis，作用机制为 CFTR 蛋白功能调节，适用于特定突变类型（如 F508del）的 CF 患者。具体用药须结合患者基因型（尤其是否为响应突变）、年龄、肝肾功能及合并症，由临床专家复核后决策。 |

###### 3.1.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42272190 | Real-World Clinical Outcomes of Lumacaftor-Ivacaftor or Tezacaftor-Ivacaftor Therapy in Children With Cystic Fibrosis Homozygous for Phe508del. | Aerssens N, Vermeulen F, Boon M, Proesmans M. Pediatric Pulmonology. 2026. | 真实世界研究评估 lumacaftor/ivacaftor 或 tezacaftor/ivacaftor 双联 CFTR 调节剂对 Phe508del 纯合儿童 1 年治疗结局的影响，显示临床获益。 | moderate |
| 42234158 | Early effect of CFTR modulators on the mental health of patients with cystic fibrosis and parents. | Yetişgin H, Akyan Soydaş ŞS, Özkan Tabakçı S, Bilgiç I, Kürtül Çakar M, Akca Dinç G, Ünlü A, Yıldırım Ç, Çetin MA, Tuğcu GD, Ademhan Tural D, Eryılmaz Polat E, Şenses Dinç G, Çöp E, Cinel G. European Journal of Pediatrics. 2026. | 前瞻性观察研究显示，使用 CFTR 调节剂治疗的患儿焦虑评分显著低于未治疗组，且家长抑郁焦虑评分也更低，提示调节剂对患者及家庭心理健康有早期获益。 | moderate |
| 42206906 | Comparison of Long Term Effects of Treatment of Different CFTR Modulators in People With Cystic Fibrosis. | Famulska P, Więckowska B, Narożna B, Sapiejka E, Osińska M, Musiał A, Szczepankiewicz A, Tąpolska-Jóźwiak K, Wiesner A, Steinert-Dymecki A, Jóźwiak M, Wojsyk-Banaszak I. Pediatric Pulmonology. 2026. | 比较不同 CFTR 调节剂的长期治疗效果，证明 CFTR 调节剂在改善患者健康结局与生活质量方面的突破性作用。 | moderate |


#### 3.1.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | cystic fibrosis; congenital bilateral aplasia of vas deferens from CFTR mutation. 基于 Open Targets 关联补充：cystic fibrosis (MONDO_0009061, score 0.913); congenital bilateral aplasia of vas deferens from CFTR mutation (MONDO_0010178, score 0.828); hereditary chronic pancreatitis (MONDO_0008185, score 0.712); bronchiectasis with or without elevated sweat chloride 1 (MONDO_0008887, score 0.695); congenital bilateral absence of vas deferens (MONDO_0018801, score 0.637). |
| 关联通路 | Defective CFTR causes cystic fibrosis |
| 临床建议 | 患儿表现为重度矮小、轻微漏斗胸、肋外翻、右脚内翻、爬楼梯困难及不能双脚跳，伴低磷血症与代谢性酸中毒（低碳酸氢根），提示骨骼、电解质及酸碱平衡受累。HPO 术语涵盖骨骼畸形、生长异常及肺/胰腺相关表型。样本在 CFTR 基因检出 3 个变异：c.1392G>T（p.Lys464Asn，ClinVar Pathogenic/Likely pathogenic，CADD 34，REVEL 0.938，SpliceAI 0.94）；c.1360_1362del（p.Leu454del，框内缺失，ClinVar 分类矛盾）；c.1392+5_1392+6insC（剪接供体位点插入）。三处变异 reads 支持比例约 9–12%，与 GATK 基因型 AF（0.5）不一致，且位点命中假基因相关区域，提示需警惕假基因比对干扰或测序偏差，解读时应优先参考 reads 支持并结合功能验证。综合临床表型、变异致病性评分及 CFTR 功能缺失机制，该基因与样本表型存在显著关联，但假基因区域提示需进一步家系与功能实验确认。 |

#### 3.1.5 严格筛选用药建议

严格匹配后保留 3 项候选：IVACAFTOR、LUMACAFTOR、TEZACAFTOR（详见下表，需临床专家复核）。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| IVACAFTOR | cystic fibrosis | APPROVAL | strong | 适应症与 cystic fibrosis 关联；与样本临床/HPO 表型部分匹配；作用机制涉及 CFTR | 仅基于 Open Targets 数据库关联，需结合 ClinVar/家系/临床表型与伦理规范确认；不得视为超适应症用药依据。 |
| LUMACAFTOR | cystic fibrosis | APPROVAL | strong | 适应症与 cystic fibrosis 关联；与样本临床/HPO 表型部分匹配；作用机制涉及 CFTR | 仅基于 Open Targets 数据库关联，需结合 ClinVar/家系/临床表型与伦理规范确认；不得视为超适应症用药依据。 |
| TEZACAFTOR | cystic fibrosis | APPROVAL | strong | 适应症与 cystic fibrosis 关联；与样本临床/HPO 表型部分匹配；作用机制涉及 CFTR | 仅基于 Open Targets 数据库关联，需结合 ClinVar/家系/临床表型与伦理规范确认；不得视为超适应症用药依据。 |


---

### 3.2 基因卡片 2：KMT2C


#### 3.2.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | KMT2C |
| 染色体位置 | chr7:152248171（GRCh38） |
| 主要转录本 | NM_170606.3 |
| 基因功能 | This gene is a member of the myeloid/lymphoid or mixed-lineage leukemia (MLL) family and encodes a nuclear protein with an AT hook DNA-binding domain, a DHHC-type zinc finger, six PHD-type zinc fingers, a SET domain, a post-SET domain and a RING-type zinc finger. This protein is a member of the ASC-2/NCOA6 complex (ASCOM), which possesses histone methylation activity and is involved in transcriptional coactivation. [provided by RefSeq, Jul 2008] |
| 遗传模式 | Kleefstra syndrome 2 (Autosomal dominant) |
| 主要关联表型 | Kleefstra syndrome 2; prostate adenocarcinoma |
| 主要关联通路 | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 致病性排名 | #6 |

#### 3.2.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| KMT2C p.Gln755Ter | chr7:152248171 G>A | ENST00000262189.11 | stop_gained | 34 | 0 | 0.0000 | Pathogenic | **10.2%** |
| KMT2C p.Pro309Ser | chr7:152273792 G>A | ENST00000262189.11 | missense_variant | 31 | 0.31 | 0.0000 | Uncertain significance | **12.7%** |
| KMT2C p.Tyr987His | chr7:152229940 A>G | ENST00000262189.11 | missense_variant | 25.2 | 0.01 | 0.0000 | - | **31.4%** |
| KMT2C p.Gly315Cys | chr7:152273774 C>A | ENST00000262189.11 | missense_variant | 27.0 | 0 | 0.0000 | - | **15.2%** |
| KMT2C p.Gly838Ser | chr7:152247922 C>T | ENST00000262189.11 | missense_variant | 25.4 | 0.01 | 0.001701 | - | **51.9%** |
| KMT2C p.Ser793= | chr7:152248055 C>T | ENST00000262189.11 | synonymous_variant | 7.062 | 0 | 0.0000 | - | **43.5%** |
| KMT2C p.Ser784= | chr7:152248082 G>T | ENST00000262189.11 | synonymous_variant | 3.345 | 0 | 0.0003994 | - | **48.8%** |
| KMT2C chr7:152286325 A>G | chr7:152286325 A>G | ENST00000262189.11 | intron_variant | 19.78 | 0.1 | 0.0000 | - | **13.7%** |
| KMT2C chr7:152286324 C>T | chr7:152286324 C>T | ENST00000262189.11 | intron_variant | 17.49 | 0 | 0.0000 | - | **13.6%** |
| KMT2C chr7:152286348 C>T | chr7:152286348 C>T | ENST00000262189.11 | intron_variant | 17.74 | 0.02 | 0.0000 | - | **10.2%** |
| KMT2C chr7:152286393 A>G | chr7:152286393 A>G | ENST00000262189.11 | intron_variant | 18.11 | 0 | 0.0000 | - | **22.2%** |
| KMT2C chr7:152286407 A>G | chr7:152286407 A>G | ENST00000262189.11 | intron_variant | 17.88 | 0 | 0.0000 | - | **22.0%** |
| KMT2C chr7:152286435 T>C | chr7:152286435 T>C | ENST00000262189.11 | intron_variant | 15.37 | 0 | 0.0000 | - | **19.2%** |
| KMT2C chr7:152286471 A>G | chr7:152286471 A>G | ENST00000262189.11 | intron_variant | 16.00 | 0 | 0.0000 | - | **25.5%** |
| KMT2C chr7:152286493 A>G | chr7:152286493 A>G | ENST00000262189.11 | intron_variant | 14.12 | 0 | 0.0000 | - | **12.4%** |
| KMT2C chr7:152291406 G>A | chr7:152291406 G>A | ENST00000262189.11 | intron_variant | 11.14 | 0 | 0.0000 | - | **12.1%** |
| KMT2C chr7:152291760 C>T | chr7:152291760 C>T | ENST00000262189.11 | intron_variant | 11.78 | 0 | 0.0000 | - | **31.0%** |
| KMT2C chr7:152411203 T>G | chr7:152411203 T>G | ENST00000262189.11 | intron_variant | 11.25 | 0 | 0.0000 | - | **31.1%** |
| KMT2C chr7:152411205 A>ATATTTTTGTATC | chr7:152411205 A>ATATTTTTGTATC | ENST00000262189.11 | intron_variant | 12.26 | - | 0.0000 | - | **75.3%** |
| KMT2C chr7:152411453 C>A | chr7:152411453 C>A | ENST00000262189.11 | intron_variant | 10.93 | 0 | 0.0000 | - | **23.3%** |
| KMT2C chr7:152411534 G>C | chr7:152411534 G>C | ENST00000262189.11 | intron_variant | 14.17 | 0 | 0.0000 | - | **23.0%** |

#### 3.2.3 变异详细分析

##### 3.2.3.1 KMT2C p.Gln755Ter

###### 3.2.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152248171 G>A（GRCh38） |
| 测序等位基因比例 | **10.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 88 条 / 变异序列 10 条（合计 98 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 105 |
| 碱基质量指标 | QD（质量/深度）=0.38；FS（链偏倚）=21.887；MQ（比对质量）=46.27 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | 14/59 |

###### 3.2.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.2263C>T |
| HGVSp | p.Gln755Ter |
| VEP 后果 | stop_gained |
| VEP 影响等级 | HIGH |

###### 3.2.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 34 | > 20，高度可疑有害 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | HC | LoF 预测标记 |

###### 3.2.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | Pathogenic（criteria provided, single submitter，1 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PANTHER:PTHR45888 |
| 证据摘要 | ClinVar=pathogenic(base=40,star_factor=1.00,review_factor=1.00,benign_adjust_factor=1.00,score=40); consequence=stop_gained(+33); splice_lof=SpliceAI:0(+15); CADD=34(+12); domain(+3); total=+103 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.2 KMT2C p.Pro309Ser

###### 3.2.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152273792 G>A（GRCh38） |
| 测序等位基因比例 | **12.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 192 条 / 变异序列 28 条（合计 220 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 241 |
| 碱基质量指标 | QD（质量/深度）=0.87；FS（链偏倚）=25.812；MQ（比对质量）=46.66 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | 7/59 |

###### 3.2.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.925C>T |
| HGVSp | p.Pro309Ser |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 31 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.31 | acceptor_gain |
| REVEL | 0.562 | ≥ 0.5，可疑有害 |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | Uncertain significance（no assertion criteria provided，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PANTHER:PTHR45888,SMART:SM00249,CDD:cd15696,Gene3D:3.30.40.10,Pfam:PF13771,PROSITE_profiles:PS51805 |
| 证据摘要 | ClinVar=uncertain_significance(base=3,star_factor=1.00,review_factor=1.00,benign_adjust_factor=1.00,score=3); consequence=missense_variant(+15); splice_lof=SpliceAI:0.31(+10); REVEL=0.562(+8); CADD=31(+12); domain(+3); total=+51 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.3 KMT2C p.Tyr987His

###### 3.2.3.3.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152229940 A>G（GRCh38） |
| 测序等位基因比例 | **31.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 109 条 / 变异序列 50 条（合计 159 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 164 |
| 碱基质量指标 | QD（质量/深度）=5.64；FS（链偏倚）=1.392；MQ（比对质量）=45.42 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 18/59 |


###### 3.2.3.3.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.2959T>C |
| HGVSp | p.Tyr987His |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.3.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 25.2 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | 0.815 | ≥ 0.5，可疑有害 |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.3.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.3.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PANTHER:PTHR45888,SMART:SM00249,SMART:SM00184,CDD:cd15596,Gene3D:3.30.40.10,Pfam:PF00628,PROSITE_profiles:PS50016,Superfamily:SSF57903 |
| 证据摘要 | consequence=missense_variant(+15); REVEL=0.815(+12); CADD=25.2(+9); domain(+3); total=+39 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.3.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.4 KMT2C p.Gly315Cys

###### 3.2.3.4.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152273774 C>A（GRCh38） |
| 测序等位基因比例 | **15.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 201 条 / 变异序列 36 条（合计 237 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 274 |
| 碱基质量指标 | QD（质量/深度）=1.48；FS（链偏倚）=10.443；MQ（比对质量）=47.62 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | 7/59 |

###### 3.2.3.4.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.4.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.943G>T |
| HGVSp | p.Gly315Cys |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.4.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 27.0 | > 20，高度可疑有害 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | 0.768 | ≥ 0.5，可疑有害 |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.4.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.4.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PANTHER:PTHR45888,SMART:SM00249,CDD:cd15696,Gene3D:3.30.40.10,Pfam:PF13771,PROSITE_profiles:PS51805 |
| 证据摘要 | consequence=missense_variant(+15); REVEL=0.768(+12); CADD=27(+9); domain(+3); total=+39 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.4.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.5 KMT2C p.Gly838Ser

###### 3.2.3.5.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152247922 C>T（GRCh38） |
| 测序等位基因比例 | **51.9%**（基于测序 reads） |
| Reads 支持 | 参考序列 128 条 / 变异序列 138 条（合计 266 条 reads） |
| 测序深度 | 310 |
| 碱基质量指标 | QD（质量/深度）=12.42；FS（链偏倚）=2.505；MQ（比对质量）=51.66 |
| 外显子 | 14/59 |


###### 3.2.3.5.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.2512G>A |
| HGVSp | p.Gly838Ser |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.2.3.5.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 25.4 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | 0.448 | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.5.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.001701 |
| gnomAD Popmax AF | 0.006517 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.5.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PANTHER:PTHR45888,MobiDB_lite:mobidb-lite,MobiDB_lite:mobidb-lite |
| 证据摘要 | consequence=missense_variant(+15); REVEL=0.448(+3); CADD=25.4(+9); EAS_AF=0.001701; frequency(+3); domain(+3); total=+33 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.5.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.6 KMT2C p.Ser793=

###### 3.2.3.6.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152248055 C>T（GRCh38） |
| 测序等位基因比例 | **43.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 87 条 / 变异序列 67 条（合计 154 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 188 |
| 碱基质量指标 | QD（质量/深度）=10.22；FS（链偏倚）=0.565；MQ（比对质量）=52.78 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 14/59 |


###### 3.2.3.6.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.2379G>A |
| HGVSp | p.Ser793= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.2.3.6.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 7.062 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.6.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 8.961e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.6.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Low_complexity_(Seg):seg,PANTHER:PTHR45888,MobiDB_lite:mobidb-lite |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0; frequency(+10); domain(+3); total=+15 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.6.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.7 KMT2C p.Ser784=

###### 3.2.3.7.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152248082 G>T（GRCh38） |
| 测序等位基因比例 | **48.8%**（基于测序 reads） |
| Reads 支持 | 参考序列 64 条 / 变异序列 61 条（合计 125 条 reads） |
| 测序深度 | 140 |
| 碱基质量指标 | QD（质量/深度）=12.46；FS（链偏倚）=13.572；MQ（比对质量）=49.4 |
| 外显子 | 14/59 |


###### 3.2.3.7.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.2352C>A |
| HGVSp | p.Ser784= |
| VEP 后果 | synonymous_variant |
| VEP 影响等级 | LOW |

###### 3.2.3.7.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 3.345 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.7.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0003994 |
| gnomAD Popmax AF | 0.001375 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.7.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | Low_complexity_(Seg):seg,PANTHER:PTHR45888,MobiDB_lite:mobidb-lite,MobiDB_lite:mobidb-lite |
| 证据摘要 | consequence=synonymous_variant(+2); EAS_AF=0.0003994; frequency(+8); domain(+3); total=+13 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.7.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.8 KMT2C chr7:152286325 A>G

###### 3.2.3.8.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286325 A>G（GRCh38） |
| 测序等位基因比例 | **13.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 113 条 / 变异序列 18 条（合计 131 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 143 |
| 碱基质量指标 | QD（质量/深度）=3.1；FS（链偏倚）=2.843；MQ（比对质量）=45.72 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.2.3.8.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.8.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12458T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.8.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 19.78 | 需结合其他证据 |
| SpliceAI DS max | 0.1 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.8.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.004091 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.8.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); splice_lof=SpliceAI:0.1(+3); CADD=19.78(+2); EAS_AF=0; frequency(+10); total=+12 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.8.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.9 KMT2C chr7:152286324 C>T

###### 3.2.3.9.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286324 C>T（GRCh38） |
| 测序等位基因比例 | **13.6%**（基于测序 reads） |
| Reads 支持 | 参考序列 114 条 / 变异序列 18 条（合计 132 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 144 |
| 碱基质量指标 | QD（质量/深度）=3.06；FS（链偏倚）=2.854；MQ（比对质量）=45.73 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.2.3.9.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.9.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12457G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.9.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 17.49 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.9.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.003945 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.9.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=17.49(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.9.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.10 KMT2C chr7:152286348 C>T

###### 3.2.3.10.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286348 C>T（GRCh38） |
| 测序等位基因比例 | **10.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 158 条 / 变异序列 18 条（合计 176 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 199 |
| 碱基质量指标 | QD（质量/深度）=0.69；FS（链偏倚）=0；MQ（比对质量）=49.07 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.2.3.10.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.10.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12481G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.10.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 17.74 | 需结合其他证据 |
| SpliceAI DS max | 0.02 | donor_gain |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.10.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 2.41e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.10.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=17.74(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.10.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.11 KMT2C chr7:152286393 A>G

###### 3.2.3.11.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286393 A>G（GRCh38） |
| 测序等位基因比例 | **22.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 175 条 / 变异序列 50 条（合计 225 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 271 |
| 碱基质量指标 | QD（质量/深度）=6.68；FS（链偏倚）=0；MQ（比对质量）=51.93 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.11.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12526T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.11.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 18.11 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.11.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.007029 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.11.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=18.11(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.11.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.12 KMT2C chr7:152286407 A>G

###### 3.2.3.12.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286407 A>G（GRCh38） |
| 测序等位基因比例 | **22.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 181 条 / 变异序列 51 条（合计 232 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 280 |
| 碱基质量指标 | QD（质量/深度）=6.58；FS（链偏倚）=0.959；MQ（比对质量）=52.21 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.12.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12540T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.12.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 17.88 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.12.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.007044 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.12.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=17.88(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.12.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.13 KMT2C chr7:152286435 T>C

###### 3.2.3.13.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286435 T>C（GRCh38） |
| 测序等位基因比例 | **19.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 193 条 / 变异序列 46 条（合计 239 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 292 |
| 碱基质量指标 | QD（质量/深度）=2.42；FS（链偏倚）=5.896；MQ（比对质量）=52.14 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.2.3.13.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.13.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12568A>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.13.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 15.37 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.13.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 2.412e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.13.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=15.37(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.13.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.14 KMT2C chr7:152286471 A>G

###### 3.2.3.14.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286471 A>G（GRCh38） |
| 测序等位基因比例 | **25.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 158 条 / 变异序列 54 条（合计 212 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 259 |
| 碱基质量指标 | QD（质量/深度）=4.54；FS（链偏倚）=3.592；MQ（比对质量）=52.93 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.14.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12604T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.14.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 16.00 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.14.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.004415 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.14.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=16(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.14.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.15 KMT2C chr7:152286493 A>G

###### 3.2.3.15.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152286493 A>G（GRCh38） |
| 测序等位基因比例 | **12.4%**（基于测序 reads） |
| Reads 支持 | 参考序列 149 条 / 变异序列 21 条（合计 170 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 208 |
| 碱基质量指标 | QD（质量/深度）=0.5；FS（链偏倚）=8.633；MQ（比对质量）=52.8 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.2.3.15.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.15.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-12626T>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.15.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 14.12 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.15.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.002602 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.15.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=14.12(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.15.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.16 KMT2C chr7:152291406 G>A

###### 3.2.3.16.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152291406 G>A（GRCh38） |
| 测序等位基因比例 | **12.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 109 条 / 变异序列 15 条（合计 124 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 134 |
| 碱基质量指标 | QD（质量/深度）=0.77；FS（链偏倚）=0；MQ（比对质量）=42.13 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持；位点质量指标 QD 偏低 |
| 外显子 | - |

###### 3.2.3.16.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 假基因区域 | 命中假基因相关区域（-，来源 Reads_mapped） | 假基因区变异致病权重通常较低，避免误判为功能基因致病变异 |

###### 3.2.3.16.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-17539C>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.16.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 11.14 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.16.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0004878 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.16.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=11.14(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.16.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.17 KMT2C chr7:152291760 C>T

###### 3.2.3.17.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152291760 C>T（GRCh38） |
| 测序等位基因比例 | **31.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 129 条 / 变异序列 58 条（合计 187 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 197 |
| 碱基质量指标 | QD（质量/深度）=6.45；FS（链偏倚）=15.99；MQ（比对质量）=48.84 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.17.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.850-17893G>A |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.17.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 11.78 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.17.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 1.47e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.17.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=11.78(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.17.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.18 KMT2C chr7:152411203 T>G

###### 3.2.3.18.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152411203 T>G（GRCh38） |
| 测序等位基因比例 | **31.1%**（基于测序 reads） |
| Reads 支持 | 参考序列 104 条 / 变异序列 47 条（合计 151 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 196 |
| 碱基质量指标 | QD（质量/深度）=10.28；FS（链偏倚）=5.664；MQ（比对质量）=58.97 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.2.3.18.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 1 例，ALT 等位基因计数 1 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.2.3.18.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.161+24423A>C |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.18.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 11.25 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.18.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 9.846e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.18.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=11.25(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.18.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.19 KMT2C chr7:152411205 A>ATATTTTTGTATC

###### 3.2.3.19.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152411205 A>ATATTTTTGTATC（GRCh38） |
| 测序等位基因比例 | **75.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 36 条 / 变异序列 110 条（合计 146 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 195 |
| 碱基质量指标 | QD（质量/深度）=30.07；FS（链偏倚）=0.704；MQ（比对质量）=58.96 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.19.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.161+24420_161+24421insGATACAAAAATA |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.19.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 12.26 | 需结合其他证据 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.19.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.19.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=12.26(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.19.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.20 KMT2C chr7:152411453 C>A

###### 3.2.3.20.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152411453 C>A（GRCh38） |
| 测序等位基因比例 | **23.3%**（基于测序 reads） |
| Reads 支持 | 参考序列 171 条 / 变异序列 52 条（合计 223 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 258 |
| 碱基质量指标 | QD（质量/深度）=7.29；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.2.3.20.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.161+24173G>T |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.20.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 10.93 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.20.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 0.0000 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.20.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=10.93(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.20.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |

##### 3.2.3.21 KMT2C chr7:152411534 G>C

###### 3.2.3.21.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr7:152411534 G>C（GRCh38） |
| 测序等位基因比例 | **23.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 221 条 / 变异序列 66 条（合计 287 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 336 |
| 碱基质量指标 | QD（质量/深度）=3.06；FS（链偏倚）=4.659；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |

###### 3.2.3.21.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 调控元件 | 远端增强子样元件 (dELS)（重叠 1 个 cCRE） | 提示该变异可能影响顺式调控，非编码/深度内含子变异需重点评估 |

###### 3.2.3.21.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262189.11 |
| RefSeq | NM_170606.3 |
| HGVSc | c.161+24092C>G |
| HGVSp | - |
| VEP 后果 | intron_variant |
| VEP 影响等级 | MODIFIER |

###### 3.2.3.21.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 14.17 | 需结合其他证据 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | - | LoF 预测标记 |

###### 3.2.3.21.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0000 |
| gnomAD Popmax AF | 7.24e-05 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.2.3.21.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=intron_variant(-3); CADD=14.17(+2); EAS_AF=0; frequency(+10); total=+9 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.2.3.21.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |


#### 3.2.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 | Epigenetic regulation by WDR5-containing histone modifying complexes |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.2.5 严格筛选用药建议

经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.3 基因卡片 3：GJB2


#### 3.3.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | GJB2 |
| 染色体位置 | chr13:20189346（GRCh38） |
| 主要转录本 | NM_004004.6 |
| 基因功能 | This gene encodes a member of the gap junction protein family (gap junction beta 2) but is more commonly known as connexin 26. The gap junctions were first characterized by electron microscopy as regionally specialized structures on plasma membranes of contacting adherent cells. These structures were shown to consist of cell-to-cell channels that facilitate the transfer of ions and small molecules between cells. Connexins form hexameric channels in the plasma membrane which regulate passage of ions and small molecules between the cell and its environment or, when joined with another cell, form a dodecameric intercellular gap junction channel. The connexin proteins are grouped into alpha, beta, and gamma subfamilies. Mutations in this gene are responsible for as much as 50% of pre-lingual, recessive deafness. [provided by RefSeq, Mar 2026] |
| 遗传模式 | Bart-Pumphrey syndrome (Autosomal dominant); Deafness, autosomal dominant 3A (Autosomal dominant); Deafness, autosomal recessive 1A (AR, DD); Hystrix-like ichthyosis with deafness (Autosomal dominant); Keratitis-ichthyosis-deafness syndrome (Autosomal dominant); Keratoderma, palmoplantar, with deafness (Autosomal dominant); Vohwinkel syndrome (Autosomal dominant) |
| 主要关联表型 | palmoplantar keratoderma-deafness syndrome; keratoderma hereditarium mutilans |
| 主要关联通路 | Gap junction assembly |
| 致病性排名 | #10 |

#### 3.3.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| GJB2 p.Leu79CysfsTer3 | chr13:20189346 AG>A | ENST00000382848.5 | frameshift_variant | 34 | - | 0.008677 | Pathogenic | **47.7%** |
| GJB2 p.Val37Ile | chr13:20189473 C>T | ENST00000382848.5 | missense_variant | 20.4 | 0 | 0.0448809 | Pathogenic | **58.5%** |

#### 3.3.3 变异详细分析

##### 3.3.3.1 GJB2 p.Leu79CysfsTer3

###### 3.3.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr13:20189346 AG>A（GRCh38） |
| 测序等位基因比例 | **47.7%**（基于测序 reads） |
| Reads 支持 | 参考序列 23 条 / 变异序列 21 条（合计 44 条 reads） |
| 测序深度 | 55 |
| 碱基质量指标 | QD（质量/深度）=13.79；FS（链偏倚）=7.906；MQ（比对质量）=60 |
| 外显子 | 2/2 |

###### 3.3.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 6 例，ALT 等位基因计数 6 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000296095（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.3.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000382848.5 |
| RefSeq | NM_004004.6 |
| HGVSc | c.235del |
| HGVSp | p.Leu79CysfsTer3 |
| VEP 后果 | frameshift_variant |
| VEP 影响等级 | HIGH |

###### 3.3.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 34 | > 20，高度可疑有害 |
| SpliceAI DS max | - | 无显著剪接影响 |
| REVEL | - | - |
| LOFTEE | LC | LoF 预测标记 |

###### 3.3.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.008677 |
| gnomAD Popmax AF | 0.008677 |
| gnomAD 纯合数 | - |
| ClinVar | Pathogenic（reviewed by expert panel，3 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:2zw3.A,PDB-ENSP_mappings:2zw3.B,PDB-ENSP_mappings:2zw3.C,PDB-ENSP_mappings:2zw3.D,PDB-ENSP_mappings:2zw3.E,PDB-ENSP_mappings:2zw3.F,PDB-ENSP_mappings:3iz1.A,PDB-ENSP_mappings:3iz1.B,PDB-ENSP_mappings:3iz1.C,PDB-ENSP_mappings:3iz2.A,PDB-ENSP_mappings:3iz2.B,PDB-ENSP_mappings:3iz2.C,PDB-ENSP_mappings:5er7.A,PDB-ENSP_mappings:5er7.B,PDB-ENSP_mappings:5era.A,PDB-ENSP_mappings:5era.B,PDB-ENSP_mappings:6uvr.A,PDB-ENSP_mappings:6uvr.B,PDB-ENSP_mappings:6uvr.C,PDB-ENSP_mappings:6uvr.D,PDB-ENSP_mappings:6uvr.E,PDB-ENSP_mappings:6uvr.F,PDB-ENSP_mappings:6uvr.G,PDB-ENSP_mappings:6uvr.H,PDB-ENSP_mappings:6uvr.I,PDB-ENSP_mappings:6uvr.J,PDB-ENSP_mappings:6uvr.K,PDB-ENSP_mappings:6uvr.L,PDB-ENSP_mappings:6uvs.A,PDB-ENSP_mappings:6uvs.B,PDB-ENSP_mappings:6uvs.C,PDB-ENSP_mappings:6uvs.D,PDB-ENSP_mappings:6uvs.E,PDB-ENSP_mappings:6uvs.F,PDB-ENSP_mappings:6uvs.G,PDB-ENSP_mappings:6uvs.H,PDB-ENSP_mappings:6uvs.I,PDB-ENSP_mappings:6uvs.J,PDB-ENSP_mappings:6uvs.K,PDB-ENSP_mappings:6uvs.L,PDB-ENSP_mappings:6uvt.A,PDB-ENSP_mappings:6uvt.B,PDB-ENSP_mappings:6uvt.C,PDB-ENSP_mappings:6uvt.D,PDB-ENSP_mappings:6uvt.E,PDB-ENSP_mappings:6uvt.F,PDB-ENSP_mappings:6uvt.G,PDB-ENSP_mappings:6uvt.H,PDB-ENSP_mappings:6uvt.I,PDB-ENSP_mappings:6uvt.J,PDB-ENSP_mappings:6uvt.K,PDB-ENSP_mappings:6uvt.L,PDB-ENSP_mappings:7qeo.A,PDB-ENSP_mappings:7qeo.B,PDB-ENSP_mappings:7qeq.A,PDB-ENSP_mappings:7qeq.B,PDB-ENSP_mappings:7qeq.C,PDB-ENSP_mappings:7qeq.D,PDB-ENSP_mappings:7qeq.E,PDB-ENSP_mappings:7qeq.F,PDB-ENSP_mappings:7qeq.G,PDB-ENSP_mappings:7qeq.H,PDB-ENSP_mappings:7qeq.I,PDB-ENSP_mappings:7qeq.J,PDB-ENSP_mappings:7qeq.K,PDB-ENSP_mappings:7qeq.L,PDB-ENSP_mappings:7qer.A,PDB-ENSP_mappings:7qer.B,PDB-ENSP_mappings:7qer.C,PDB-ENSP_mappings:7qer.D,PDB-ENSP_mappings:7qer.E,PDB-ENSP_mappings:7qer.F,PDB-ENSP_mappings:7qer.G,PDB-ENSP_mappings:7qer.H,PDB-ENSP_mappings:7qer.I,PDB-ENSP_mappings:7qer.J,PDB-ENSP_mappings:7qer.K,PDB-ENSP_mappings:7qer.L,PDB-ENSP_mappings:7qes.A,PDB-ENSP_mappings:7qes.B,PDB-ENSP_mappings:7qet.A,PDB-ENSP_mappings:7qet.B,PDB-ENSP_mappings:7qet.C,PDB-ENSP_mappings:7qet.D,PDB-ENSP_mappings:7qet.E,PDB-ENSP_mappings:7qet.F,PDB-ENSP_mappings:7qet.G,PDB-ENSP_mappings:7qet.H,PDB-ENSP_mappings:7qet.I,PDB-ENSP_mappings:7qet.J,PDB-ENSP_mappings:7qet.K,PDB-ENSP_mappings:7qet.L,PDB-ENSP_mappings:7qeu.A,PDB-ENSP_mappings:7qeu.B,PDB-ENSP_mappings:7qev.A,PDB-ENSP_mappings:7qev.B,PDB-ENSP_mappings:7qew.G,PDB-ENSP_mappings:7qew.H,PDB-ENSP_mappings:7qew.I,PDB-ENSP_mappings:7qew.J,PDB-ENSP_mappings:7qew.K,PDB-ENSP_mappings:7qew.L,PDB-ENSP_mappings:7qey.G,PDB-ENSP_mappings:7qey.H,PDB-ENSP_mappings:7qey.I,PDB-ENSP_mappings:7qey.J,PDB-ENSP_mappings:7qey.K,PDB-ENSP_mappings:7qey.L,PDB-ENSP_mappings:8q9z.A,PDB-ENSP_mappings:8q9z.B,PDB-ENSP_mappings:8q9z.C,PDB-ENSP_mappings:8q9z.D,PDB-ENSP_mappings:8q9z.E,PDB-ENSP_mappings:8q9z.F,PDB-ENSP_mappings:8q9z.G,PDB-ENSP_mappings:8q9z.H,PDB-ENSP_mappings:8q9z.I,PDB-ENSP_mappings:8q9z.J,PDB-ENSP_mappings:8q9z.K,PDB-ENSP_mappings:8q9z.L,PDB-ENSP_mappings:8qa0.A,PDB-ENSP_mappings:8qa0.B,PDB-ENSP_mappings:8qa0.C,PDB-ENSP_mappings:8qa0.D,PDB-ENSP_mappings:8qa0.E,PDB-ENSP_mappings:8qa0.F,PDB-ENSP_mappings:8qa0.G,PDB-ENSP_mappings:8qa0.H,PDB-ENSP_mappings:8qa0.I,PDB-ENSP_mappings:8qa0.J,PDB-ENSP_mappings:8qa0.K,PDB-ENSP_mappings:8qa0.L,PDB-ENSP_mappings:8qa1.A,PDB-ENSP_mappings:8qa1.B,PDB-ENSP_mappings:8qa1.C,PDB-ENSP_mappings:8qa1.D,PDB-ENSP_mappings:8qa1.E,PDB-ENSP_mappings:8qa1.F,PDB-ENSP_mappings:8qa1.G,PDB-ENSP_mappings:8qa1.H,PDB-ENSP_mappings:8qa1.I,PDB-ENSP_mappings:8qa1.J,PDB-ENSP_mappings:8qa1.K,PDB-ENSP_mappings:8qa1.L,PDB-ENSP_mappings:8qa2.A,PDB-ENSP_mappings:8qa2.B,PDB-ENSP_mappings:8qa2.C,PDB-ENSP_mappings:8qa2.D,PDB-ENSP_mappings:8qa2.E,PDB-ENSP_mappings:8qa2.F,PDB-ENSP_mappings:8qa2.G,PDB-ENSP_mappings:8qa2.H,PDB-ENSP_mappings:8qa2.I,PDB-ENSP_mappings:8qa2.J,PDB-ENSP_mappings:8qa2.K,PDB-ENSP_mappings:8qa2.L,PDB-ENSP_mappings:8qa3.A,PDB-ENSP_mappings:8qa3.B,PDB-ENSP_mappings:8qa3.C,PDB-ENSP_mappings:8qa3.D,PDB-ENSP_mappings:8qa3.E,PDB-ENSP_mappings:8qa3.F,PDB-ENSP_mappings:8qa3.G,PDB-ENSP_mappings:8qa3.H,PDB-ENSP_mappings:8qa3.I,PDB-ENSP_mappings:8qa3.J,PDB-ENSP_mappings:8qa3.K,PDB-ENSP_mappings:8qa3.L,PANTHER:PTHR11984,Pfam:PF00029,Gene3D:1.20.1440.80,Prints:PR00206,Phobius:TRANSMEMBRANE,Transmembrane_helices:TMhelix,AFDB-ENSP_mappings:AF-P29033-F1 |
| 证据摘要 | ClinVar=pathogenic(base=40,star_factor=1.15,review_factor=1.15,benign_adjust_factor=1.00,score=53); consequence=frameshift_variant(+33); splice_lof=SpliceAI:unknown(-8); CADD=34(+12); EAS_AF=0.008677; frequency(+3); domain(+3); total=+96 |
| 治疗意义 | 严格筛选后暂无符合标准的用药候选。当前管理以对症支持治疗与遗传咨询为主：听力损失需耳鼻喉科评估并考虑助听器/人工耳蜗干预；低磷血症及骨骼异常建议内分泌/骨科专科随访。建议对家系成员进行级联遗传检测与生育咨询。 |

###### 3.3.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42278361 | Connexin 26 in Hearing Health and Disease: Structural Foundations, Mutation Mechanisms, and Therapeutic Perspectives. | Qiu W; Schneider K; Guo Y - Int J Mol Sci, 2026 | 综述 GJB2/Cx26 的蛋白结构、突变致病机制及治疗前景；强调 Cx26 是遗传性耳聋最常见的致病基因，涵盖现有治疗策略与未来方向。 | PubMed 文献检索，综述类 |
| 42235969 | Genetic and Congenital Cytomegalovirus-Related Hearing Loss in Children: Volumetric MRI Analysis of Auditory and Visual Cortices. | Hiremath SB; Wagner M; Cushing SL; Gordon KA; Bitnun A; Amirabadi A; Vidarsson H; Ertl-Wagner BB - AJNR Am J Neuroradiol, 2026 | 对比 GJB2 相关与先天性巨细胞病毒相关听力损失的脑皮层结构差异，支持 GJB2 突变在感音神经性聋病因学中的核心地位。 | PubMed 文献检索，原创研究 |
| 42216359 | Prevalence of GJB2 gene mutations in nonsyndromic hearing impairments: A systematic review and meta-analysis. | Feng R; Mangantig E; Wan Yusoff WSY; Li H; Li X; Abu MN - Medicine (Baltimore), 2026 | 系统综述和 meta 分析全球 GJB2 突变在非综合征性听力障碍中的患病率及热点变异分布，提示 c.235del 与 c.109G>A 等变异在不同人群中的检出意义。 | PubMed 文献检索，系统综述/meta 分析 |

##### 3.3.3.2 GJB2 p.Val37Ile

###### 3.3.3.2.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr13:20189473 C>T（GRCh38） |
| 测序等位基因比例 | **58.5%**（基于测序 reads） |
| Reads 支持 | 参考序列 17 条 / 变异序列 24 条（合计 41 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 49 |
| 碱基质量指标 | QD（质量/深度）=15.43；FS（链偏倚）=8.761；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | 2/2 |

###### 3.3.3.2.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 变异相位 | 已完成相位推断，置信度高 | 可用于复合杂合/顺反式判断，建议结合家系样本确认 |
| 中国参考人群 | 携带该 ALT 约 57 例，ALT 等位基因计数 61 | 补充 gnomAD 之外的本国参考人群携带信息 |
| 非编码 RNA | ENSG00000296095（lncRNA） | 变异位于非编码 RNA 基因区域，需结合功能注释谨慎解读 |

###### 3.3.3.2.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000382848.5 |
| RefSeq | NM_004004.6 |
| HGVSc | c.109G>A |
| HGVSp | p.Val37Ile |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.3.3.2.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 20.4 | > 20，高度可疑有害 |
| SpliceAI DS max | 0 | 无显著剪接影响 |
| REVEL | 0.656 | ≥ 0.5，可疑有害 |
| LOFTEE | - | LoF 预测标记 |

###### 3.3.3.2.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0448809 |
| gnomAD Popmax AF | 0.0448809 |
| gnomAD 纯合数 | 101 |
| ClinVar | Pathogenic（reviewed by expert panel，3 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.3.3.2.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:2zw3.A,PDB-ENSP_mappings:2zw3.B,PDB-ENSP_mappings:2zw3.C,PDB-ENSP_mappings:2zw3.D,PDB-ENSP_mappings:2zw3.E,PDB-ENSP_mappings:2zw3.F,PDB-ENSP_mappings:3iz1.A,PDB-ENSP_mappings:3iz1.B,PDB-ENSP_mappings:3iz1.C,PDB-ENSP_mappings:3iz2.A,PDB-ENSP_mappings:3iz2.B,PDB-ENSP_mappings:3iz2.C,PDB-ENSP_mappings:5er7.A,PDB-ENSP_mappings:5er7.B,PDB-ENSP_mappings:5era.A,PDB-ENSP_mappings:5era.B,PDB-ENSP_mappings:6uvr.A,PDB-ENSP_mappings:6uvr.B,PDB-ENSP_mappings:6uvr.C,PDB-ENSP_mappings:6uvr.D,PDB-ENSP_mappings:6uvr.E,PDB-ENSP_mappings:6uvr.F,PDB-ENSP_mappings:6uvr.G,PDB-ENSP_mappings:6uvr.H,PDB-ENSP_mappings:6uvr.I,PDB-ENSP_mappings:6uvr.J,PDB-ENSP_mappings:6uvr.K,PDB-ENSP_mappings:6uvr.L,PDB-ENSP_mappings:6uvs.A,PDB-ENSP_mappings:6uvs.B,PDB-ENSP_mappings:6uvs.C,PDB-ENSP_mappings:6uvs.D,PDB-ENSP_mappings:6uvs.E,PDB-ENSP_mappings:6uvs.F,PDB-ENSP_mappings:6uvs.G,PDB-ENSP_mappings:6uvs.H,PDB-ENSP_mappings:6uvs.I,PDB-ENSP_mappings:6uvs.J,PDB-ENSP_mappings:6uvs.K,PDB-ENSP_mappings:6uvs.L,PDB-ENSP_mappings:6uvt.A,PDB-ENSP_mappings:6uvt.B,PDB-ENSP_mappings:6uvt.C,PDB-ENSP_mappings:6uvt.D,PDB-ENSP_mappings:6uvt.E,PDB-ENSP_mappings:6uvt.F,PDB-ENSP_mappings:6uvt.G,PDB-ENSP_mappings:6uvt.H,PDB-ENSP_mappings:6uvt.I,PDB-ENSP_mappings:6uvt.J,PDB-ENSP_mappings:6uvt.K,PDB-ENSP_mappings:6uvt.L,PDB-ENSP_mappings:7qeo.A,PDB-ENSP_mappings:7qeo.B,PDB-ENSP_mappings:7qeq.A,PDB-ENSP_mappings:7qeq.B,PDB-ENSP_mappings:7qeq.C,PDB-ENSP_mappings:7qeq.D,PDB-ENSP_mappings:7qeq.E,PDB-ENSP_mappings:7qeq.F,PDB-ENSP_mappings:7qeq.G,PDB-ENSP_mappings:7qeq.H,PDB-ENSP_mappings:7qeq.I,PDB-ENSP_mappings:7qeq.J,PDB-ENSP_mappings:7qeq.K,PDB-ENSP_mappings:7qeq.L,PDB-ENSP_mappings:7qer.A,PDB-ENSP_mappings:7qer.B,PDB-ENSP_mappings:7qer.C,PDB-ENSP_mappings:7qer.D,PDB-ENSP_mappings:7qer.E,PDB-ENSP_mappings:7qer.F,PDB-ENSP_mappings:7qer.G,PDB-ENSP_mappings:7qer.H,PDB-ENSP_mappings:7qer.I,PDB-ENSP_mappings:7qer.J,PDB-ENSP_mappings:7qer.K,PDB-ENSP_mappings:7qer.L,PDB-ENSP_mappings:7qes.A,PDB-ENSP_mappings:7qes.B,PDB-ENSP_mappings:7qet.A,PDB-ENSP_mappings:7qet.B,PDB-ENSP_mappings:7qet.C,PDB-ENSP_mappings:7qet.D,PDB-ENSP_mappings:7qet.E,PDB-ENSP_mappings:7qet.F,PDB-ENSP_mappings:7qet.G,PDB-ENSP_mappings:7qet.H,PDB-ENSP_mappings:7qet.I,PDB-ENSP_mappings:7qet.J,PDB-ENSP_mappings:7qet.K,PDB-ENSP_mappings:7qet.L,PDB-ENSP_mappings:7qeu.A,PDB-ENSP_mappings:7qeu.B,PDB-ENSP_mappings:7qev.A,PDB-ENSP_mappings:7qev.B,PDB-ENSP_mappings:7qew.G,PDB-ENSP_mappings:7qew.H,PDB-ENSP_mappings:7qew.I,PDB-ENSP_mappings:7qew.J,PDB-ENSP_mappings:7qew.K,PDB-ENSP_mappings:7qew.L,PDB-ENSP_mappings:7qey.G,PDB-ENSP_mappings:7qey.H,PDB-ENSP_mappings:7qey.I,PDB-ENSP_mappings:7qey.J,PDB-ENSP_mappings:7qey.K,PDB-ENSP_mappings:7qey.L,PDB-ENSP_mappings:8q9z.A,PDB-ENSP_mappings:8q9z.B,PDB-ENSP_mappings:8q9z.C,PDB-ENSP_mappings:8q9z.D,PDB-ENSP_mappings:8q9z.E,PDB-ENSP_mappings:8q9z.F,PDB-ENSP_mappings:8q9z.G,PDB-ENSP_mappings:8q9z.H,PDB-ENSP_mappings:8q9z.I,PDB-ENSP_mappings:8q9z.J,PDB-ENSP_mappings:8q9z.K,PDB-ENSP_mappings:8q9z.L,PDB-ENSP_mappings:8qa0.A,PDB-ENSP_mappings:8qa0.B,PDB-ENSP_mappings:8qa0.C,PDB-ENSP_mappings:8qa0.D,PDB-ENSP_mappings:8qa0.E,PDB-ENSP_mappings:8qa0.F,PDB-ENSP_mappings:8qa0.G,PDB-ENSP_mappings:8qa0.H,PDB-ENSP_mappings:8qa0.I,PDB-ENSP_mappings:8qa0.J,PDB-ENSP_mappings:8qa0.K,PDB-ENSP_mappings:8qa0.L,PDB-ENSP_mappings:8qa1.A,PDB-ENSP_mappings:8qa1.B,PDB-ENSP_mappings:8qa1.C,PDB-ENSP_mappings:8qa1.D,PDB-ENSP_mappings:8qa1.E,PDB-ENSP_mappings:8qa1.F,PDB-ENSP_mappings:8qa1.G,PDB-ENSP_mappings:8qa1.H,PDB-ENSP_mappings:8qa1.I,PDB-ENSP_mappings:8qa1.J,PDB-ENSP_mappings:8qa1.K,PDB-ENSP_mappings:8qa1.L,PDB-ENSP_mappings:8qa2.A,PDB-ENSP_mappings:8qa2.B,PDB-ENSP_mappings:8qa2.C,PDB-ENSP_mappings:8qa2.D,PDB-ENSP_mappings:8qa2.E,PDB-ENSP_mappings:8qa2.F,PDB-ENSP_mappings:8qa2.G,PDB-ENSP_mappings:8qa2.H,PDB-ENSP_mappings:8qa2.I,PDB-ENSP_mappings:8qa2.J,PDB-ENSP_mappings:8qa2.K,PDB-ENSP_mappings:8qa2.L,PDB-ENSP_mappings:8qa3.A,PDB-ENSP_mappings:8qa3.B,PDB-ENSP_mappings:8qa3.C,PDB-ENSP_mappings:8qa3.D,PDB-ENSP_mappings:8qa3.E,PDB-ENSP_mappings:8qa3.F,PDB-ENSP_mappings:8qa3.G,PDB-ENSP_mappings:8qa3.H,PDB-ENSP_mappings:8qa3.I,PDB-ENSP_mappings:8qa3.J,PDB-ENSP_mappings:8qa3.K,PDB-ENSP_mappings:8qa3.L,PANTHER:PTHR11984,Pfam:PF00029,Gene3D:1.20.1440.80,Prints:PR00206,Phobius:TRANSMEMBRANE,Transmembrane_helices:TMhelix,AFDB-ENSP_mappings:AF-P29033-F1 |
| 证据摘要 | ClinVar=pathogenic(base=40,star_factor=1.15,review_factor=1.15,benign_adjust_factor=1.00,score=53); consequence=missense_variant(+15); REVEL=0.656(+8); CADD=20.4(+6); EAS_AF=4.488090e-02; frequency(-30); domain(+3); total=+55 |
| 治疗意义 | 严格筛选后暂无符合标准的用药候选。当前管理以对症支持治疗与遗传咨询为主：听力损失需耳鼻喉科评估并考虑助听器/人工耳蜗干预；低磷血症及骨骼异常建议内分泌/骨科专科随访。建议对家系成员进行级联遗传检测与生育咨询。 |

###### 3.3.3.2.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 42278361 | Connexin 26 in Hearing Health and Disease: Structural Foundations, Mutation Mechanisms, and Therapeutic Perspectives. | Qiu W; Schneider K; Guo Y - Int J Mol Sci, 2026 | 综述 GJB2/Cx26 的蛋白结构、突变致病机制及治疗前景；强调 Cx26 是遗传性耳聋最常见的致病基因，涵盖现有治疗策略与未来方向。 | PubMed 文献检索，综述类 |
| 42235969 | Genetic and Congenital Cytomegalovirus-Related Hearing Loss in Children: Volumetric MRI Analysis of Auditory and Visual Cortices. | Hiremath SB; Wagner M; Cushing SL; Gordon KA; Bitnun A; Amirabadi A; Vidarsson H; Ertl-Wagner BB - AJNR Am J Neuroradiol, 2026 | 对比 GJB2 相关与先天性巨细胞病毒相关听力损失的脑皮层结构差异，支持 GJB2 突变在感音神经性聋病因学中的核心地位。 | PubMed 文献检索，原创研究 |
| 42216359 | Prevalence of GJB2 gene mutations in nonsyndromic hearing impairments: A systematic review and meta-analysis. | Feng R; Mangantig E; Wan Yusoff WSY; Li H; Li X; Abu MN - Medicine (Baltimore), 2026 | 系统综述和 meta 分析全球 GJB2 突变在非综合征性听力障碍中的患病率及热点变异分布，提示 c.235del 与 c.109G>A 等变异在不同人群中的检出意义。 | PubMed 文献检索，系统综述/meta 分析 |


#### 3.3.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 | palmoplantar keratoderma-deafness syndrome; keratoderma hereditarium mutilans (Open Targets); autosomal dominant nonsyndromic hearing loss 3A; autosomal dominant keratitis-ichthyosis-hearing loss syndrome; Bart-Pumphrey syndrome (OMIM/GeneDisease associations, score ≥0.79) |
| 关联通路 | Gap junction assembly |
| 临床建议 | 样本检出 GJB2 双等位基因复合变异：chr13:20189346 c.235del（p.Leu79CysfsTer3，移码截断，ClinVar=Pathogenic，CADD=34，reads VAF≈47.7%）与 chr13:20189473 c.109G>A（p.Val37Ile，错义，ClinVar=Pathogenic，CADD=20.4，reads VAF≈58.5%）。相位推断已完成且置信度高，提示可能处于顺式或反式；结合 GATK AF 均为 0.5，高度提示复合杂合可能。GJB2 已知为遗传性耳聋首要致病基因，主要引起非综合征性/综合征性感音神经性聋，与本例 HPO 中听力障碍（HP:0002148）一致。然而，患儿的重度矮小、漏斗胸、肋外翻、右脚内翻、爬楼梯困难及低磷、低碳酸氢根等骨骼/代谢表现，并非 GJB2 经典表型范畴；HPO 条目（HP:0000767、HP:0000887、HP:0002148、HP:0003510、HP:0003551、HP:0025802、HP:0032066、HP:5200134）需结合完整 HPO 命名进一步评估是否存在表型扩展或合并其他致病机制。建议补充家系验证、耳科专科评估及骨骼/代谢病因鉴别。 |

#### 3.3.5 严格筛选用药建议

经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.4 基因卡片 4：SLC4A1


#### 3.4.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | SLC4A1 |
| 染色体位置 | chr17:44253327（GRCh38） |
| 主要转录本 | NM_000342.4 |
| 基因功能 | The protein encoded by this gene is part of the anion exchanger (AE) family and is expressed in the erythrocyte plasma membrane, where it functions as a chloride/bicarbonate exchanger involved in carbon dioxide transport from tissues to lungs. The protein comprises two domains that are structurally and functionally distinct. The N-terminal 40kDa domain is located in the cytoplasm and acts as an attachment site for the red cell skeleton by binding ankyrin. The glycosylated C-terminal membrane-associated domain contains 12-14 membrane spanning segments and carries out the stilbene disulphonate-sensitive exchange transport of anions. The cytoplasmic tail at the extreme C-terminus of the membrane domain binds carbonic anhydrase II. The encoded protein associates with the red cell membrane protein glycophorin A and this association promotes the correct folding and translocation of the exchanger. This protein is predominantly dimeric but forms tetramers in the presence of ankyrin. Many mutations in this gene are known in man, and these mutations can lead to two types of disease: destabilization of red cell membrane leading to hereditary spherocytosis, and defective kidney acid secretion leading to distal renal tubular acidosis. Other mutations that do not give rise to disease result in novel blood group antigens, which form the Diego blood group system. Southeast Asian ovalocytosis (SAO, Melanesian ovalocytosis) results from the heterozygous presence of a deletion in the encoded protein and is common in areas where Plasmodium falciparum malaria is endemic. One null mutation in this gene is known, resulting in very severe anemia and nephrocalcinosis. [provided by RefSeq, Jul 2008] |
| 遗传模式 |  |
| 主要关联表型 | hereditary spherocytosis type 4; autosomal dominant distal renal tubular acidosis |
| 主要关联通路 | - |
| 致病性排名 | #15 |

#### 3.4.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| SLC4A1 p.Gly701Asp | chr17:44253327 C>T | ENST00000262418.12 | missense_variant | 28.2 | 0.01 | 0.000267404 | Pathogenic/Likely pathogenic | **100.0%** |

#### 3.4.3 变异详细分析

##### 3.4.3.1 SLC4A1 p.Gly701Asp

###### 3.4.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr17:44253327 C>T（GRCh38） |
| 测序等位基因比例 | **100.0%**（基于测序 reads） |
| Reads 支持 | 参考序列 0 条 / 变异序列 30 条（合计 30 条 reads） |
| 测序深度 | 38 |
| 碱基质量指标 | QD（质量/深度）=30.1；FS（链偏倚）=0；MQ（比对质量）=60 |
| 外显子 | 17/20 |

###### 3.4.3.1.1b 基因组注释与人群上下文

| 维度 | 结果 | 解读提示 |
|------|------|----------|
| 中国参考人群 | 携带该 ALT 约 3 例，ALT 等位基因计数 3 | 补充 gnomAD 之外的本国参考人群携带信息 |

###### 3.4.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000262418.12 |
| RefSeq | NM_000342.4 |
| HGVSc | c.2102G>A |
| HGVSp | p.Gly701Asp |
| VEP 后果 | missense_variant |
| VEP 影响等级 | MODERATE |

###### 3.4.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 28.2 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.01 | donor_gain |
| REVEL | 0.923 | ≥ 0.5，可疑有害 |
| LOFTEE | - | LoF 预测标记 |

###### 3.4.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.000267404 |
| gnomAD Popmax AF | 0.000267404 |
| gnomAD 纯合数 | 0 |
| ClinVar | Pathogenic/Likely pathogenic（criteria provided, multiple submitters, no conflicts，2 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.4.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | PDB-ENSP_mappings:4yzf.A,PDB-ENSP_mappings:4yzf.B,PDB-ENSP_mappings:4yzf.C,PDB-ENSP_mappings:4yzf.D,PDB-ENSP_mappings:7tvz.A,PDB-ENSP_mappings:7tvz.B,PDB-ENSP_mappings:7tw0.A,PDB-ENSP_mappings:7tw0.B,PDB-ENSP_mappings:7tw1.A,PDB-ENSP_mappings:7tw1.B,PDB-ENSP_mappings:7tw2.A,PDB-ENSP_mappings:7tw2.B,PDB-ENSP_mappings:7tw3.A,PDB-ENSP_mappings:7tw3.B,PDB-ENSP_mappings:7tw5.A,PDB-ENSP_mappings:7tw5.B,PDB-ENSP_mappings:7tw6.A,PDB-ENSP_mappings:7tw6.B,PDB-ENSP_mappings:7tw6.J,PDB-ENSP_mappings:7tw6.K,PDB-ENSP_mappings:7ty4.A,PDB-ENSP_mappings:7ty4.B,PDB-ENSP_mappings:7ty6.A,PDB-ENSP_mappings:7ty6.B,PDB-ENSP_mappings:7ty7.A,PDB-ENSP_mappings:7ty7.B,PDB-ENSP_mappings:7ty8.A,PDB-ENSP_mappings:7ty8.B,PDB-ENSP_mappings:7tya.A,PDB-ENSP_mappings:7tya.B,PDB-ENSP_mappings:7uz3.C,PDB-ENSP_mappings:7uz3.E,PDB-ENSP_mappings:7uzu.W,PDB-ENSP_mappings:7uzv.C,PDB-ENSP_mappings:7uzv.E,PDB-ENSP_mappings:7v07.C,PDB-ENSP_mappings:7v07.E,PDB-ENSP_mappings:7v0k.O,PDB-ENSP_mappings:7v0k.P,PDB-ENSP_mappings:7v0k.W,PDB-ENSP_mappings:7v0m.W,PDB-ENSP_mappings:7v0t.C,PDB-ENSP_mappings:7v0t.E,PDB-ENSP_mappings:7v0u.D,PDB-ENSP_mappings:7v0u.F,PDB-ENSP_mappings:7v0y.C,PDB-ENSP_mappings:7v0y.E,PDB-ENSP_mappings:7v19.C,PDB-ENSP_mappings:7v19.E,PDB-ENSP_mappings:8crq.C,PDB-ENSP_mappings:8crq.E,PDB-ENSP_mappings:8crr.C,PDB-ENSP_mappings:8crr.E,PDB-ENSP_mappings:8crt.C,PDB-ENSP_mappings:8crt.E,PDB-ENSP_mappings:8cs9.V,PDB-ENSP_mappings:8cs9.Y,PDB-ENSP_mappings:8cs9.Z,PDB-ENSP_mappings:8cs9.e,PDB-ENSP_mappings:8cs9.f,PDB-ENSP_mappings:8cs9.g,PDB-ENSP_mappings:8csl.V,PDB-ENSP_mappings:8csl.W,PDB-ENSP_mappings:8csl.Y,PDB-ENSP_mappings:8csl.Z,PDB-ENSP_mappings:8csl.e,PDB-ENSP_mappings:8csl.f,PDB-ENSP_mappings:8csl.g,PDB-ENSP_mappings:8csv.W,PDB-ENSP_mappings:8csy.C,PDB-ENSP_mappings:8csy.E,PDB-ENSP_mappings:8ct3.C,PDB-ENSP_mappings:8ct3.E,PDB-ENSP_mappings:8cte.P,PDB-ENSP_mappings:8cte.T,PDB-ENSP_mappings:8cte.W,PDB-ENSP_mappings:8t3r.A,PDB-ENSP_mappings:8t3r.B,PDB-ENSP_mappings:8t3u.A,PDB-ENSP_mappings:8t3u.B,PDB-ENSP_mappings:8t44.A,PDB-ENSP_mappings:8t44.B,PDB-ENSP_mappings:8t45.A,PDB-ENSP_mappings:8t45.B,PDB-ENSP_mappings:8t47.A,PDB-ENSP_mappings:8t47.B,PDB-ENSP_mappings:8t6u.A,PDB-ENSP_mappings:8t6u.B,PDB-ENSP_mappings:8t6v.A,PDB-ENSP_mappings:8t6v.B,Phobius:TRANSMEMBRANE,Prints:PR01231,PANTHER:PTHR11453,NCBIFAM:TIGR00834,Pfam:PF00955,Transmembrane_helices:TMhelix,AFDB-ENSP_mappings:AF-P02730-F1 |
| 证据摘要 | ClinVar=pathogenic/likely_pathogenic(base=35,star_factor=1.10,review_factor=1.10,benign_adjust_factor=1.00,score=42); consequence=missense_variant(+15); REVEL=0.923(+15); CADD=28.2(+9); EAS_AF=2.674040e-04; frequency(+8); domain(+3); total=+92 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.4.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |


#### 3.4.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.4.5 严格筛选用药建议

经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。

| 药物 | 适应症 | 临床阶段 | 证据等级 | 匹配依据 | 注意事项 |
|------|--------|----------|----------|----------|----------|
| - | - | - | - | 暂无通过严格筛选的候选 | 请以遗传咨询、对症与支持治疗为主 |


---

### 3.5 基因卡片 5：FER1L6


#### 3.5.1 基因概述

| 属性 | 内容 |
|------|------|
| 基因名 | FER1L6 |
| 染色体位置 | chr8:123970098（GRCh38） |
| 主要转录本 | NM_001039112.2 |
| 基因功能 | Predicted to enable metal ion binding activity. Predicted to be involved in positive regulation of gene expression. Predicted to act upstream of or within response to bacterium. Predicted to be located in membrane. [provided by Alliance of Genome Resources, Jul 2025] |
| 遗传模式 |  |
| 主要关联表型 | atrioventricular block; diverticulitis |
| 主要关联通路 | - |
| 致病性排名 | #16 |

#### 3.5.2 变异列表

| 变异 | 坐标（GRCh38） | 转录本 | 后果 | CADD | SpliceAI DS max | gnomAD AF | ClinVar | 测序比例 |
|------|----------------|--------|------|------|-----------------|-----------|---------|-----|
| FER1L6 chr8:123970098 G>A | chr8:123970098 G>A | ENST00000522917.5 | splice_donor_variant | 34 | 0.98 | 0.0001928 | - | **32.2%** |

#### 3.5.3 变异详细分析

##### 3.5.3.1 FER1L6 chr8:123970098 G>A

###### 3.5.3.1.1 基因组与测序质量

| 属性 | 内容 |
|------|------|
| 基因组坐标 | chr8:123970098 G>A（GRCh38） |
| 测序等位基因比例 | **32.2%**（基于测序 reads） |
| Reads 支持 | 参考序列 40 条 / 变异序列 19 条（合计 59 条 reads） |
| GATK 基因型 AF | 50.0% |
| 测序深度 | 63 |
| 碱基质量指标 | QD（质量/深度）=6.6；FS（链偏倚）=0；MQ（比对质量）=60 |
| 解读提示 | 测序 reads 比例与 GATK 基因型 AF 不一致，解读时优先参考 reads 支持 |
| 外显子 | - |


###### 3.5.3.1.2 转录本与功能影响

| 属性 | 内容 |
|------|------|
| 转录本 | ENST00000522917.5 |
| RefSeq | NM_001039112.2 |
| HGVSc | c.447+1G>A |
| HGVSp | - |
| VEP 后果 | splice_donor_variant |
| VEP 影响等级 | HIGH |

###### 3.5.3.1.3 预测工具评分

| 工具 | 值 | 解读 |
|------|-----|------|
| CADD | 34 | > 20，高度可疑有害 |
| SpliceAI DS max | 0.98 | donor_loss |
| REVEL | - | - |
| LOFTEE | HC | LoF 预测标记 |

###### 3.5.3.1.4 人群频率与数据库证据

| 数据库 | 结果 |
|--------|------|
| gnomAD EAS AF | 0.0001928 |
| gnomAD Popmax AF | 0.001451 |
| gnomAD 纯合数 | - |
| ClinVar | -（-，0 星） |
| 临床相关表达组织 | -（TPM -） |
| GTEx Top5 | - |

###### 3.5.3.1.5 蛋白质结构域与功能影响

| 属性 | 内容 |
|------|------|
| 蛋白结构域 | - |
| 证据摘要 | consequence=splice_donor_variant(+33); splice_lof=SpliceAI:0.98(+37); CADD=34(+12); EAS_AF=0.0001928; frequency(+8); total=+90 |
| 治疗意义 | 经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。 |

###### 3.5.3.1.6 文献证据

| PMID | 标题 | 作者/期刊/年份 | 一句话摘要 | 证据等级 |
|------|------|----------------|------------|----------|
| 待 Agent 补充 | - | - | - | - |


#### 3.5.4 基因-表型-通路关联解读

| 维度 | 内容 |
|------|------|
| 关联表型 |  |
| 关联通路 |  |
| 临床建议 | 结合临床表型与家系信息进一步评估 |

#### 3.5.5 严格筛选用药建议

经严格筛选（基因-疾病关联 + 样本临床/HPO 表型 + 临床阶段 + 作用机制），暂无符合标准的用药建议；请以对症/支持治疗与遗传咨询为主。

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
排序宽表输出（/mnt/workspace/lixinhang/code/search_agent/test_data/test_case/case_v3_26B03419791/vep_output.with_info.ranked_large.top10000.csv）
    ↓
本报告渲染（v1.1 结构）
```

### 4.2 数据质量说明

| 项目 | 状态 |
|------|------|
| 样本编号 | 26B03419791 |
| VCF 路径 | 未提供 |
| Liftover 输出 | 未提供 |
| 比对参考基因组 | GRCh38 |
| 宽表总行数 | 注释展开行（含多转录本） |
| 去重后变异数 | 3897 |
| 注释基因数 | 1795 |
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
| 未进入 Top 5 的基因 | 宽表共注释 1795 个基因，其中 1790 个未纳入本报告 Top 列表；可应要求扩展分析 |
| 总变异位点数 | 去重后共 3897 个变异位点 |
| 拷贝数变异（CNV） | 当前输入为 SNV/Indel 排序宽表，未包含 CNV 信息 |
| 融合基因 | 未纳入本次 SNV/Indel 宽表分析范围 |
| 非编码区 / 深度内含子变异 | 默认过滤阈值以外区域未重点解读 |

---

## 7. 临床建议摘要（遗传咨询师视角）

### 7.1 立即建议


### 7.2 动态监测


### 7.3 患者/家属沟通要点


### 7.4 严格筛选用药与试验团队（摘要）

**CFTR**
- IVACAFTOR：cystic fibrosis（APPROVAL，证据 strong）
- LUMACAFTOR：cystic fibrosis（APPROVAL，证据 strong）
- TEZACAFTOR：cystic fibrosis（APPROVAL，证据 strong）


---

## 8. 报告输出元信息（ReportOutput）

```json
{
  "report_version": "v1.1",
  "report_title": "26B03419791 基因组变异分析报告",
  "gene_count": 5,
  "variant_count": 28,
  "top_genes": [
    "CFTR",
    "KMT2C",
    "GJB2",
    "SLC4A1",
    "FER1L6"
  ],
  "output_path": "/mnt/workspace/lixinhang/code/search_agent/test_data/test_case/case_v3_26B03419791/report.md",
  "literature_strategy": "precomputed_plus_online_fallback",
  "disclaimer_included": true
}
```

---

*报告结束。变异注释数值以排序宽表为准；叙事性解读需经临床遗传学专家复核。*