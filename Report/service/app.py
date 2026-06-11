"""
Rare-disease report service.

A thin FastAPI wrapper around the rare-disease-report skill. Your UI agent can't
run code, so it calls this service; the service runs the skill's scripts.

POST /report/stream  (Server-Sent Events):
  1. build the deterministic skeleton (report.md + per-slot grounding).
  2. walk the document in order:
       - static block   -> stream out immediately (already-finished text)
       - narrative slot -> generate, VALIDATE against the slot's ground_text,
                           regenerate/fallback if it invented a number/ID,
                           then emit the whole slot.
     The full markdown is accumulated server-side as we go.
  3. render the finished markdown to PDF and emit a final event with its URL.

Anti-hallucination: hard data is never produced by the model (it is rendered by
build_context.py from the CSV). The only model text is the narrative slots, and
validate_narrative.find_violations() blocks any ungrounded number/ID before it
reaches the user — so even under streaming, regulated fields can't be fabricated.

Run (from the rare-disease-report/ directory):
  pip install -r service/requirements.txt
  uvicorn service.app:app --host 0.0.0.0 --port 8010
"""
import asyncio, json, os, re, sys, uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

SKILL_DIR = Path(__file__).resolve().parent.parent      # rare-disease-report/
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import build_context as bc                               # noqa: E402
import render_pdf as rp                                  # noqa: E402
from validate_narrative import find_violations           # noqa: E402

WORK = Path(os.environ.get("REPORT_WORK_DIR", "/tmp/rdr_runs"))
WORK.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Rare Disease Report Service")
NARR_RE = re.compile(r"\{\{narrative:([^}]+)\}\}")
MAX_RETRIES = 2


class ReportRequest(BaseModel):
    # In production these resolve to data pulled from your upstream HTTP services /
    # DB. Here they are paths the service can read. Wide table is required.
    wide: str
    phenotype: str | None = None
    ppi: str | None = None
    case_id: str | None = None
    hpo_file: str | None = None
    symptom_text: str | None = None
    top_n: int = 10
    k: int = 5
    genes: str | None = None            # comma-separated; overrides top_n


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


def _segments(md: str):
    """Yield ('static', text) and ('narrative', slot_id) in document order."""
    pos = 0
    for m in NARR_RE.finditer(md):
        if m.start() > pos:
            yield "static", md[pos:m.start()]
        yield "narrative", m.group(1)
        pos = m.end()
    if pos < len(md):
        yield "static", md[pos:]


# --------------------------- narrative generation -----------------------------
async def _generate_once(slot: str, ctx: dict, retry_note: str = "") -> str:
    """PLUG POINT. Return the full narrative text for one slot.

    Offline default returns a short grounded line so the pipeline runs without an
    LLM. Set ANTHROPIC_API_KEY to use a real model that writes from ctx only.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return await _anthropic_once(slot, ctx, retry_note)
    # ---- offline stub (no model): safe, grounded, number-free prose ----
    if slot == "phenotype_overview":
        return "（离线占位）患者表型概述将在接入模型后生成；本段不含任何数值，仅作流程占位。"
    ph = (ctx.get("context", {}) or {}).get("phenotype", {}) or {}
    code = ph.get("conclusion_code", "")
    gene = (ctx.get("context", {}) or {}).get("gene", "")
    tail = f"表型匹配结论为 {code}。" if code else ""
    return (f"（离线占位）{gene} 的综合解读将在接入模型后生成。{tail}"
            "本段不复述上方任何坐标、频率或分数，仅作流程占位。")


async def _anthropic_once(slot: str, ctx: dict, retry_note: str) -> str:
    import httpx
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = os.environ.get("REPORT_MODEL", "claude-sonnet-4-6")
    sys_prompt = (
        "你在为一份探索性罕见病候选基因报告撰写叙事段落。"
        "只能使用提供的 context 中已出现的数字、ID、分数；"
        "绝不新增或改写任何坐标、频率、OMIM/MONDO/HP ID 或分数。"
        "如实说明证据强弱与不确定性。输出中文 2-6 句，不要标题或列表。" + retry_note
    )
    user = (f"slot={slot}\ninstruction={ctx.get('instruction','')}\n"
            f"context={json.dumps(ctx.get('context', {}), ensure_ascii=False)}")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{base_url}/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 400,
                "system": sys_prompt,
                "messages": [{"role": "user", "content": user}],
                "thinking": {"type": "disabled"},
            },
        )
        resp.raise_for_status()
        data = resp.json()
    # Prefer text blocks; some providers put output only in thinking blocks
    text = "".join(
        b["text"] for b in data.get("content", []) if b.get("type") == "text"
    ).strip()
    if not text:
        text = "".join(
            b["thinking"] for b in data.get("content", []) if b.get("type") == "thinking"
        ).strip()
    return text


async def _filled_slot(slot: str, ctx: dict) -> str:
    """Generate + validate; retry on hallucination; safe fallback if it persists."""
    ground = ctx.get("ground_text", "")
    note = ""
    for _ in range(MAX_RETRIES + 1):
        text = await _generate_once(slot, ctx, note)
        bad = find_violations(text, ground)
        if not bad:
            return text
        note = (f" 上次输出包含未在 context 中出现的内容：{bad}，"
                "请删除这些数值/ID，只引用 context 内已有的值。")
    # give up generating numbers: emit a guaranteed-grounded, number-free summary
    inner = (ctx.get("context", {}) or {})
    gene = inner.get("gene", "")
    if gene:
        ph = inner.get("phenotype", {}) or {}
        code = ph.get("conclusion_code", "")
        disease = ph.get("best_disease_name", "")
        clues = []
        if code:
            clues.append(f"表型匹配结论为 {code}")
        if disease:
            clues.append(f"最匹配疾病为 {disease}")
        tail = "；".join(clues) + "。" if clues else ""
        return f"（自动改写·{gene}）{tail}由于模型多次引入未经核对的数值，此处已屏蔽具体数字，请直接参考上方三块确定性证据表格。"
    return ("（自动改写）综合上方确定性证据进行解读；"
            "为避免引入未经核对的数值，此处不复述具体数字，请以上方表格为准。")


async def _stream(req: ReportRequest, run_id: str, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    # build_context touches a 20k+ row CSV -> run off the event loop
    md, slots, stats = await asyncio.to_thread(
        bc.build, req.wide, req.phenotype, req.ppi, req.top_n, req.k,
        req.genes, req.case_id, req.hpo_file, req.symptom_text)
    yield _sse({"type": "meta", "run_id": run_id, **stats})

    full = []
    for kind, payload in _segments(md):
        if kind == "static":
            full.append(payload)
            yield _sse({"type": "md", "text": payload})
        else:
            text = await _filled_slot(payload, slots.get(payload, {}))
            full.append(text)
            yield _sse({"type": "md", "text": text, "slot": payload})

    filled = "".join(full)
    (outdir / "report.filled.md").write_text(filled, encoding="utf-8")
    await asyncio.to_thread(rp.md_to_pdf, filled, str(outdir / "report.pdf"))
    yield _sse({"type": "done", "run_id": run_id, "pdf_url": f"/report/{run_id}/pdf"})


@app.post("/report/stream")
async def report_stream(req: ReportRequest):
    run_id = uuid.uuid4().hex[:12]
    return StreamingResponse(
        _stream(req, run_id, WORK / run_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/report/{run_id}/pdf")
def get_pdf(run_id: str):
    p = WORK / run_id / "report.pdf"
    if not p.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(p, media_type="application/pdf", filename=f"{run_id}.pdf")


@app.get("/health")
def health():
    return {"status": "ok"}
