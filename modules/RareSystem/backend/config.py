"""
VEP API Configuration

Loaded from environment variables with sensible defaults.
"""
import os

VEP_API_BASE_URL = os.getenv("VEP_API_BASE_URL", "http://localhost:8000")
VEP_POLL_MAX_RETRIES = int(os.getenv("VEP_POLL_MAX_RETRIES", "180"))
VEP_POLL_INTERVAL_SECONDS = int(os.getenv("VEP_POLL_INTERVAL_SECONDS", "10"))
VEP_ENABLED = os.getenv("VEP_ENABLED", "true").lower() in ("true", "1", "yes")
VEP_API_KEY = os.getenv("VEP_API_KEY", "")

# VEP异步处理配置：最长等待30分钟 (180次 * 10秒)
VEP_ASYNC_POLL_INTERVAL = int(os.getenv("VEP_ASYNC_POLL_INTERVAL", "10"))
VEP_ASYNC_MAX_DURATION = int(os.getenv("VEP_ASYNC_MAX_DURATION", "1800"))  # 30分钟

HPO_API_BASE_URL = os.getenv("HPO_API_BASE_URL", "http://localhost:9001")
HPO_POLL_INTERVAL_SECONDS = int(os.getenv("HPO_POLL_INTERVAL_SECONDS", "10"))
HPO_POLL_MAX_ATTEMPTS = int(os.getenv("HPO_POLL_MAX_ATTEMPTS", "12"))

PHENOTYPE_HPO_API_BASE_URL = os.getenv("PHENOTYPE_HPO_API_BASE_URL", "http://localhost:7002")
PHENOTYPE_HPO_POLL_INTERVAL = int(os.getenv("PHENOTYPE_HPO_POLL_INTERVAL", "10"))
PHENOTYPE_HPO_MAX_DURATION = int(os.getenv("PHENOTYPE_HPO_MAX_DURATION", "1800"))

PPI_SCORE_API_BASE_URL = os.getenv("PPI_SCORE_API_BASE_URL", "http://localhost:9000")
PPI_SCORE_POLL_INTERVAL = int(os.getenv("PPI_SCORE_POLL_INTERVAL", "10"))
PPI_SCORE_MAX_DURATION = int(os.getenv("PPI_SCORE_MAX_DURATION", "1800"))

REPORT_API_BASE_URL = os.getenv("REPORT_API_BASE_URL", "http://localhost:7000")
REPORT_POLL_INTERVAL = int(os.getenv("REPORT_POLL_INTERVAL", "2"))
REPORT_MAX_DURATION = int(os.getenv("REPORT_MAX_DURATION", "3600"))
