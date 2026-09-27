from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.models.models import (
    Instrument, Application, Certificate, VerificationSession, VerificationResult,
    RiskFlag, OCRDocument, User, UserRole, CertificateVerificationLog
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

@router.get("/dashboard")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    in_30_days = now + timedelta(days=30)

    total_instruments = db.query(Instrument).count()
    total_applications = db.query(Application).count()
    pending_scrutiny = db.query(Application).filter(Application.status == "SUBMITTED").count()
    assigned_inspections = db.query(Application).filter(Application.status.in_(["ASSIGNED", "SCHEDULED"])).count()
    
    total_certificates = db.query(Certificate).count()
    valid_certificates = db.query(Certificate).filter(Certificate.status == "VALID").count()
    
    # Expiry alerts
    expiring_soon = db.query(Certificate).filter(
        Certificate.status == "VALID",
        Certificate.valid_until <= in_30_days,
        Certificate.valid_until >= now
    ).count()

    # Pass vs Fail counts
    passed_sessions = db.query(VerificationSession).filter(VerificationSession.overall_result == VerificationResult.PASS).count()
    failed_sessions = db.query(VerificationSession).filter(VerificationSession.overall_result == VerificationResult.FAIL).count()

    # Risk flags
    total_risk_flags = db.query(RiskFlag).filter(RiskFlag.is_resolved == False).count()

    # OCR records
    total_ocr_docs = db.query(OCRDocument).count()
    verified_ocr_docs = db.query(OCRDocument).filter(OCRDocument.manual_verified == True).count()

    # Public verification scans
    total_public_scans = db.query(CertificateVerificationLog).count()

    # Monthly distribution demo data
    monthly_trend = [
        {"month": "May", "inspections": 18, "passed": 17, "failed": 1},
        {"month": "Jun", "inspections": 24, "passed": 22, "failed": 2},
        {"month": "Jul", "inspections": 31, "passed": 29, "failed": 2},
        {"month": "Aug", "inspections": 42, "passed": 39, "failed": 3},
        {"month": "Sep", "inspections": max(total_applications, 45), "passed": max(passed_sessions, 40), "failed": max(failed_sessions, 5)},
    ]

    district_breakdown = [
        {"district": "Hazaribagh (Barhi)", "instruments": max(total_instruments, 48), "compliance_rate": "95.2%"},
        {"district": "Ranchi", "instruments": 64, "compliance_rate": "96.8%"},
        {"district": "Dhanbad", "instruments": 52, "compliance_rate": "92.4%"},
        {"district": "Bokaro", "instruments": 38, "compliance_rate": "94.0%"},
        {"district": "East Singhbhum (Jamshedpur)", "instruments": 45, "compliance_rate": "97.1%"},
    ]

    return {
        "summary": {
            "total_instruments": total_instruments,
            "total_applications": total_applications,
            "pending_scrutiny": pending_scrutiny,
            "assigned_inspections": assigned_inspections,
            "total_certificates": total_certificates,
            "valid_certificates": valid_certificates,
            "expiring_soon": expiring_soon,
            "passed_verifications": passed_sessions,
            "failed_verifications": failed_sessions,
            "total_risk_flags": total_risk_flags,
            "ocr_digitized_total": total_ocr_docs,
            "ocr_verified_count": verified_ocr_docs,
            "total_public_scans": total_public_scans
        },
        "monthly_trend": monthly_trend,
        "district_breakdown": district_breakdown
    }
