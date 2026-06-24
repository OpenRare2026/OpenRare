"""
Tests for DELETE /cases/{patient_id} endpoint - TDD Red Phase.
These tests are expected to FAIL until the endpoint is implemented.
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database import Patient, VCFFile, Variant, ACMGClassification
from database.case_models import CaseDocument, CaseEmbedding, ChatSession, ChatMessageRecord, LLMSettings


@pytest.fixture
def db_engine():
    """Create a file-based SQLite database engine for testing."""
    import tempfile
    import os
    
    # Use a temporary file for the database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_engine):
    """Create a TestClient with database dependency override."""
    from fastapi.testclient import TestClient
    from main import app
    from database import get_db
    
    def override_get_db():
        Session = sessionmaker(bind=db_engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patient(db_session):
    """Create a sample patient for testing."""
    patient = Patient(
        id=1,
        name="Test Patient",
        age=30,
        sex="M",
        ethnicity="Asian",
        diagnosis_description="Test diagnosis",
        medical_history="Test history"
    )
    db_session.add(patient)
    db_session.commit()
    return patient


@pytest.fixture
def sample_vcf_file(db_session, sample_patient):
    """Create a sample VCF file for testing."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.vcf', delete=False) as f:
        f.write(b"##fileformat=VCFv4.2\n")
        temp_path = f.name
    
    vcf = VCFFile(
        id=1,
        file_name="test.vcf",
        file_path=temp_path,
        patient_id=sample_patient.id,
        upload_date=datetime.utcnow()
    )
    db_session.add(vcf)
    db_session.commit()
    
    yield vcf
    
    # Cleanup temp file if it exists
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_variant(db_session, sample_vcf_file):
    """Create a sample variant for testing."""
    variant = Variant(
        id=1,
        chromosome="chr1",
        position=1000,
        ref="A",
        alt="T",
        variant_type="SNV",
        vcf_file_id=sample_vcf_file.id
    )
    db_session.add(variant)
    db_session.commit()
    return variant


@pytest.fixture
def sample_case_document(db_session, sample_patient):
    """Create a sample case document for testing."""
    doc = CaseDocument(
        id=1,
        patient_id=sample_patient.id,
        document_type="patient_summary",
        title="Test Document",
        content="Test content"
    )
    db_session.add(doc)
    db_session.commit()
    return doc


@pytest.fixture
def sample_chat_session(db_session, sample_patient):
    """Create a sample chat session for testing."""
    session = ChatSession(
        id=1,
        patient_id=sample_patient.id,
        session_token="test-token-123",
        is_active=1
    )
    db_session.add(session)
    db_session.commit()
    return session


@pytest.fixture
def sample_llm_settings(db_session, sample_patient):
    """Create sample LLM settings for testing."""
    settings = LLMSettings(
        id=1,
        patient_id=sample_patient.id,
        provider="openai",
        api_key="sk-test",
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=1024,
        is_active=1
    )
    db_session.add(settings)
    db_session.commit()
    return settings


class TestDeleteCaseEndpoint:
    """Test cases for DELETE /cases/{patient_id} endpoint."""

    def test_delete_case_success(self, client, db_session, sample_patient, sample_vcf_file):
        """
        Test successful deletion of a case.
        DELETE existing case should return 200 and delete Patient + all related data.
        """
        patient_id = sample_patient.id
        
        # Verify patient exists before deletion
        patient_before = db_session.query(Patient).filter(Patient.id == patient_id).first()
        assert patient_before is not None
        
        # Delete the case
        response = client.delete(f"/api/cases/{patient_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Case deleted"
        assert data["patient_id"] == patient_id
        
        # Verify patient is deleted
        db_session.expire_all()
        patient_after = db_session.query(Patient).filter(Patient.id == patient_id).first()
        assert patient_after is None
        
        # Verify VCF file is deleted (cascade)
        vcf_after = db_session.query(VCFFile).filter(VCFFile.patient_id == patient_id).first()
        assert vcf_after is None

    def test_delete_case_not_found(self, client):
        """
        Test deletion of non-existent case.
        DELETE non-existent patient_id should return 404.
        """
        # Try to delete non-existent patient
        response = client.delete("/api/cases/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Case not found"

    def test_delete_case_cleans_vcf_files(self, client, db_session, sample_patient, sample_vcf_file):
        """
        Test that VCF files on disk are deleted when case is deleted.
        """
        patient_id = sample_patient.id
        file_path = sample_vcf_file.file_path
        
        # Verify VCF file exists on disk
        assert os.path.exists(file_path)
        
        # Delete the case
        response = client.delete(f"/api/cases/{patient_id}")
        
        assert response.status_code == 200
        
        # Verify VCF file is deleted from disk
        assert not os.path.exists(file_path)

    def test_delete_case_cleans_non_cascaded(
        self, 
        client, 
        db_session, 
        sample_patient, 
        sample_case_document,
        sample_chat_session,
        sample_llm_settings
    ):
        """
        Test that non-cascaded records are deleted:
        - CaseDocument
        - ChatSession
        - LLMSettings
        """
        patient_id = sample_patient.id
        
        # Verify records exist before deletion
        assert db_session.query(CaseDocument).filter(CaseDocument.patient_id == patient_id).count() > 0
        assert db_session.query(ChatSession).filter(ChatSession.patient_id == patient_id).count() > 0
        assert db_session.query(LLMSettings).filter(LLMSettings.patient_id == patient_id).count() > 0
        
        # Delete the case
        response = client.delete(f"/api/cases/{patient_id}")
        
        assert response.status_code == 200
        
        # Verify non-cascaded records are deleted
        db_session.expire_all()
        assert db_session.query(CaseDocument).filter(CaseDocument.patient_id == patient_id).count() == 0
        assert db_session.query(ChatSession).filter(ChatSession.patient_id == patient_id).count() == 0
        assert db_session.query(LLMSettings).filter(LLMSettings.patient_id == patient_id).count() == 0

    def test_delete_case_clears_faiss_index(self, client, db_session, sample_patient, sample_case_document):
        """
        Test that embedding_service.clear_index() is called after CaseDocument deletion.
        """
        patient_id = sample_patient.id
        
        with patch('services.embedding_service.get_embedding_service') as mock_get_service:
            mock_service = MagicMock()
            mock_service.clear_index.return_value = True
            mock_get_service.return_value = mock_service
            
            # Delete the case
            response = client.delete(f"/api/cases/{patient_id}")
            
            assert response.status_code == 200
            # Verify clear_index was called
            mock_service.clear_index.assert_called_once()

    def test_delete_case_file_missing_on_disk(self, client, db_session, sample_patient):
        """
        Test that deletion succeeds even if VCF file doesn't exist on disk.
        Should log a warning but not throw an error.
        """
        patient_id = sample_patient.id
        
        # Create a VCF file record with non-existent file path
        vcf = VCFFile(
            id=99,
            file_name="missing.vcf",
            file_path="/non/existent/path/missing.vcf",
            patient_id=patient_id,
            upload_date=datetime.utcnow()
        )
        db_session.add(vcf)
        db_session.commit()
        
        # Verify file doesn't exist
        assert not os.path.exists(vcf.file_path)
        
        # Delete the case - should not raise error
        response = client.delete(f"/api/cases/{patient_id}")
        
        assert response.status_code == 200
        
        # Verify patient is still deleted
        db_session.expire_all()
        patient_after = db_session.query(Patient).filter(Patient.id == patient_id).first()
        assert patient_after is None
