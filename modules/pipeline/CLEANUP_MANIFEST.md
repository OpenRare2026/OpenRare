# pipeline cleanup manifest

记录 API 启动与目录迁移相关说明。

## API 启动

```bash
cd modules/pipeline
FULL_PIPELINE_API_PORT=18901 pixi run api
```

或：

```bash
bash modules/pipeline/scripts/start_full_pipeline_api.sh
```

## 目录说明

- **模块根**：`modules/pipeline/`（`pixi.toml`、`.env`）
- **CLI 入口**：`scripts/run_full_pipeline.sh`
- **API 服务**：`complete_pipeline/full_pipeline_api.py`
- **API 任务**：`complete_pipeline/api_jobs/`（默认，可 `FULL_PIPELINE_API_JOBS_DIR` 覆盖）
