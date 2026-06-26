"""OpenRare Gateway — single public entry point that launches each module as a
subprocess in its own pixi environment, then dispatches routes and orchestrates
cross-module data flow over local HTTP.

Pattern adapted from my-backend-project_v2 (verified with pixi 0.68).

Why a gateway: each module lives in its own pixi environment with independent
dependency solving. They CANNOT be imported into one Python process. So each
runs as its own uvicorn, and the gateway is the public entry point.

No shell scripts — pure Python subprocess, cross-platform.
"""

from __future__ import annotations

import asyncio
import atexit
import contextlib
import subprocess
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response

from pydantic import BaseModel


# ── Locate repo root ──────────────────────────────────────────────────

def find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "pixi.toml").exists():
            return p
    raise RuntimeError(f"pixi.toml not found above {start}")


REPO_ROOT = find_root(Path(__file__).resolve())

# ── Module registry ───────────────────────────────────────────────────
# Each module defines how it's launched inside its own pixi environment.
# "cmd" uses pixi run -m <manifest> -- <cmd...> (uvicorn directly). This
# lets the gateway control the port, avoiding macOS AirPlay conflicts.
# "task" uses pixi run -m <manifest> <task> for complex modules that need
# shell-script setup (pipeline, phenotype_score).

MODULES = {
    "RAG-HPO": {
        "manifest": "modules/pixi_RAG-HPO/pixi.toml",
        "port": 8001,
        "health": "/api/v1/health",
        "cmd": ["uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8001"],
        "cwd": "modules/pixi_RAG-HPO/src",
    },
    "pipeline": {
        "manifest": "modules/pipeline/pixi.toml",
        "port": 8002,
        "health": "/health",
        "task": "api",
    },
    "phenotype_score": {
        "manifest": "modules/pixi_phenotype_score/pixi.toml",
        "port": 8003,
        "health": "/health",
        "task": "serve",
    },
    "ppi_score": {
        "manifest": "modules/pixi_ppi_score/pixi.toml",
        "port": 8004,
        "health": "/health",
        "cmd": ["uvicorn", "app.api:app", "--host", "127.0.0.1", "--port", "8004"],
        "cwd": "modules/pixi_ppi_score",
        "env": {"PYTHONPATH": "app"},
    },
    "rare_sort": {
        "manifest": "modules/pixi_rare_sort_fastapi/pixi.toml",
        "port": 8005,
        "health": "/jobs",
        "cmd": ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8005"],
        "cwd": "modules/pixi_rare_sort_fastapi",
    },
    "report": {
        "manifest": "modules/pixi_report/pixi.toml",
        "port": 8006,
        "health": "/health",
        "cmd": ["uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8006"],
        "cwd": "modules/pixi_report",
    },
    "RareSystem": {
        "manifest": "modules/RareSystem/pixi.toml",
        "port": 8007,
        "health": "/api/health",
        "cmd": ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8007"],
        "cwd": "modules/RareSystem/backend",
    },
}

_procs: dict[str, subprocess.Popen] = {}
_dead: set[str] = set()  # modules whose process exited non-zero during startup

# ── Process lifecycle ─────────────────────────────────────────────────


def start_module(name: str, cfg: dict) -> None:
    manifest = REPO_ROOT / cfg["manifest"]
    if not manifest.exists():
        print(f"[gateway] SKIP {name}: manifest not found ({cfg['manifest']})", flush=True)
        return
    print(f"[gateway] starting {name} (port {cfg['port']})...", flush=True)

    if "task" in cfg:
        _procs[name] = subprocess.Popen(
            ["pixi", "run", "-m", str(manifest), cfg["task"]],
            cwd=REPO_ROOT, stderr=subprocess.DEVNULL,
        )
    else:
        cmd = [
            "pixi", "run", "-m", str(manifest), "--",
        ] + cfg["cmd"]
        cwd = REPO_ROOT / cfg.get("cwd", ".")
        env = {**__import__("os").environ}
        if cfg.get("env"):
            env.update(cfg["env"])
        _procs[name] = subprocess.Popen(cmd, cwd=cwd, env=env, stderr=subprocess.DEVNULL)

    # Quick detect: if the process exits within 3s, mark it dead
    try:
        rc = _procs[name].wait(timeout=3.0)
        if rc != 0:
            print(f"[gateway] {name} exited early (code {rc}) — skipped", flush=True)
            _dead.add(name)
            del _procs[name]
    except subprocess.TimeoutExpired:
        pass  # still running, good


