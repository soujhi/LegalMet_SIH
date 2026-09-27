import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    TRADER = "TRADER"
    ADMIN = "ADMIN"
    LMO = "LMO"
    PUBLIC = "PUBLIC"

class ApplicationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    QUERIED = "QUERIED"
    RESUBMITTED = "RESUBMITTED"
    APPROVED = "APPROVED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    SCHEDULED = "SCHEDULED"
    ASSIGNED = "ASSIGNED"
    FIELD_VERIFICATION = "FIELD_VERIFICATION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CERTIFICATE_ISSUED = "CERTIFICATE_ISSUED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REVERIFICATION_DUE = "REVERIFICATION_DUE"

class ApplicationType(str, enum.Enum):
    INITIAL_VERIFICATION = "INITIAL_VERIFICATION"
    RE_VERIFICATION = "RE_VERIFICATION"

class VerificationResult(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

class CertificateStatus(str, enum.Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class SourceProvenance(str, enum.Enum):
    GOVERNMENT_PORTAL = "GOVERNMENT_PORTAL"
    DOCA_MODEL_APPROVAL = "DOCA_MODEL_APPROVAL"
    OCR = "OCR"
    MANUAL = "MANUAL"
    DEMO_DATA = "DEMO_DATA"

# ----------------- Models -----------------

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    registration_number = Column(String(100), unique=True, nullable=True)
    address = Column(Text, nullable=True)
    state = Column(String(100), nullable=False, default="Jharkhand")
    district = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    users = relationship("User", back_populates="organization")
    instruments = relationship("Instrument", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TRADER, nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    organization = relationship("Organization", back_populates="users")
    officer_profile = relationship("Officer", back_populates="user", uselist=False)
    applications = relationship("Application", foreign_keys="Application.applicant_id", back_populates="applicant")


class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    officer_code = Column(String(50), unique=True, nullable=False)
    designation = Column(String(150), default="Legal Metrology Officer (LMO)")
    jurisdiction_state = Column(String(100), default="Jharkhand")
    jurisdiction_district = Column(String(100), default="Hazaribagh / Barhi")
    badge_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="officer_profile")
    verification_sessions = relationship("VerificationSession", back_populates="officer")


class InstrumentCategory(Base):
    __tablename__ = "instrument_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    standard_rule_ref = Column(String(255), default="Legal Metrology (General) Rules, 2011 - Seventh Schedule")

    models = relationship("InstrumentModel", back_populates="category")
    instruments = relationship("Instrument", back_populates="category")
    rules = relationship("RegulatoryRule", back_populates="category")


class InstrumentModel(Base):
    __tablename__ = "instrument_models"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("instrument_categories.id"), nullable=False)
    certificate_no = Column(String(100), nullable=True, index=True)
    application_no = Column(String(100), nullable=True)
    issue_date = Column(String(50), nullable=True)
    file_number = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=False)
    model_series = Column(String(255), nullable=False)
    equipment = Column(String(255), nullable=True)
    instrument_type = Column(String(255), nullable=True)
    accuracy_class = Column(String(50), nullable=False, default="Class III")  # Class I, Class II, Class III, Class IIII
    max_capacity = Column(Float, nullable=True, default=30.0)
    min_capacity = Column(Float, nullable=True, default=0.1)
    verification_scale_interval = Column(Float, nullable=True, default=5.0)  # 'e' value
    capacity_unit = Column(String(20), default="kg")
    raw_capacity = Column(String(255), nullable=True)
    raw_min_capacity = Column(String(255), nullable=True)
    raw_scale_interval = Column(String(255), nullable=True)
    display_type = Column(String(100), default="Digital LED/LCD")
    working_principle = Column(String(255), default="Strain Gauge Load Cell")
    load_cell_make = Column(String(255), nullable=True)
    load_cell_model = Column(String(255), nullable=True)
    load_cell_class = Column(String(100), nullable=True)
    load_cell_capacity = Column(String(100), nullable=True)
    software_version = Column(String(100), nullable=True)
    checksum = Column(String(100), nullable=True)
    approval_mark = Column(String(100), nullable=True, index=True)
    approval_date = Column(String(50), nullable=True)
    sealing_details = Column(Text, nullable=True)
    approval_coverage = Column(Text, nullable=True)
    n_value = Column(String(100), nullable=True)
    e_value = Column(String(100), nullable=True)
    source_pdf = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    source_provenance = Column(SQLEnum(SourceProvenance), default=SourceProvenance.DOCA_MODEL_APPROVAL)
    extraction_method = Column(String(50), default="PDF_TEXT")
    extraction_confidence = Column(Float, nullable=True, default=95.0)
    manual_verified = Column(Boolean, default=False)
    raw_extracted_text = Column(Text, nullable=True)

    category = relationship("InstrumentCategory", back_populates="models")
    instruments = relationship("Instrument", back_populates="model")


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("instrument_categories.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("instrument_models.id"), nullable=True)
    serial_number = Column(String(100), index=True, nullable=False)
    asset_number = Column(String(100), nullable=True)
    capacity = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    accuracy_class = Column(String(50), default="Class III")
    verification_scale_interval = Column(Float, default=5.0)  # e.g., 5g
    location = Column(String(255), nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, PENDING_VERIFICATION, EXPIRED, QUARANTINED
    last_verified_date = Column(DateTime, nullable=True)
    next_verification_date = Column(DateTime, nullable=True)
    source_provenance = Column(SQLEnum(SourceProvenance), default=SourceProvenance.DEMO_DATA)
    created_at = Column(DateTime, default=utc_now)

    organization = relationship("Organization", back_populates="instruments")
    category = relationship("InstrumentCategory", back_populates="instruments")
    model = relationship("InstrumentModel", back_populates="instruments")
    applications = relationship("Application", back_populates="instrument")
    certificates = relationship("Certificate", back_populates="instrument")
    risk_flags = relationship("RiskFlag", back_populates="instrument")
    model_matches = relationship("ModelMatch", back_populates="instrument")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(100), unique=True, index=True, nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    application_type = Column(SQLEnum(ApplicationType), default=ApplicationType.RE_VERIFICATION)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False)
    
    submitted_at = Column(DateTime, default=utc_now)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    scheduled_at = Column(DateTime, nullable=True)
    assigned_officer_id = Column(Integer, ForeignKey("officers.id"), nullable=True)
    
    payment_status = Column(String(50), default="PAID")  # PAID, PENDING, EXEMPT
    payment_amount = Column(Float, default=250.0)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    instrument = relationship("Instrument", back_populates="applications")
    applicant = relationship("User", foreign_keys=[applicant_id], back_populates="applications")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    assigned_officer = relationship("Officer")
    status_history = relationship("ApplicationStatusHistory", back_populates="application")
    documents = relationship("ApplicationDocument", back_populates="application")
    verification_session = relationship("VerificationSession", back_populates="application", uselist=False)
    certificate = relationship("Certificate", back_populates="application", uselist=False)


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=True)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    application = relationship("Application", back_populates="status_history")
    changed_by = relationship("User")


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # INVOICE, PREVIOUS_CERTIFICATE, MODEL_APPROVAL
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=utc_now)

    application = relationship("Application", back_populates="documents")


