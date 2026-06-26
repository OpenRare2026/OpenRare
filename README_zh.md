# OpenRare 
![last commit](https://img.shields.io/badge/last_commit-2026.06.26-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)
![Badge](https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FOpenRare2026%2FOpenRare&label=Visitors&icon=github&color=%23198754&message=&style=flat&tz=UTC)


<div align="center">
  <img src="./OpenRare.JPG" alt="OpenRare 标志" width="500">
</div>

[🇨🇳 中文版本](README_zh.md) | [🇬🇧 English Version](README.md)

---

## OpenRare 罕见病 Agent

**面向罕见病变异优先级排序的可解释 AI 系统**

Rare Disease Agent 是一个面向罕见病诊断场景的开源基因分析系统。

我们的目标不是替代临床医生进行诊断，而是帮助医生在海量基因变异中更高效地发现最有可能解释患者表型的候选致病变异，并提供可追溯、可解释、可审计的证据链。

系统融合患者临床表现、基因测序数据、生物医学知识库以及 AI Agent 技术，构建从症状理解、变异注释、致病性排序到报告生成的完整分析流程。

---

## 环境配置（Pixi）

在仓库根目录安装一次，统一管理各模块：

```bash
cp modules/pipeline/.env.example modules/pipeline/.env   # 配置外部数据路径
pixi install
pixi run pipeline-test    # 或 pixi run api
```

常用任务（根目录 `pixi.toml`）：

| 任务 | 说明 |
|------|------|
| `pipeline-test` | 完整流程冒烟测试 |
| `api` | 启动 Full Pipeline API |
| `api-test` | API 集成测试 |
| `vep-dry-run` | VEP 配置 dry-run |
| `vep-setup-plugins` / `vep-verify-plugins` | VEP 插件安装与校验 |

也可仅在 pipeline 子目录内开发：`cd modules/pipeline && pixi install && pixi run pipeline-test`。
PPI 模块可独立运行：`cd modules/pixi_ppi_score && pixi install && pixi run serve`。

## Pipeline 模块

主流程代码位于 [`modules/pipeline/`](modules/pipeline/README.md)。详见 [modules/pipeline/README.md](modules/pipeline/README.md)。  

## 表型关联模块
表型关联评分模块代码位于[`modules/pixi_phenotype_score`](modules/pixi_phenotype_score/README.md)。详见 [modules/pixi_phenotype_score/README.md](modules/pixi_phenotype_score/README.md)。

## PPI 评分模块

PPI 评分服务位于 [`modules/pixi_ppi_score/`](modules/pixi_ppi_score/README.md)，支持 phenotype-gene CSV、VEP CSV 和 HPO 输入，输出 PPI 评分表与融合后的 final score。

## 报告生成模块

基因组变异分析报告服务位于 [`modules/pixi_report/`](modules/pixi_report/README.md)，基于排序宽表、临床表型与 HPO 术语，通过 FastAPI 流式或命令行生成可追溯的分析报告。
