"""Gateway: one public service that supervises the module subprocesses and
orchestrates the cross-module data flow.

Why a gateway instead of one merged app: module-a (py3.8) and module-b (py3.12)
live in different pixi environments with possibly conflicting dependencies, so
they CANNOT be imported into a single Python process. Each module therefore runs
as its own uvicorn process in its own environment, and this gateway is the single
public entry point that routes / chains requests to them over local HTTP.

No shell scripts are used: subprocesses are launched with a list of args and
shell=False (the default), which behaves identically on Linux / macOS / Windows.
"""
import asyncio
import atexit
import contextlib
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response

from contracts.schemas import AInput, AOutput, BInput, BOutput


def find_root(start: Path) -> Path:
    """Walk up until the workspace pixi.toml is found (cross-platform)."""
    for p in [start, *start.parents]:
        if (p / "pixi.toml").exists():
            return p
    raise RuntimeError("pixi.toml not found above %s" % start)


REPO_ROOT = find_root(Path(__file__).resolve())

# Single source of truth for orchestration: name -> (pixi env, internal port, ASGI app)
MODULES = {
    "module-a": {"env": "module-a", "port": 8001, "app": "module_a.main:app"},
    "module-b": {"env": "module-b", "port": 8002, "app": "module_b.main:app"},
}

_procs: "dict[str, subprocess.Popen]" = {}


def start_modules() -> None:
    for name, cfg in MODULES.items():
        print(f">> starting {name} (env={cfg['env']}, port={cfg['port']})", flush=True)
        _procs[name] = subprocess.Popen(
            [
                "pixi", "run", "-e", cfg["env"],
                "uvicorn", cfg["app"],
                "--host", "127.0.0.1", "--port", str(cfg["port"]),
            ],
            cwd=REPO_ROOT,  # so the nested `pixi run` resolves this workspace
        )


def stop_modules() -> None:
    for name, p in _procs.items():
        if p.poll() is None:
            print(f">> stopping {name}", flush=True)
            p.terminate()  # SIGTERM on Unix, TerminateProcess on Windows
    for p in _procs.values():
        with contextlib.suppress(Exception):
            p.wait(timeout=10)
    _procs.clear()


# Belt-and-suspenders: clean up children even on an unexpected exit.
atexit.register(stop_modules)


async def wait_healthy() -> None:
    async with httpx.AsyncClient() as client:
        for name, cfg in MODULES.items():
            url = f"http://127.0.0.1:{cfg['port']}/health"
            for _ in range(120):  # up to ~60s
                with contextlib.suppress(httpx.HTTPError):
                    resp = await client.get(url, timeout=1.0)
                    if resp.status_code == 200:
                        print(f">> {name} healthy", flush=True)
                        break
                await asyncio.sleep(0.5)
            else:
                raise RuntimeError(f"{name} did not become healthy in time")


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_modules()
    await wait_healthy()
    app.state.client = httpx.AsyncClient(timeout=60.0)
    print(">> gateway ready on http://0.0.0.0:8000", flush=True)
    yield
    await app.state.client.aclose()
    stop_modules()


app = FastAPI(title="my-backend-project gateway", lifespan=lifespan)


async def _call(module: str, path: str, model) -> dict:
    """POST a pydantic model to a module and return the parsed JSON body."""
    cfg = MODULES[module]
    r = await app.state.client.post(
        f"http://127.0.0.1:{cfg['port']}{path}", json=model.model_dump()
    )
    r.raise_for_status()
    return r.json()


@app.get("/health")
async def health():
    return {"status": "ok", "modules": list(MODULES)}


# ---- Transparent dispatch: /m/<module>/<path>  ->  that module's /<path> ----
@app.api_route("/m/{module}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dispatch(module: str, path: str, request: Request):
    if module not in MODULES:
        raise HTTPException(status_code=404, detail=f"unknown module: {module}")
    cfg = MODULES[module]
    upstream = await app.state.client.request(
        request.method,
        f"http://127.0.0.1:{cfg['port']}/{path}",
        content=await request.body(),
        headers={"content-type": request.headers.get("content-type", "application/json")},
    )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )


# ---- Orchestration: module-a's OUTPUT becomes module-b's INPUT ----
# This is where you encode "whose output feeds into which module as input".
# model_validate() fails fast if a module's output violates the next contract.
@app.post("/pipeline/forecast", response_model=BOutput)
async def forecast(payload: AInput) -> BOutput:
    a_out = AOutput.model_validate(await _call("module-a", "/process", payload))
    b_in = BInput(series=a_out.cleaned, window=3)   # <-- transform / wiring logic
    b_out = BOutput.model_validate(await _call("module-b", "/process", b_in))
    return b_out


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