class VerificationSession(Base):
    __tablename__ = "verification_sessions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    officer_id = Column(Integer, ForeignKey("officers.id"), nullable=False)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    
    # Field geo-evidence
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_accuracy = Column(Float, nullable=True)
    location_address = Column(String(500), nullable=True)
    device_timestamp = Column(DateTime, nullable=True)
    
    overall_result = Column(SQLEnum(VerificationResult), default=VerificationResult.IN_PROGRESS)
    remarks = Column(Text, nullable=True)
    photos_json = Column(JSON, nullable=True)  # List of photo objects / URLs
    signature_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    application = relationship("Application", back_populates="verification_session")
    officer = relationship("Officer", back_populates="verification_sessions")
    tests = relationship("VerificationTest", back_populates="session", cascade="all, delete-orphan")
    certificate = relationship("Certificate", back_populates="verification_session", uselist=False)
    evidence = relationship("VerificationEvidence", back_populates="session", cascade="all, delete-orphan")
    measurements = relationship("VerificationMeasurement", back_populates="session", cascade="all, delete-orphan")
    rule_evaluations = relationship("RuleEvaluation", back_populates="session", cascade="all, delete-orphan")


class VerificationTest(Base):
    __tablename__ = "verification_tests"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("verification_sessions.id"), nullable=False)
    test_name = Column(String(150), nullable=False)
    test_type = Column(String(100), nullable=False)  # ZERO_LOAD, HALF_CAPACITY, MAX_CAPACITY, ECCENTRICITY, REPEATABILITY
    test_load = Column(Float, nullable=False)
    expected_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    tolerance_mpe = Column(Float, nullable=False)
    error_calculated = Column(Float, nullable=False)
    result = Column(SQLEnum(VerificationResult), nullable=False)
    rule_applied_id = Column(Integer, ForeignKey("regulatory_rules.id"), nullable=True)
    remarks = Column(Text, nullable=True)

    session = relationship("VerificationSession", back_populates="tests")
    rule = relationship("RegulatoryRule")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(100), unique=True, index=True, nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    verification_session_id = Column(Integer, ForeignKey("verification_sessions.id"), unique=True, nullable=False)
    
    issue_date = Column(DateTime, default=utc_now)
    valid_from = Column(DateTime, default=utc_now)
    valid_until = Column(DateTime, nullable=False)
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.VALID)
    
    pdf_url = Column(String(500), nullable=True)
    qr_token = Column(String(255), unique=True, index=True, nullable=False)
    certificate_hash = Column(String(128), nullable=False)
    
    issuing_officer_id = Column(Integer, ForeignKey("officers.id"), nullable=False)
    issuing_officer_name = Column(String(255), nullable=False)
    verification_location = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    instrument = relationship("Instrument", back_populates="certificates")
    application = relationship("Application", back_populates="certificate")
    verification_session = relationship("VerificationSession", back_populates="certificate")
    issuing_officer = relationship("Officer")
    logs = relationship("CertificateVerificationLog", back_populates="certificate")


