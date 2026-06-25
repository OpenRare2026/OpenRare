# module-a

Data-cleaning service. **Python 3.8**, FastAPI.

- `GET /health`
- `POST /process`  body: `{"raw": [..]}`  -> `{"cleaned": [..], "meta": {..}}`

Run standalone: `pixi run -e module-a serve`  (listens on 127.0.0.1:8001)
