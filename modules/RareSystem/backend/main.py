"""
Rare Disease Genetic Diagnosis Analysis System - Backend API
"""
import logging
import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from api.middleware import (
    RequestLoggingMiddleware,
    api_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
    setup_logging,
    APIException,
)

setup_logging(level="INFO")

logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Loopback by default: this API serves patient genomic data and has no
# authentication layer yet, so it must not listen on every interface unless
# the operator opts in. Containers set API_HOST=0.0.0.0 explicitly — the
# container boundary is what limits exposure there.
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8888,http://127.0.0.1:8888,http://localhost:8181,http://127.0.0.1:8181").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Rare Disease Genetic Diagnosis System API")
    logger.info(f"CORS enabled for origins: {CORS_ORIGINS}")
    from database.session import init_db, close_db
    init_db()
    logger.info("Database tables initialized")
    yield
    logger.info("Shutting down API server")
    close_db()


app = FastAPI(
    title="Rare Disease Genetic Diagnosis System",
    description="Multi-type variant detection and ACMG classification API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Request/Response Models
class HealthResponse(BaseModel):
    status: str


# Register routes
from api.health import router as health_router
from api.chat import router as chat_router
from api.variants import router as variants_router
from api.acmg import router as acmg_router
from api.settings import router as settings_router
from api.cases import router as cases_router
from api.skills import router as skills_router
from api.pubmed import router as pubmed_router
from api.genes import router as genes_router
from api.vep import router as vep_router
from api.hpo import router as hpo_router
from api.pathways import router as pathways_router
from api.phenotype_hpo import router as phenotype_hpo_router
from api.ppi_score import router as ppi_score_router
from api.report import router as report_router
app.include_router(health_router, prefix="/api", tags=["health"])

from api.ws_manager import ConnectionManager as _CM
from api.chat import manager as _chat_manager
from services.rag_service import create_rag_service as _create_rag_service
from database import get_db as _get_db

@app.websocket("/api/chat/ws/{patient_id}")
async def websocket_chat(websocket: WebSocket, patient_id: int):
    await _chat_manager.connect(websocket, patient_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "chat")

            if msg_type == "cancel":
                await _chat_manager.send_to_client(patient_id, {"type": "done", "content": ""})
                continue

            try:
                db = next(_get_db())
                rag_service = _create_rag_service(db)

                if msg_type == "chat":
                    for chunk in rag_service.ask_stream(
                        query=data.get("content", ""),
                        patient_id=patient_id,
                        session_token=data.get("session_token")
                    ):
                        await _chat_manager.send_to_client(patient_id, chunk)
                elif msg_type == "skill":
                    for chunk in rag_service.ask_stream(
                        query=data.get("content", ""),
                        patient_id=patient_id,
                        skill_name=data.get("skill_name"),
                        session_token=data.get("session_token")
                    ):
                        await _chat_manager.send_to_client(patient_id, chunk)

            except Exception as e:
                logger.error(f"WebSocket chat error: {e}")
                await _chat_manager.send_to_client(patient_id, {"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        _chat_manager.disconnect(websocket, patient_id)

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(variants_router, prefix="/api", tags=["variants"])
app.include_router(acmg_router, prefix="/api", tags=["acmg"])
app.include_router(settings_router, prefix="/api", tags=["settings"])
app.include_router(cases_router, prefix="/api", tags=["cases"])
app.include_router(skills_router, prefix="/api", tags=["skills"])
app.include_router(pubmed_router, prefix="/api", tags=["pubmed"])
app.include_router(genes_router, prefix="/api", tags=["genes"])
app.include_router(vep_router, prefix="/api", tags=["vep"])
app.include_router(hpo_router, prefix="/api", tags=["hpo"])
app.include_router(pathways_router, prefix="/api", tags=["pathways"])
app.include_router(phenotype_hpo_router, prefix="/api", tags=["phenotype-hpo"])
app.include_router(ppi_score_router, prefix="/api", tags=["ppi-score"])
app.include_router(report_router, prefix="/api", tags=["report"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
