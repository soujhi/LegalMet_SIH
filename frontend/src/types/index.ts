export type UserRole = 'TRADER' | 'ADMIN' | 'LMO' | 'PUBLIC';

export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'QUERIED'
  | 'RESUBMITTED'
  | 'APPROVED'
  | 'PAYMENT_PENDING'
  | 'SCHEDULED'
  | 'ASSIGNED'
  | 'FIELD_VERIFICATION'
  | 'VERIFICATION_COMPLETED'
  | 'PASSED'
  | 'FAILED'
  | 'CERTIFICATE_ISSUED'
  | 'REJECTED'
  | 'CANCELLED'
  | 'EXPIRED';

export type VerificationResult = 'PASS' | 'FAIL' | 'IN_PROGRESS';

export type CertificateStatus = 'VALID' | 'EXPIRED' | 'REVOKED';

export type SourceProvenance =
  | 'GOVERNMENT_PORTAL'
  | 'DOCA_MODEL_APPROVAL'
  | 'OCR'
  | 'MANUAL'
  | 'DEMO_DATA';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  organization_id?: number;
  organization_name?: string;
  officer_id?: number;
  officer_code?: string;
  jurisdiction?: string;
}

export interface InstrumentCategory {
  id: number;
  code: string;
  name: string;
  description?: string;
  standard_rule_ref?: string;
}

export interface InstrumentModel {
  id: number;
  category_id: number;
  certificate_no?: string;
  application_no?: string;
  issue_date?: string;
  file_number?: string;
  company_name?: string;
  manufacturer: string;
  brand: string;
  model_series: string;
  equipment?: string;
  instrument_type?: string;
  accuracy_class: string;
  max_capacity: number;
  min_capacity?: number;
  verification_scale_interval: number;
  capacity_unit: string;
  raw_capacity?: string;
  raw_min_capacity?: string;
  raw_scale_interval?: string;
  display_type?: string;
  working_principle?: string;
  load_cell_make?: string;
  load_cell_model?: string;
  load_cell_class?: string;
  load_cell_capacity?: string;
  software_version?: string;
  checksum?: string;
  approval_mark?: string;
  approval_date?: string;
  sealing_details?: string;
  approval_coverage?: string;
  n_value?: string;
  e_value?: string;
  source_pdf?: string;
  source_url?: string;
  source_provenance: SourceProvenance;
  extraction_method?: string;
  extraction_confidence?: number;
  manual_verified?: boolean;
  raw_extracted_text?: string;
}

export interface DataQualityStats {
  total_models: number;
  doca_models: number;
  ocr_models: number;
  manual_models: number;
  manual_verified_count: number;
  high_confidence_count: number;
  missing_fields_summary: {
    load_cell_model: number;
    approval_coverage: number;
    checksum: number;
    software_version: number;
    sealing_details: number;
  };
  accuracy_class_distribution: Record<string, number>;
}

export interface Instrument {
  id: number;
  organization_id: number;
  category_id: number;
  model_id?: number;
  serial_number: string;
  asset_number?: string;
  capacity: number;
  unit: string;
  accuracy_class: string;
  verification_scale_interval: number;
  location?: string;
  status: string;
  last_verified_date?: string;
  next_verification_date?: string;
  source_provenance: SourceProvenance;
  created_at: string;
  category?: InstrumentCategory;
  model?: InstrumentModel;
}

export interface Application {
  id: number;
  application_number: string;
  instrument_id: number;
  applicant_id: number;
  organization_id?: number;
  application_type: 'INITIAL_VERIFICATION' | 'RE_VERIFICATION';
  status: ApplicationStatus;
  submitted_at: string;
  reviewed_at?: string;
  reviewer_notes?: string;
  scheduled_at?: string;
  assigned_officer_id?: number;
  payment_status: string;
  payment_amount: number;
  created_at: string;
  updated_at: string;
  instrument?: Instrument;
  applicant?: User;
}

export interface ApplicationTimelineEvent {
  id: number;
  from_status?: string;
  to_status: string;
  remarks?: string;
  changed_by: string;
  created_at: string;
}

export interface TestObservation {
  test_name: string;
  test_type: string;
  test_load: number;
  expected_value: number;
  observed_value: number;
  unit?: string;
  remarks?: string;
}

export interface RuleEvaluationResult {
  is_compliant: boolean;
  result: VerificationResult;
  test_load: number;
  observed_value: number;
  error_calculated: number;
  tolerance_mpe: number;
  unit: string;
  mpe_formula: string;
  rule_code: string;
  is_verified_government_rule: boolean;
  rule_source_reference: string;
  explanation: string;
}

export interface Certificate {
  id: number;
  certificate_number: string;
  instrument_id: number;
  application_id: number;
  verification_session_id: number;
  issue_date: string;
  valid_from: string;
  valid_until: string;
  status: CertificateStatus;
  pdf_url?: string;
  qr_token: string;
  certificate_hash: string;
  issuing_officer_name: string;
  verification_location?: string;
  remarks?: string;
  created_at: string;
  instrument?: Instrument;
}

export interface PublicVerification {
  is_valid: boolean;
  status: string;
  certificate_number: string;
  instrument_category?: string;
  instrument_model?: string;
  manufacturer?: string;
  serial_number?: string;
  capacity?: string;
  accuracy_class?: string;
  verification_date?: string;
  valid_until?: string;
  issuing_authority?: string;
  issuing_officer?: string;
  verification_location?: string;
  certificate_hash?: string;
  record_integrity_verified?: boolean;
  tamper_detected?: boolean;
  computed_hash?: string;
  stored_hash?: string;
  integrity_status?: string;
  disclaimer?: string;
  model_approval_reference?: {
    model_id: number;
    certificate_no?: string;
    approval_mark?: string;
    manufacturer: string;
    brand: string;
    model_series: string;
    accuracy_class: string;
    max_capacity: string;
    verification_scale_interval: string;
    source_pdf?: string;
    provenance: string;
  };
  tests_summary?: any[];
  message: string;
}

export interface OCRDocument {
  id: number;
  source_file: string;
  certificate_no?: string;
  area?: string;
  concern_name?: string;
  verification_date?: string;
  next_verification_date?: string;
  instrument_type?: string;
  manufacturer?: string;
  model?: string;
  capacity?: string;
  accuracy_class?: string;
  verification_fee?: string;
  raw_ocr_text?: string;
  ocr_confidence: number;
  manual_verified: boolean;
  source_type: SourceProvenance;
  created_at: string;
}

export interface DashboardMetrics {
  summary: {
    total_instruments: number;
    total_applications: number;
    pending_scrutiny: number;
    assigned_inspections: number;
    total_certificates: number;
    valid_certificates: number;
    expiring_soon: number;
    passed_verifications: number;
    failed_verifications: number;
    total_risk_flags: number;
    ocr_digitized_total: number;
    ocr_verified_count: number;
    total_public_scans: number;
  };
  monthly_trend: Array<{ month: string; inspections: number; passed: number; failed: number }>;
  district_breakdown: Array<{ district: string; instruments: number; compliance_rate: string }>;
}
