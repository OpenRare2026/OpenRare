"""module-b : a simple forecasting FastAPI service (runs on Python 3.12)."""
from fastapi import FastAPI

from contracts.schemas import BInput, BOutput

app = FastAPI(title="module-b (py3.12)")


@app.get("/health")
def health():
    return {"status": "ok", "module": "module-b"}


@app.post("/process", response_model=BOutput)
def process(payload: BInput) -> BOutput:
    series = payload.series
    window = max(1, payload.window)
    if not series:
        return BOutput(forecast=[])
    if len(series) < window:
        avg = sum(series) / len(series)
        return BOutput(forecast=[avg])
    # naive forecast: repeat the moving average of the last `window` points
    moving_avg = sum(series[-window:]) / window
    return BOutput(forecast=[moving_avg, moving_avg, moving_avg])
