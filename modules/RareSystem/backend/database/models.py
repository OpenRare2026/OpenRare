"""
SQLAlchemy Data Models for Rare Disease Genetic Diagnosis System
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, func, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class Patient(Base):
    """
    Patient model - stores de-identified patient information.
    
    Note: Only de-identified characteristics are stored.
    No personally identifiable information (PII) should be stored.
    """
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)  # De-identified identifier (e.g., "Patient_001")
    age = Column(Integer, nullable=True)  # Age at time of analysis
    sex = Column(String(20), nullable=True)  # M/F/Other
    ethnicity = Column(String(100), nullable=True)  # Self-reported or inferred ethnicity
    diagnosis_description = Column(Text, nullable=True)  # Clinical phenotype description
    medical_history = Column(Text, nullable=True)  # Relevant medical history
    hpo_terms = Column(JSON, nullable=True)  # Extracted HPO terms from clinical notes
    
    # Relationships
    vcf_files = relationship("VCFFile", back_populates="patient", cascade="all, delete-orphan")
    clinical_reports = relationship("ClinicalReport", back_populates="patient", cascade="all, delete-orphan")
    research_reports = relationship("ResearchReport", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"


class VCFFile(Base):
    """
    VCF File model - stores metadata about uploaded VCF files.
    """
    __tablename__ = "vcf_files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)  # Original file name
    file_path = Column(String(512), nullable=False)  # Path to stored file
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="vcf_files")
    variants = relationship("Variant", back_populates="vcf_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VCFFile(id={self.id}, file_name='{self.file_name}')>"


class Variant(Base):
    """
    Variant model - stores genetic variant information detected from VCF files.
    
    Supports multiple variant types:
    - SNV (Single Nucleotide Variant)
    - INDEL (Insertion/Deletion)
    - STR (Short Tandem Repeat)
    - CNV (Copy Number Variation)
    """
    __tablename__ = "variants"
    
    id = Column(Integer, primary_key=True, index=True)
    chromosome = Column(String(10), nullable=False, index=True)  # e.g., "chr1", "chrX"
    position = Column(Integer, nullable=False, index=True)  # 1-based genomic position
    ref = Column(String(512), nullable=False)  # Reference allele
    alt = Column(String(512), nullable=False)  # Alternate allele(s)
    variant_type = Column(String(50), nullable=False, index=True)  # SNV, INDEL, STR, CNV
    quality = Column(Float, nullable=True)  # Quality score from variant caller
    filter_status = Column(String(50), nullable=True)  # PASS or filter flags
    info_field = Column(JSON, nullable=True)  # Additional INFO field data
    gene = Column(String(100), nullable=True, index=True)  # Gene symbol from GFF3 annotation
    vcf_file_id = Column(Integer, ForeignKey("vcf_files.id"), nullable=False)

    # VEP annotation fields
    hgvs_c = Column(String(255), nullable=True)
    hgvs_p = Column(String(255), nullable=True)
    consequence = Column(String(200), nullable=True)
    impact = Column(String(50), nullable=True)
    transcript = Column(String(50), nullable=True)
    all_genes = Column(String(500), nullable=True)
    cdna_position = Column(String(50), nullable=True)
    cds_position = Column(String(50), nullable=True)
    protein_position = Column(String(50), nullable=True)
    amino_acids = Column(String(100), nullable=True)
    codons = Column(String(100), nullable=True)
    exon = Column(String(50), nullable=True)
    intron = Column(String(50), nullable=True)
    strand = Column(String(10), nullable=True)
    protein_domains = Column(String(500), nullable=True)
    revel_score = Column(Float, nullable=True)
    cadd = Column(Float, nullable=True)
    spliceai_ds_max = Column(Float, nullable=True)
    spliceai_type = Column(String(50), nullable=True)
    loftee_lof_flag = Column(String(50), nullable=True)
    loftee_lof_filter = Column(String(200), nullable=True)
    clinvar_significance = Column(String(100), nullable=True)
    clinvar_review_status = Column(String(200), nullable=True)
    clinvar_star_rating = Column(Integer, nullable=True)
    sift = Column(String(100), nullable=True)
    polyphen = Column(String(100), nullable=True)
    gnomad_popmax_af = Column(Float, nullable=True)
    gnomad_eas_af = Column(Float, nullable=True)
    gnomad_nhomalt = Column(Integer, nullable=True)
    pathogenic_rank = Column(Integer, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    vep_annotated = Column(Boolean, default=False)
    
    __table_args__ = (
        UniqueConstraint('chromosome', 'position', 'ref', 'alt', 'vcf_file_id', name='uix_variant_unique'),
    )
    
    # Relationships
    vcf_file = relationship("VCFFile", back_populates="variants")
    acmg_evidence = relationship("ACMGEvidence", back_populates="variant", cascade="all, delete-orphan")
    acmg_classification = relationship("ACMGClassification", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Variant(id={self.id}, chr={self.chromosome}:{self.position}, {self.ref}>{self.alt})>"


class ACMGEvidence(Base):
    """
    ACMG Evidence model - stores evidence for ACMG/AMP classification criteria.
    
    Evidence levels:
    - Very Strong (PVS1)
    - Strong (PS1-PS4)
    - Moderate (PM1-PM6)
    - Supporting (PP1-PP5)
    - Benign Standalone (BA1)
    - Benign Strong (BS1-BS4)
    - Benign Moderate (BP1-BP7)
    """
    __tablename__ = "acmg_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)
    criterion = Column(String(10), nullable=False, index=True)  # e.g., "PVS1", "PS1", "PM2"
    evidence_level = Column(String(50), nullable=False)  # Very Strong, Strong, Moderate, Supporting, Benign
    description = Column(Text, nullable=False)  # Detailed evidence description
    evidence_source = Column(String(255), nullable=True)  # Database or literature source
    is_applied = Column(Boolean, default=True, nullable=False)  # Whether this criterion is applied
    
    # Relationships
    variant = relationship("Variant", back_populates="acmg_evidence")
    
    def __repr__(self):
        return f"<ACMGEvidence(id={self.id}, variant_id={self.variant_id}, criterion={self.criterion})>"


class ACMGClassification(Base):
    """
    ACMG Classification model - stores final ACMG/AMP classification for a variant.
    
    Classification categories:
    - Pathogenic
    - Likely Pathogenic
    - Variant of Uncertain Significance (VUS)
    - Likely Benign
    - Benign
    """
    __tablename__ = "acmg_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False, unique=True)
    classification = Column(String(50), nullable=False, index=True)  # Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0 confidence in classification
    classification_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    classifier_version = Column(String(50), nullable=True)  # Version of classification algorithm
    notes = Column(Text, nullable=True)  # Additional notes or comments
    
    # Relationships
    variant = relationship("Variant", back_populates="acmg_classification")
    
    def __repr__(self):
        return f"<ACMGClassification(id={self.id}, variant_id={self.variant_id}, classification={self.classification})>"


class ClinicalReport(Base):
    """
    Clinical Report model - stores clinical-grade reports for patient variants.
    
    Clinical track requirements:
    - ACMG classification compliance
    - Fully verified evidence chains
    - Traceable to source data
    - Editable by clinicians
    """
    __tablename__ = "clinical_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    report_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    report_content = Column(Text, nullable=False)  # Full report content (HTML or structured JSON)
    report_version = Column(String(20), nullable=True)  # Version number for tracking edits
    is_final = Column(Boolean, default=False, nullable=False)  # Whether report is finalized
    clinician_id = Column(String(100), nullable=True)  # ID of reviewing clinician
    review_date = Column(DateTime, nullable=True)  # Date of clinician review
    
    # Relationships
    patient = relationship("Patient", back_populates="clinical_reports")
    
    def __repr__(self):
        return f"<ClinicalReport(id={self.id}, patient_id={self.patient_id}, report_date={self.report_date})>"


class ResearchReport(Base):
    """
    Research Report model - stores research-track hypotheses and findings.
    
    Research track characteristics:
    - Exploratory findings
    - Documented uncertainty
    - Hypothesis generation
    - NOT for clinical decision-making
    - Must have clear uncertainty quantification
    """
    __tablename__ = "research_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    report_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    hypotheses = Column(Text, nullable=False)  # Research hypotheses (structured JSON or text)
    uncertainty_metrics = Column(JSON, nullable=True)  # Quantified uncertainty measures
    evidence_gaps = Column(Text, nullable=True)  # Identified gaps in evidence
    priority_score = Column(Float, nullable=True)  # 0.0-1.0 priority for follow-up
    is_reviewed = Column(Boolean, default=False, nullable=False)  # Whether reviewed by researcher
    
    # Relationships
    patient = relationship("Patient", back_populates="research_reports")
    
    def __repr__(self):
        return f"<ResearchReport(id={self.id}, patient_id={self.patient_id}, report_date={self.report_date})>"


class VEPJob(Base):
    __tablename__ = "vep_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True)
    vcf_file_id = Column(Integer, ForeignKey("vcf_files.id"), nullable=False)
    status = Column(String(50), nullable=False, default="queued")
    input_filename = Column(String(255), nullable=True)
    input_bytes = Column(Integer, nullable=True)
    options = Column(JSON, nullable=True)
    status_url = Column(String(500), nullable=True)
    result_url = Column(String(500), nullable=True)
    log_url = Column(String(500), nullable=True)
    rows = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    vcf_file = relationship("VCFFile", backref="vep_jobs")

    def __repr__(self):
        return f"<VEPJob(job_id={self.job_id}, status={self.status})>"


class HPOJob(Base):
    """
    HPO Job model - tracks async HPO extraction jobs.
    
    Status flow: queued -> processing -> completed/failed
    Results are stored in the results column as JSON when complete.
    """
    __tablename__ = "hpo_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    clinical_note = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="queued")
    results = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    patient = relationship("Patient", backref="hpo_jobs")
    
    def __repr__(self):
        return f"<HPOJob(job_id={self.job_id}, status={self.status})>"
