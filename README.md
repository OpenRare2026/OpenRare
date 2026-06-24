# OpenRare

罕见病变异注释与排序 monorepo。

## Pipeline 模块

主流程代码位于 [`modules/pipeline/`](modules/pipeline/README.md)：

```bash
cd modules/pipeline
cp .env.example .env   # 配置外部数据路径
pixi install
pixi run pipeline-test
```

详见 [modules/pipeline/README.md](modules/pipeline/README.md)。
