from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import random
import uuid

from app.core.database import get_db
from app.models.models import (
    Application, ApplicationStatus, ApplicationStatusHistory, VerificationSession,
    VerificationTest, VerificationResult, Certificate, CertificateStatus,
    Instrument, Officer, User, UserRole, RiskFlag
)
from app.schemas.schemas import (
    VerificationStartRequest, VerificationCompleteRequest, ApplicationOut, CertificateOut
)
from app.routers.auth import get_current_user
from app.services.rule_engine import rule_engine
from app.services.certificate_generator import certificate_generator
from app.services.audit_service import audit_service
from app.core.config import settings

router = APIRouter(prefix="/verification", tags=["Field Verification"])

@router.post("/start/{application_id}")
def start_verification(
    application_id: int,
    req: VerificationStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LMO, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only LMO officers or Admins can start verification sessions")

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    officer = current_user.officer_profile
    if not officer:
        # Fallback if admin starts verification
        officer = db.query(Officer).first()

    now = datetime.now(timezone.utc)
    
    # Check or create session
    session = db.query(VerificationSession).filter(VerificationSession.application_id == application_id).first()
    if not session:
        session = VerificationSession(
            application_id=app.id,
            officer_id=officer.id,
            started_at=now,
            latitude=req.latitude or 24.3015,
            longitude=req.longitude or 85.4228,
            location_accuracy=req.location_accuracy or 5.0,
            location_address=req.location_address or "Barhi Market Yard, Hazaribagh",
            device_timestamp=req.device_timestamp or now,
            overall_result=VerificationResult.IN_PROGRESS
        )
        db.add(session)
    else:
        session.started_at = now
        session.latitude = req.latitude or session.latitude or 24.3015
        session.longitude = req.longitude or session.longitude or 85.4228
        session.device_timestamp = req.device_timestamp or now

    old_status = app.status.value
    app.status = ApplicationStatus.FIELD_VERIFICATION
    app.updated_at = now

    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=ApplicationStatus.FIELD_VERIFICATION.value,
        remarks=f"Field verification started by {current_user.full_name} with GPS lock ({session.latitude}, {session.longitude}).",
        changed_by_id=current_user.id
    )
    db.add(hist)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "application_id": app.id,
        "status": app.status.value,
        "started_at": session.started_at,
        "location": {
            "latitude": session.latitude,
            "longitude": session.longitude,
            "address": session.location_address
        }
    }

