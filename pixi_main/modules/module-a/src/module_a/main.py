"""module-a : a data-cleaning FastAPI service (runs on Python 3.8)."""
from fastapi import FastAPI

from contracts.schemas import AInput, AOutput

app = FastAPI(title="module-a (py3.8)")


@app.get("/health")
def health():
    return {"status": "ok", "module": "module-a"}


@app.post("/process", response_model=AOutput)
def process(payload: AInput):
    # Demo "cleaning": drop NaNs (x != x is True only for NaN) and keep the rest.
    cleaned = [x for x in payload.raw if x == x]
    count = float(len(cleaned))
    mean = (sum(cleaned) / count) if cleaned else 0.0
    return AOutput(cleaned=cleaned, meta={"count": count, "mean": mean})
