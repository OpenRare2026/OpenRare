"""
Chat API endpoints for case Q&A functionality.
"""
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, ChatSession as ChatSessionModel, ChatMessageRecord
from database.case_models import CaseDocument
from services.rag_service import RAGService, create_rag_service
from api.middleware import APIException, ErrorCode
from api.ws_manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_token: Optional[str] = None


class ChatReferenceResponse(BaseModel):
    id: str
    type: str
    label: str
    url: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str
    references: Optional[List[ChatReferenceResponse]] = None
    confidence: Optional[float] = None


class ChatSessionResponse(BaseModel):
    session_token: str
    patient_id: int
    created_at: str
    messages: List[ChatMessageResponse]


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    patient_id: int
    session_token: Optional[str] = None


class QAResponse(BaseModel):
    answer: str
    sources: List[ChatReferenceResponse]
    confidence: float
    reasoning: Optional[str] = None
    session_token: str


class IndexDocumentRequest(BaseModel):
    patient_id: int
    document_type: str = Field(..., pattern="^(patient_summary|variant_report|clinical_notes)$")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    metadata: Optional[dict] = None


class IndexDocumentResponse(BaseModel):
    document_id: int
    message: str


def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    return create_rag_service(db)


@router.post("/{patient_id}", response_model=ChatMessageResponse)
async def send_chat_message(
    patient_id: int,
    request: ChatMessageRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        response = rag_service.ask(
            query=request.message,
            patient_id=patient_id,
            session_token=request.session_token
        )
        
        references = None
        if response.sources:
            references = [
                ChatReferenceResponse(
                    id=s.reference_id,
                    type=s.reference_type,
                    label=s.label,
                    url=s.url
                )
                for s in response.sources
            ]
        
        return ChatMessageResponse(
            id="",
            role="assistant",
            content=response.answer,
            timestamp=datetime.utcnow().isoformat(),
            references=references,
            confidence=response.confidence
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_msg = str(e)
        if "faiss" in error_msg.lower() or "sentence-transformers" in error_msg.lower() or "not installed" in error_msg.lower():
            return ChatMessageResponse(
                id="",
                role="assistant",
                content="Vector search is currently unavailable (required libraries not installed). "
                        "I can still provide general responses based on case context. "
                        "Please ask your question and I'll do my best with the available information.",
                timestamp=datetime.utcnow().isoformat(),
                references=None,
                confidence=0.3
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_token}", response_model=ChatSessionResponse)
async def get_chat_history(
    session_token: str,
    db: Session = Depends(get_db)
):
    session = db.query(ChatSessionModel).filter(
        ChatSessionModel.session_token == session_token
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessageRecord).filter(
        ChatMessageRecord.session_id == session.id
    ).order_by(ChatMessageRecord.created_at).all()
    
    message_responses = [
        ChatMessageResponse(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            timestamp=msg.created_at.isoformat(),
            references=msg.references,
            confidence=msg.confidence
        )
        for msg in messages
    ]
    
    return ChatSessionResponse(
        session_token=session.session_token,
        patient_id=session.patient_id,
        created_at=session.created_at.isoformat(),
        messages=message_responses
    )


@router.post("/qa", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        response = rag_service.ask(
            query=request.question,
            patient_id=request.patient_id,
            session_token=request.session_token
        )
        
        sources = [
            ChatReferenceResponse(
                id=s.reference_id,
                type=s.reference_type,
                label=s.label,
                url=s.url
            )
            for s in response.sources
        ]
        
        session_token = rag_service.get_or_create_session(
            request.patient_id, request.session_token
        )
        
        return QAResponse(
            answer=response.answer,
            sources=sources,
            confidence=response.confidence,
            reasoning=response.reasoning,
            session_token=session_token
        )
    
    except Exception as e:
        logger.error(f"QA error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/document", response_model=IndexDocumentResponse)
async def index_document(
    request: IndexDocumentRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        document_id = rag_service.index_case_document(
            patient_id=request.patient_id,
            document_type=request.document_type,
            title=request.title,
            content=request.content,
            metadata=request.metadata
        )
        
        return IndexDocumentResponse(
            document_id=document_id,
            message="Document indexed successfully"
        )
    
    except Exception as e:
        logger.error(f"Index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/patient/{patient_id}")
async def index_patient_variants(
    patient_id: int,
    background_tasks: BackgroundTasks,
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        def index_task():
            count = rag_service.index_patient_variants(patient_id)
            logger.info(f"Indexed {count} documents for patient {patient_id}")
        
        background_tasks.add_task(index_task)
        
        return {
            "message": "Indexing started in background",
            "patient_id": patient_id
        }
    
    except Exception as e:
        logger.error(f"Index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_token}")
async def end_chat_session(
    session_token: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    success = rag_service.end_session(session_token)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session ended", "session_token": session_token}


@router.get("/session/{session_token}/history")
async def get_session_history(
    session_token: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    history = rag_service.get_session_history(session_token)
    
    return {
        "session_token": session_token,
        "history": [
            {"role": role, "content": content}
            for role, content in history
        ]
    }


manager = ConnectionManager()
