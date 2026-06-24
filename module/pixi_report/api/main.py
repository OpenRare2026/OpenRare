"""Genome report HTTP API (FastAPI).

启动服务（在 module/pix_report 目录）::

    pixi install
    cp .env.example .env   # 配置 LLM / Open Targets MCP 等

    pixi run api

或::

    pixi run python -m api.main

接口：
    GET  /health              健康检查
    POST /report/stream       SSE 流式生成报告
    GET  /report/{run_id}/md  下载 report.md

交互式文档：http://127.0.0.1:8800/docs
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from agent.config import PROJECT_ROOT
from api.schemas import HealthResponse, ReportStreamRequest
from api.service import OUTPUT_ROOT, stream_report_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Genome Report API",
    version="0.1.0",
    description=(
        "从宽表 + phenotype.csv + hpo_terms.txt 流式生成基因组变异分析报告。"
        " 启动：`pixi run api`"
    ),
)


def _resolve_input_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _validate_input_paths(request: ReportStreamRequest) -> None:
    missing: list[str] = []
    for label, path_str in (
        ("wide_path", request.wide_path),
        ("phenotype_path", request.phenotype_path),
        ("hpo_path", request.hpo_path),
    ):
        if not _resolve_input_path(path_str).is_file():
            missing.append(f"{label}: {path_str}")
    # if request.ppi_path.strip() and not Path(request.ppi_path).is_file():
    #     missing.append(f"ppi_path: {request.ppi_path}")
    if missing:
        raise HTTPException(
            status_code=400,
            detail={"message": "Input file(s) not found", "missing": missing},
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/report/stream")
async def report_stream(request: ReportStreamRequest) -> EventSourceResponse:
    _validate_input_paths(request)
    logger.info(
        "POST /report/stream top_n=%d sample_paths ok",
        request.top_n,
    )

    async def event_generator():
        try:
            async for event in stream_report_events(
                wide_path=str(_resolve_input_path(request.wide_path)),
                phenotype_path=str(_resolve_input_path(request.phenotype_path)),
                hpo_path=str(_resolve_input_path(request.hpo_path)),
                ppi_path=str(_resolve_input_path(request.ppi_path))
                if request.ppi_path.strip()
                else "",
                top_n=request.top_n,
            ):
                yield {"data": json.dumps(event, ensure_ascii=False)}
        except Exception as exc:
            logger.exception("report stream failed")
            yield {
                "data": json.dumps(
                    {"type": "error", "message": str(exc)},
                    ensure_ascii=False,
                )
            }

    return EventSourceResponse(event_generator())


@app.get("/report/{run_id}/md")
async def download_report_md(run_id: str) -> FileResponse:
    if not run_id.isalnum():
        raise HTTPException(status_code=400, detail="Invalid run_id")

    md_path = OUTPUT_ROOT / run_id / "report.md"
    if not md_path.is_file():
        raise HTTPException(status_code=404, detail="Markdown report not found")

    return FileResponse(
        md_path,
        media_type="text/markdown; charset=utf-8",
        filename=f"report_{run_id}.md",
    )


def main() -> None:
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8800, reload=False)


if __name__ == "__main__":
    main()
