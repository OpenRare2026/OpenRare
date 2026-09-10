"""
Development server runner for Rare Disease Genetic Diagnosis System
"""
import logging
import sys
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).parent
ENV_FILE = BACKEND_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def main():
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    env = os.getenv("ENVIRONMENT", "development")

    logger.info("=" * 60)
    logger.info("Rare Disease Genetic Diagnosis System - Backend Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {env}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"API Documentation: http://localhost:{port}/docs")
    logger.info(f"Health Check: http://localhost:{port}/api/health")
    logger.info("=" * 60)

    # Initialize database BEFORE starting the server.
    # This ensures all tables exist before uvicorn starts accepting requests,
    # eliminating the race between init_db() in startup_event and incoming API calls.
    logger.info("Initializing database...")
    try:
        from database.session import init_db
        init_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error("Server will exit - cannot operate without database")
        sys.exit(1)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
