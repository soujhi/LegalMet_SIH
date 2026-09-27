from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.models.models import (
    UserRole, ApplicationStatus, ApplicationType, VerificationResult, CertificateStatus, SourceProvenance
)

# ----------------- Auth Schemas -----------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.TRADER
    phone: Optional[str] = None
    organization_name: Optional[str] = None
    trade_name: Optional[str] = None
    state: Optional[str] = "Jharkhand"
    district: Optional[str] = "Hazaribagh"
    address: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool
    organization_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Organization & Instrument Schemas -----------------

class OrganizationOut(BaseModel):
    id: int
    name: str
    trade_name: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    state: str
    district: Optional[str] = None
    pincode: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    class Config:
        from_attributes = True

class InstrumentCategoryOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    standard_rule_ref: Optional[str] = None

    class Config:
        from_attributes = True

class InstrumentModelOut(BaseModel):
    id: int
    category_id: int
    certificate_no: Optional[str] = None
    application_no: Optional[str] = None
    issue_date: Optional[str] = None
    file_number: Optional[str] = None
    company_name: Optional[str] = None
    manufacturer: str
    brand: str
    model_series: str
    equipment: Optional[str] = None
    instrument_type: Optional[str] = None
    accuracy_class: str
    max_capacity: Optional[float] = None
    min_capacity: Optional[float] = None
    verification_scale_interval: Optional[float] = None
    capacity_unit: Optional[str] = "kg"
    raw_capacity: Optional[str] = None
    raw_min_capacity: Optional[str] = None
    raw_scale_interval: Optional[str] = None
    display_type: Optional[str] = "Digital LED/LCD"
    working_principle: Optional[str] = "Strain Gauge Load Cell"
    load_cell_make: Optional[str] = None
    load_cell_model: Optional[str] = None
    load_cell_class: Optional[str] = None
    load_cell_capacity: Optional[str] = None
    software_version: Optional[str] = None
    checksum: Optional[str] = None
    approval_mark: Optional[str] = None
    approval_date: Optional[str] = None
    sealing_details: Optional[str] = None
    approval_coverage: Optional[str] = None
    n_value: Optional[str] = None
    e_value: Optional[str] = None
    source_pdf: Optional[str] = None
    source_url: Optional[str] = None
    source_provenance: SourceProvenance
    extraction_method: Optional[str] = "PDF_TEXT"
    extraction_confidence: Optional[float] = 95.0
    manual_verified: Optional[bool] = False
    raw_extracted_text: Optional[str] = None

    class Config:
        from_attributes = True

class ModelUpdate(BaseModel):
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model_series: Optional[str] = None
    instrument_type: Optional[str] = None
    accuracy_class: Optional[str] = None
    max_capacity: Optional[float] = None
    min_capacity: Optional[float] = None
    verification_scale_interval: Optional[float] = None
    capacity_unit: Optional[str] = None
    approval_mark: Optional[str] = None
    load_cell_make: Optional[str] = None
    load_cell_model: Optional[str] = None
    software_version: Optional[str] = None
    checksum: Optional[str] = None
    sealing_details: Optional[str] = None
    approval_coverage: Optional[str] = None
    manual_verified: Optional[bool] = True

class DataQualityStats(BaseModel):
    total_models: int
    doca_models: int
    ocr_models: int
    manual_models: int
    manual_verified_count: int
    high_confidence_count: int
    missing_fields_summary: Dict[str, int]
    accuracy_class_distribution: Dict[str, int]

class InstrumentCreate(BaseModel):
    category_id: int
    model_id: Optional[int] = None
    serial_number: str
    asset_number: Optional[str] = None
    capacity: float
    unit: str = "kg"
    accuracy_class: str = "Class III"
    verification_scale_interval: float = 5.0
    location: Optional[str] = None

class InstrumentOut(BaseModel):
    id: int
    organization_id: int
    category_id: int
    model_id: Optional[int] = None
    serial_number: str
    asset_number: Optional[str] = None
    capacity: float
    unit: str
    accuracy_class: str
    verification_scale_interval: float
    location: Optional[str] = None
    status: str
    last_verified_date: Optional[datetime] = None
    next_verification_date: Optional[datetime] = None
    source_provenance: SourceProvenance
    created_at: datetime
    category: Optional[InstrumentCategoryOut] = None
    model: Optional[InstrumentModelOut] = None
    organization: Optional[OrganizationOut] = None

    class Config:
        from_attributes = True

# ----------------- PRD Section 7: Reconciliation Schemas -----------------

class ReconcileRequest(BaseModel):
    manufacturer: str
    model_query: str
    capacity: Optional[float] = None
    accuracy_class: Optional[str] = None

class ReconcileResponse(BaseModel):
    status: str  # MATCH, AMBIGUOUS, NO_MATCH
    match_score: float
    review_required: bool
    matched_model: Optional[Dict[str, Any]] = None
    candidates: List[Dict[str, Any]] = []
    source_pdf: Optional[str] = None
    matched_fields: List[str] = []
    unmatched_fields: List[str] = []
    explanation: str

