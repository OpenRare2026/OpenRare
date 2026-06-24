"""
WebSocket Connection Manager for real-time chat streaming.
"""
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections keyed by patient_id."""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, patient_id: int):
        """Accept a WebSocket connection and register it."""
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append(websocket)
        logger.info(f"WebSocket connected for patient {patient_id}")

    def disconnect(self, websocket: WebSocket, patient_id: int):
        """Remove a WebSocket connection."""
        if patient_id in self.active_connections:
            try:
                self.active_connections[patient_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[patient_id]:
                del self.active_connections[patient_id]
        logger.info(f"WebSocket disconnected for patient {patient_id}")

    async def send_to_client(self, patient_id: int, message: dict):
        """Send a JSON message to all connections for a patient."""
        if patient_id in self.active_connections:
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send WebSocket message: {e}")
