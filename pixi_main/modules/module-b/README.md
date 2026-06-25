# module-b

Forecasting service. **Python 3.12**, FastAPI.

- `GET /health`
- `POST /process`  body: `{"series": [..], "window": 3}`  -> `{"forecast": [..]}`

Run standalone: `pixi run -e module-b serve`  (listens on 127.0.0.1:8002)
