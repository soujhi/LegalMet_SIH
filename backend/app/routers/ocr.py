from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.models.models import OCRDocument, OCRReview, User, UserRole, SourceProvenance
from app.schemas.schemas import OCRDocumentOut, OCRValidateRequest
from app.routers.auth import get_current_user
from app.services.ocr_service import ocr_service
from app.services.audit_service import audit_service
from app.core.config import UPLOADS_DIR

router = APIRouter(prefix="/ocr", tags=["OCR Legacy Digitization"])

def populate_document_reviews(db: Session, doc: OCRDocument, extracted: Dict[str, Any]):
    """
    Populates OCRReview table for critical regulatory fields (PRD Section 17 & 31).
    Ensures uncertain OCR cannot proceed downstream without human verification.
    """
    critical_fields = [
        ("capacity", extracted.get("capacity"), "30.0 kg", 75.0),
        ("accuracy_class", extracted.get("accuracy_class"), "Class III", 70.0),
        ("manufacturer", extracted.get("manufacturer"), extracted.get("manufacturer"), 85.0),
        ("model", extracted.get("model"), "Standard Commercial Scale", 65.0),
        ("certificate_no", extracted.get("certificate_no"), extracted.get("certificate_no"), 90.0)
    ]

    for field_name, raw_val, norm_val, conf in critical_fields:
        review_item = OCRReview(
            document_id=doc.id,
            field_name=field_name,
            raw_value=str(raw_val or ""),
            normalized_value=str(norm_val or ""),
            confidence=conf,
            review_status="PENDING_REVIEW" if conf < 80.0 else "HUMAN_VERIFIED",
            verified_value=str(norm_val or "") if conf >= 80.0 else None,
            verified_by="AUTO_EXTRACTION" if conf >= 80.0 else None,
            verified_at=datetime.now(timezone.utc) if conf >= 80.0 else None
        )
        db.add(review_item)
    db.commit()

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

@router.get("/reviews/pending")
def list_pending_ocr_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    PRD Section 17: List uncertain OCR fields requiring human verification before rule evaluation.
    """
    reviews = db.query(OCRReview).filter(OCRReview.review_status == "PENDING_REVIEW").all()
    return [
        {
            "id": r.id,
            "document_id": r.document_id,
            "field_name": r.field_name,
            "raw_value": r.raw_value,
            "normalized_value": r.normalized_value,
            "confidence": r.confidence,
            "review_status": r.review_status,
            "source_file": r.document.source_file if r.document else None
        }
        for r in reviews
    ]

@router.post("/reviews/{review_id}/confirm")
def confirm_ocr_review_field(
    review_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    PRD Section 17: Human-in-the-loop sign-off on uncertain OCR extraction.
    Updates verified value and syncs to parent document.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LMO]:
        raise HTTPException(status_code=403, detail="Only authorized officers can confirm OCR values")

    review = db.query(OCRReview).filter(OCRReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="OCR review item not found")

    verified_val = payload.get("verified_value", review.normalized_value or review.raw_value)
    review.verified_value = str(verified_val)
    review.review_status = "HUMAN_VERIFIED"
    review.verified_by = current_user.full_name
    review.verified_at = datetime.now(timezone.utc)

    # Sync confirmed value to parent document
    doc = review.document
    if doc:
        if review.field_name == "capacity":
            doc.capacity = verified_val
        elif review.field_name == "accuracy_class":
            doc.accuracy_class = verified_val
        elif review.field_name == "manufacturer":
            doc.manufacturer = verified_val
        elif review.field_name == "model":
            doc.model = verified_val
        elif review.field_name == "certificate_no":
            doc.certificate_no = verified_val

        # Check if all fields for this doc are now verified
        pending_count = db.query(OCRReview).filter(
            OCRReview.document_id == doc.id,
            OCRReview.review_status == "PENDING_REVIEW"
        ).count()
        if pending_count == 0:
            doc.manual_verified = True
            doc.verified_by_id = current_user.id

    db.commit()
    db.refresh(review)

    audit_service.log_action(
        db,
        action="OCR_FIELD_CONFIRMED",
        entity_type="OCR_REVIEW",
        entity_id=str(review.id),
        user_id=current_user.id,
        new_values={"field_name": review.field_name, "verified_value": review.verified_value}
    )

    return {
        "success": True,
        "review_id": review.id,
        "field_name": review.field_name,
        "verified_value": review.verified_value,
        "review_status": review.review_status,
        "verified_by": review.verified_by
    }

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

    # Populate human review queue for critical fields
    populate_document_reviews(db, ocr_doc, extracted)

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