def start_modules() -> None:
    for name, cfg in MODULES.items():
        start_module(name, cfg)


def stop_modules() -> None:
    for name, p in list(_procs.items()):
        if p.poll() is None:
            print(f"[gateway] stopping {name}", flush=True)
            p.terminate()
    for p in _procs.values():
        with contextlib.suppress(Exception):
            p.wait(timeout=10)
    _procs.clear()
    _dead.clear()


atexit.register(stop_modules)


async def wait_healthy(timeout: float = 60.0) -> list[str]:
    """Wait for live modules to respond. Skips dead/never-started modules."""
    ready: list[str] = []
    async with httpx.AsyncClient() as client:
        for name, cfg in MODULES.items():
            if name in _dead or name not in _procs:
                print(f"[gateway] {name} not running — skipped", flush=True)
                continue
            url = f"http://127.0.0.1:{cfg['port']}{cfg['health']}"
            ok = False
            for _ in range(int(timeout * 2)):
                proc = _procs.get(name)
                if proc and proc.poll() is not None:
                    print(f"[gateway] {name} exited during health check", flush=True)
                    break
                with contextlib.suppress(httpx.HTTPError):
                    resp = await client.get(url, timeout=1.0)
                    if resp.status_code < 500:
                        print(f"[gateway] {name} healthy", flush=True)
                        ready.append(name)
                        ok = True
                        break
                await asyncio.sleep(0.5)
            if not ok:
                print(f"[gateway] WARN {name} not healthy within {timeout}s", flush=True)
    return ready


# ── FastAPI app with lifespan ─────────────────────────────────────────


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    start_modules()
    ready = await wait_healthy()
    app.state.ready_modules = ready
    app.state.client = httpx.AsyncClient(timeout=120.0)
    print(f"[gateway] ready on http://0.0.0.0:8000 — {len(ready)}/{len(MODULES)} modules up", flush=True)
    yield
    await app.state.client.aclose()
    stop_modules()


app = FastAPI(title="OpenRare Gateway", version="0.1.0", lifespan=lifespan)

# ── Health ────────────────────────────────────────────────────────────


class ModuleStatus(BaseModel):
    port: int
    running: bool


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "modules": {
            name: ModuleStatus(port=cfg["port"], running=name in app.state.ready_modules)
            for name, cfg in MODULES.items()
        },
    }


# ── Transparent dispatch: /m/<module>/<path> → module's /<path> ─────


@app.api_route("/m/{module}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatch(module: str, path: str, request: Request):
    if module not in MODULES:
        raise HTTPException(status_code=404, detail=f"unknown module: {module}")
    if module not in app.state.ready_modules:
        raise HTTPException(status_code=503, detail=f"module '{module}' is not running")

    cfg = MODULES[module]
    try:
        upstream = await app.state.client.request(
            request.method,
            f"http://127.0.0.1:{cfg['port']}/{path}",
            content=await request.body(),
            headers={"content-type": request.headers.get("content-type", "application/json")},
            timeout=60.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"upstream error: {exc}")

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )


# ── Pipeline orchestration placeholder ────────────────────────────────
# Add cross-module pipelines here as POST endpoints, e.g.:
#   rare_sort → phenotype_score → ppi_score → report


@app.get("/pipeline/status")
async def pipeline_status():
    """Return which modules are ready and their ports."""
    return {
        "ready": sorted(app.state.ready_modules),
        "ports": {name: cfg["port"] for name, cfg in MODULES.items()},
    }


# ── Entry point ───────────────────────────────────────────────────────


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
