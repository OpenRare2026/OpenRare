"""
External Microservice Configuration

All URLs loaded from environment variables.
MUST set these in backend/.env when deploying to a new environment.
Defaults point to localhost for local development.
"""
import os

# VEP (Variant Effect Predictor) API
VEP_API_BASE_URL = os.getenv("VEP_API_BASE_URL", "http://127.0.0.1:8000")
VEP_POLL_MAX_RETRIES = int(os.getenv("VEP_POLL_MAX_RETRIES", "180"))
VEP_POLL_INTERVAL_SECONDS = int(os.getenv("VEP_POLL_INTERVAL_SECONDS", "10"))
VEP_ENABLED = os.getenv("VEP_ENABLED", "true").lower() in ("true", "1", "yes")
VEP_API_KEY = os.getenv("VEP_API_KEY", "")

# VEP异步处理配置：最长等待30分钟 (180次 * 10秒)
VEP_ASYNC_POLL_INTERVAL = int(os.getenv("VEP_ASYNC_POLL_INTERVAL", "10"))
VEP_ASYNC_MAX_DURATION = int(os.getenv("VEP_ASYNC_MAX_DURATION", "1800"))  # 30分钟

# HPO (Human Phenotype Ontology) API
HPO_API_BASE_URL = os.getenv("HPO_API_BASE_URL", "http://127.0.0.1:9001")
HPO_POLL_INTERVAL_SECONDS = int(os.getenv("HPO_POLL_INTERVAL_SECONDS", "10"))
HPO_POLL_MAX_ATTEMPTS = int(os.getenv("HPO_POLL_MAX_ATTEMPTS", "12"))

# Phenotype-HPO mapping API
PHENOTYPE_HPO_API_BASE_URL = os.getenv("PHENOTYPE_HPO_API_BASE_URL", "http://127.0.0.1:7002")
PHENOTYPE_HPO_POLL_INTERVAL = int(os.getenv("PHENOTYPE_HPO_POLL_INTERVAL", "10"))
PHENOTYPE_HPO_MAX_DURATION = int(os.getenv("PHENOTYPE_HPO_MAX_DURATION", "1800"))

# PPI Score (Protein-Protein Interaction) API
PPI_SCORE_API_BASE_URL = os.getenv("PPI_SCORE_API_BASE_URL", "http://127.0.0.1:9000")
PPI_SCORE_POLL_INTERVAL = int(os.getenv("PPI_SCORE_POLL_INTERVAL", "10"))
PPI_SCORE_MAX_DURATION = int(os.getenv("PPI_SCORE_MAX_DURATION", "1800"))

# Ranking service API
RANK_API_BASE_URL = os.getenv("RANK_API_BASE_URL", "http://127.0.0.1:5002")
RANK_POLL_INTERVAL = int(os.getenv("RANK_POLL_INTERVAL", "10"))
RANK_MAX_DURATION = int(os.getenv("RANK_MAX_DURATION", "1800"))

# Report generation API
REPORT_API_BASE_URL = os.getenv("REPORT_API_BASE_URL", "http://127.0.0.1:7000")
REPORT_POLL_INTERVAL = int(os.getenv("REPORT_POLL_INTERVAL", "2"))
REPORT_MAX_DURATION = int(os.getenv("REPORT_MAX_DURATION", "3600"))