class CertificateVerificationLog(Base):
    __tablename__ = "certificate_verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=True)
    certificate_number = Column(String(100), nullable=False)
    verified_at = Column(DateTime, default=utc_now)
    verifier_ip = Column(String(100), nullable=True)
    verifier_user_agent = Column(String(500), nullable=True)
    verification_status_found = Column(String(50), nullable=False)
    lookup_type = Column(String(50), default="QR_SCAN")

    certificate = relationship("Certificate", back_populates="logs")


class RegulatoryRule(Base):
    __tablename__ = "regulatory_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(100), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("instrument_categories.id"), nullable=False)
    accuracy_class = Column(String(50), nullable=False)  # Class I, Class II, Class III, Class IIII
    test_type = Column(String(100), nullable=False)
    min_range_e = Column(Float, nullable=False)  # Range lower bound in multiples of verification scale interval 'e'
    max_range_e = Column(Float, nullable=False)  # Range upper bound in multiples of 'e'
    mpe_formula = Column(String(100), nullable=False)  # e.g., "±1.0 e" or "±1.5 e" or "±0.5 e"
    mpe_multiplier = Column(Float, nullable=False)  # 0.5, 1.0, 1.5, 2.0
    is_verified_government_rule = Column(Boolean, default=True)
    rule_source_reference = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    category = relationship("InstrumentCategory", back_populates="rules")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    old_values_json = Column(JSON, nullable=True)
    new_values_json = Column(JSON, nullable=True)
    ip_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO")
    is_read = Column(Boolean, default=False)
    link_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User")


class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    flag_type = Column(String(100), nullable=False)
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    instrument = relationship("Instrument", back_populates="risk_flags")


class OCRDocument(Base):
    __tablename__ = "ocr_documents"

    id = Column(Integer, primary_key=True, index=True)
    source_file = Column(String(255), nullable=False)
    certificate_no = Column(String(100), nullable=True)
    area = Column(String(100), default="BARHI")
    concern_name = Column(String(255), nullable=True)
    verification_date = Column(String(50), nullable=True)
    next_verification_date = Column(String(50), nullable=True)
    instrument_type = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    capacity = Column(String(100), nullable=True)
    accuracy_class = Column(String(50), nullable=True)
    verification_fee = Column(String(50), nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, default=0.0)
    manual_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_type = Column(SQLEnum(SourceProvenance), default=SourceProvenance.GOVERNMENT_PORTAL)
    created_at = Column(DateTime, default=utc_now)

    reviews = relationship("OCRReview", back_populates="document", cascade="all, delete-orphan")


