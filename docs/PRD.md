# LegalMet Verify (SIH26036) — Product Requirements Document (PRD)

## 1. Executive Summary
**LegalMet Verify** is a digital lifecycle management platform for weighing and measuring instruments under the Legal Metrology Act, 2009. The platform connects commercial stakeholders (traders/manufacturers), legal metrology administrators, field inspection officers (LMO/GATC), and citizens/consumers into an integrated, transparent, and auditable verification ecosystem.

## 2. Problem Statement & Goals
- **Eliminate manual paperwork & fragmented tracking:** Replace paper records and uncoordinated verification registers with a centralized statutory lifecycle workflow.
- **Traceable Verification Chain:** Maintain end-to-end provenance from instrument registration and administrative scrutiny to field inspection observations, rule engine evaluation, and certificate issuance.
- **Mobile-First Field Verification:** Provide Legal Metrology Officers with GPS-locked, timestamped, and photo-evidenced mobile verification tools.
- **Deterministic Regulatory Compliance:** Apply statutory Maximum Permissible Error (MPE) calculations strictly under the Legal Metrology (General) Rules, 2011 (Seventh Schedule) without arbitrary AI hallucination.
- **Public Trust & Anti-Counterfeiting:** Enable instant public authentication of certificates via tamper-proof QR codes and SHA-256 digital certificate fingerprints.
- **Assisted Legacy Digitization:** Ingest historical state inspection records with OCR confidence metrics while enforcing mandatory human officer validation before certifying.

## 3. User Roles & Capabilities
1. **Trader / Commercial Stakeholder:**
   - Registers enterprise and instruments against DoCA Model Approval catalog.
   - Files initial verification and periodic re-verification applications.
   - Tracks application status timeline and responds to scrutiny queries.
   - Accesses digital certificate vault to view and download PDF certificates.
2. **Legal Metrology Administrator:**
   - Scrutinizes submitted applications (Approve / Query / Reject).
   - Assigns LMO inspectors and schedules on-site field appointments.
   - Oversees statutory regulatory rule sets and MPE limit configurations.
   - Monitors state-wide compliance metrics, risk flags, and audit trails.
   - Reviews and validates legacy OCR records.
3. **Legal Metrology Officer (LMO / GATC):**
   - Receives daily queue of assigned field inspections on a mobile-friendly interface.
   - Captures GPS coordinates, device timestamp, and physical establishment photos.
   - Records standard weight load test observations (Zero, Half, Max capacity, Eccentricity).
   - Triggers deterministic Rule Engine to evaluate Pass/Fail compliance.
   - Submits results; automatically generates digital QR certificate upon passing.
4. **Public / Consumer:**
   - Scans certificate QR code or enters certificate number without login.
   - Verifies validity status (VALID / EXPIRED / REVOKED / NOT FOUND).
   - Inspects instrument capacity, class, verification date, and issuing authority without exposing private personal data.

## 4. Application State Machine
```
[DRAFT]
  ↓
[SUBMITTED]
  ↓
[UNDER_REVIEW] ──(Query)──→ [QUERIED] ──(Resubmit)──→ [UNDER_REVIEW]
  ↓
[APPROVED] / [REJECTED]
  ↓
[SCHEDULED & ASSIGNED]
  ↓
[FIELD_VERIFICATION]
  ↓
[VERIFICATION_COMPLETED]
  ↓
  ├── PASS ──→ [CERTIFICATE_ISSUED] (PDF + QR Generated)
  └── FAIL ──→ [FAILED] (Risk Flag Recorded)
```
