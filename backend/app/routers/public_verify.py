from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.core.database import get_db
from app.models.models import Certificate, CertificateVerificationLog, CertificateStatus
from app.schemas.schemas import PublicVerificationResponse
from app.services.certificate_generator import certificate_generator

router = APIRouter(prefix="/public", tags=["Public Verification"])

@router.get("/verify/{certificate_number:path}", response_model=PublicVerificationResponse)
def verify_certificate_public(
    certificate_number: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public QR Verification Endpoint.
    Distinguishes Certificate Record Existence from Cryptographic Record Integrity.
    Links physical verification to statutory DoCA Model Approval reference.
    """
    # Normalize certificate number (strip whitespace, decode slashes)
    cert_no = certificate_number.strip()

    cert = db.query(Certificate).filter(
        (Certificate.certificate_number == cert_no) | 
        (Certificate.qr_token == cert_no)
    ).first()

    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown Browser")

    if not cert:
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
            record_integrity_verified=False,
            tamper_detected=False,
            integrity_status="CERTIFICATE_NOT_FOUND",
            message="No matching legal metrology certificate found in the central registry."
        )

    # Check expiration
    now = datetime.now(timezone.utc)
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

    # Cryptographic Hash Integrity Recomputation
    model_series_val = (
        inst.model.model_series if inst and inst.model
        else (inst.asset_number or "Commercial Scale")
    )
    canonical_payload = certificate_generator.build_canonical_hash_payload(
        certificate_number=cert.certificate_number,
        serial_number=inst.serial_number if inst else "",
        category=inst.category.name if inst and inst.category else "",
        model_series=model_series_val,
        capacity=f"{inst.capacity} {inst.unit}" if inst else "",
        issue_date=cert.issue_date.isoformat(),
        valid_until=cert.valid_until.isoformat(),
        issuing_officer=cert.issuing_officer_name,
        verification_location=cert.verification_location or ""
    )
    recomputed_hash = certificate_generator.compute_certificate_hash(canonical_payload)
    is_integrity_valid = (recomputed_hash == cert.certificate_hash)

    # Format official DoCA model approval reference
    model_ref = None
    if inst and inst.model:
        model_ref = {
            "model_id": inst.model.id,
            "certificate_no": inst.model.certificate_no,
            "approval_mark": inst.model.approval_mark,
            "manufacturer": inst.model.manufacturer,
            "brand": inst.model.brand,
            "model_series": inst.model.model_series,
            "accuracy_class": inst.model.accuracy_class,
            "max_capacity": f"{inst.model.max_capacity} {inst.model.capacity_unit or 'kg'}",
            "verification_scale_interval": f"{inst.model.verification_scale_interval} g",
            "source_pdf": inst.model.source_pdf,
            "provenance": inst.model.source_provenance.value if hasattr(inst.model.source_provenance, 'value') else str(inst.model.source_provenance)
        }

    tests_summary = []
    if session and session.tests:
        for t in session.tests:
            tests_summary.append({
                "test_name": t.test_name,
                "test_type": t.test_type,
                "test_load": f"{t.test_load} {t.unit}",
                "expected_value": f"{t.expected_value} {t.unit}",
                "observed_value": f"{t.observed_value} {t.unit}",
                "error": f"{t.error_calculated:+.4f} {t.unit}",
                "tolerance_mpe": f"±{t.tolerance_mpe} {t.unit}",
                "result": t.result.value,
                "remarks": t.remarks
            })

    return PublicVerificationResponse(
        is_valid=(status_str == "VALID" and is_integrity_valid),
        status=status_str if is_integrity_valid else "TAMPER_DETECTED",
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
        record_integrity_verified=is_integrity_valid,
        tamper_detected=(not is_integrity_valid),
        computed_hash=recomputed_hash,
        stored_hash=cert.certificate_hash,
        integrity_status="RECORD_INTEGRITY_VERIFIED" if is_integrity_valid else "TAMPER_DETECTED",
        disclaimer="Application-level cryptographic SHA-256 fingerprint verification (Tamper Detection). Not a government PKI digital signature.",
        model_approval_reference=model_ref,
        tests_summary=tests_summary,
        message=(
            "Official Legal Metrology Verification record authenticated successfully with verified SHA-256 cryptographic fingerprint."
            if is_integrity_valid else
            "SECURITY ALERT: Record tampering detected! Stored certificate hash does not match computed ledger fingerprint."
        )
    )
