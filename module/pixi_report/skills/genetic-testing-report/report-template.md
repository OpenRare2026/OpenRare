# 临床单基因遗传病基因检测报告

> 标准：T/SZGIA 4-2018《临床单基因遗传病基因检测报告规范》
> 报告编号：{{report_id}}　　报告日期：{{report_date}}

---

## 一、检测机构信息

| 项目 | 内容 |
| ---- | ---- |
| 机构名称 | {{institution.name}} |
| 地址 | {{institution.address}} |
| 联系电话 | {{institution.phone}} |
| 实验室资质 | {{institution.lab_license}} |

---

## 二、受检者信息

| 项目 | 内容 |
| ---- | ---- |
| 姓名 | {{subject.name}} |
| 性别 | {{subject.sex}} |
| 出生日期 | {{subject.date_of_birth}} |
| 临床指征 | {{subject.clinical_indication}} |
| 主要症状 | {{subject.symptoms}} |
| 发病年龄 | {{subject.age_of_onset}} |
| 临床拟诊 | {{subject.provisional_diagnosis}} |
| 家族史 | {{subject.family_history}} |

---

## 三、送检信息

| 项目 | 内容 |
| ---- | ---- |
| 送检单位 | {{referring.institution}} |
| 送检科室 | {{referring.department}} |
| 送检医师 | {{referring.physician_name}} |

---

## 四、样本信息

| 项目 | 内容 |
| ---- | ---- |
| 样本类型 | {{sample.sample_type}} |
| 采样日期 | {{sample.collection_date}} |
| 收样日期 | {{sample.receipt_date}} |

---

## 五、检测项目与方法

| 项目 | 内容 |
| ---- | ---- |
| 检测项目 | {{test.test_name}} |
| 检测方法 | {{test.method_summary}} |
| 检测基因 | {{test.genes_tested}} |

---

## 六、检测结果

| 基因 | 转录本 | 核苷酸改变 | 氨基酸改变 | 基因型 | 变异来源 | 人群频率 | ACMG分类 | 证据 |
| ---- | ------ | ---------- | ---------- | ------ | -------- | -------- | -------- | ---- |
| {{variant.gene}} | {{variant.transcript}} | {{variant.hgvs_c}} | {{variant.hgvs_p}} | {{variant.genotype}} | {{variant.inheritance_origin}} | {{variant.allele_frequency}} | {{variant.classification}} | {{variant.acmg_evidence}} |

> 注：仅列出与受检者临床指征相关或需报告的变异。

---

## 七、检测结论

{{conclusion}}

---

## 八、结果解释

{{interpretation}}

---

## 九、建议

{{#each recommendations}}
- {{this}}
{{/each}}

---

## 十、参考文献

{{#each references}}
[{{@index}}] {{citation}} {{#if pmid}}PMID: {{pmid}}{{/if}}
{{/each}}

---

## 附录：检测方法说明与局限性

### 检测方法

{{method_limitations.method_description}}

### 局限性

{{#each method_limitations.limitations}}
- {{this}}
{{/each}}

---

## 签名

| 角色 | 姓名 | 日期 |
| ---- | ---- | ---- |
| 检验者 | {{signatures.author}} | |
| 核对者 | {{signatures.reviewer}} | |
| 签发者 | {{signatures.approver}} | |

（检测报告专用章）

---

*本报告仅对送检样本负责，结果需结合临床由遗传咨询医师或临床医师综合判断。*
