# Dependency Summary

Dependencies were collected from the original `app/requirements.txt` and by scanning
imports in `app/*.py`.

## Runtime Packages

| Package | Source import / use |
| --- | --- |
| `python >=3.10,<3.12` | Matches the existing remote runtime, Python 3.10. |
| `numpy` | Numerical arrays and scoring helpers. |
| `pandas` | CSV loading, aggregation, and output tables. |
| `networkx` | STRING PPI graph construction and traversal. |
| `scipy` | Scientific utilities used by the scorer. |
| `pydantic >=2` | FastAPI request models and validators. |
| `fastapi` | HTTP API service. |
| `uvicorn` | ASGI server. |
| `python-multipart` | Upload endpoints with form files. |
| `owlready2` | HPO OWL parsing. |

## Files

- Pixi manifest: `pixi.toml`
- Plain requirement summary: `requirements.txt`
- Original requirement source: `app/requirements.txt`

No large reference datasets are vendored into this Pixi project.
