# my-backend-project

A monorepo of independent FastAPI modules, each in its **own isolated pixi
environment** (so they can use conflicting dependencies — even different Python
versions), fronted by a single **gateway** service that dispatches routes and
orchestrates the cross-module data flow.

```
my-backend-project/
├── pixi.toml                     # one workspace, one isolated env per module
├── packages/contracts/           # shared pydantic I/O schemas (pydantic-only)
├── modules/
│   ├── module-a/                 # Python 3.8  FastAPI  -> 127.0.0.1:8001
│   └── module-b/                 # Python 3.12 FastAPI  -> 127.0.0.1:8002
└── gateway/                      # public service       -> 0.0.0.0:8000
```

- **module-a** runs on **Python 3.8**, **module-b** on **Python 3.12**.
- Each `pixi` environment uses `no-default-feature = true`, so nothing leaks
  between modules. Conflicting deps are fine: each env is solved independently.
- The gateway is the ONLY public entry point. Internally it launches each module
  as its own `uvicorn` subprocess (pure Python `subprocess`, **no shell scripts**,
  cross-platform) and talks to them over local HTTP with `httpx`.

## Prerequisites

Install pixi: https://pixi.prefix.dev/latest/installation/

## Quick Start (verified on macOS arm64, pixi 0.68.1; Linux / Windows workflow identical)

```bash
# 1. Install all three isolated environments (first time also generates pixi.lock)
pixi install -e module-a -e module-b -e orchestrator

# 2. Ensure port 8000 is free (the gateway binds to 0.0.0.0:8000)
#    macOS / Linux:
lsof -ti :8000 | xargs kill -9 2>/dev/null
#    Windows (PowerShell):
#    netstat -ano | findstr :8000          # find the PID
#    taskkill /PID <pid> /F                # kill it

# 3. Start everything with a single command
pixi run -e orchestrator up
```

Startup output should show:
```
>> starting module-a (env=module-a, port=8001)
>> starting module-b (env=module-b, port=8002)
>> module-a healthy
>> module-b healthy
>> gateway ready on http://0.0.0.0:8000
```

Then verify:
```bash
curl -s localhost:8000/m/module-a/process \
  -H 'content-type: application/json' \
  -d '{"raw": [1.0, 2.0, 3.0, 4.0]}'
# → {"cleaned":[1.0,2.0,3.0,4.0],"meta":{"count":4.0,"mean":2.5}}

curl -s localhost:8000/pipeline/forecast \
  -H 'content-type: application/json' \
  -d '{"raw": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]}'
# → {"forecast":[5.0,5.0,5.0]}
```

Press Ctrl-C to stop — all child processes are terminated automatically.

Interactive API docs (the single public surface): http://localhost:8000/docs

## Where to add things

- **A new module**: create `modules/module-x/` (mirroring module-a), add a
  `[feature.module-x.*]` block + an `environments` entry in `pixi.toml`, then
  register it in `gateway/src/gateway/main.py` -> `MODULES`.
- **A new data-flow / pipeline**: add the request/response models to
  `packages/contracts/src/contracts/schemas.py` and write a new
  `@app.post("/pipeline/...")` function in the gateway. All cross-module wiring
  lives in the gateway; modules never call each other directly.

## Notes & troubleshooting

- **Python 3.8 is end-of-life (Oct 2024).** It still resolves on conda-forge,
  but if `pixi install` fails to solve module-a because some package became too
  new, pin it down, e.g. add `fastapi = "<0.113"` / `starlette = "<0.38"` under
  `[feature.module-a.dependencies]`. pydantic is already capped to `>=2,<3`.
- `pixi.lock` is **not** committed here (it must be generated on a machine with
  network access). After your first `pixi install`, commit the generated
  `pixi.lock` for reproducibility.
- Modules bind to `127.0.0.1` only; the gateway is the sole public listener.