class MatchReviewRequest(BaseModel):
    model_id: Optional[int] = None
    status: str = "REVIEWED"
    remarks: Optional[str] = None

# ----------------- Application Schemas -----------------

class ApplicationCreate(BaseModel):
    instrument_id: int
    application_type: ApplicationType = ApplicationType.RE_VERIFICATION
    documents: Optional[List[Dict[str, str]]] = None

class StatusUpdate(BaseModel):
    status: ApplicationStatus
    remarks: Optional[str] = None

class OfficerAssign(BaseModel):
    officer_id: int
    scheduled_at: datetime
    remarks: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    application_number: str
    instrument_id: int
    applicant_id: int
    organization_id: Optional[int] = None
    application_type: ApplicationType
    status: ApplicationStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    assigned_officer_id: Optional[int] = None
    payment_status: str
    payment_amount: float
    created_at: datetime
    updated_at: datetime
    instrument: Optional[InstrumentOut] = None
    applicant: Optional[UserOut] = None

    class Config:
        from_attributes = True

# ----------------- Verification & Testing Schemas -----------------

class TestObservationInput(BaseModel):
    test_name: str
    test_type: str  # ZERO_LOAD, HALF_CAPACITY, MAX_CAPACITY, ECCENTRICITY, REPEATABILITY
    test_load: float
    expected_value: float
    observed_value: float
    unit: str = "kg"
    remarks: Optional[str] = None

class RuleEvaluationRequest(BaseModel):
    category_code: str = "NAWI"
    accuracy_class: str = "Class III"
    capacity: float
    verification_scale_interval: float  # e in grams or kg
    unit: str = "kg"
    test_type: str
    test_load: float
    observed_value: float

class RuleEvaluationResponse(BaseModel):
    is_compliant: bool
    result: VerificationResult
    test_load: float
    observed_value: float
    error_calculated: float
    tolerance_mpe: float
    unit: str
    mpe_formula: str
    rule_code: str
    is_verified_government_rule: bool
    rule_source_reference: str
    explanation: str

class VerificationStartRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy: Optional[float] = None
    location_address: Optional[str] = None
    device_timestamp: Optional[datetime] = None

class VerificationCompleteRequest(BaseModel):
    observations: List[TestObservationInput]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy: Optional[float] = None
    location_address: Optional[str] = None
    device_timestamp: Optional[datetime] = None
    remarks: Optional[str] = None
    photos: Optional[List[str]] = None
    signature_data: Optional[str] = None

# ----------------- Certificate Schemas -----------------

class CertificateOut(BaseModel):
    id: int
    certificate_number: str
    instrument_id: int
    application_id: int
    verification_session_id: int
    issue_date: datetime
    valid_from: datetime
    valid_until: datetime
    status: CertificateStatus
    pdf_url: Optional[str] = None
    qr_token: str
    certificate_hash: str
    issuing_officer_name: str
    verification_location: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime
    instrument: Optional[InstrumentOut] = None

    class Config:
        from_attributes = True

class PublicVerificationResponse(BaseModel):
    is_valid: bool
    status: str  # VALID, EXPIRED, REVOKED, NOT_FOUND
    certificate_number: str
    instrument_category: Optional[str] = None
    instrument_model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    capacity: Optional[str] = None
    accuracy_class: Optional[str] = None
    verification_date: Optional[str] = None
    valid_until: Optional[str] = None
    issuing_authority: Optional[str] = None
    issuing_officer: Optional[str] = None
    verification_location: Optional[str] = None
    certificate_hash: Optional[str] = None
    record_integrity_verified: Optional[bool] = True
    tamper_detected: Optional[bool] = False
    computed_hash: Optional[str] = None
    stored_hash: Optional[str] = None
    integrity_status: Optional[str] = "RECORD_INTEGRITY_VERIFIED"
    disclaimer: Optional[str] = "Application-level cryptographic SHA-256 fingerprint verification (Tamper Detection). Not a government PKI digital signature."
    model_approval_reference: Optional[Dict[str, Any]] = None
    tests_summary: Optional[List[Dict[str, Any]]] = None
    message: str

# ----------------- OCR & Audit Schemas -----------------

class OCRDocumentOut(BaseModel):
    id: int
    source_file: str
    certificate_no: Optional[str] = None
    area: Optional[str] = None
    concern_name: Optional[str] = None
    verification_date: Optional[str] = None
    next_verification_date: Optional[str] = None
    instrument_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capacity: Optional[str] = None
    accuracy_class: Optional[str] = None
    verification_fee: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    ocr_confidence: float
    manual_verified: bool
    source_type: SourceProvenance
    created_at: datetime

    class Config:
        from_attributes = True

class OCRValidateRequest(BaseModel):
    certificate_no: Optional[str] = None
    concern_name: Optional[str] = None
    verification_date: Optional[str] = None
    next_verification_date: Optional[str] = None
    instrument_type: Optional[str] = None
    manufacturer: Optional[str] = None
    capacity: Optional[str] = None
    accuracy_class: Optional[str] = None
    verification_fee: Optional[str] = None
    manual_verified: bool = True
