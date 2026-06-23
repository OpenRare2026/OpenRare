# Dependency Summary

Dependencies were collected from the original `app/requirements.txt` and by scanning
imports in `app/*.py`.

## Runtime Packages

| Package | Source import / use |
| --- | --- |
| `python >=3.10,<3.12` | Compatible with the existing Python 3.10 service and the Pixi-locked Python 3.11 environment. |
| `numpy` | Numerical arrays and scoring helpers. |
| `pandas >=2.3,<3` | CSV loading, aggregation, and output tables. Pinned below 3.x to match the existing validated service runtime and avoid a Pandas 3.0 chunked CSV parsing issue on large VEP files. |
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
