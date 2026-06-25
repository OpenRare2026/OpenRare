# OpenRare

罕见病变异注释与排序 monorepo。

## 环境（Pixi）

在仓库根目录安装一次，统一管理各 module：

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

## PPI 评分模块

PPI 评分服务位于 [`modules/pixi_ppi_score/`](modules/pixi_ppi_score/README.md)，支持 phenotype-gene CSV、VEP CSV 和 HPO 输入，输出 PPI 评分表与融合后的 final score。
