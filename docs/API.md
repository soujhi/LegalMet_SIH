# API Surface & Endpoints Specification

## Base URL
`/api`

## Authentication & Session
- `POST /api/auth/login`: Authenticate with email and password. Returns JWT access token and user payload.
- `POST /api/auth/register`: Register a new commercial trader establishment and proprietor user.
- `GET /api/auth/me`: Get current authenticated user profile and jurisdiction.

## Instruments Master
- `GET /api/instruments`: List registered instruments (filtered by trader organization or all for admin).
- `POST /api/instruments`: Register a new weighing/measuring instrument against DoCA approved models.
- `GET /api/instruments/{id}`: Fetch detailed instrument record with category and model specs.
- `PUT /api/instruments/{id}`: Update instrument parameters or installation location.
- `GET /api/instruments/categories`: List supported instrument categories (NAWI, AWI, etc.).
- `GET /api/instruments/models`: List DoCA approved models with technical specs.

## Verification Applications
- `GET /api/applications`: List applications (supports status filters).
- `POST /api/applications`: Submit new verification or re-verification application.
- `GET /api/applications/{id}`: Get application details and linked instrument.
- `PUT /api/applications/{id}/status`: Scrutinize application status (APPROVE / QUERY / REJECT / RESUBMITTED).
- `GET /api/applications/{id}/timeline`: Retrieve chronological status history audit trail.

## Scheduling & Assignment
- `GET /api/schedule/officers`: List active Legal Metrology Officers and jurisdictions.
- `GET /api/schedule`: List approved applications pending field assignment.
- `POST /api/schedule/assign/{application_id}`: Assign an LMO officer and schedule inspection timestamp.

## LMO Field Verification & Rule Engine
- `POST /api/verification/start/{application_id}`: Initiate field verification session and lock GPS/timestamp.
- `POST /api/verification/{application_id}/complete`: Submit field test observations, evaluate MPE compliance, and trigger certificate issuance on PASS or risk logging on FAIL.
- `POST /api/rules/evaluate`: Interactive simulator endpoint for deterministic MPE calculation.
- `GET /api/rules`: List all codified statutory rules and source citations.

## Certificates & Public Verification
- `GET /api/certificates`: List issued certificates.
- `GET /api/certificates/{id}`: Retrieve single certificate details.
- `GET /api/certificates/{id}/pdf`: Download official signed PDF certificate.
- `GET /api/public/verify/{certificate_number}`: Open public endpoint (no auth required) to verify QR token or certificate number.

## OCR Legacy Digitization
- `GET /api/ocr`: List scanned legacy certificate records with OCR confidence scores.
- `GET /api/ocr/{id}`: Get raw OCR text and extracted fields for a legacy document.
- `PUT /api/ocr/{id}/validate`: Save human-verified fields and mark `manual_verified=True`.
- `POST /api/ocr/upload`: Upload a new scanned certificate image/PDF for OCR extraction.

## Analytics & Audit
- `GET /api/analytics/dashboard`: Retrieve compliance KPIs, pass/fail counts, and district breakdowns.
- `GET /api/audit-logs`: Fetch system-wide immutable audit trail.
