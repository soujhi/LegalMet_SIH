from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pathlib import Path

from app.core.database import get_db
from app.models.models import Certificate, User, UserRole, Instrument
from app.schemas.schemas import CertificateOut
from app.routers.auth import get_current_user
from app.core.config import CERTIFICATES_DIR

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("", response_model=List[CertificateOut])
def list_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Certificate)
    if current_user.role == UserRole.TRADER:
        q = q.join(Instrument).filter(Instrument.organization_id == current_user.organization_id)
    return q.order_by(Certificate.issue_date.desc()).all()

@router.get("/{id}", response_model=CertificateOut)
def get_certificate(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cert = db.query(Certificate).filter(Certificate.id == id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert

@router.get("/{id}/pdf")
def download_certificate_pdf(
    id: int,
    db: Session = Depends(get_db)
):
    cert = db.query(Certificate).filter(Certificate.id == id).first()
    if not cert or not cert.pdf_url:
        raise HTTPException(status_code=404, detail="Certificate PDF not found")
    
    filename = Path(cert.pdf_url).name
    file_path = CERTIFICATES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file missing on server storage")

    return FileResponse(
        path=str(file_path),
        filename=f"LegalMet_Certificate_{cert.certificate_number.replace('/', '_')}.pdf",
        media_type="application/pdf"
    )
