# Pixi PPI Score Service

This directory is the Pixi refactor of the original `script1/` FastAPI PPI scorer.
The business code lives in `app/`; Pixi owns the Python runtime and dependency graph.

## Dependency Files

- `pixi.toml`: Pixi environment, channels, package dependencies, and runnable tasks.
- `requirements.txt`: plain dependency summary extracted from the original project.
- `docs/DEPENDENCIES.md`: notes about how the dependency list was derived.
- `docs/PATHS.md`: all important input, output, intermediate, and external paths.

## Run

From this directory:

```bash
pixi install
pixi run serve
```

If `pixi` is not on `PATH`, install it first with the official installer:

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

The service defaults to port `9000` and uses these relative paths:

```text
RARE_PPI_DATA_DIR=../../data
RARE_PPI_OUTPUT_DIR=output
RARE_PPI_UPLOAD_DIR=uploads
```

Override them with environment variables when needed.

## Test With curl

In another shell:

```bash
pixi run health
pixi run test-score
```

`pixi run test-score` posts `tests/inputs/score_request.json` to `/score`, writes the
response to `tests/outputs/score_response.json`, and verifies that the returned CSV
exists.

Clean-case examples are recorded in `docs/CLEAN_CASE_TESTS.md` and can be run with:

```bash
pixi run case5-clean
pixi run case6-clean
```
