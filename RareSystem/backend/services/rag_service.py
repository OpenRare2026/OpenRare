"""
RAG Service - Retrieval-Augmented Generation for case Q&A.

Combines:
- Vector similarity search for relevant context retrieval
- LLM integration for answer generation
- Source citation and confidence scoring
"""
import logging
import secrets
from typing import List, Optional, Dict, Any, Tuple, Iterator
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.case_models import CaseDocument, CaseEmbedding, ChatSession, ChatMessageRecord, LLMSettings
from database.models import Patient, Variant, ACMGClassification, ACMGEvidence
from services.embedding_service import EmbeddingService, SearchResult
from services.llm_client import LLMClient, create_llm_client, LLMClientError
from services.settings_service import SettingsService, create_settings_service

logger = logging.getLogger(__name__)

MAX_CONTEXT_DOCUMENTS = 5
MAX_HISTORY_MESSAGES = 10
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


@dataclass
class ChatReference:
    reference_id: str
    reference_type: str
    label: str
    url: Optional[str] = None


@dataclass
class QAResponse:
    answer: str
    sources: List[ChatReference]
    confidence: float
    reasoning: Optional[str] = None


@dataclass
class CaseContext:
    patient_info: Optional[str] = None
    variant_info: List[str] = field(default_factory=list)
    clinical_notes: List[str] = field(default_factory=list)
    relevant_documents: List[str] = field(default_factory=list)


class RAGServiceError(Exception):
    pass


class SessionNotFoundError(RAGServiceError):
    pass


class NoRelevantContextError(RAGServiceError):
    pass


