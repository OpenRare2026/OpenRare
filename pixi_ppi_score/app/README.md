# app 代码目录

这里放 FastAPI 服务和 PPI 评分核心代码。一般用户不需要从本目录直接启动。

推荐入口：

```bash
cd ..
pixi install
pixi run serve
```

主要文件：

| 文件 | 说明 |
| --- | --- |
| `api.py` | FastAPI 接口，包含 `/health`、`/score`、`/score/clean-case` 等路由。 |
| `Network.py` | PPI 网络加载、锚点构建和评分逻辑。 |
| `config.py` | 默认数据路径和运行参数模型。 |
| `run_clean_case.py` | phenotype + VEP + HPO 的最终病例融合流程。 |
| `download_data.sh` | 参考数据下载脚本。 |
| `prepare_gtex_v11.py` | GTEx v11 预处理脚本。 |

完整使用说明见上一级 `README.md` 和仓库根目录 `README.md`。