@router.post("/{application_id}/complete")
def complete_verification(
    application_id: int,
    req: VerificationCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LMO, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only LMO officers or Admins can submit verification results")

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    session = db.query(VerificationSession).filter(VerificationSession.application_id == application_id).first()
    if not session:
        officer = current_user.officer_profile or db.query(Officer).first()
        session = VerificationSession(
            application_id=app.id,
            officer_id=officer.id,
            started_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.flush()

    inst = app.instrument
    accuracy_class = inst.accuracy_class or "Class III"
    capacity = inst.capacity
    scale_interval_e = inst.verification_scale_interval or 5.0
    unit = inst.unit or "kg"

    # Evaluate each observation through deterministic rule engine
    is_overall_pass = True
    recorded_tests = []
    
    # Clear any previous test observations for this session
    db.query(VerificationTest).filter(VerificationTest.session_id == session.id).delete()

    for obs in req.observations:
        eval_res = rule_engine.evaluate_test(
            accuracy_class=accuracy_class,
            capacity=capacity,
            scale_interval_e=scale_interval_e,
            test_load=obs.test_load,
            observed_value=obs.observed_value,
            test_type=obs.test_type,
            unit=obs.unit or unit
        )

        test_record = VerificationTest(
            session_id=session.id,
            test_name=obs.test_name,
            test_type=obs.test_type,
            test_load=obs.test_load,
            expected_value=obs.expected_value,
            observed_value=obs.observed_value,
            unit=obs.unit or unit,
            tolerance_mpe=eval_res["tolerance_mpe"],
            error_calculated=eval_res["error_calculated"],
            result=eval_res["result"],
            remarks=obs.remarks or eval_res["explanation"]
        )
        db.add(test_record)
        recorded_tests.append(eval_res)

        if eval_res["result"] == VerificationResult.FAIL:
            is_overall_pass = False

    now = datetime.now(timezone.utc)
    session.completed_at = now
    session.overall_result = VerificationResult.PASS if is_overall_pass else VerificationResult.FAIL
    session.remarks = req.remarks
    session.photos_json = req.photos or [
        "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=400&q=80"
    ]
    session.signature_data = req.signature_data
    if req.latitude:
        session.latitude = req.latitude
    if req.longitude:
        session.longitude = req.longitude
    if req.location_address:
        session.location_address = req.location_address

    old_status = app.status.value
    created_cert = None

    if is_overall_pass:
        app.status = ApplicationStatus.PASSED
        db.flush()

        # Generate Certificate
        cert_num = f"LM/JH/{now.strftime('%Y')}/{random.randint(100000, 999999)}"
        valid_until = now + timedelta(days=365)
        qr_token = str(uuid.uuid4())
        
        # Link for public verification
        qr_verification_url = f"{settings.FRONTEND_URL}/verify/{cert_num}"

        inst_dict = {
            "organization_name": app.applicant.organization.name if app.applicant.organization else "Trading Concern",
            "location": session.location_address or inst.location or "Barhi Sub-Division",
            "category_name": inst.category.name if inst.category else "Non-Automatic Weighing Instrument",
            "manufacturer": inst.model.manufacturer if inst.model else "Nilkanth Digital Scale CO.",
            "brand": inst.model.brand if inst.model else "NK SCALE",
            "model_series": inst.model.model_series if inst.model else "NKTT-30",
            "serial_number": inst.serial_number,
            "asset_number": inst.asset_number or "N/A",
            "capacity": inst.capacity,
            "unit": inst.unit,
            "verification_scale_interval": inst.verification_scale_interval,
            "accuracy_class": inst.accuracy_class
        }

        officer_name = current_user.full_name

        pdf_path, qr_path, cert_hash = certificate_generator.generate_pdf_certificate(
            certificate_number=cert_num,
            instrument_dict=inst_dict,
            officer_name=officer_name,
            issue_date=now,
            valid_until=valid_until,
            verification_location=session.location_address or "Barhi Market Yard",
            tests_summary=recorded_tests,
            qr_url=qr_verification_url
        )

        cert = Certificate(
            certificate_number=cert_num,
            instrument_id=inst.id,
            application_id=app.id,
            verification_session_id=session.id,
            issue_date=now,
            valid_from=now,
            valid_until=valid_until,
            status=CertificateStatus.VALID,
            pdf_url=pdf_path,
            qr_token=qr_token,
            certificate_hash=cert_hash,
            issuing_officer_id=session.officer_id,
            issuing_officer_name=officer_name,
            verification_location=session.location_address or "Barhi Market Yard",
            remarks=req.remarks or "Verification completed and passed statutory limits."
        )
        db.add(cert)
        
        # Update instrument verified dates
        inst.last_verified_date = now
        inst.next_verification_date = valid_until
        inst.status = "VERIFIED"

        app.status = ApplicationStatus.CERTIFICATE_ISSUED
        created_cert = cert

        audit_service.send_notification(
            db,
            user_id=app.applicant_id,
            title="Verification Passed — Certificate Issued!",
            message=f"Certificate {cert_num} has been issued for your instrument {inst.serial_number}.",
            notification_type="CERTIFICATE_ISSUED",
            link_url=f"/certificates"
        )
    else:
        app.status = ApplicationStatus.FAILED
        inst.status = "VERIFICATION_FAILED"

        # Record Risk Flag
        risk = RiskFlag(
            instrument_id=inst.id,
            application_id=app.id,
            flag_type="TOLERANCE_ERROR_EXCEEDED",
            severity="HIGH",
            description=f"Field verification failed: Instrument {inst.serial_number} exceeded Maximum Permissible Error (MPE) during test observations."
        )
        db.add(risk)

        audit_service.send_notification(
            db,
            user_id=app.applicant_id,
            title="Verification Failed — Compliance Violation",
            message=f"Your instrument {inst.serial_number} failed statutory verification limits. Rectification required.",
            notification_type="VERIFICATION_FAILED",
            link_url=f"/applications/{app.id}"
        )

    # Status History
    hist = ApplicationStatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=app.status.value,
        remarks=f"Verification completed. Outcome: {session.overall_result.value}. {req.remarks or ''}",
        changed_by_id=current_user.id
    )
    db.add(hist)
    db.commit()

    audit_service.log_action(
        db,
        action="VERIFICATION_COMPLETED",
        entity_type="VERIFICATION_SESSION",
        entity_id=str(session.id),
        user_id=current_user.id,
        new_values={
            "result": session.overall_result.value,
            "certificate_number": created_cert.certificate_number if created_cert else None
        }
    )

    return {
        "success": True,
        "application_id": app.id,
        "status": app.status.value,
        "overall_result": session.overall_result.value,
        "certificate_number": created_cert.certificate_number if created_cert else None,
        "pdf_url": created_cert.pdf_url if created_cert else None,
        "tests": recorded_tests
    }
