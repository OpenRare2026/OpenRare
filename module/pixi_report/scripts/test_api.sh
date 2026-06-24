#!/usr/bin/env bash
# 在 module/pix_report 目录下执行：pixi run test-api
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${API_BASE:-http://127.0.0.1:8800}"
REQUEST="${ROOT}/fixtures/test_request.json"
SSE_OUT="${ROOT}/.test_sse.txt"

cd "$ROOT"

echo "=== 1. GET /health ==="
curl -sf "$BASE/health"
echo

echo "=== 2. POST /report/stream (fixtures, top_n=2) ==="
rm -f "$SSE_OUT"
timeout 600 curl -sN -X POST "$BASE/report/stream" \
  -H 'Content-Type: application/json' \
  -d @"$REQUEST" | tee "$SSE_OUT" | python3 -c "
import sys, json
meta=done=None
md=0
for line in sys.stdin:
    line=line.strip()
    if not line.startswith('data: '):
        continue
    e=json.loads(line[6:])
    t=e.get('type')
    if t=='meta':
        print(f'  meta: run_id={e[\"run_id\"]} genes={e[\"genes\"]}')
    elif t=='md':
        md+=1
        if md<=2:
            preview=e.get('text','')[:60].replace('\n',' ')
            print(f'  md #{md}: {preview}...')
    elif t=='done':
        done=e
        print(f'  done: {e.get(\"md_url\")}')
    elif t=='error':
        print('  ERROR:', e)
        sys.exit(1)
print(f'  summary: md_events={md} done={bool(done)}')
if not done:
    sys.exit(2)
"

RUN_ID=$(grep -o '"run_id": "[^"]*"' "$SSE_OUT" | head -1 | cut -d'"' -f4)
echo "=== 3. GET /report/${RUN_ID}/md ==="
curl -sf -o "${ROOT}/.test_report.md" \
  -w "HTTP %{http_code} bytes=%{size_download}\n" \
  "$BASE/report/${RUN_ID}/md"
head -6 "${ROOT}/.test_report.md"
echo "=== ALL OK run_id=${RUN_ID} ==="