# ----------------- PRD Section 31 Database Additions -----------------

class VerificationEvidence(Base):
    """
    Evidence bundle connecting physical inspection to verification decision.
    Front/nameplate/serial/display/seal/test-setup photos & documents with SHA-256 integrity.
    """
    __tablename__ = "verification_evidence"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verification_sessions.id"), nullable=False)
    evidence_type = Column(String(100), nullable=False)  # FRONT_NAMEPLATE, SERIAL_NUMBER, SEAL_WIRE, TEST_SETUP, SUPPORTING_DOC
    file_path = Column(String(500), nullable=False)
    sha256 = Column(String(64), nullable=False)
    captured_at = Column(DateTime, default=utc_now)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    uploaded_by = Column(String(255), nullable=True)

    session = relationship("VerificationSession", back_populates="evidence")


class VerificationMeasurement(Base):
    """
    Structured measurement entries with deterministic error calculation and unit normalization.
    """
    __tablename__ = "verification_measurements"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verification_sessions.id"), nullable=False)
    test_name = Column(String(150), nullable=False)
    reference_value = Column(Float, nullable=False)
    reference_unit = Column(String(20), default="kg")
    observed_value = Column(Float, nullable=False)
    observed_unit = Column(String(20), default="kg")
    calculated_error = Column(Float, nullable=False)
    result = Column(String(50), nullable=False)  # PASS, FAIL, REVIEW_REQUIRED

    session = relationship("VerificationSession", back_populates="measurements")


class RuleEvaluation(Base):
    """
    Audit record linking physical observation to statutory rule, MPE, and explainable decision.
    """
    __tablename__ = "rule_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verification_sessions.id"), nullable=False)
    rule_id = Column(String(100), nullable=False)
    input_snapshot = Column(JSON, nullable=True)
    mpe_value = Column(Float, nullable=False)
    mpe_unit = Column(String(20), default="kg")
    calculated_error = Column(Float, nullable=False)
    decision = Column(String(50), nullable=False)  # PASS, FAIL, REVIEW_REQUIRED
    source_reference = Column(String(500), nullable=False)
    evaluated_at = Column(DateTime, default=utc_now)

    session = relationship("VerificationSession", back_populates="rule_evaluations")


class ModelMatch(Base):
    """
    Reconciliation record between physical trader instrument and official DoCA Model Approval catalog.
    Distinguishes MATCH (source PDF linked), AMBIGUOUS (manual review required), and NO_MATCH.
    """
    __tablename__ = "model_matches"

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("instrument_models.id"), nullable=True)
    match_method = Column(String(50), default="EXACT")  # EXACT, FUZZY, MANUAL
    match_score = Column(Float, default=1.0)
    status = Column(String(50), default="MATCH")  # MATCH, AMBIGUOUS, NO_MATCH, REVIEWED
    review_required = Column(Boolean, default=False)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    matched_fields = Column(JSON, nullable=True)
    unmatched_fields = Column(JSON, nullable=True)
    source_pdf = Column(String(255), nullable=True)

    instrument = relationship("Instrument", back_populates="model_matches")
    model = relationship("InstrumentModel")


class OCRReview(Base):
    """
    Human-in-the-loop review for legacy scanned verification documents.
    Uncertain OCR fields (< 80% confidence) are routed for human sign-off before entering rule engine.
    """
    __tablename__ = "ocr_review"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("ocr_documents.id"), nullable=False)
    field_name = Column(String(100), nullable=False)  # capacity, accuracy_class, manufacturer, model, etc.
    raw_value = Column(String(255), nullable=True)
    normalized_value = Column(String(255), nullable=True)
    confidence = Column(Float, default=0.0)
    review_status = Column(String(50), default="PENDING_REVIEW")  # PENDING_REVIEW, HUMAN_VERIFIED, REJECTED
    verified_value = Column(String(255), nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    document = relationship("OCRDocument", back_populates="reviews")
