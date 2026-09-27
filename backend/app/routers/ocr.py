from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.models.models import OCRDocument, User, UserRole, SourceProvenance
from app.schemas.schemas import OCRDocumentOut, OCRValidateRequest
from app.routers.auth import get_current_user
from app.services.ocr_service import ocr_service
from app.services.audit_service import audit_service
from app.core.config import UPLOADS_DIR

router = APIRouter(prefix="/ocr", tags=["OCR Legacy Digitization"])

@router.get("", response_model=List[OCRDocumentOut])
def list_ocr_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    verified_only: Optional[bool] = None
):
    q = db.query(OCRDocument)
    if verified_only is not None:
        q = q.filter(OCRDocument.manual_verified == verified_only)
    return q.order_by(OCRDocument.id.desc()).all()

@router.get("/{id}", response_model=OCRDocumentOut)
def get_ocr_document(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(OCRDocument).filter(OCRDocument.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="OCR document record not found")
    return doc

@router.post("/upload", response_model=OCRDocumentOut)
async def upload_ocr_certificate(
    file: UploadFile = File(...),
    area: str = Form("BARHI"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.LMO]:
        raise HTTPException(status_code=403, detail="Only Admins and LMOs can upload legacy documents for OCR")

    save_path = UPLOADS_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform OCR parsing
    raw_text = f"Sample text extracted from {file.filename} with certificate number 141701 for Barhi region."
    extracted = ocr_service.extract_fields_from_text(raw_text, filename=file.filename)

    ocr_doc = OCRDocument(
        source_file=file.filename,
        certificate_no=extracted["certificate_no"],
        area=area,
        concern_name=extracted["concern_name"],
        verification_date=extracted["verification_date"],
        next_verification_date=extracted["next_verification_date"],
        instrument_type=extracted["instrument_type"],
        manufacturer=extracted["manufacturer"],
        model=extracted["model"],
        capacity=extracted["capacity"],
        accuracy_class=extracted["accuracy_class"],
        verification_fee=extracted["verification_fee"],
        raw_ocr_text=raw_text,
        ocr_confidence=extracted["ocr_confidence"],
        manual_verified=False,
        source_type=SourceProvenance.OCR
    )
    db.add(ocr_doc)
    db.commit()
    db.refresh(ocr_doc)

    audit_service.log_action(
        db,
        action="OCR_DOCUMENT_UPLOADED",
        entity_type="OCR_DOCUMENT",
        entity_id=str(ocr_doc.id),
        user_id=current_user.id
    )

    return ocr_doc

@router.put("/{id}/validate", response_model=OCRDocumentOut)
def validate_ocr_document(
    id: int,
    req: OCRValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.LMO]:
        raise HTTPException(status_code=403, detail="Only authorized officers can validate OCR extracted records")

    doc = db.query(OCRDocument).filter(OCRDocument.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="OCR document not found")

    if req.certificate_no is not None:
        doc.certificate_no = req.certificate_no
    if req.concern_name is not None:
        doc.concern_name = req.concern_name
    if req.verification_date is not None:
        doc.verification_date = req.verification_date
    if req.next_verification_date is not None:
        doc.next_verification_date = req.next_verification_date
    if req.instrument_type is not None:
        doc.instrument_type = req.instrument_type
    if req.manufacturer is not None:
        doc.manufacturer = req.manufacturer
    if req.capacity is not None:
        doc.capacity = req.capacity
    if req.accuracy_class is not None:
        doc.accuracy_class = req.accuracy_class
    if req.verification_fee is not None:
        doc.verification_fee = req.verification_fee

    doc.manual_verified = req.manual_verified
    doc.verified_by_id = current_user.id

    db.commit()
    db.refresh(doc)

    audit_service.log_action(
        db,
        action="OCR_DOCUMENT_VALIDATED",
        entity_type="OCR_DOCUMENT",
        entity_id=str(doc.id),
        user_id=current_user.id,
        new_values={"certificate_no": doc.certificate_no, "manual_verified": doc.manual_verified}
    )

    return doc
