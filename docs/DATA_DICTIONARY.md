# Data Dictionary & Database Specification

This document details the database schema (18 tables) implemented in LegalMet Verify.

## 1. Core Tables

### `organizations`
- `id` (INTEGER, PK): Unique organization ID.
- `name` (VARCHAR): Legal enterprise name.
- `trade_name` (VARCHAR): Registered trade / storefront name.
- `registration_number` (VARCHAR): Government establishment registration / GST.
- `address`, `district`, `state`, `pincode`: Establishment physical location.
- `contact_email`, `contact_phone`: Official communication coordinates.

### `users`
- `id` (INTEGER, PK): User identifier.
- `email` (VARCHAR, UNIQUE): Login email.
- `hashed_password` (VARCHAR): Bcrypt salted password hash.
- `full_name` (VARCHAR): User legal name.
- `role` (ENUM): `TRADER`, `ADMIN`, `LMO`, `PUBLIC`.
- `organization_id` (FK -> organizations.id): Associated enterprise.

### `officers`
- `id` (INTEGER, PK): Officer profile identifier.
- `user_id` (FK -> users.id, UNIQUE): Linked user account.
- `officer_code` (VARCHAR, UNIQUE): Official departmental code (e.g., `LMO-JH-001`).
- `designation` (VARCHAR): Official post.
- `jurisdiction_state`, `jurisdiction_district`: Geographical authority boundary.
- `badge_number` (VARCHAR): Departmental identity badge.

### `instrument_categories`
- `id` (INTEGER, PK): Category identifier.
- `code` (VARCHAR, UNIQUE): Code (e.g. `NAWI`, `AWI`, `CAP_MEASURE`).
- `name` (VARCHAR): Category title.
- `standard_rule_ref` (VARCHAR): Relevant Schedule reference under LM Rules 2011.

### `instrument_models` (Layer A: DoCA Model Approval Master)
- `id` (INTEGER, PK): Model approval ID.
- `category_id` (FK -> instrument_categories.id): Category.
- `manufacturer`, `brand`, `model_series`: Make and model series.
- `accuracy_class`: `Class I`, `Class II`, `Class III`, `Class IIII`.
- `max_capacity`, `min_capacity`: Operating range.
- `verification_scale_interval`: Scale verification interval ($e$) in grams.
- `approval_mark` (VARCHAR): DoCA Model Approval number (e.g., `IND/09/2022/145`).
- `source_provenance` (ENUM): `DOCA_MODEL_APPROVAL`.

### `instruments`
- `id` (INTEGER, PK): Physical instrument record ID.
- `organization_id` (FK -> organizations.id): Owner enterprise.
- `category_id` (FK -> instrument_categories.id): Category.
- `model_id` (FK -> instrument_models.id): Approved model reference.
- `serial_number` (VARCHAR): Stamped manufacturer serial number.
- `capacity`, `unit`, `accuracy_class`, `verification_scale_interval`: Physical specs.
- `status`: `ACTIVE`, `VERIFIED`, `PENDING_VERIFICATION`, `QUARANTINED`.
- `last_verified_date`, `next_verification_date`: Statutory cycle timestamps.

### `applications`
- `id` (INTEGER, PK): Application ID.
- `application_number` (VARCHAR, UNIQUE): Formatted tracking number (`LM-APP-YYYYMM-XXXXX`).
- `instrument_id` (FK -> instruments.id): Target instrument.
- `applicant_id` (FK -> users.id): Applicant.
- `application_type`: `INITIAL_VERIFICATION`, `RE_VERIFICATION`.
- `status`: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `QUERIED`, `RESUBMITTED`, `APPROVED`, `SCHEDULED`, `ASSIGNED`, `FIELD_VERIFICATION`, `PASSED`, `FAILED`, `CERTIFICATE_ISSUED`, `REJECTED`.
- `scheduled_at` (TIMESTAMP): Inspection appointment.
- `assigned_officer_id` (FK -> officers.id): Assigned field inspector.

### `verification_sessions`
- `id` (INTEGER, PK): Inspection session ID.
- `application_id` (FK -> applications.id, UNIQUE): Linked application.
- `officer_id` (FK -> officers.id): Field officer.
- `started_at`, `completed_at`: Verification duration.
- `latitude`, `longitude`, `location_accuracy`, `location_address`: Field GPS lock.
- `overall_result`: `PASS`, `FAIL`, `IN_PROGRESS`.
- `photos_json` (JSON): Field photos evidence URLs.

### `verification_tests`
- `id` (INTEGER, PK): Test observation ID.
- `session_id` (FK -> verification_sessions.id): Session.
- `test_name`, `test_type`: `ZERO_LOAD`, `HALF_CAPACITY`, `MAX_CAPACITY`, `ECCENTRICITY`.
- `test_load`, `expected_value`, `observed_value`: Numerical readings.
- `tolerance_mpe`: Calculated Maximum Permissible Error limit.
- `error_calculated`: Observed value minus test load.
- `result`: `PASS` or `FAIL`.

### `certificates`
- `id` (INTEGER, PK): Certificate ID.
- `certificate_number` (VARCHAR, UNIQUE): Statutory certificate number (`LM/JH/YYYY/XXXXXX`).
- `instrument_id`, `application_id`, `verification_session_id`: Relational links.
- `issue_date`, `valid_from`, `valid_until`: Validity window.
- `status`: `VALID`, `EXPIRED`, `REVOKED`.
- `pdf_url` (VARCHAR): Generated PDF certificate path.
- `qr_token` (VARCHAR, UNIQUE): Unique UUID for QR linking.
- `certificate_hash` (VARCHAR): SHA-256 digital fingerprint.
- `issuing_officer_id`, `issuing_officer_name`: Authorized signatory.

### `regulatory_rules`
- `id` (INTEGER, PK): Rule ID.
- `rule_code` (VARCHAR, UNIQUE): Code (e.g. `LM-NAWI-CL3-R1`).
- `accuracy_class`, `test_type`, `min_range_e`, `max_range_e`, `mpe_formula`, `mpe_multiplier`.
- `is_verified_government_rule` (BOOLEAN): Source authenticity flag.
- `rule_source_reference` (VARCHAR): Official gazette / statutory schedule citation.

### `ocr_documents` (Layer B: State Field Scans)
- `id` (INTEGER, PK): OCR record ID.
- `source_file`, `certificate_no`, `area`, `concern_name`, `verification_date`, `capacity`, `accuracy_class`.
- `raw_ocr_text` (TEXT): Unedited OCR text stream.
- `ocr_confidence` (FLOAT): Extraction confidence percentage.
- `manual_verified` (BOOLEAN): Human validation flag (`True` after officer approval).
- `source_type` (ENUM): `GOVERNMENT_PORTAL`, `OCR`.