class RAGService:
    def __init__(
        self,
        db: Session,
        embedding_service: Optional[EmbeddingService] = None,
        llm_client: Optional[LLMClient] = None,
        settings_service: Optional[SettingsService] = None
    ):
        self._db = db
        self._embedding_service = embedding_service or EmbeddingService()
        self._llm_client = llm_client
        self._settings_service = settings_service

    def _get_llm_client(self, patient_id: int) -> Optional[LLMClient]:
        if self._llm_client:
            return self._llm_client

        if not self._settings_service:
            self._settings_service = create_settings_service(self._db)

        settings = self._settings_service.get_llm_settings(patient_id)
        if not settings:
            logger.warning(f"No LLM settings found for patient {patient_id}, using mock response")
            return None

        try:
            return create_llm_client(
                provider=settings.provider,
                api_key=settings.api_key,
                model=settings.model,
                base_url=settings.base_url
            )
        except LLMClientError as e:
            logger.error(f"Failed to create LLM client: {e}")
            return None

    def _build_patient_context(self, patient_id: int) -> str:
        patient = self._db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return ""
        
        parts = []
        if patient.diagnosis_description:
            parts.append(f"Phenotype: {patient.diagnosis_description}")
        if patient.medical_history:
            parts.append(f"Medical History: {patient.medical_history}")
        if patient.age:
            parts.append(f"Age: {patient.age}")
        if patient.sex:
            parts.append(f"Sex: {patient.sex}")
        if patient.ethnicity:
            parts.append(f"Ethnicity: {patient.ethnicity}")
        
        return " | ".join(parts)

    def _build_variant_context(
        self,
        patient_id: int,
        limit: int = 10
    ) -> List[Tuple[str, Dict[str, Any]]]:
        from database.models import VCFFile
        
        vcf_files = self._db.query(VCFFile.id).filter(
            VCFFile.patient_id == patient_id
        ).all()
        
        if not vcf_files:
            return []
        
        vcf_ids = [v.id for v in vcf_files]
        
        variants = self._db.query(Variant).filter(
            Variant.vcf_file_id.in_(vcf_ids)
        ).limit(limit).all()
        
        results = []
        for variant in variants:
            classification = self._db.query(ACMGClassification).filter(
                ACMGClassification.variant_id == variant.id
            ).first()
            
            evidence_list = self._db.query(ACMGEvidence).filter(
                ACMGEvidence.variant_id == variant.id
            ).all()
            
            text_parts = [
                f"Variant: {variant.chromosome}:{variant.position} {variant.ref}>{variant.alt}",
                f"Type: {variant.variant_type}",
                f"Quality: {variant.quality}"
            ]
            
            if classification:
                text_parts.append(f"Classification: {classification.classification}")
                if classification.confidence_score:
                    text_parts.append(f"Confidence: {classification.confidence_score:.2f}")
            
            if evidence_list:
                evidence_texts = [f"{e.criterion}: {e.description}" for e in evidence_list[:3]]
                text_parts.append(f"Evidence: {'; '.join(evidence_texts)}")
            
            metadata = {
                "variant_id": variant.id,
                "chromosome": variant.chromosome,
                "position": variant.position,
                "classification": classification.classification if classification else None
            }
            
            results.append((" | ".join(text_parts), metadata))
        
        return results

    def _build_case_context(self, patient_id: int) -> CaseContext:
        context = CaseContext()
        
        context.patient_info = self._build_patient_context(patient_id)
        
        variant_contexts = self._build_variant_context(patient_id)
        context.variant_info = [v[0] for v in variant_contexts]
        
        documents = self._db.query(CaseDocument).filter(
            CaseDocument.patient_id == patient_id
        ).all()
        
        for doc in documents:
            if doc.document_type == "clinical_notes":
                context.clinical_notes.append(doc.content)
            else:
                context.relevant_documents.append(doc.content)
        
        return context

    def _retrieve_relevant_documents(
        self,
        query: str,
        patient_id: Optional[int] = None,
        k: int = MAX_CONTEXT_DOCUMENTS
    ) -> List[Tuple[SearchResult, Dict[str, Any]]]:
        from services.embedding_service import IndexNotBuiltError, ModelNotLoadedError

        try:
            if patient_id:
                documents = self._db.query(CaseDocument).filter(
                    CaseDocument.patient_id == patient_id
                ).all()
                
                doc_map = {d.id: (d.content, {"type": d.document_type, "patient_id": d.patient_id}) for d in documents}
                
                if doc_map:
                    results = self._embedding_service.search_with_metadata(
                        query=query,
                        documents=doc_map,
                        k=k
                    )
                    return [(r, doc_map[r.document_id][1]) for r in results]
            
            results = self._embedding_service.search(query=query, k=k)
            return [(r, {}) for r in results]

        except (IndexNotBuiltError, ModelNotLoadedError) as e:
            logger.warning(f"Vector search unavailable: {e}. Skipping document retrieval.")
            return []

    def _format_context_for_prompt(
        self,
        context: CaseContext,
        retrieved_docs: List[Tuple[SearchResult, Dict[str, Any]]]
    ) -> str:
        parts = []
        
        if context.patient_info:
            parts.append(f"[Patient Information]: {context.patient_info}")
        
        if context.variant_info:
            parts.append("[Variants]:")
            for i, variant in enumerate(context.variant_info[:5], 1):
                parts.append(f"  {i}. {variant}")
        
        if retrieved_docs:
            parts.append("[Relevant Context]:")
            for doc, metadata in retrieved_docs[:3]:
                doc_type = metadata.get("type", "document")
                parts.append(f"  [{doc_type}] {doc.content[:500]}...")
        
        if context.clinical_notes:
            parts.append("[Clinical Notes]:")
            for note in context.clinical_notes[:2]:
                parts.append(f"  {note[:300]}...")
        
        return " | ".join(parts)

    def _generate_answer(
        self,
        query: str,
        context: str,
        history: Optional[List[Tuple[str, str]]] = None,
        patient_id: Optional[int] = None
    ) -> Tuple[str, float, str]:
        prompt = self._build_rag_prompt(query, context, history)

        llm_client = None
        if patient_id:
            llm_client = self._get_llm_client(patient_id)

        if llm_client:
            try:
                settings = self._settings_service.get_llm_settings(patient_id) if self._settings_service else None
                temperature = settings.temperature if settings else 0.7
                max_tokens = settings.max_tokens if settings else 1024

                messages = [{"role": "user", "content": prompt}]
                response = llm_client.chat(messages, temperature=temperature, max_tokens=max_tokens)

                answer = response.content
                confidence = 0.85
                reasoning = f"Generated by {response.model} based on retrieved case documents"

                logger.info(f"LLM response generated: model={response.model}, tokens={response.usage}")
                return answer, confidence, reasoning

            except LLMClientError as e:
                logger.error(f"LLM API error: {e}, falling back to mock response")

        answer = self._mock_llm_response(query, context)
        confidence = 0.75
        reasoning = "Based on retrieved case documents and variant information (mock response)"

        return answer, confidence, reasoning

    def _build_rag_prompt(
        self,
        query: str,
        context: str,
        history: Optional[List[Tuple[str, str]]] = None
    ) -> str:
        prompt_parts = [
            "You are a clinical genetics assistant helping analyze rare disease cases.",
            "Use the provided context to answer questions accurately.",
            "Always cite your sources and indicate confidence level.",
            "If uncertain, clearly state limitations.",
            "",
            f"Context: {context}",
            ""
        ]
        
        if history:
            prompt_parts.append("Previous conversation:")
            for user_msg, assistant_msg in history[-3:]:
                prompt_parts.append(f"  Q: {user_msg}")
                prompt_parts.append(f"  A: {assistant_msg}")
            prompt_parts.append("")
        
        prompt_parts.append(f"Question: {query}")
        prompt_parts.append("")
        prompt_parts.append("Answer (with citations):")
        
        return " | ".join(prompt_parts)

    def _mock_llm_response(self, query: str, context: str) -> str:
        query_lower = query.lower()
        
        if "variant" in query_lower or "pathogenic" in query_lower:
            return (
                "Based on the case analysis, the most significant variants have been identified. "
                "The ACMG classification follows standard guidelines with supporting evidence from "
                "population databases and functional predictions. Please refer to the variant details "
                "for specific criteria applied."
            )
        elif "acmg" in query_lower or "classification" in query_lower:
            return (
                "The ACMG/AMP classification applies pathogenic and benign criteria based on "
                "evidence levels. Pathogenic classifications require combinations of PVS, PS, PM, and PP criteria. "
                "The specific criteria applied to each variant are documented in the evidence section."
            )
        elif "treatment" in query_lower or "therapy" in query_lower:
            return (
                "Treatment recommendations depend on the specific genetic condition identified. "
                "Please consult with clinical specialists for personalized treatment plans. "
                "Research literature may provide additional therapeutic insights for rare conditions."
            )
        elif "gene" in query_lower:
            return (
                "The genes associated with this phenotype have been identified through variant analysis. "
                "Gene-disease associations are based on established databases including OMIM and ClinGen. "
                "Further functional studies may be needed for novel gene-phenotype associations."
            )
        else:
            return (
                "Based on the available case information and variant analysis, "
                "I can provide insights into the genetic findings. Please ask specific questions "
                "about variants, ACMG classification, or clinical implications for more detailed responses."
            )

    def _create_references(
        self,
        retrieved_docs: List[Tuple[SearchResult, Dict[str, Any]]]
    ) -> List[ChatReference]:
        references = []
        for doc, metadata in retrieved_docs[:3]:
            ref_type = metadata.get("type", "document")
            label = f"{ref_type.replace('_', ' ').title()}"
            
            references.append(ChatReference(
                reference_id=str(doc.document_id),
                reference_type=ref_type,
                label=label,
                url=None
            ))
        return references

    def create_session(self, patient_id: int) -> str:
        session_token = secrets.token_urlsafe(32)
        
        session = ChatSession(
            patient_id=patient_id,
            session_token=session_token,
            is_active=1
        )
        self._db.add(session)
        self._db.commit()
        
        logger.info(f"Created chat session for patient {patient_id}")
        return session_token

    def get_or_create_session(self, patient_id: int, session_token: Optional[str] = None) -> str:
        if session_token:
            session = self._db.query(ChatSession).filter(
                and_(
                    ChatSession.session_token == session_token,
                    ChatSession.patient_id == patient_id,
                    ChatSession.is_active == 1
                )
            ).first()
            
            if session:
                return session_token
        
        return self.create_session(patient_id)

    def get_session_history(
        self,
        session_token: str,
        limit: int = MAX_HISTORY_MESSAGES
    ) -> List[Tuple[str, str]]:
        session = self._db.query(ChatSession).filter(
            ChatSession.session_token == session_token
        ).first()
        
        if not session:
            return []
        
        messages = self._db.query(ChatMessageRecord).filter(
            ChatMessageRecord.session_id == session.id
        ).order_by(ChatMessageRecord.created_at.desc()).limit(limit).all()
        
        history = []
        for msg in reversed(messages):
            history.append((msg.role, msg.content))
        
        return history

    def add_message(
        self,
        session_token: str,
        role: str,
        content: str,
        references: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None
    ) -> int:
        session = self._db.query(ChatSession).filter(
            ChatSession.session_token == session_token
        ).first()
        
        if not session:
            raise SessionNotFoundError(f"Session not found: {session_token}")
        
        message = ChatMessageRecord(
            session_id=session.id,
            role=role,
            content=content,
            references=references,
            confidence=confidence
        )
        self._db.add(message)
        self._db.commit()
        
        return message.id

    def ask(
        self,
        query: str,
        patient_id: int,
        session_token: Optional[str] = None
    ) -> QAResponse:
        session_token = self.get_or_create_session(patient_id, session_token)
        
        self.add_message(session_token, "user", query)
        
        context = self._build_case_context(patient_id)
        retrieved_docs = self._retrieve_relevant_documents(query, patient_id)
        
        context_text = self._format_context_for_prompt(context, retrieved_docs)
        history = self.get_session_history(session_token)
        
        answer, confidence, reasoning = self._generate_answer(
            query, context_text, history, patient_id
        )
        
        references = self._create_references(retrieved_docs)
        
        ref_dicts = [
            {
                "id": r.reference_id,
                "type": r.reference_type,
                "label": r.label,
                "url": r.url
            }
            for r in references
        ]
        self.add_message(session_token, "assistant", answer, ref_dicts, confidence)
        
        return QAResponse(
            answer=answer,
            sources=references,
            confidence=confidence,
            reasoning=reasoning
        )

    def ask_stream(
        self,
        query: str,
        patient_id: int,
        skill_name: Optional[str] = None,
        session_token: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        session_token = self.get_or_create_session(patient_id, session_token)
        self.add_message(session_token, "user", query)

        if skill_name:
            yield from self._execute_skill_stream(skill_name, query, patient_id, session_token)
            return

        yield from self._stream_rag_response(query, patient_id, session_token)

    def _execute_skill_stream(
        self,
        skill_name: str,
        query: str,
        patient_id: int,
        session_token: str
    ) -> Iterator[Dict[str, Any]]:
        from services.skill_base import create_skill_registry, SkillContext

        registry = create_skill_registry()
        skill = registry.get(skill_name)

        if not skill:
            yield {"type": "error", "content": f"Skill not found: {skill_name}"}
            yield {"type": "done", "content": "", "session_token": session_token}
            return

        llm_client = self._get_llm_client(patient_id)
        case_context = self._build_case_context(patient_id)
        context = SkillContext(
            query=query,
            patient_id=patient_id,
            db_session=self._db,
            llm_client=llm_client,
            case_context=self._format_case_context_brief(case_context)
        )

        if skill.skill_type == "prompt_injection" and llm_client:
            yield from self._stream_prompt_injection_skill(skill, context, session_token)
        else:
            # Send progress message for tool_call skills (may take time)
            yield {
                "type": "skill_progress",
                "content": f"正在执行 {skill.description.split(' - ')[0] if ' - ' in skill.description else skill.name}...",
                "skill_name": skill_name,
                "skill_type": skill.skill_type,
            }
            result = skill.execute(context)
            yield {
                "type": "skill_result",
                "content": result.content,
                "skill_name": skill_name,
                "skill_type": skill.skill_type,
                "references": [
                    {"id": r.reference_id, "type": r.reference_type, "label": r.label}
                    for r in result.references
                ],
                "confidence": result.confidence,
            }
            self.add_message(session_token, "assistant", result.content)
            yield {"type": "done", "content": "", "session_token": session_token}

    def _stream_prompt_injection_skill(
        self,
        skill,
        context,
        session_token: str
    ) -> Iterator[Dict[str, Any]]:
        result = skill.execute(context)
        full_content = result.content

        chunk_size = 20
        for i in range(0, len(full_content), chunk_size):
            yield {
                "type": "chunk",
                "content": full_content[i:i + chunk_size],
                "skill_name": skill.name,
                "skill_type": skill.skill_type,
            }

        self.add_message(session_token, "assistant", full_content)
        yield {
            "type": "done",
            "content": "",
            "session_token": session_token,
            "references": [
                {"id": r.reference_id, "type": r.reference_type, "label": r.label}
                for r in result.references
            ],
            "confidence": result.confidence,
        }

    def _stream_rag_response(
        self,
        query: str,
        patient_id: int,
        session_token: str
    ) -> Iterator[Dict[str, Any]]:
        context = self._build_case_context(patient_id)
        retrieved_docs = self._retrieve_relevant_documents(query, patient_id)
        context_text = self._format_context_for_prompt(context, retrieved_docs)
        history = self.get_session_history(session_token)

        llm_client = self._get_llm_client(patient_id)

        if llm_client:
            try:
                settings = self._settings_service.get_llm_settings(patient_id) if self._settings_service else None
                temperature = settings.temperature if settings else 0.7
                max_tokens = settings.max_tokens if settings else 1024

                prompt = self._build_rag_prompt(query, context_text, history)
                messages = [{"role": "user", "content": prompt}]

                full_content = ""
                for chunk in llm_client.chat_stream(messages, temperature=temperature, max_tokens=max_tokens):
                    full_content += chunk
                    yield {"type": "chunk", "content": chunk}

                references = self._create_references(retrieved_docs)
                ref_dicts = [
                    {"id": r.reference_id, "type": r.reference_type, "label": r.label}
                    for r in references
                ]
                self.add_message(session_token, "assistant", full_content, ref_dicts, 0.85)

                yield {
                    "type": "done",
                    "content": "",
                    "session_token": session_token,
                    "references": ref_dicts,
                    "confidence": 0.85,
                }
                return
            except LLMClientError as e:
                logger.error(f"LLM streaming error: {e}, falling back to mock")

        answer, confidence, _ = self._generate_answer(query, context_text, history, patient_id)
        references = self._create_references(retrieved_docs)
        ref_dicts = [
            {"id": r.reference_id, "type": r.reference_type, "label": r.label}
            for r in references
        ]
        self.add_message(session_token, "assistant", answer, ref_dicts, confidence)

        chunk_size = 20
        for i in range(0, len(answer), chunk_size):
            yield {"type": "chunk", "content": answer[i:i + chunk_size]}

        yield {
            "type": "done",
            "content": "",
            "session_token": session_token,
            "references": ref_dicts,
            "confidence": confidence,
        }

    def _format_case_context_brief(self, context: CaseContext) -> str:
        parts = []
        if context.patient_info:
            parts.append(context.patient_info)
        if context.variant_info:
            parts.append("; ".join(context.variant_info[:3]))
        return " | ".join(parts)

    def index_case_document(
        self,
        patient_id: int,
        document_type: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        from services.embedding_service import IndexNotBuiltError, ModelNotLoadedError

        document = CaseDocument(
            patient_id=patient_id,
            document_type=document_type,
            title=title,
            content=content,
            metadata=metadata
        )
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        
        try:
            embedding = self._embedding_service.generate_embedding(content)
            
            import pickle
            embedding_record = CaseEmbedding(
                document_id=document.id,
                embedding_vector=pickle.dumps(embedding),
                embedding_model=self._embedding_service._model_name,
                vector_dimension=len(embedding)
            )
            self._db.add(embedding_record)
            self._db.commit()
            
            self._embedding_service.add_document(document.id, content, metadata)
        except (IndexNotBuiltError, ModelNotLoadedError, ImportError) as e:
            logger.warning(f"Embedding generation skipped for document {document.id}: {e}")
        
        logger.info(f"Indexed document {document.id} for patient {patient_id}")
        return document.id

    def index_patient_variants(self, patient_id: int) -> int:
        indexed = 0
        
        patient_context = self._build_patient_context(patient_id)
        if patient_context:
            self.index_case_document(
                patient_id=patient_id,
                document_type="patient_summary",
                title=f"Patient {patient_id} Summary",
                content=patient_context
            )
            indexed += 1
        
        variant_contexts = self._build_variant_context(patient_id, limit=20)
        for i, (variant_text, metadata) in enumerate(variant_contexts):
            self.index_case_document(
                patient_id=patient_id,
                document_type="variant_report",
                title=f"Variant Report {i+1}",
                content=variant_text,
                metadata=metadata
            )
            indexed += 1
        
        logger.info(f"Indexed {indexed} documents for patient {patient_id}")
        return indexed

    def end_session(self, session_token: str) -> bool:
        session = self._db.query(ChatSession).filter(
            ChatSession.session_token == session_token
        ).first()
        
        if not session:
            return False
        
        session.is_active = 0
        self._db.commit()
        
        logger.info(f"Ended session {session_token}")
        return True


def create_rag_service(
    db: Session,
    embedding_service: Optional[EmbeddingService] = None,
    llm_client: Optional[LLMClient] = None,
    settings_service: Optional[SettingsService] = None
) -> RAGService:
    return RAGService(
        db=db,
        embedding_service=embedding_service,
        llm_client=llm_client,
        settings_service=settings_service
    )
