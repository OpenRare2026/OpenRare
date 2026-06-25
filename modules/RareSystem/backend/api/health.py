"""
Health check endpoint
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns:
        HealthResponse: {"status": "healthy"} if service is operational
    """
    return HealthResponse(status="healthy")
