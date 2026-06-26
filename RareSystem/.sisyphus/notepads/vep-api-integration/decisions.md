# VEP API Integration - Decisions

## 2026-05-28
- VEP API base URL configurable via .env (default: http://127.0.0.1:8000)
- Async job: submit → poll → get CSV → parse → update variants
- Upload is synchronous from frontend perspective (backend handles VEP internally)
- Fallback to pysam+GFF3 on VEP failure/timeout
- Timeout: 10 minutes (600 seconds)
- Poll interval: 5 seconds (configurable)
- VEP options: hgvs, no_pick, format, fork (user selectable in upload form)
- VEP job info persisted to VEPJob table
- CSV format unknown → dynamic header detection
