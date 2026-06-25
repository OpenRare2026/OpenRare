"""
Case and Embedding models for Q&A RAG system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, LargeBinary
from sqlalchemy.orm import relationship

from .base import Base


class CaseDocument(Base):
    """
    Case Document model - stores indexed case information for RAG retrieval.
    
    Document types:
    - patient_summary: Patient phenotype and clinical history
    - variant_report: Variant analysis and ACMG classification
    - clinical_notes: Clinical observations and interpretations
    """
    __tablename__ = "case_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    relationships = relationship("CaseEmbedding", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CaseDocument(id={self.id}, type={self.document_type}, patient_id={self.patient_id})>"


class CaseEmbedding(Base):
    """
    Case Embedding model - stores vector embeddings for case documents.
    
    Uses FAISS for similarity search. Embeddings are generated using
    sentence-transformers models optimized for medical/biomedical text.
    """
    __tablename__ = "case_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("case_documents.id"), nullable=False, unique=True)
    embedding_vector = Column(LargeBinary, nullable=False)
    embedding_model = Column(String(100), nullable=False)
    vector_dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    document = relationship("CaseDocument", back_populates="relationships")
    
    def __repr__(self):
        return f"<CaseEmbedding(id={self.id}, document_id={self.document_id}, dim={self.vector_dimension})>"


class ChatSession(Base):
    """
    Chat Session model - stores Q&A session history.
    
    Tracks conversation history for context-aware responses
    and enables follow-up questions with proper context.
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    session_token = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1, nullable=False)
    
    messages = relationship("ChatMessageRecord", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, token={self.session_token})>"


class ChatMessageRecord(Base):
    """
    Chat Message Record model - stores individual messages in a chat session.
    
    Supports user questions and assistant responses with
    source references and confidence scores.
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    references = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessageRecord(id={self.id}, role={self.role})>"


class LLMSettings(Base):
    """
    LLM Settings model - stores configuration for Large Language Models.
    
    Supports multiple providers: OpenAI, Anthropic, Ollama, and custom endpoints.
    Configuration is per-patient for Case Q&A functionality.
    """
    __tablename__ = "llm_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    is_active = Column(Integer, default=1, nullable=False)
    
    provider = Column(String(50), nullable=False, index=True)
    provider_name = Column(String(100), nullable=True)
    
    api_key = Column(Text, nullable=False)
    base_url = Column(String(500), nullable=True)
    model = Column(String(100), nullable=False)
    
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=1024, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = relationship("Patient", backref="llm_settings")
    
    def __repr__(self):
        return f"<LLMSettings(id={self.id}, provider={self.provider}, patient_id={self.patient_id})>"


class SkillConfig(Base):
    __tablename__ = "skill_configs"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), unique=True, nullable=False, index=True)
    is_enabled = Column(Integer, default=1, nullable=False)
    config = Column(JSON, default=dict, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SkillConfig(id={self.id}, skill_name={self.skill_name}, is_enabled={self.is_enabled})>"
