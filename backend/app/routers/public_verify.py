from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.models.models import Certificate, CertificateVerificationLog, CertificateStatus
from app.schemas.schemas import PublicVerificationResponse

router = APIRouter(prefix="/public", tags=["Public Verification"])

@router.get("/verify/{certificate_number:path}", response_model=PublicVerificationResponse)
def verify_certificate_public(
    certificate_number: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Normalize certificate number (strip whitespace, decode slashes)
    cert_no = certificate_number.strip()

    cert = db.query(Certificate).filter(
        (Certificate.certificate_number == cert_no) | 
        (Certificate.qr_token == cert_no)
    ).first()

    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown Browser")

    if not cert:
        # Also check Jharkhand legacy OCR records if available
        # Still log unverified attempt
        log = CertificateVerificationLog(
            certificate_number=cert_no,
            verifier_ip=ip_address,
            verifier_user_agent=user_agent,
            verification_status_found="NOT_FOUND",
            lookup_type="PUBLIC_LOOKUP"
        )
        db.add(log)
        db.commit()

        return PublicVerificationResponse(
            is_valid=False,
            status="NOT_FOUND",
            certificate_number=cert_no,
            message="No matching legal metrology certificate found in the central registry."
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    # Ensure cert.valid_until is timezone-aware if comparing
    valid_until = cert.valid_until
    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)

    status_str = cert.status.value
    if status_str == "VALID" and now > valid_until:
        status_str = "EXPIRED"

    # Log public scan
    log = CertificateVerificationLog(
        certificate_id=cert.id,
        certificate_number=cert.certificate_number,
        verifier_ip=ip_address,
        verifier_user_agent=user_agent,
        verification_status_found=status_str,
        lookup_type="QR_SCAN"
    )
    db.add(log)
    db.commit()

    inst = cert.instrument
    session = cert.verification_session

    tests_summary = []
    if session and session.tests:
        for t in session.tests:
            tests_summary.append({
                "test_name": t.test_name,
                "test_load": f"{t.test_load} {t.unit}",
                "observed_value": f"{t.observed_value} {t.unit}",
                "error": f"{t.error_calculated:+.4f} {t.unit}",
                "tolerance_mpe": f"±{t.tolerance_mpe} {t.unit}",
                "result": t.result.value
            })

    return PublicVerificationResponse(
        is_valid=(status_str == "VALID"),
        status=status_str,
        certificate_number=cert.certificate_number,
        instrument_category=inst.category.name if inst and inst.category else "Weighing Instrument",
        instrument_model=f"{inst.model.brand} - {inst.model.model_series}" if inst and inst.model else "Commercial Scale",
        manufacturer=inst.model.manufacturer if inst and inst.model else "Nilkanth Digital Scale CO.",
        serial_number=inst.serial_number if inst else "N/A",
        capacity=f"{inst.capacity} {inst.unit}" if inst else "N/A",
        accuracy_class=inst.accuracy_class if inst else "Class III",
        verification_date=cert.issue_date.strftime("%d-%B-%Y"),
        valid_until=cert.valid_until.strftime("%d-%B-%Y"),
        issuing_authority="Department of Legal Metrology, Government of Jharkhand",
        issuing_officer=cert.issuing_officer_name,
        verification_location=cert.verification_location or "Barhi Sub-Division",
        certificate_hash=cert.certificate_hash,
        tests_summary=tests_summary,
        message="Official Legal Metrology Verification record authenticated successfully."
    )
