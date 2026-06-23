# 依赖说明

依赖来自当前 `app/requirements.txt` 和 `app/*.py` 的实际 import。
Pixi 配置文件为 `pixi.toml`，解析后的锁文件为 `pixi.lock`。

## 运行依赖

| 包 | 用途 |
| --- | --- |
| `python >=3.10,<3.12` | 与旧服务 Python 3.10 兼容；当前 Pixi 锁定 Python 3.11。 |
| `numpy` | 数值计算。 |
| `pandas >=2.3,<3` | CSV 分块读取、聚合和表格输出；锁在 3 以下以规避 Pandas 3.x 大 VEP CSV 分块读取问题。 |
| `networkx` | STRING PPI 网络构建和路径计算。 |
| `scipy` | 科学计算辅助。 |
| `pydantic >=2` | 请求模型和参数校验。 |
| `fastapi` | HTTP API 服务。 |
| `uvicorn` | ASGI 服务启动器。 |
| `python-multipart` | 表单和文件上传接口。 |
| `owlready2` | HPO OWL 解析。 |

## 文件

| 文件 | 说明 |
| --- | --- |
| `pixi.toml` | 人维护的 Pixi 依赖和任务定义。 |
| `pixi.lock` | Pixi 解析后的稳定环境版本。 |
| `requirements.txt` | 便于人工查看的依赖摘要。 |
| `app/requirements.txt` | 当前服务代码旁保留的原始依赖列表。 |

大型参考数据不进入 Pixi 环境，也不提交到 GitHub。
